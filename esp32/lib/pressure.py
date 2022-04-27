from machine import ADC, Pin

class pressure:
    def __init__(self, pin, high = 20.6843, low = 0):
        self.analog = ADC(pin, atten=ADC.ATTN_11DB)
        self.high = high
        self.low = low
        self.last_reading = 0
        
    def update(self, n = 10):
        if n > 0:
            r = range(n)
            reading = 0
            for i in r:
                reading += self.analog.read_uv()
            self.last_reading = ((self.high-self.low)*(reading/n - 330000)
                                          /2600000 + self.low)
        
    def read(self, n = 10):
        if n > 0:
            self.update(n)
        return self.last_reading