# Visualization of the simulation

import socket
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def display_client(host="127.0.0.1", port=65432):
    """
    Connects to the coordinator server and visualizes updates.
    """
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info(f"Attempting to connect to the coordinator server at {host}:{port}...")
        client_socket.connect((host, port))
        logging.info(f"Connected to server at {host}:{port}")

        while True:
            data = client_socket.recv(1024)
            if not data:
                logging.info("No data received. Closing connection...")
                break
            update_message = json.loads(data.decode("utf-8"))
            logging.info(f"Received update: {update_message}")
    except ConnectionRefusedError:
        logging.error("Connection refused. Ensure the coordinator server is running.")
    except Exception as e:
        logging.error(f"Error in display_client: {e}")
    finally:
        client_socket.close()

