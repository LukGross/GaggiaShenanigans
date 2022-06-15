import uasyncio
from microdot_asyncio import Microdot
from machine import Pin

# setup webserver
app = Microdot()

led = Pin(2, Pin.OUT)
per_file = open("period.txt","r")
period = int(per_file.read())
per_file.close


async def blink(period):
    while True:
        led(1)
        await uasyncio.sleep_ms(period)
        led(0)
        await uasyncio.sleep_ms(period)

@app.route('/')
async def query_period(request):
    global period
    return str(period) + "ms"

@app.route('/set')
async def set_period(request):
    global period
    global blinker
    period = int(request.args['period'])
    per_file = open("period.txt","w")
    per_file.write(str(period))
    per_file.close
    if blinker:
        blinker.cancel()
    blinker = uasyncio.create_task(blink(period))
    return 'period set to ' + str(period) + "ms"


def main():
    global blinker
    blinker = uasyncio.create_task(blink(period))
    server = uasyncio.create_task(app.start_server(port = 80))
    print(server)
    while True:
        await uasyncio.sleep(1)

uasyncio.run(main())