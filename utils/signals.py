# Signal handling logic

import signal

class SignalHandler:
    def __init__(self):
        self.priority_signal = False
        self.priority_source = None

    def notify_priority(self, vehicle):
        self.priority_signal = True
        self.priority_source = vehicle["source"] # signal_handler.notify_priority({"source": "N"})

    def has_priority_signal(self):
        return self.priority_signal
    #Returns the current status of the priority_signal flag.
    #Useful for processes like lights to check whether they need to override normal light cycling.
    #In the light process: 
    # if signal_handler.has_priority_signal():
            #Override light cycle for priority vehicle



    def get_priority_source(self):
        return self.priority_source

