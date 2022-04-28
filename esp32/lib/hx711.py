from machine import enable_irq, disable_irq, idle
import time
from timing import timer
import uasyncio as aio

class HX711:
    def __init__(self, pd_sck, dout_left, dout_right, gain=128, deadtime = 100):
        self.pSCK = pd_sck
        self.pOUT_left = dout_left
        self.pOUT_right = dout_right
        self.pSCK.value(False)

        self.GAIN = 0
        self.OFFSET = 0
        self.SCALE = 192.7/342900

        self.time_constant = 0.25
        self.filtered = 0
        
        self.deadtime = deadtime
        self.deadtimer = timer()
        self.deadtimer.start()
        self.last = 0

        self.set_gain(gain)
        self.tare()

    def set_gain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32:
            self.GAIN = 2

        self.read()
        self.filtered = self.read()

    def is_ready(self):
        return self.pOUT_left() == 0 and self.pOUT_right() == 0

    def read(self):
        if self.deadtimer.current() < self.deadtime:
            return self.last
        
        # wait for the device being ready
        for _ in range(500):
            if self.is_ready:
                break
            time.sleep_ms(1)
        else:
            raise OSError("Sensor does not respond")

        # shift in data, and gain & channel info
        result_left = 0
        result_right = 0
        for j in range(24 + self.GAIN):
            state = disable_irq()
            self.pSCK(True)
            self.pSCK(False)
            enable_irq(state)
            result_left = (result_left << 1) | self.pOUT_left()
            result_right = (result_right << 1) | self.pOUT_right()
        
        # restart deadtimer
        self.deadtimer.start()
        
        # shift back the extra bits
        result_left >>= self.GAIN
        result_right >>= self.GAIN

        # check sign
        if result_left > 0x7fffff:
            result_left -= 0x1000000
        if result_right > 0x7fffff:
            result_right -= 0x1000000
            
        self.last = result_left + result_right

        return self.last

    def read_average(self, times=3, sleeptime=0.1):
        total = 0
        for i in range(times):
            total += self.read()
            time.sleep(sleeptime)
        return total / times
    
    async def read_average_async(self, times=3, sleeptime=0.1):
        total = 0
        for i in range(times):
            total += self.read()
            await aio.sleep(sleeptime)
        return total / times

    def read_lowpass(self):
        self.filtered += self.time_constant * (self.read() - self.filtered)
        return self.filtered

    def get_value(self):
        return self.SCALE*(self.read() - self.OFFSET)

    def get_value_average(self, times=3):
        return self.SCALE*(self.read_average(times) - self.OFFSET)

    def get_units(self):
        return self.get_value() / self.SCALE

    def tare(self, times=15):
        self.set_offset(self.read_average(times))
        
    async def tare_async(self, times=15):
        reading = await aio.create_task(self.read_average_async(times))
        self.set_offset(reading)
    
    def set_scale(self, scale):
        self.SCALE = scale

    def set_offset(self, offset):
        self.OFFSET = offset

    def set_time_constant(self, time_constant = None):
        if time_constant is None:
            return self.time_constant
        elif 0 < time_constant < 1.0:
            self.time_constant = time_constant

    def power_down(self):
        self.pSCK.value(False)
        self.pSCK.value(True)

    def power_up(self):
        self.pSCK.value(False)
