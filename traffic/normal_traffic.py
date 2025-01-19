# Functions and processes for normal traffic generation

def normal_traffic_gen(queue, interval):
    """Generate normal traffic and enqueue it."""
    while True:
        vehicle = create_vehicle("normal")
        queue.put(vehicle)
        time.sleep(interval)
