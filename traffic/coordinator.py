# Coordination and management of traffic
"""
Coordinator's Job is:
1- Manage Vehicle flow based on light state
2- Manage Priority Vehicles (receive signal of priority vehicle and alert/interrupt light state if necessary)
3- Update the intersection state in shared memory for other processes to access

"""
import time
import socket
import json
import time

def proceed(vehicle):
    # Proceed with vehicle movement
    print(f"Vehicle {vehicle['source']} to {vehicle['destination']} is moving")

"""
def coordinator(queues, lights, shared_memory):
    
    #Coordinate vehicle movement and manage light states.
    #Priority vehicles are processed first.
    #Non-priority vehicles proceed only if the light is green.
    
    while True:
        # Check for priority vehicles
        for direction, queue in queues.items():
            if not queue.empty():
                vehicle = queue.get()

                # Priority handling
                if vehicle["type"] == "priority":
                    print(f"Priority vehicle detected from {vehicle['source']} to {vehicle['destination']}")
                    lights.override_for_priority(vehicle)  # Override light state for priority vehicle
                    shared_memory.update_state("current_vehicle", vehicle)  # Update shared memory
                    proceed(vehicle)
                # Normal vehicle handling
                elif shared_memory.get_light_state(vehicle["source"]):
                    print(f"Normal vehicle moving from {vehicle['source']} to {vehicle['destination']}")
                    shared_memory.update_state("current_vehicle", vehicle)  # Update shared memory
                    proceed(vehicle)
                else:
                    print(f"Vehicle {vehicle['id']} from {vehicle['source']} waiting for green light")

        # Avoid CPU overuse
        time.sleep(0.1)
"""
def coordinator_server(queues, lights, shared_memory, host="127.0.0.1", port=65432):
    """
    Coordinator server sends real-time updates about traffic light states
    and vehicle movements to the display process.
    """
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(1)  # Listen for one client
        print(f"Coordinator server listening on {host}:{port}")

        conn, addr = server_socket.accept()
        print(f"Display process connected from {addr}")

        while True:
            # Update light states and queue lengths
            lights_state = shared_memory.get_state("lights") or {
                "S": "GREEN", "N": "RED", "W": "RED", "E": "RED"
            }
            queue_lengths = {direction: queues[direction].qsize() for direction in queues}

            # Package data into an update message
            update_message = {
                "lights_state": lights_state,
                "queue_lengths": queue_lengths,
            }

            # Send the update message to the display
            conn.sendall(json.dumps(update_message).encode("utf-8"))
            time.sleep(1)
    except Exception as e:
        print(f"Error in coordinator_server: {e}")
    finally:
        server_socket.close()
