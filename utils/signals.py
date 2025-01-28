from multiprocessing import Value, Manager
from ctypes import c_bool

class SignalHandler:
    def __init__(self):
        # Shared state for priority signal (multiprocessing-safe)
        self.priority_signal = Value(c_bool, False)  # Boolean value shared between processes
        manager = Manager()
        self.priority_source = manager.Value('u', "")  # Shared string value for priority source

    def notify_priority(self, vehicle):
        """Notify the system about a priority vehicle."""
        if "source" in vehicle:
            with self.priority_signal.get_lock():  # Lock to safely update the shared value
                self.priority_signal.value = True
                self.priority_source.value = vehicle["source"]
        else:
            print("Invalid vehicle data: 'source' key is missing.")

    def has_priority_signal(self):
        """Check if a priority signal is active."""
        with self.priority_signal.get_lock():
            return self.priority_signal.value

    def get_priority_source(self):
        """Retrieve the source of the priority signal."""
        return self.priority_source.value

    def reset_priority_signal(self):
        """Reset the priority signal."""
        with self.priority_signal.get_lock():  # Lock to safely reset the shared values
            self.priority_signal.value = False
            self.priority_source.value = ""


