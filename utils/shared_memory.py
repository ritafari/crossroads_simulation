# Functions for managing shared memory
# shared_memory.py
import logging
from multiprocessing import Manager, Lock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shared_memory")

class SharedMemory:
    def __init__(self, manager):
        self.manager = manager
        self.lock = Lock()
        self.state = self.manager.dict({
            "lights": {"N": "GREEN", "S": "GREEN", "E": "RED", "W": "RED"},
            "priority_mode": False,
            "priority_direction": None
        })

    def set_light(self, direction, color):
        """Set individual light state"""
        with self.lock:
            if direction not in ["N", "S", "E", "W"]:
                raise ValueError("Invalid direction")
            self.state["lights"][direction] = color
            logger.info(f"Light {direction} set to {color}")

    def set_priority_mode(self, direction):
        """Activate priority for a specific direction"""
        with self.lock:
            self.state["priority_mode"] = True
            self.state["priority_direction"] = direction
            logger.info(f"Priority mode activated for {direction}")

    def reset_priority_mode(self):
        with self.lock:
            self.state["priority_mode"] = False
            self.state["priority_direction"] = None
            logger.info("Priority mode deactivated")

    def get_light_state(self):
        """Return full light state"""
        with self.lock:
            return dict(self.state["lights"])

    def in_priority_mode(self):
        """Check if system is in priority mode."""
        with self.lock:
            return self.state["priority_mode"]
        
    def update_state(self, key, value):
        with self.lock:
            self.state[key] = value
            
    def get_state(self, key):
        with self.lock:
            return self.state.get(key)
