from time import ticks_cpu, ticks_diff, sleep
from collections import deque


class tsic:
    def __init__(self, pin, maxBitTime=100000, high=150, low=-50, prec=1, bits=11):
        self.ZACwire = pin
        self.maxBitTime = maxBitTime
        self.high = high
        self.low = low
        self.prec = prec
        self.bits = bits
        self.q = deque((), 41)
        self.T = None

        self.startBuffer()

    def ReadBuffer(self):
        if len(self.q) < 41:
            # print("short")
            return None
        t1 = self.q.popleft()
        t2 = self.q.popleft()
        t = ticks_diff(t2, t1)
        if t < self.maxBitTime:
            # print("shifted")
            return None
        t1 = t2
        t2 = self.q.popleft()
        t3 = self.q.popleft()
        strobe = ticks_diff(t2, t1)
        var = abs(1 - ticks_diff(t2, t1) / strobe)
        if var > 0.2:
            # print("shifted")
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
            # print("parity")
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
            # print("parity")
            return None
        return bitstr

    def ReadTemp_int(self):
        temp = self.ReadBuffer()
        if temp != None:
            self.T = temp
        return self.T

    def ReadTemp_c(self):
        temp = self.ReadBuffer()
        if temp != None:
            self.T = temp
        if self.T != None:
            return round(
                self.T / (2**self.bits - 1) * (self.high - self.low) + self.low,
                self.prec,
            )

    def push(self, pin):
        t = ticks_cpu()
        self.q.append(t)

    def startBuffer(self):
        self.ZACwire.irq(trigger=3, handler=self.push)
        sleep(0.2)


class tsicActive(tsic):
    def __init__(
        self, dataPin, powerPin, maxBitTime=40000, high=150, low=-50, prec=1, bits=11
    ):
        self.data = dataPin
        self.power = powerPin
        self.power.value(0)
        self.maxBitTime = maxBitTime
        self.high = high
        self.low = low
        self.prec = prec
        self.bits = bits
        self.q = deque((), 41)

    def fillBuffer(self):
        self.q = deque((), 41)
        self.power.value(1)
        self.q.append(ticks_cpu())
        while len(self.q) < 41:
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
