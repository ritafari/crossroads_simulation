# Coordination and management of traffic
"""
Coordinator's Job is:
1- Manage Vehicle flow based on light state
2- Manage Priority Vehicles (receive signal of priority vehicle and alert/interrupt light state if necessary)
3- Update the intersection state in shared memory for other processes to access

"""
from multiprocessing import Queue
import logging
import time
import socket
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def coordinator(queues, shared_memory):
    """
    Handles vehicle flow based on light states and priority.
    """
    while True:
        for direction, queue in queues.items():
            if not queue.empty():
                vehicle = queue.get()
                lights_state = shared_memory.get_state("lights")

                if vehicle["type"] == "priority":
                    logging.info(f"Priority vehicle detected from {vehicle['source']} to {vehicle['destination']}")
                    shared_memory.update_state("current_vehicle", vehicle)
                elif lights_state.get(vehicle["source"]) == "GREEN":
                    logging.info(f"Normal vehicle moving from {vehicle['source']} to {vehicle['destination']}")
                    shared_memory.update_state("current_vehicle", vehicle)
                else:
                    logging.info(f"Vehicle {vehicle['id']} waiting for green light")
        time.sleep(0.1)

def coordinator_server(queues, shared_memory, host="127.0.0.1", port=65432):
    """
    Sends real-time updates about traffic light states and queue lengths
    to the display process.
    """
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(1)  # Listen for one client
        logging.info(f"Coordinator server listening on {host}:{port}")

        conn, addr = server_socket.accept()
        logging.info(f"Display process connected from {addr}")

        while True:
            # Extract serializable data from SharedMemory
            lights_state = shared_memory.get_state("lights")
            queue_lengths = {direction: queues[direction].qsize() for direction in queues}

            # Package data into an update message
            update_message = {
                "lights_state": lights_state,
                "queue_lengths": queue_lengths,
            }

            # Send the update message to the display process
            conn.sendall(json.dumps(update_message).encode("utf-8"))
            time.sleep(1)
    except Exception as e:
        logging.error(f"Error in coordinator_server: {e}")
    finally:
        server_socket.close()


