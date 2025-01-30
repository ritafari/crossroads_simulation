# priority_traffic.py (fixed)
import time
import random
import uuid
import logging
from multiprocessing import Process, Manager
from utils.message_queues import enqueue, create_queues
from utils.signals import SignalHandler
import os

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("priority_traffic")

DIRECTIONS = ["N", "S", "E", "W"]
EMERGENCY_TYPES = ["ambulance", "fire_truck", "police"]

def create_emergency_vehicle():
    """Creates a priority vehicle with complete attributes."""
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

def get_lights_pid():
    """Read PID from file created by lights process"""
    for _ in range(10):
        try:
            with open("lights.pid", "r") as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            time.sleep(1)
    raise RuntimeError("Failed to get lights PID")

def priority_traffic_gen(queues, interval, shutdown_flag):
    lights_pid = get_lights_pid()
    signal_handler = SignalHandler(lights_pid)
    
    while not shutdown_flag.is_set():
        while os.path.exists("lights.pid"):
            vehicle = create_emergency_vehicle()
            enqueue(queues, vehicle, vehicle["source"])
            signal_handler.notify_priority(vehicle)
                
            logger.warning(
                    f"EMERGENCY {vehicle['type']} {vehicle['id'][:8]} "
                    f"from {vehicle['source']}"
                )
                
            time.sleep(interval)

if __name__ == "__main__":
    # Initialize Manager context
    with Manager() as manager:
        shutdown_flag = manager.Event()
        queues = create_queues(manager)  # Use manager instance
        Process(target=priority_traffic_gen, args=(queues, 5, shutdown_flag )).start()