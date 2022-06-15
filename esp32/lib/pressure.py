from machine import ADC, Pin

class pressure:
    def __init__(self, pin, high = 12, low = -1):
        self.analog = ADC(pin, atten=ADC.ATTN_11DB)
        self.uvolts = 3_300_000
        self.high = high
        self.low = low
        self.last_reading = 0
        
    def update(self, n = 10):
        if n > 0:
            read = self.analog.read_uv
            r = range(n)
            reading = 0
            for i in r:
                reading += read()
            self.last_reading = ((self.high-self.low)*(reading/n - self.uvolts*0.1)
                                          /(self.uvolts*0.8) + self.low)
        
    def read(self, n = 10):
        if n > 0:
            self.update(n)
        return self.last_reading