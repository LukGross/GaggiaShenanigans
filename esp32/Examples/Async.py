import uasyncio
from time import ticks_ms, ticks_diff, ticks_us
c = 0
timesup = uasyncio.Event()

async def blink(led, period_ms):
    global c
    while not timesup.is_set():
        led.on()
        await uasyncio.sleep_ms(period_ms)
        led.off()
        c += 1
        await uasyncio.sleep_ms(period_ms)
    return True

async def count(max):
    global c
    timesup.clear()
    while c <= max:
        print(c)
        await uasyncio.sleep_ms(10)
    timesup.set()
        


def main(led):
    global c
    period = 50
    increment = 50
    for i in range(10):
        c = 0
        counter = uasyncio.create_task(count(5))
        blinker = uasyncio.create_task(blink(led,period))
        period += increment
        a = await blinker
    
    


# Running on a generic board
from machine import Pin
led = Pin(2, Pin.OUT)
uasyncio.run(main(led))
