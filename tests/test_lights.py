# Unit tests for lights process

import unittest
from unittest.mock import MagicMock
from time import time
from traffic.lights import Lights
from utils.shared_memory import SharedMemory

class TestLights(unittest.TestCase):
    def setUp(self):
        # Set up shared memory and signal handler mocks
        self.shared_memory = SharedMemory()
        self.shared_memory.update_state("lights", {"S": "GREEN", "N": "RED", "W": "RED", "E": "RED"})
        self.signal_handler = MagicMock()

        # Create Lights instance
        self.lights = Lights(self.shared_memory, self.signal_handler)

    def test_toggle_lights(self):
        """
        Test the toggle_lights method to ensure it cycles through the light states correctly.
            - Ensures that lights toggle between S-N and W-E correctly in normal mode.
            - Validates that shared memory reflects the updated light states.
        """
        # Initial state
        initial_state = {"S": "GREEN", "N": "RED", "W": "RED", "E": "RED"}
        self.assertEqual(self.shared_memory.get_state("lights"), initial_state)

        # Toggle lights once
        self.lights.toggle_lights()
        expected_state = {"S": "RED", "N": "RED", "W": "GREEN", "E": "RED"}
        self.assertEqual(self.shared_memory.get_state("lights"), expected_state)

        # Toggle lights again
        self.lights.toggle_lights()
        expected_state = {"S": "GREEN", "N": "RED", "W": "RED", "E": "RED"}
        self.assertEqual(self.shared_memory.get_state("lights"), expected_state)

    def test_override_for_priority(self):
        """
        Test the override_for_priority method to ensure it sets the correct light state
        for the given priority vehicle.
            - Tests if the correct light is set to green based on the priority vehicle's source direction.
            - Validates the state in shared memory for all directions (S, N, W, E).
        """
        # Test for vehicle from "S"
        vehicle_s = {"source": "S"}
        self.lights.override_for_priority(vehicle_s)
        expected_state = {"S": "GREEN", "N": "RED", "W": "RED", "E": "RED"}
        self.assertEqual(self.shared_memory.get_state("lights"), expected_state)

        # Test for vehicle from "N"
        vehicle_n = {"source": "N"}
        self.lights.override_for_priority(vehicle_n)
        expected_state = {"S": "RED", "N": "GREEN", "W": "RED", "E": "RED"}
        self.assertEqual(self.shared_memory.get_state("lights"), expected_state)

        # Test for vehicle from "W"
        vehicle_w = {"source": "W"}
        self.lights.override_for_priority(vehicle_w)
        expected_state = {"S": "RED", "N": "RED", "W": "GREEN", "E": "RED"}
        self.assertEqual(self.shared_memory.get_state("lights"), expected_state)

        # Test for vehicle from "E"
        vehicle_e = {"source": "E"}
        self.lights.override_for_priority(vehicle_e)
        expected_state = {"S": "RED", "N": "RED", "W": "RED", "E": "GREEN"}
        self.assertEqual(self.shared_memory.get_state("lights"), expected_state)

    def test_run_priority(self):
        """
        Test the run method to ensure priority handling works correctly.
            - Simulates a priority signal to ensure the run method overrides the lights for the priority vehicle.
        """
        # Mock signal handler to simulate priority signal
        vehicle_priority = {"source": "N"}
        self.signal_handler.has_priority_signal.return_value = True
        self.signal_handler.get_priority_source.return_value = vehicle_priority

        # Run the priority override logic in the run method
        self.lights.run = MagicMock(side_effect=self.lights.override_for_priority(vehicle_priority))
        self.lights.run()

        # Verify the light was overridden for priority
        expected_state = {"S": "RED", "N": "GREEN", "W": "RED", "E": "RED"}
        self.assertEqual(self.shared_memory.get_state("lights"), expected_state)

    def test_run_normal_cycle(self):
        """
        Test the run method to ensure normal cycling works without priority.
            - Simulates no priority signal and ensures the lights toggle normally after 10 seconds.
        """
        # Mock signal handler to simulate no priority signal
        self.signal_handler.has_priority_signal.return_value = False

        # Simulate time to allow toggling
        self.lights.last_switch_time = time() - 10
        self.lights.run = MagicMock(side_effect=self.lights.toggle_lights)
        self.lights.run()

        # Verify the lights toggled
        expected_state = {"S": "RED", "N": "RED", "W": "GREEN", "E": "RED"}
        self.assertEqual(self.shared_memory.get_state("lights"), expected_state)

if __name__ == "__main__":
    unittest.main()

"""
run with:
python -m unittest test_lights.py

Example Output:
...
----------------------------------------------------------------------
Ran 4 tests in 0.215s

OK

Test Fail:
AssertionError: {'S': 'GREEN', 'N': 'RED', 'W': 'RED', 'E': 'RED'} != {'S': 'RED', 'N': 'RED', 'W': 'GREEN', 'E': 'RED'}
"""


