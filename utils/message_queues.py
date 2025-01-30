# Helper functions for message queue management

import logging
from multiprocessing import Manager
from queue import Empty, Full

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("message_queues")

def create_queues(manager):
    """Create queues using a Manager instance"""
    return manager.dict({
        "N": manager.Queue(),
        "S": manager.Queue(),
        "E": manager.Queue(),
        "W": manager.Queue()
    })

def enqueue(queues, vehicle, direction):
    try:
        queues[direction].put(vehicle)
        logger.info(f"Enqueued {vehicle['id'][:8]} to {direction}")
    except Exception as e:
        logger.error(f"Queue error: {str(e)}")

def dequeue(queue, direction):
    """Remove and return a vehicle from the specified direction queue."""
    try:
        item = queue[direction].get(timeout=1)
        logger.info(f"Dequeued vehicle {item['id']} from {direction} queue")
        return item
    except Empty:
        logger.debug(f"Queue {direction} is empty")
        return None