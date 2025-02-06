#!/usr/bin/env python3
import time
import os
import signal
import logging
from multiprocessing import Manager, Process
from multiprocessing.managers import SyncManager
from utils.shared_memory import SharedMemory
from lights import TrafficLights

logging.basicConfig(level=logging.INFO, format="%(name)s - %(process)d - %(message)s")
logger = logging.getLogger("test_lights")

def poll_shared_memory(shared_mem: SharedMemory, duration: int = 20):
    """
    Polls the shared memory for a given duration and logs the current traffic lights state.
    """
    start_time = time.time()
    while time.time() - start_time < duration:
        lights = shared_mem.get_light_state()
        logger.info(f"Polled lights state: {lights}")
        time.sleep(3)  # Poll every 3 seconds

def simulate_emergency():
    """
    Reads the lights.pid file and sends a SIGUSR1 signal to simulate an emergency.
    """
    try:
        with open("lights.pid", "r") as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGUSR1)
        logger.info("Simulated emergency signal (SIGUSR1) sent to TrafficLights process.")
    except Exception as e:
        logger.error(f"Failed to simulate emergency: {e}")

def test_lights():
    # Create a single Manager instance.
    manager: SyncManager = Manager()
    # Create the shutdown flag using the Manager.
    shutdown_flag = manager.Event()
    
    # Create shared memory.
    shared_mem = SharedMemory(manager)
    
    # Instantiate the TrafficLights process.
    lights_instance = TrafficLights(shared_mem, shutdown_flag)
    lights_process = Process(target=lights_instance.run, name="TrafficLights")
    
    # Start the lights process.
    lights_process.start()
    logger.info("TrafficLights process started.")
    
    # Poll the shared memory for normal operation.
    logger.info("Polling shared memory during normal operation...")
    poll_shared_memory(shared_mem, duration=15)
    
    # Simulate an emergency after 15 seconds.
    simulate_emergency()
    
    # Poll the shared memory for additional 15 seconds to observe emergency mode.
    logger.info("Polling shared memory during emergency mode...")
    poll_shared_memory(shared_mem, duration=15)
    
    # Signal shutdown and wait for the lights process to exit.
    shutdown_flag.set()
    lights_process.join(timeout=5)
    if lights_process.is_alive():
        logger.error("TrafficLights process did not shut down gracefully; terminating.")
        lights_process.terminate()
    
    # Final poll to see the lights state after shutdown.
    final_state = shared_mem.get_light_state()
    logger.info(f"Final lights state after shutdown: {final_state}")
    
    manager.shutdown()
    logger.info("Test for TrafficLights completed.")

if __name__ == "__main__":
    try:
        test_lights()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, exiting test.")
