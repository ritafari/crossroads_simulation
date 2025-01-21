# Traffic light control logic
"""
changes the color of the lights at regular intervals in normal mode, it is notified by the signal handler
if there is a priority vehicle to set the lights to the appropriate color.
"""

import time

class Lights:
    def __init__(self, shared_memory, signal_handler):
        self.shared_memory = shared_memory
        self.signal_handler = signal_handler
        self.state = {"S-N": "GREEN", "W-E": "RED"}  # Initial state
        self.last_switch_time = time.time()

    def toggle_lights(self):
        """Toggle normal light cycle."""
        self.state = {"S-N": "RED", "W-E": "GREEN"} if self.state["S-N"] == "GREEN" else {"S-N": "GREEN", "W-E": "RED"}
        self.shared_memory.update_state("lights", self.state)
        print(f"Lights toggled: {self.state}")

    def override_for_priority(self, vehicle):
        """Override the light state for a priority vehicle."""
        source = vehicle["source"]
        if source in ("S", "N"):
            self.state = {"S-N": "GREEN", "W-E": "RED"}
        elif source in ("W", "E"):
            self.state = {"S-N": "RED", "W-E": "GREEN"}
        self.shared_memory.update_state("lights", self.state)
        print(f"Priority override! Lights switched for {source}")

    def lights(self):
        """Control traffic lights based on normal cycling and priority overrides."""
        while True:
            # Check for priority signal
            if self.signal_handler.has_priority_signal():
                vehicle = self.signal_handler.get_priority_source()
                self.override_for_priority(vehicle)
                self.signal_handler.priority_signal = False  # Reset priority signal
            # Normal light cycle every 10 seconds
            elif time.time() - self.last_switch_time >= 10:
                self.toggle_lights()
                self.last_switch_time = time.time()

            time.sleep(0.1)
