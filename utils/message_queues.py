import logging
from multiprocessing import Queue, Manager
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("message_queues")

"""
def create_queues(manager: SyncManager) -> Dict[str, Queue]:
    return manager.dict({
        "N": manager.Queue(),
        "S": manager.Queue(),
        "E": manager.Queue(),
        "W": manager.Queue()
    })

def enqueue(queues: Dict[str, Queue], vehicle: dict, direction: str) -> None:
    try:
        queues[direction].put(vehicle)
        logger.info(f"Enqueued {vehicle['id'][:8]} to {direction}")
    except Exception as e:
        logger.error(f"Queue error: {str(e)}")

        
ISSUES: 
-------------------------------------------------------------------------------
manager.dict() does not work well with Queue()
    - Queue() objects cannot be stored inside a manager.dict() because multiprocessing.Queue() is not shareable via manager.dict().
    - Fix: Use a regular dictionary with Queue() objects directly.
Ensure direction is valid before enqueueing
    - The function should check if the direction is one of ["N", "S", "E", "W"].
"""

def create_queues() -> Dict[str, Queue]:
    """
    Creates a dictionary of queues for each direction.
    Returns a dictionary containing multiprocessing.Queue() objects.
    """
    return {
        "N": Queue(),
        "S": Queue(),
        "E": Queue(),
        "W": Queue()
    }

def enqueue(queues: Dict[str, Queue], vehicle: dict, direction: str) -> None:
    """
    Enqueues a vehicle into the specified direction's queue.
    
    :param queues: Dictionary of queues for each direction.
    :param vehicle: Dictionary representing the vehicle with an 'id' key.
    :param direction: Direction ('N', 'S', 'E', 'W') where the vehicle should be enqueued.
    """
    try:
        if direction not in queues:
            raise ValueError(f"Invalid direction '{direction}' (must be N, S, E, or W)")

        if "id" not in vehicle:
            raise KeyError("Vehicle dictionary missing 'id' key")

        queues[direction].put(vehicle)
        logger.info(f"🚗 Enqueued vehicle {vehicle['id']} to {direction}")

    except (KeyError, ValueError) as e:
        logger.error(f"Enqueue error: {e}")
    except Exception as e:
        logger.error(f"Unexpected queue error: {e}")
