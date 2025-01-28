# Traffic light control logic
"""
changes the color of the lights at regular intervals in normal mode, it is notified by the signal handler
if there is a priority vehicle to set the lights to the appropriate color.
"""

import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

class Lights:
    def __init__(self, shared_memory, signal_handler):
        self.shared_memory = shared_memory
        self.signal_handler = signal_handler
        self.state = {"S": "GREEN", "N": "RED", "W": "RED", "E": "RED"}  # Initial state
        self.last_switch_time = time.time()

    def toggle_lights(self):
        """Toggle normal light cycle."""
        if self.state["S"] == "GREEN":
            self.state = {"S": "RED", "N": "RED", "W": "GREEN", "E": "RED"}
        else:
            self.state = {"S": "GREEN", "N": "RED", "W": "RED", "E": "RED"}
        self.shared_memory.update_state("lights", self.state)
        logging.info(f"Normal lights toggled: {self.state}")

    def override_for_priority(self, vehicle):
        """Override the light state for a priority vehicle."""
        source = vehicle["source"]
        self.state = {key: "RED" for key in self.state.keys()}
        self.state[source] = "GREEN"
        self.shared_memory.update_state("lights", self.state)
        logging.info(f"Priority override! Lights switched for {source}")

    def run(self):
        """Control traffic lights based on normal cycling and priority overrides."""
        while True:
            if self.signal_handler.has_priority_signal():
                vehicle = self.signal_handler.get_priority_source()
                self.override_for_priority(vehicle)
                self.signal_handler.priority_signal = False  # Reset priority signal
            elif time.time() - self.last_switch_time >= 10:
                self.toggle_lights()
                self.last_switch_time = time.time()
            time.sleep(0.1)
