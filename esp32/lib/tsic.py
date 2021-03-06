from time import ticks_cpu, ticks_ms, ticks_diff, sleep, ticks_us
from collections import deque
from machine import Timer, Pin


class tsic:
    def __init__(self, pin, maxBitTime=100000, high=150, low=-50, prec=1,
                 bits=11):
        self.data = pin
        self.maxBitTime = maxBitTime
        self.high = high
        self.low = low
        self.prec = prec
        self.bits = bits
        self.q = deque((), 40)
        self.T = None
        self.tau = 0
        self.deathcount = 0
        self.edgecount = 0
        self.timer = Timer(0)

        self.data.irq(trigger=3, handler = self.irqhandler)

    def ReadBuffer(self):
        t1 = self.q.popleft()
        t2 = self.q.popleft()
        t3 = self.q.popleft()
        strobe = ticks_diff(t3, t2)
        var = abs(1 - ticks_diff(t2, t1) / strobe)
        if var > 0.2:
            return None
        bitstr = 0
        parity = False
        t1 = t3
        for i in range(8):
            t2 = self.q.popleft()
            t = ticks_diff(t2, t1)
            if t > strobe:
                bitstr = bitstr << 1 | 0
            else:
                bitstr = bitstr << 1 | 1
                parity = not parity
            t1 = self.q.popleft()
        t2 = self.q.popleft()
        t = ticks_diff(t2, t1)
        if not parity == (t < strobe):
            return None
        t1 = self.q.popleft()
        t2 = self.q.popleft()
        strobe = ticks_diff(t2, t1)
        parity = False
        for i in range(8):
            t1 = self.q.popleft()
            t2 = self.q.popleft()
            t = ticks_diff(t2, t1)
            if t > strobe:
                bitstr = bitstr << 1 | 0
            else:
                bitstr = bitstr << 1 | 1
                parity = not parity
        t1 = self.q.popleft()
        t2 = self.q.popleft()
        t = ticks_diff(t2, t1)
        if not parity == (t < strobe):
            return None
        return bitstr

    def ReadTemp_int(self):
        return self.T

    def ReadTemp_c(self):
        if self.T != None:
            return round(self.T / (2**self.bits - 1) * (self.high - self.low)
                         + self.low, self.prec)
        else:
            return None
        
    def irqhandler(self, pin):
        self.q.append(ticks_cpu())
        self.edgecount = self.edgecount + 1
        if self.edgecount == 40:
            self.timer.init(period=50, mode=Timer.ONE_SHOT, callback=self.timerhandler)
                
    def timerhandler(self, timer):
        self.edgecount = 0
        self.deathcount += 1
        temp = self.ReadBuffer()
        if temp != None and (temp >= 0 and temp < 2**self.bits):
            if self.T == None or abs(temp - self.T) < 0.1 * 2**self.bits:
                self.T = temp
                self.deathcount = 0
        if self.deathcount > 10:
            self.T = None
             
    def calc_ticks_diffs(self):
        ticks = [self.q.popleft() for i in range(len(self.q))]
        diffs = [ticks[i+1]-ticks[i] for i in range(len(ticks)-1)]
        return ticks, diffs

