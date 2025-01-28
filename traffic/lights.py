import time
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(message)s")

class Lights:
    def __init__(self, shared_memory, signal_handler):
        self.shared_memory = shared_memory
        self.signal_handler = signal_handler

        # Initial state (all red)
        self.state = {"S": "RED", "N": "RED", "W": "RED", "E": "RED"}
        self.last_switch_time = time.time()

        # Current active direction
        self.active_directions = ["S", "N"]  # Start with North-South

        # Initialize the shared memory with the initial state
        logging.debug("Initializing light states...")
        self.shared_memory.update_state("lights", self.state)
        logging.debug(f"Initial light state: {self.state}")

    def update_light(self, direction, color):
        """Update a single light's color."""
        self.state[direction] = color
        self.shared_memory.update_state("lights", self.state)
        logging.debug(f"Updated light for {direction} to {color}. Current state: {self.state}")

    def normal_light_cycle(self):
        """Cycle lights for opposing directions."""
        current_time = time.time()
        elapsed_time = current_time - self.last_switch_time

        # Check if it's time to switch the lights
        if elapsed_time >= 10:  #timer
            # Switch active directions between opposing pairs
            if self.active_directions == ["S", "N"]:
                self.active_directions = ["W", "E"]
            else:
                self.active_directions = ["S", "N"]

            logging.info(f"10 seconds passed. Switching lights to: {self.active_directions}")

            # Update light states for all directions
            new_state = {direction: "GREEN" if direction in self.active_directions else "RED" for direction in self.state.keys()}

            # Only update shared memory if the state actually changes
            if new_state != self.state:
                self.state = new_state
                self.shared_memory.update_state("lights", self.state)

                for direction, color in self.state.items():
                    logging.info(f"Updated light for {direction} to {color}. Current state: {self.state}")

            # Reset the last switch time
            self.last_switch_time = current_time
            logging.info(f"Lights switched. Last switch time updated to: {self.last_switch_time:.2f}")


    def handle_priority_vehicle(self, source):
        MIN_PRIORITY_GREEN_DURATION = 7
        """Handle a priority vehicle arriving from a specific direction."""
        logging.info(f"Handling priority vehicle from {source}...")

        # Log before resetting last_switch_time
        logging.debug(f"Before priority: last_switch_time = {self.last_switch_time:.2f}")

        # Set all lights to RED except the source
        for direction in self.state.keys():
            self.state[direction] = "RED"
        self.state[source] = "GREEN"

        # Update the shared memory
        self.shared_memory.update_state("lights", self.state)
        logging.info(f"Priority override! Light for {source} set to GREEN. Current state: {self.state}")

        # Reset last_switch_time
        self.last_switch_time = time.time()
        logging.debug(f"After priority: last_switch_time reset to {self.last_switch_time:.2f}")

        # Ensure the green light stays active for at least MIN_PRIORITY_GREEN_DURATION
        time.sleep(MIN_PRIORITY_GREEN_DURATION)

        # Log completion of priority handling
        logging.info(f"Priority vehicle from {source} has passed. Minimum green time of {MIN_PRIORITY_GREEN_DURATION}s ensured.")

    def run(self):
        """Control traffic lights based on normal cycling and priority overrides."""
        while True:
            # Check for priority vehicle
            if self.signal_handler.has_priority_signal():
                source = self.signal_handler.get_priority_source()
                if source:
                    self.handle_priority_vehicle(source)
                    self.signal_handler.reset_priority_signal()
            else:
                # Perform normal cycling
                self.normal_light_cycle()

            # Sleep briefly to avoid high CPU usage
            time.sleep(0.1)
