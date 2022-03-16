from time import ticks_cpu, ticks_diff
from collections import deque

class tsic306:
    def __init__(self, pin, maxBitTime = 40000):
        self.maxBitTime = maxBitTime
        self.ZACwire = pin
        self.q = deque((),41)
        self.T = None
        
        def push(pin):
            t = ticks_cpu()
            self.q.append(t)
        self.ZACwire.irq(trigger=3, handler=push)
    
    def ReadBuffer(self):
        if len(self.q) < 41:
            #print("short")
            return None
        t1 = self.q.popleft()
        t2 = self.q.popleft()
        t = ticks_diff(t2,t1)
        if t < self.maxBitTime:
            #print("shifted")
            return None
        t1 = t2
        t2 = self.q.popleft()
        t3 = self.q.popleft()
        strobe = ticks_diff(t2,t1)
        var = abs(1-ticks_diff(t2,t1)/strobe)
        if var > 0.2:
            #print("shifted")
            return None
        bitstr = 0
        parity = False
        t1 = t3
        for i in range(8):
            t2 = self.q.popleft()
            t = ticks_diff(t2,t1)
            if t > strobe:
                bitstr = bitstr << 1 | 0
            else:
                bitstr = bitstr << 1 | 1
                parity = not parity
            t1 = self.q.popleft()
        t2 = self.q.popleft()
        t = ticks_diff(t2,t1)
        if not parity == (t<strobe):
            #print("parity")
            return None
        t1 = self.q.popleft()
        t2 = self.q.popleft()
        strobe = ticks_diff(t2,t1)
        parity = False
        for i in range(8):
            t1 = self.q.popleft()
            t2 = self.q.popleft()
            t = ticks_diff(t2,t1)
            if t > strobe:
                bitstr = bitstr << 1 | 0
            else:
                bitstr = bitstr << 1 | 1
                parity = not parity
        t1 = self.q.popleft()
        t2 = self.q.popleft()
        t = ticks_diff(t2,t1)
        if not parity == (t<strobe):
            #print("parity")
            return None
        return bitstr & 0b11111111111
    
    def ReadTemp_int(self):
        temp = self.ReadBuffer()
        if temp != None:
            self.T = temp
        return self.T
        
        
    def ReadTemp_c(self):
        temp = self.ReadBuffer()
        if temp != None:
            self.T = temp
        return self.T/2047*200-50