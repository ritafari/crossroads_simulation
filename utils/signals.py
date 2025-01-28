class SignalHandler:
    def __init__(self):
        self.priority_signal = False
        self.priority_source = None

    def notify_priority(self, vehicle):
        """Notify the system about a priority vehicle."""
        self.priority_signal = True
        self.priority_source = vehicle["source"]

    def has_priority_signal(self):
        """Check if a priority signal is active."""
        return self.priority_signal

    def get_priority_source(self):
        """Retrieve the source of the priority signal."""
        return self.priority_source


