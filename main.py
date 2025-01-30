import os
import time
import signal
import logging
from multiprocessing import Process, Manager
from utils.shared_memory import SharedMemory
from coordinator import Coordinator, DisplayServer
from display import TrafficDisplay
from lights import TrafficLights
from normal_traffic import normal_traffic_gen
from priority_traffic import priority_traffic_gen

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("main")

def main():
    processes = []
    
    def shutdown_handler(signum, frame):
        logger.info("\n🔴 SHUTTING DOWN ALL PROCESSES")
        # Step 1: Signal all processes to stop via shutdown_flag
        shutdown_flag.set()
        
        # Step 2: Wait briefly for graceful exit
        logger.info("Waiting for processes to finish current operations...")
        time.sleep(0.5)
        
        # Step 3: Force terminate any remaining processes
        for p in reversed(processes):
            if p.is_alive():
                logger.info(f"Force terminating {p.name} (PID: {p.pid})")
                p.terminate()
        
        # Step 4: Cleanup resources
        if os.path.exists("lights.pid"):
            os.remove("lights.pid")
        os._exit(0)
    
    signal.signal(signal.SIGINT, shutdown_handler)

    with Manager() as manager:
        try:
            # Create shared components
            shutdown_flag = manager.Event()
            shared_memory = SharedMemory(manager)
            queues = manager.dict({
                "N": manager.Queue(),
                "S": manager.Queue(),
                "E": manager.Queue(),
                "W": manager.Queue()
            })

            # Create processes IN ORDER OF DEPENDENCY
            processes = [
                # Core system components
                Process(target=TrafficLights(shared_memory).run, name="Lights"),
                
                # Coordinator needs to start before display
                Process(target=Coordinator(queues, shared_memory, shutdown_flag).run, name="Coordinator"),
                
                # Network components
                Process(
                        target=DisplayServer(
                            queues=queues,
                            shared_memory=shared_memory,
                            shutdown_flag=shutdown_flag
                        ).run,
                        name="DisplayServer"
                    ),

                Process(
                        target=TrafficDisplay(shutdown_flag=shutdown_flag).run,
                        name="TrafficDisplay"
                    ),

                # Traffic generators (start last)
                
                Process(
                        target=normal_traffic_gen,
                        args=(queues, 2, shutdown_flag),  # (queues, interval, flag)
                        name="NormalTraffic"
                    ),
                Process(
                        target=priority_traffic_gen,
                        args=(queues, 5, shutdown_flag),  # (queues, interval, flag)
                        name="PriorityTraffic"
                    )
            ]

            # Start processes with staggered initialization
            logger.info("🚀 Launching system...")
            for p in processes:
                p.start()
                time.sleep(1) 

            # Monitor process health
            while True:
                for p in processes:
                    if not p.is_alive():
                        logger.error(f"Process {p.name} crashed!")
                        shutdown_handler(None, None)
                time.sleep(1)

        except Exception as e:
            logger.error(f"Fatal error: {str(e)}")
            shutdown_handler(None, None)

if __name__ == "__main__":
    main()