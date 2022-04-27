from time import ticks_cpu, ticks_ms, ticks_diff, sleep, ticks_us
from collections import deque
from machine import Timer


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
        self.timer = Timer(0)
        self.period = 77
        self.deathcount = 0

        self.startReading(self.timer)

    def ReadBuffer(self):
        t1 = self.q.popleft()
        t2 = self.q.popleft()
        t3 = self.q.popleft()
        strobe = ticks_diff(t2, t1)
        var = abs(1 - ticks_diff(t2, t1) / strobe)
        if var > 0.2:
            #print("shifted")
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
            #print("parity")
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
            #print("parity")
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
        
    def startReading(self, t):
        self.deathcount += 1
        t0 = ticks_us()        
        for i in range(20):
            while self.data.value() == 1:
                pass
            self.q.append(ticks_cpu())
            while self.data.value() == 0:
                pass
            self.q.append(ticks_cpu())
        self.ReadTemp_int()
        
        temp = self.ReadBuffer()
        if temp != None and (temp >= 0 and temp < 2**self.bits):
            if self.T == None or abs(temp - self.T) < 0.1 * 2**self.bits:
                self.T = temp
                self.deathcount = 0
        if self.deathcount > 10:
            self.T = None

        self.tau = ticks_diff(ticks_us(), t0)
        if self.tau < 4000:
            self.period = (self.period-1) % 120
        elif self.tau > 5000:
            self.period = (self.period+1) % 120
        t.init(mode=Timer.ONE_SHOT, period = self.period,
               callback = self.startReading)
        
        


class tsicActive(tsic):
    def __init__(
        self, dataPin, powerPin, maxBitTime=40000, high=150, low=-50,
        prec=1, bits=11
    ):
        self.data = dataPin
        self.power = powerPin
        self.power.value(0)
        self.maxBitTime = maxBitTime
        self.high = high
        self.low = low
        self.prec = prec
        self.bits = bits
        self.q = deque((), 40)

    def fillBuffer(self):
        self.q = deque((), 40)
        self.power.value(1)
        self.q.append(ticks_cpu())
        while len(self.q) < 40:
            while self.data.value() == 1:
                pass
            self.q.append(ticks_cpu())
            while self.data.value() == 0:
                pass
            self.q.append(ticks_cpu())
        self.power.value(0)

    def ReadTemp_int(self):
        self.fillBuffer()
        return self.ReadBuffer()

    def ReadTemp_c(self):
        self.fillBuffer()
        temp = self.ReadBuffer()
        if temp != None:
            T = temp
        return round(
            T / (2**self.bits - 1) * (self.high - self.low) + self.low, self.prec
        )