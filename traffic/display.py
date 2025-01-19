# Visualization of the simulation

def display(shared_memory):
    """Render the intersection state to the operator."""
    while True:
        state = shared_memory.get_state()
        render(state)  # Render the state visually
        time.sleep(0.5)
