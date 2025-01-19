# Signal handling logic

import signal

class SignalHandler:
    def __init__(self):
        self.priority_signal = False
        self.priority_source = None

    def notify_priority(self, vehicle):
        self.priority_signal = True
        self.priority_source = vehicle["source"]

    def has_priority_signal(self):
        return self.priority_signal

    def get_priority_source(self):
        return self.priority_source

