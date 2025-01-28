# Functions for managing shared memory

from multiprocessing import Manager, Lock

class SharedMemory:
    def __init__(self):
        self.manager = Manager()
        self.lock = Lock()  # Lock for thread/process safety
        self.state = self.manager.dict({
            "lights": {"S": "GREEN", "N": "RED", "W": "RED", "E": "RED"}  # Default light states
        })
        

    def update_state(self, key, value):
        """Update the state in shared memory."""
        with self.lock:  # Ensure atomic update
            if key in self.state:
                self.state[key] = value
            else:
                # Automatically initialize missing keys instead of failing
                self.state[key] = value
                print(f"Key {key} not found in shared memory. Initializing...")


    def get_state(self, key):
        """Retrieve a state from shared memory."""
        with self.lock:  # Ensure atomic access
            return self.state.get(key, None)


