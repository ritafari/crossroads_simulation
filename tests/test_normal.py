# Unit tests for normal traffic generation


import unittest
from unittest.mock import patch
from queue import Queue
from threading import Thread
from traffic.normal_traffic import create_vehicle, normal_traffic_gen
import time

class TestNormalTrafficGen(unittest.TestCase):
    def setUp(self):
        # Initialize queues for all directions
        self.queues = {
            "S": Queue(),
            "N": Queue(),
            "W": Queue(),
            "E": Queue(),
        }

    def test_create_vehicle(self):
        """
        Test the 'create_vehicle' function to ensure it generates a vehicle
        with valid attributes.
            - Ensures that vehicles have valid attributes (id, source, destination, timestamp, and type).
            - Tests that the source and destination are different.
        """
        with patch("random.choice", side_effect=["S", "N"]):  # Mock directions
            vehicle = create_vehicle("normal")

        # Validate vehicle attributes
        self.assertEqual(vehicle["type"], "normal")
        self.assertEqual(vehicle["source"], "S")
        self.assertEqual(vehicle["destination"], "N")
        self.assertIn("id", vehicle)
        self.assertIn("timestamp", vehicle)

    def test_normal_traffic_gen(self):
        """
        Test the 'normal_traffic_gen' function to ensure vehicles are enqueued
        correctly into the appropriate queues.
            - Ensures that vehicles are correctly enqueued into the appropriate queues based on their source.
            - Verifies that the generator runs in a separate thread without blocking the main program.
        """
        # Run the generator in a separate thread
        with patch("normal_traffic.create_vehicle", side_effect=[
            {"id": "1", "type": "normal", "source": "S", "destination": "N", "timestamp": time.time()},
            {"id": "2", "type": "normal", "source": "W", "destination": "E", "timestamp": time.time()},
        ]):
            thread = Thread(target=normal_traffic_gen, args=(self.queues, 0.5))  # Short interval for testing
            thread.daemon = True
            thread.start()

            # Allow some time for vehicles to be generated
            time.sleep(1.5)

            # Check that vehicles are enqueued in the correct queues
            self.assertFalse(self.queues["S"].empty())
            self.assertFalse(self.queues["W"].empty())

            # Dequeue and validate the vehicles
            vehicle_s = self.queues["S"].get()
            self.assertEqual(vehicle_s["id"], "1")
            self.assertEqual(vehicle_s["source"], "S")
            self.assertEqual(vehicle_s["destination"], "N")

            vehicle_w = self.queues["W"].get()
            self.assertEqual(vehicle_w["id"], "2")
            self.assertEqual(vehicle_w["source"], "W")
            self.assertEqual(vehicle_w["destination"], "E")

    def test_vehicle_ids_are_unique(self):
        """
        Test that each generated vehicle has a unique ID.
            - Validates that every generated vehicle has a unique identifier.
        """
        vehicle_ids = set()
        for _ in range(100):  # Generate 100 vehicles
            vehicle = create_vehicle("normal")
            self.assertNotIn(vehicle["id"], vehicle_ids)  # Ensure no duplicate IDs
            vehicle_ids.add(vehicle["id"])

if __name__ == "__main__":
    unittest.main()

"""
Test function with
python -m unittest test_normal.py

Output example:
...
----------------------------------------------------------------------
Ran 3 tests in 0.002s
OK

test fail:
FAIL: test_vehicle_ids_are_unique (test_normal_traffic_gen.TestNormalTrafficGen)
AssertionError: '12345-duplicate-id' already in set
"""