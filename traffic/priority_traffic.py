# Functions and processes for priority traffic generation


def priority_traffic_gen(queue, signal, interval):
    """Generate priority vehicles and notify signal handler."""
    while True:
        vehicle = create_vehicle("priority")
        queue.put(vehicle)
        signal(vehicle)
        time.sleep(interval)
