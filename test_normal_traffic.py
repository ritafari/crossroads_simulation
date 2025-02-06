#!/usr/bin/env python3
import time
from multiprocessing import Manager, Process
from multiprocessing.managers import SyncManager
from utils.message_queues import create_queues, enqueue
from normal_traffic import normal_traffic_gen
import logging

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("test_normal_traffic")

def main():
    # Create a single Manager instance.
    manager: SyncManager = Manager()
    # Create the shutdown flag using the Manager.
    shutdown_flag = manager.Event()
    
    # Create the directional queues (create_queues() takes no parameters).
    queues = create_queues()
    
    # Start the normal traffic generator process with a limit of 5 vehicles.
    process = Process(target=normal_traffic_gen, args=(queues, 2, shutdown_flag, 5))
    process.start()
    logger.info("Normal traffic generator process started.")
    
    # Wait for the generator process to finish.
    process.join(timeout=15)
    
    # If the process is still running after the timeout, shut it down.
    if process.is_alive():
        logger.error("Normal traffic generator did not finish in time; terminating process.")
        shutdown_flag.set()
        process.terminate()
    
    # After the process terminates, check the queues.
    for direction, queue in queues.items():
        size = queue.qsize()
        logger.info(f"Queue {direction} size: {size}")
        while not queue.empty():
            vehicle = queue.get()
            logger.info(f"Vehicle in queue {direction}: {vehicle}")
    
    # Shutdown the Manager to free resources.
    manager.shutdown()
    logger.info("Test for normal traffic generator completed.")

if __name__ == "__main__":
    main()
