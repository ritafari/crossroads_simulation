# Coordination and management of traffic
"""
Coordinator's Job is:
1- Manage Vehicle flow based on light state
2- Manage Priority Vehicles (receive signal of priority vehicle and alert/interrupt light state if necessary)
3- Update the intersection state in shared memory for other processes to access

"""
import time

def proceed(vehicle):
    # Proceed with vehicle movement
    print(f"Vehicle {vehicle['source']} to {vehicle['destination']} is moving")


def coordinator(queues, lights, shared_memory):
    """
    Coordinate vehicle movement and manage light states.
    Priority vehicles are processed first.
    Non-priority vehicles proceed only if the light is green.
    """
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


