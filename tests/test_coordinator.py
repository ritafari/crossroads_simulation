# Unit tests for coordinator logic

import unittest
from unittest.mock import MagicMock, patch
from queue import Queue
from threading import Thread
import socket
import json
import time

from traffic.coordinator import coordinator_server
from utils.shared_memory import SharedMemory
from traffic.lights import Lights

class TestCoordinator(unittest.TestCase):
    def setUp(self):
        # Set up shared memory
        self.shared_memory = SharedMemory()
        self.shared_memory.update_state("lights", {"S": "GREEN", "N": "RED", "W": "RED", "E": "RED"})

        # Set up mock lights
        self.lights = Lights(self.shared_memory, MagicMock())

        # Set up queues for each direction
        self.queues = {
            "S": Queue(),
            "N": Queue(),
            "W": Queue(),
            "E": Queue(),
        }

        # Add test vehicles to queues
        self.queues["S"].put({"id": 1, "type": "normal", "source": "S", "destination": "N"})
        self.queues["N"].put({"id": 2, "type": "priority", "source": "N", "destination": "S"})
        self.queues["W"].put({"id": 3, "type": "normal", "source": "W", "destination": "E"})

    """
    TEST COORDINATOR TWO FUNCTIONS:
        - Normal Vehicles: Ensures vehicles with type "normal" are processed only when their light is green.
        - Priority Vehicles: Ensures vehicles with type "priority" are processed immediately, and lights are overridden.
    """

    def test_coordinator_normal_vehicle(self):
        # Mock proceed to capture its calls
        with patch("coordinator.proceed", autospec=True) as mock_proceed:
            # Run coordinator in a thread to avoid blocking
            coordinator_thread = Thread(target=coordinator_server, args=(self.queues, self.lights, self.shared_memory))
            coordinator_thread.daemon = True
            coordinator_thread.start()

            # Allow some time for the coordinator to process
            time.sleep(0.5)

            # Assert that the normal vehicle from "S" was processed
            mock_proceed.assert_any_call({"id": 1, "type": "normal", "source": "S", "destination": "N"})

    def test_coordinator_priority_vehicle(self):
        # Mock override_for_priority and proceed
        self.lights.override_for_priority = MagicMock()
        with patch("coordinator.proceed", autospec=True) as mock_proceed:
            # Run coordinator in a thread
            coordinator_thread = Thread(target=coordinator_server, args=(self.queues, self.lights, self.shared_memory))
            coordinator_thread.daemon = True
            coordinator_thread.start()

            # Allow time for the coordinator to process
            time.sleep(0.5)

            # Assert that priority vehicle was processed and lights were overridden
            self.lights.override_for_priority.assert_called_with({"id": 2, "type": "priority", "source": "N", "destination": "S"})
            mock_proceed.assert_any_call({"id": 2, "type": "priority", "source": "N", "destination": "S"})

    """
    TEST COORDINATOR SERVER:
    Mocks the socket connection to verify that the server sends the correct data structure (lights_state and queue_lengths) to the client.
    """
    @patch("socket.socket")  # Mock socket to avoid actual network usage
    def test_coordinator_server(self, mock_socket):
        # Mock the connection and its behavior
        mock_conn = MagicMock()
        mock_socket.return_value.accept.return_value = (mock_conn, ("127.0.0.1", 12345))

        # Run coordinator_server in a thread
        server_thread = Thread(target=coordinator_server, args=(self.queues, self.lights, self.shared_memory))
        server_thread.daemon = True
        server_thread.start()

        # Allow some time for the server to start and send data
        time.sleep(1)

        # Assert that the connection sent data
        mock_conn.sendall.assert_called()
        sent_data = mock_conn.sendall.call_args[0][0].decode("utf-8")
        update_message = json.loads(sent_data)

        # Validate the data structure in the update
        self.assertIn("lights_state", update_message)
        self.assertIn("queue_lengths", update_message)
        self.assertEqual(update_message["lights_state"], {"S": "GREEN", "N": "RED", "W": "RED", "E": "RED"})

if __name__ == "__main__":
    unittest.main()





"""
Run test using unitest: 
python -m unittest test_coordinator.py

Example of Output:
...
----------------------------------------------------------------------
Ran 3 tests in 0.123s

OK
"""