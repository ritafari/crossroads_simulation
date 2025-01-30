# normal_traffic.py
import time
import random
import uuid
import logging
from multiprocessing import Process
from utils.message_queues import enqueue  # Use centralized queue management

# Configure logging to match other modules
logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("normal_traffic")

DIRECTIONS = ["N", "S", "E", "W"]
TURN_PROBABILITY = 0.3  # 30% chance to turn right

def create_vehicle():
    """Creates a vehicle with complete attributes including turn direction."""
    source = random.choice(DIRECTIONS)
    
    # Ensure valid destination and determine turn direction
    possible_destinations = [d for d in DIRECTIONS if d != source]
    destination = random.choice(possible_destinations)
    
    # Determine if this is a right turn (priority)
    is_right_turn = random.random() < TURN_PROBABILITY
    turn = "right" if is_right_turn else random.choice(["left", "straight"])
    
    return {
        "id": str(uuid.uuid4()),
        "type": "normal",
        "source": source,
        "destination": destination,
        "turn": turn,
        "timestamp": time.time(),
        "priority": False
    }

def normal_traffic_gen(queues, interval, shutdown_flag, max_vehicles=None):
    """
    Generate normal traffic with configurable parameters
    Args:
        queues: Dictionary of message queues (from message_queues.create_queues())
        interval: Time between vehicle generation (seconds)
        max_vehicles: Optional limit for testing purposes
    """
    count = 0
    while not shutdown_flag.is_set():
        if max_vehicles and count >= max_vehicles:
            logger.info("Reached maximum vehicle count")
            break

        vehicle = create_vehicle()
                
        # Use centralized enqueue function with proper error handling
        enqueue(queues, vehicle, vehicle["source"])
                
        logger.info(f"Generated {vehicle['type']} vehicle {vehicle['id'][:8]} "
                        f"from {vehicle['source']} to {vehicle['destination']} "
                        f"(turn: {vehicle['turn']})")
                
        time.sleep(interval)
        count += 1

if __name__ == "__main__":
    from utils.message_queues import create_queues
    
    # Initialize proper queues from central module
    queues = create_queues()
    
    # Run as a separate process with clean startup
    process = Process(target=normal_traffic_gen, args=(queues, 2))
    
    try:
        process.start()
        logger.info("Normal traffic generator started")
        process.join()
    finally:
        if process.is_alive():
            process.terminate()