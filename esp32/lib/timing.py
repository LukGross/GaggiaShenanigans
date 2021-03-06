import time
from collections import deque

class timer:
    def __init__(self, scale = "ms"):
        self.scale = scale
        self.t0 = 0
        self.runtime = 0
        self.running = False
        
        def get_time(x):
            return {
                's' : 'time',
                'ms': 'ticks_ms',
                'us': 'ticks_us',
                'cpu':'ticks_cpu'
            }.get(x, 'time') # seconds is default if x is not found
        self.time = getattr(time, get_time(scale))
        self.diff = time.ticks_diff
            
    def reset(self):
        self.t0 = 0
        self.runtime = 0
        self.running = False
        
    def start(self):
        self.reset()
        self.running = True
        self.t0 = self.time()
    
    def stop(self):
        if self.running:
            self.runtime = self.diff(self.time(), self.t0)
            self.running = False
            return self.runtime
        else:
            return 0
    
    def current(self):
        if self.running:
            return self.diff(self.time(), self.t0)
        else:
            return self.runtime
        
        
        

class timer_laps(timer):
    def __init__(self, scale = "ms", nlaps = 10):
        timer.__init__(self, scale)
        self.tlast = 0
        self.que = deque((),nlaps)
        self.laps = []
            
    def reset(self, nlaps = 10):
        timer.reset(self)
        self.que = deque((),nlaps)
        self.laps = []
        self.runtime = 0       
        
    def start(self):
        self.reset()
        timer.start(self)
        self.tlast = self.t0
    
    def lap(self):
        t = self.time()
        laptime = self.diff(t, self.tlast)
        self.que.append(laptime)
        self.tlast = t
        return laptime
    
    def stop(self):
        t = self.time()
        laptime = self.diff(t, self.tlast)
        self.runtime = self.diff(t, self.t0)
        self.que.append(self.diff(t, self.tlast))
        self.laps = [self.que.popleft() for i in range(len(self.que))]
        self.running = False
        return self.runtime
        
        
        