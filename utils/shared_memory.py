# Functions for managing shared memory

from multiprocessing import Manager

class SharedMemory:
    def __init__(self):
        self.manager = Manager()
        self.state = self.manager.dict({"lights": {}, "vehicles": {}})

    def update_state(self, key, value):
        self.state[key] = value

    def get_light_state(self, road):
        return self.state["lights"].get(road, False)

