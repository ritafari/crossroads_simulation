import logging
import time
from multiprocessing.managers import SyncManager
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shared_memory")

class SharedMemory:
    def __init__(self, manager: SyncManager):
        self.manager = manager
        self.lock = manager.Lock()
        self.state = self.manager.dict({
            "lights": {"N": "GREEN", "S": "GREEN", "E": "RED", "W": "RED"},
            "priority_mode": False,
            "priority_direction": None,
            "current_vehicle": None,
            "event_logs": manager.list()
        })
    
    def set_light(self, direction: str, color: str) -> None:
        with self.lock:
            if direction not in ["N", "S", "E", "W"]:
                raise ValueError("Invalid direction")
            self.state["lights"][direction] = color
            logger.info(f"Light {direction} set to {color}")
    
    def set_priority_mode(self, direction: str) -> None:
        with self.lock:
            self.state["priority_mode"] = True
            self.state["priority_direction"] = direction
            logger.info(f"Priority mode activated for {direction}")
    
    def reset_priority_mode(self) -> None:
        with self.lock:
            self.state["priority_mode"] = False
            self.state["priority_direction"] = None
            logger.info("Priority mode deactivated")
    
    def get_light_state(self) -> Dict[str, str]:
        with self.lock:
            return dict(self.state["lights"])
    
    def in_priority_mode(self) -> bool:
        with self.lock:
            return self.state["priority_mode"]
    
    def update_state(self, key: str, value: Any) -> None:
        with self.lock:
            self.state[key] = value
    
    def get_state(self, key: str) -> Any:
        with self.lock:
            return self.state.get(key)
    
    def append_event_log(self, event: str) -> None:
        with self.lock:
            current_time = time.time()
            logs = list(self.state["event_logs"])
            logs.append({"time": current_time, "msg": event})
            # Keep only the last 5 events.
            logs = logs[-5:]
            self.state["event_logs"].clear()
            for log in logs:
                self.state["event_logs"].append(log)
