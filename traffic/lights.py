# Traffic light control logic

def lights(shared_memory, signal_handler):
    """Control traffic lights based on normal cycling and priority overrides."""
    while True:
        if signal_handler.has_priority_signal():
            shared_memory.set_priority_light(signal_handler.get_priority_source())
        else:
            shared_memory.toggle_lights()
        time.sleep(1)  # Regular interval for light switching
