# Unit tests for display process

import unittest
from unittest.mock import MagicMock, patch
import socket
import json
import time
from threading import Thread
from queue import Queue

# Import the display and client functions to test
from display import display, display_client
from shared_memory import SharedMemory

class TestDisplay(unittest.TestCase):
    def setUp(self):
        # Set up shared memory with initial states
        self.shared_memory = SharedMemory()
        self.shared_memory.update_state("lights", {"S": "GREEN", "N": "RED", "W": "RED", "E": "RED"})
        self.shared_memory.update_state("queue_lengths", {"S": 1, "N": 0, "W": 2, "E": 1})

    """
    DISPLAY FUNCTION TESTS:
        - Ensures the display function retrieves the intersection state from shared memory.
        - Validates that the render function is called with the correct data (mocked here).
    DISPLAY_CLIENT FUNCTION TESTS:
        - Ensures the client successfully connects to the mocked server.
        - Validates that the received updates from the server are processed and printed.
    """
    @patch("display.render")  # Mock the render function
    def test_display(self, mock_render):
        """
        Test the 'display' function to ensure it renders shared memory state.
        """
        # Run the display function in a separate thread
        display_thread = Thread(target=display, args=(self.shared_memory,))
        display_thread.daemon = True
        display_thread.start()

        # Allow some time for the display to run and render
        time.sleep(1)

        # Assert that render was called with the correct state
        expected_state = self.shared_memory.get_state()
        mock_render.assert_called_with(expected_state)

    @patch("socket.socket")  # Mock socket to avoid actual network usage
    def test_display_client(self, mock_socket):
        """
        Test the 'display_client' function to ensure it connects to the server
        and processes updates correctly.
        """
        # Mock server behavior
        mock_conn = MagicMock()
        mock_socket.return_value = mock_conn
        mock_conn.recv.side_effect = [
            json.dumps({
                "lights_state": {"S": "GREEN", "N": "RED", "W": "RED", "E": "RED"},
                "queue_lengths": {"S": 1, "N": 0, "W": 2, "E": 1},
            }).encode("utf-8"),
            b"",  # Simulate server closing connection
        ]

        # Run the display client in a separate thread
        client_thread = Thread(target=display_client)
        client_thread.daemon = True
        client_thread.start()

        # Allow some time for the client to connect and process data
        time.sleep(1)

        # Assert that the client received and printed the correct update
        mock_conn.connect.assert_called_with(("127.0.0.1", 65432))
        mock_conn.recv.assert_called()
        self.assertIn("Received update:", mock_conn.recv.call_args_list[0][0])

if __name__ == "__main__":
    unittest.main()

"""
Test function with 
python -m unittest test_display.py

Output example:
...
----------------------------------------------------------------------
Ran 2 tests in 0.152s

OK

if test fail: 
FAIL: test_display (test_display.TestDisplay)
AssertionError: Expected render() to be called with {'lights': {'S': 'GREEN', 'N': 'RED', 'W': 'RED', 'E': 'RED'}, 'queue_lengths': {'S': 1, 'N': 0, 'W': 2, 'E': 1}}.
----------------------------------------------------------------------
"""
