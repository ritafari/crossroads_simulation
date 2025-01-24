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
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")

        while True:
            data = client_socket.recv(1024)  # Receive data (up to 1024 bytes)
            if not data:
                print("No data received. Closing connection...")
                break
            update_message = json.loads(data.decode("utf-8"))
            print(f"Received update: {update_message}")
    except Exception as e:
        print(f"Error in display_client: {e}")
    finally:
        client_socket.close()
