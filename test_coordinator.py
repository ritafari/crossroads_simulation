#!/usr/bin/env python3
import time
import threading
from multiprocessing import Manager, Process
from multiprocessing.managers import SyncManager
import logging
from utils.message_queues import create_queues, enqueue
from utils.shared_memory import SharedMemory
from coordinator import Coordinator

# Set up logging with DEBUG level for more granular output.
logging.basicConfig(level=logging.DEBUG, format="%(name)s - %(message)s")
logger = logging.getLogger("test_E_light_change")

def enqueue_vehicle_E(queues):
    """
    Enqueues a single normal vehicle into the E queue.
    """
    vehicle_e = {
        "id": "vehE001",
        "type": "normal",
        "source": "E",
        "destination": "W",
        "timestamp": time.time(),
        "priority": False,
        "turn": "left"
    }
    enqueue(queues, vehicle_e, "E")
    logger.info("Enqueued vehicle vehE001 to E (this vehicle should wait initially).")

def force_E_light_to_green(shared_mem, delay: int):
    """
    Waits for 'delay' seconds and then changes the E light to GREEN.
    """
    logger.info(f"Will change E light to GREEN after {delay} seconds.")
    time.sleep(delay)
    shared_mem.set_light("E", "GREEN")
    logger.info("E light changed to GREEN.")

def poll_shared_state(shared_mem, duration: int):
    """
    Polls the shared memory state every 3 seconds for the given duration.
    """
    start = time.time()
    while time.time() - start < duration:
        current_vehicle = shared_mem.get_state("current_vehicle")
        event_logs = list(shared_mem.get_state("event_logs"))
        lights = shared_mem.get_light_state()
        logger.info(f"Polled state: Current vehicle: {current_vehicle}, Lights: {lights}, Event logs: {event_logs}")
        time.sleep(3)

def test_E_light_change():
    # Create a Manager instance
    manager: SyncManager = Manager()
    shutdown_flag = manager.Event()
    queues = {d: manager.Queue() for d in ["N", "S", "E", "W"]}
    shared_mem = SharedMemory(manager)
    
    # Set the initial light states
    shared_mem.set_light("N", "GREEN")
    shared_mem.set_light("S", "GREEN")
    shared_mem.set_light("E", "RED")   # Force E to be RED initially.
    shared_mem.set_light("W", "RED")
    
    # Enqueue the vehicle in E
    enqueue_vehicle_E(queues)
    
    # Create and start the Coordinator process
    coordinator = Coordinator(queues, shared_mem, shutdown_flag)
    coordinator_process = Process(target=coordinator.run, name="Coordinator")
    coordinator_process.start()
    logger.info("Coordinator process started.")
    
    # In parallel, force the E light to change to GREEN after 20 seconds
    threading.Thread(target=force_E_light_to_green, args=(shared_mem, 20), daemon=True).start()
    
    # Poll the shared state for 40 seconds so we can observe what happens
    poll_shared_state(shared_mem, duration=40)
    
    # Signal shutdown.
    shutdown_flag.set()
    coordinator_process.join(timeout=5)
    if coordinator_process.is_alive():
        logger.error("Coordinator did not shut down gracefully; terminating process.")
        coordinator_process.terminate()
    
    # Log the final state.
    final_state = {
        "current_vehicle": shared_mem.get_state("current_vehicle"),
        "lights": shared_mem.get_light_state(),
        "event_logs": list(shared_mem.get_state("event_logs"))
    }
    logger.info(f"Final state: {final_state}")
    manager.shutdown()
    logger.info("Test for E light change completed.")

if __name__ == "__main__":
    test_E_light_change()
