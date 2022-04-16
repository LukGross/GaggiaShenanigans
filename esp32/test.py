from machine import Pin, PWM
from time import sleep, sleep_us
import esp32

#PC = Pin(4, Pin.OUT)
#freq = 512



r = esp32.RMT(0, pin=Pin(4), clock_div=80)
#r   # RMT(channel=0, pin=18, source_freq=80000000, clock_div=8)
# The channel resolution is 100ns (1/(source_freq/clock_div)).
#r.write_pulses((1, 20, 2, 40), 0) # Send 0 for 100ns, 1 for 2000ns, 0 for 200ns, 1 for 4000ns
phase = 1500
def zeroCross(pin):
    global phase
    r.write_pulses((phase,10), 0)
    




ZC = Pin(15, Pin.IN, Pin.PULL_DOWN)
ZC.irq(handler = zeroCross, trigger = Pin.IRQ_FALLING)


while True:
    while phase < 8500:
        sleep(.1)
        phase = phase + 100
    while phase > 1500:
        sleep(.1)
        phase = phase - 100
    