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
    for _ in range(10):
        try:
            with open("lights.pid", "r") as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            time.sleep(1)
    raise RuntimeError("Failed to get lights PID")

def priority_traffic_gen(queues, interval: float, shutdown_flag) -> None:
    lights_pid = get_lights_pid()
    signal_handler = SignalHandler(lights_pid)
    while not shutdown_flag.is_set():
        if os.path.exists("lights.pid"):
            vehicle = create_emergency_vehicle()
            enqueue(queues, vehicle, vehicle["source"])
            signal_handler.notify_priority(vehicle)
            logger.warning(f"EMERGENCY {vehicle['type']} {vehicle['id'][:8]} from {vehicle['source']}")
            time.sleep(interval)
        else:
            logger.error("Lights process not running. Exiting priority traffic generator.")
            break

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
        shutdown_flag.set()
    p.join()
