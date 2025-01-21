# Coordination and management of traffic
"""
Coordinator's Job is:
1- Manage Vehicle flow based on light state
2- Manage Priority Vehicles (receive signal of priority vehicle and alert/interrupt light state if necessary)
3- Update the intersection state in shared memory for other processes to access

"""
import time

def override_for_priority(self, vehicle):
    # Override light cycle for priority vehicle
    self.shared_memory.update_state("priority_vehicle", vehicle)
    self.signal_handler.notify_priority(vehicle)

def proceed(vehicle):
    # Proceed with vehicle movement
    print(f"Vehicle {vehicle['source']} to {vehicle['destination']} is moving")


def coordinator(normal_queue, priority_queue, lights, shared_memory):
    #Coordinate vehicle movement and manage light states.
    while True:
        # Process priority vehicles first
        if not priority_queue.empty():
            vehicle = priority_queue.get()
            lights.override_for_priority(vehicle)
        elif not normal_queue.empty():
            vehicle = normal_queue.get()
            # Proceed based on light state
            if shared_memory.get_light_state(vehicle["source"]):
                proceed(vehicle)
        time.sleep(0.1)
