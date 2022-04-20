from machine import ADC, Pin

class pressure:
    def __init__(self, pin, high = 20.6843, low = 0):
        self.analog = ADC(pin, atten=ADC.ATTN_11DB)
        self.high = high
        self.low = low
        
    def read(self, n):
        r = range(n)
        reading = 0
        for i in r:
            reading += ((self.high-self.low)*(self.analog.read_uv() - 330000)
                        /2600000 + self.low)/n
        return reading