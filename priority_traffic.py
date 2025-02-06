import time
import random
import uuid
import logging
import os
import signal
from multiprocessing import Process
from multiprocessing.managers import SyncManager
from utils.message_queues import enqueue, create_queues
from utils.signals import SignalHandler

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("priority_traffic")

DIRECTIONS = ["N", "S", "E", "W"]
EMERGENCY_TYPES = ["ambulance", "fire_truck", "police"]

def create_emergency_vehicle() -> dict:
    source = random.choice(DIRECTIONS)
    possible_destinations = [d for d in DIRECTIONS if d != source]
    destination = random.choice(possible_destinations)
    return {
        "id": str(uuid.uuid4()),
        "type": random.choice(EMERGENCY_TYPES),
        "source": source,
        "destination": destination,
        "timestamp": time.time(),
        "priority": True,
        "turn": "emergency"
    }

def get_lights_pid() -> int:
    timeout = 10  # Maximum time to wait for the PID file
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with open("lights.pid", "r") as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            time.sleep(1)
    raise RuntimeError("Failed to get lights PID within the timeout period")

def priority_traffic_gen(queues, interval: float, shutdown_flag, manager: SyncManager) -> None:
    try:
        lights_pid = get_lights_pid()
        # Pass the manager to the SignalHandler
        signal_handler = SignalHandler(lights_pid, manager)
        while not shutdown_flag.is_set():
            if not os.path.exists("lights.pid"):
                logger.error("Lights process not running. Exiting priority traffic generator.")
                break
            vehicle = create_emergency_vehicle()
            # Enqueue the emergency vehicle using the helper function.
            enqueue(queues, vehicle, vehicle["source"])
            logger.info(f"Priority vehicle added: {vehicle}")
            try:
                signal_handler.notify_priority(vehicle)
                logger.warning(f"EMERGENCY {vehicle['type']} {vehicle['id'][:8]} from {vehicle['source']}")
            except Exception as e:
                logger.error(f"Failed to notify priority for vehicle {vehicle['id'][:8]}: {e}")
            sleep_time = interval
            increments = int(sleep_time * 10)
            for _ in range(increments):
                if shutdown_flag.is_set():
                    break
                time.sleep(sleep_time / increments)
    except Exception as e:
        logger.error(f"Error in priority traffic generator: {e}")

if __name__ == "__main__":
    from multiprocessing import Manager, Event
    from multiprocessing.managers import SyncManager
    manager: SyncManager = Manager()
    shutdown_flag = manager.Event()
    queues = create_queues()
    # Pass the manager as an extra argument.
    p = Process(target=priority_traffic_gen, args=(queues, 5, shutdown_flag, manager))
    p.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down priority traffic generator...")
        shutdown_flag.set()
        p.join(timeout=5)
        if p.is_alive():
            p.terminate()
    finally:
        if p.is_alive():
            p.terminate()
        manager.shutdown()
