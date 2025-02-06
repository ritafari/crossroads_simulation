#!/usr/bin/env python3
import time
import os
import signal
from multiprocessing import Manager, Process
from multiprocessing.managers import SyncManager
from utils.message_queues import create_queues
from priority_traffic import priority_traffic_gen
from utils.signals import SignalHandler
import logging

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("test_priority_traffic")

DUMMY_PID_FILE = "lights.pid"

def create_dummy_lights_pid():
    """Creates a dummy lights.pid file with the current process's PID."""
    pid = os.getpid()
    with open(DUMMY_PID_FILE, "w") as f:
        f.write(str(pid))
    logger.info(f"Dummy lights.pid created with PID {pid}")

def remove_dummy_lights_pid():
    """Removes the dummy lights.pid file if it exists."""
    if os.path.exists(DUMMY_PID_FILE):
        os.remove(DUMMY_PID_FILE)
        logger.info("Dummy lights.pid removed.")

def test_priority_signal(manager: SyncManager):
    """
    Tests that the SignalHandler properly sets the signal_received flag
    when notify_priority() is called.
    """
    # Create a dummy lights.pid file for this test
    create_dummy_lights_pid()
    try:
        # Read the dummy PID
        dummy_pid = int(open(DUMMY_PID_FILE, "r").read().strip())
        # Create a SignalHandler instance using the dummy PID and our manager.
        sh = SignalHandler(dummy_pid, manager)
        # Create a sample emergency vehicle
        sample_vehicle = {
            "id": "testVeh",
            "source": "N",
            "destination": "E",
            "priority": True,
            "timestamp": time.time(),
            "turn": "emergency"
        }
        # Call notify_priority on the sample vehicle.
        sh.notify_priority(sample_vehicle)
        # Allow some time for the signal to be processed.
        time.sleep(1)
        logger.info(f"After notify_priority, signal_received flag is: {sh.signal_received.value}")
        # Check that the flag is set.
        if sh.signal_received.value:
            logger.info("Priority signal was successfully sent and received.")
        else:
            logger.error("Priority signal was not received as expected.")
        # Reset the flag for cleanliness.
        sh.acknowledge_signal()
    finally:
        remove_dummy_lights_pid()

def main():
    # Create a single Manager instance.
    manager: SyncManager = Manager()
    # Create the shutdown flag using the Manager.
    shutdown_flag = manager.Event()
    # Create the directional queues.
    queues = create_queues()
    
    # Start the priority traffic generator process with an interval of 5 seconds.
    p = Process(target=priority_traffic_gen, args=(queues, 5, shutdown_flag, manager))
    p.start()
    logger.info("Priority traffic generator process started.")
    
    # Let the process run for a fixed amount of time.
    time.sleep(15)
    shutdown_flag.set()
    p.join(timeout=5)
    
    if p.is_alive():
        logger.error("Priority traffic generator did not shut down gracefully; terminating process.")
        p.terminate()
    
    # Check and log the content of each queue.
    for direction, queue in queues.items():
        size = queue.qsize()
        logger.info(f"Queue {direction} size: {size}")
        while not queue.empty():
            vehicle = queue.get()
            logger.info(f"Vehicle in queue {direction}: {vehicle}")
    
    # Test the priority signal separately.
    test_priority_signal(manager)
    
    manager.shutdown()
    logger.info("Test for priority traffic generator completed.")

if __name__ == "__main__":
    main()
