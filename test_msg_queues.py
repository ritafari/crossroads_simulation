import time
from utils.message_queues import create_queues, enqueue
import logging

# Set up logging to see output on the console.
logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("test_message_queues")

def main():
    # Create the queues.
    queues = create_queues()
    
    # Create a sample vehicle.
    sample_vehicle = {
        "id": "veh123456789",
        "type": "normal",
        "source": "N",
        "destination": "E",
        "turn": "straight",
        "timestamp": time.time(),
        "priority": False
    }
    
    # Enqueue the vehicle in the 'N' direction.
    enqueue(queues, sample_vehicle, "N")
    
    # Check the size of the queue for 'N'.
    size_N = queues["N"].qsize()
    logger.info(f"Queue size for 'N' after enqueueing: {size_N}")
    
    # Dequeue the vehicle to verify it is the same.
    if size_N > 0:
        retrieved_vehicle = queues["N"].get()
        logger.info(f"Retrieved vehicle: {retrieved_vehicle}")
        if retrieved_vehicle == sample_vehicle:
            logger.info("Test passed: The enqueued vehicle was successfully retrieved.")
        else:
            logger.error("Test failed: Retrieved vehicle does not match the enqueued one.")
    else:
        logger.error("Test failed: No vehicle found in the 'N' queue.")

if __name__ == "__main__":
    main()
