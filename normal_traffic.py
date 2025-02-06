import time
import random
import uuid
import logging
from multiprocessing import Process
from multiprocessing.managers import SyncManager
from utils.message_queues import enqueue, create_queues

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("normal_traffic")

DIRECTIONS = ["N", "S", "E", "W"]
DIRECTION_MAP = {
    ("N", "E"): "right",
    ("N", "W"): "left",
    ("S", "E"): "left",
    ("S", "W"): "right",
    ("E", "N"): "left",
    ("E", "S"): "right",
    ("W", "N"): "right",
    ("W", "S"): "left"
}

def create_vehicle() -> dict:
    source = random.choice(DIRECTIONS)
    possible_destinations = [d for d in DIRECTIONS if d != source]
    destination = random.choice(possible_destinations)
    if (source, destination) in [("N", "S"), ("S", "N"), ("E", "W"), ("W", "E")]:
        turn = "straight"
    else:
        turn = DIRECTION_MAP.get((source, destination), "unknown")
    return {
        "id": str(uuid.uuid4()),
        "type": "normal",
        "source": source,
        "destination": destination,
        "timestamp": time.time(),
        "priority": False,
        "turn": turn
    }

def normal_traffic_gen(queues, interval: float, shutdown_flag, max_vehicles: int = None) -> None:
    logger.info("🚗 normal_traffic_gen started.")
    count = 0
    while not shutdown_flag.is_set():
        if max_vehicles and count >= max_vehicles:
            logger.info("Reached maximum vehicle count")
            break

        # Use the create_vehicle() function to generate a vehicle.
        vehicle = create_vehicle()
        # Enqueue the vehicle based on its source.
        enqueue(queues, vehicle, vehicle["source"])
        logger.info(f"Generated normal vehicle {vehicle['id'][:8]} from {vehicle['source']} to {vehicle['destination']} (turn: {vehicle['turn']})")
        
        count += 1
        # Sleep for the main interval.
        sleep_time = interval
        # Instead of a single sleep, we check shutdown_flag in small increments.
        increments = int(sleep_time * 10)
        for _ in range(increments):
            if shutdown_flag.is_set():
                break
            time.sleep(sleep_time / increments)

if __name__ == "__main__":
    from multiprocessing import Manager
    manager: SyncManager = Manager()
    # Use manager.Event() for consistency.
    shutdown_flag = manager.Event()
    queues = create_queues(manager)
    
    process = Process(target=normal_traffic_gen, args=(queues, 2, shutdown_flag))
    try:
        process.start()
        logger.info("Normal traffic generator started")
        process.join()
    except KeyboardInterrupt:
        logger.info("Shutting down traffic generator...")
        shutdown_flag.set()
        process.join(timeout=5)  # Wait for graceful shutdown.
        if process.is_alive():
            process.terminate()
    finally:
        if process.is_alive():
            process.terminate()
        manager.shutdown()  # Shut down the manager to release resources.
