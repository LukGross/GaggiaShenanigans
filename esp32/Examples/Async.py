import uasyncio
from time import ticks_ms, ticks_diff, ticks_us
mss = 0
t = 0
c = 0

async def blink(led, period_ms):
    while True:
        led.on()
        await uasyncio.sleep_ms(period_ms)
        led.off()
        await uasyncio.sleep_ms(period_ms)

async def count():
    global mss
    while True:
        await uasyncio.sleep_ms(100)
        mss +=1
        
async def time():
    global c
    global t
    while True:
        t0 = ticks_us()
        await uasyncio.sleep(1)
        t += ticks_diff(ticks_us(), t0)
        c += 1

async def main(led):
    blinker = uasyncio.create_task(blink(led, 10))
    counter = uasyncio.create_task(time())
    await uasyncio.sleep_ms(5000)
    blinker.cancel()
    counter.cancel()
    print(t/c/1000)
    uasyncio.create_task(blink(led, 100))
    await uasyncio.sleep_ms(5000)


# Running on a generic board
from machine import Pin
uasyncio.run(main(Pin(2, Pin.OUT)))