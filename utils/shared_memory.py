# Functions for managing shared memory

from multiprocessing import Manager

class SharedMemory:
    def __init__(self):
        self.manager = Manager()
        self.state = self.manager.dict({
            "lights": {"S": "GREEN", "N": "RED", "W": "RED", "E": "RED"}  # Default light states
        })

    def update_state(self, key, value):
        """Update the state in shared memory."""
        self.state[key] = value

    def get_state(self, key):
        """Retrieve a state from shared memory."""
        return self.state.get(key, None)


