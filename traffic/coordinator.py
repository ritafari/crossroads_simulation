# Coordination and management of traffic

def coordinator(normal_queue, priority_queue, lights, shared_memory):
    """Coordinate vehicle movement and manage light states."""
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
