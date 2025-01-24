# Visualization of the simulation

"""
def display(shared_memory):
    #Render the intersection state to the operator.
    while True:
        state = shared_memory.get_state()
        render(state)  # Render the state visually
        time.sleep(0.5)
"""

import socket
import json

def display_client(host="127.0.0.1", port=65432):
    """
    Display client connects to the coordinator server to receive real-time updates
    and visualizes the data.
    """
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f"Connected to coordinator server at {host}:{port}")

    while True:
        try:
            # Receive data from the server
            data = client_socket.recv(1024)  # Receive up to 1024 bytes
            if not data:
                break

            # Decode and parse the JSON data
            update_message = json.loads(data.decode("utf-8"))

            # Visualize the received data
            print(f"Received Update: {update_message}")
        except (ConnectionResetError, BrokenPipeError):
            print("Coordinator server disconnected. Stopping display.")
            break

    # Clean up
    client_socket.close()
    print("Disconnected from coordinator server.")  


