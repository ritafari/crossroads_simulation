import time
import random
import uuid
import logging
from multiprocessing import Process, Manager, Event
from multiprocessing.managers import SyncManager
from utils.message_queues import enqueue, create_queues
from utils.signals import SignalHandler
import os

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("priority_traffic")

DIRECTIONS = ["N", "S", "E", "W"]
EMERGENCY_TYPES = ["ambulance", "fire_truck", "police"]


def create_emergency_vehicle() -> dict:
    source = random.choice(DIRECTIONS)
    possible_destinations = [d for d in DIRECTIONS if d != source]
    return {
        "id": str(uuid.uuid4()),
        "type": random.choice(EMERGENCY_TYPES),
        "source": source,
        "destination": random.choice(possible_destinations),
        "timestamp": time.time(),
        "priority": True,
        "turn": "emergency"
    }


def get_lights_pid() -> int:
    timeout = 10  # Maximum time to wait for the PID file, adding a timeout to avoid infinite retries.
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with open("lights.pid", "r") as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            time.sleep(1)
    raise RuntimeError("Failed to get lights PID within the timeout period")


def priority_traffic_gen(queues, interval: float, shutdown_flag) -> None:
    try:
        lights_pid = get_lights_pid()
        signal_handler = SignalHandler(lights_pid)
        while not shutdown_flag.is_set():
            if not os.path.exists("lights.pid"):
                logger.error("Lights process not running. Exiting priority traffic generator.")
                break
            vehicle = create_emergency_vehicle()
            vehicle = {"id": f"P{int(time.time() * 1000)}", "source": "N", "destination": "S", "priority": True} #m
            queues["N"].put(vehicle) #m
            logger.info(f"Priority vehicle added: {vehicle}")  # Logging the vehicle addition #m
            time.sleep(interval) #m
            try:
                enqueue(queues, vehicle, vehicle["source"])
                signal_handler.notify_priority(vehicle)
                logger.warning(f"EMERGENCY {vehicle['type']} {vehicle['id'][:8]} from {vehicle['source']}")
            except Exception as e:
                logger.error(f"Failed to enqueue emergency vehicle {vehicle['id'][:8]}: {e}")
            # Sleep in smaller increments to check the shutdown flag more frequently
            for _ in range(int(interval * 10)):
                if shutdown_flag.is_set():
                    break
                time.sleep(0.1)
    except Exception as e:
        logger.error(f"Error in priority traffic generator: {e}")


if __name__ == "__main__":
    from multiprocessing import Manager, Event
    from multiprocessing.managers import SyncManager
    manager: SyncManager = Manager()
    shutdown_flag = Event()
    queues = create_queues(manager)
    p = Process(target=priority_traffic_gen, args=(queues, 5, shutdown_flag))
    p.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down priority traffic generator...")
        shutdown_flag.set()
        p.join(timeout=5)  # Wait for the process to finish gracefully
        if p.is_alive():
            p.terminate()
    finally:
        if p.is_alive():
            p.terminate()
        manager.shutdown()
