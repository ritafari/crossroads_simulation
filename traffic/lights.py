# Traffic light control logic
"""
changes the color of the lights at regular intervals in normal mode, it is notified by the signal handler
if there is a priority vehicle to set the lights to the appropriate color.
"""

import time

def lights(shared_memory, signal_handler):
    #Control traffic lights based on normal cycling and priority overrides.
    normal_cycle_time = 10 # seconds for each normal light cycle
    green = {"S-N": "GREEN", "W-E": "RED"} #initial state
    red = {"S-N": "RED", "W-E": "GREEN"}
    current_state = green
    last_switch_time = time.time()

    while True:
        if signal_handler.has_priority_signal():
            priority_source = signal_handler.get_priority_source()

            #determine the affected light
            if priority_source in ("S", "N"):
                if current_state["S-N"] == "RED":
                    current_state = green
                    shared_memory.update_state("lights", current_state)
                    print(f"Priority detected! Switching to allow {priority_source}-bound vehicle to pass")
            elif priority_source in ("W", "E"):
                if current_state["W-E"] == "RED":
                    current_state = red
                    shared_memory.update_state("lights", current_state)
                    print(f"Priority detected! Switching to allow {priority_source}-bound vehicle to pass")
            #Reset the priority signal after handliing
            signal_handler.priority_signal = False
        
        #Normal light cycling
        elif time.time() - last_switch_time >= normal_cycle_time:
            #Toggle between green nd red states 
            current_state = green if current_state == red else red
            shared_memory.update_state("lights", current_state)
            last_switch_time = time.time()
            print(f"Normal cycle switch to {current_state['S-N']}")

        time.sleep(1)

    