import logging
from multiprocessing.managers import SyncManager
from multiprocessing import Queue
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("message_queues")

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
