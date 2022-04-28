# Gaggia Final Build
# Connections:
# Pin   | function
# ------|-----------
#       | OUTs:
# 4     | solenoid valve ssr
# 5     | pump ssr
# 15    | heater ssr
# 14    | heating light (open drain)
# 18    | scl scale
#       | INs:
# 13    | steam switch
# 12    | brew switch
# 19    | dt scale left
# 21    | dt scale right
# 33    | temperature probe
# 32    | pressure transducer

# General Imports #
from timing import timer
import uasyncio as aio

# Pin Declarations #
from machine import Pin
# OUT
valve_pin = Pin(4, Pin.OUT, value = 1)
pump_pin = Pin(5, Pin.OUT, value = 0)
heater_pin = Pin(15, Pin.OUT, value = 0)
scl_scale_pin = Pin(18, Pin.OUT, value = 0)
light_pin = Pin(14, Pin.OPEN_DRAIN, value = 1)
# IN
dt_left_pin = Pin(19, Pin.IN, Pin.PULL_DOWN)
dt_right_pin = Pin(21, Pin.IN, Pin.PULL_DOWN)
steam_pin = Pin(13, Pin.IN, Pin.PULL_DOWN)
brew_pin = Pin(12, Pin.IN, Pin.PULL_DOWN)
temp_pin = Pin(33, Pin.IN, Pin.PULL_UP)
press_pin = Pin(32, Pin.IN)

# initiate tsic, scale and pressure adc #
from tsic import tsic
temp_sens = tsic(temp_pin, Pin(2,Pin.OUT))

from hx711 import HX711
scale = HX711(scl_scale_pin, dt_left_pin, dt_right_pin)
scale.tare()

from pressure import pressure
press_adc = pressure(press_pin)

class sensors:
    def __init__():
        self.temperature = temp_sens.ReadTemp_c()
        self.weight = scale.get_value()
        self.pressure = press_adc.read()
    
    def update_temperature(self):
        self.temperature = temp_sens.ReadTemp_c()
    
    def update_weight(self):
        self.weight = scale.get_value()
    
    def update_pressure(self):
        self.pressure = press_adc.read()

# initiate heater PWM and PID-controller #
brewtemp = 80
steamtemp = 95

from machine import PWM
heater = PWM(heater_pin, freq=1, duty=0)

from PID_discounted import PID
pid = PID(15, 2, 100, setpoint=brewtemp, scale='s')
pid.sample_time = 1
pid.output_limits = (0, 1023)

# actors #
def valve_on():
    valve_pin(0)
def valve_off():
    valve_pin(1)
def is_valve():
    return int(not valve_pin())


def pump_on():
    pump_pin(1)
def pump_off():
    pump_pin(0)
def is_pump():
    return pump_pin()
    
def heater_on(duty = 1023):
    if duty == None:
        duty = 0
    else:
        duty = int(duty)
    heater.duty(duty)
def heater_off():
    heater.duty(0)
def heater_duty():
    return heater.duty()

def light_on():
    light_pin(0)
def light_off():
    light_pin(1)
def is_light():
    return int(not light_pin())
    
def all_off():
    pump_off()
    heater_off()
    valve_off()
    light_off()
    
# switches #
class switches:
    def __init__(self, brew_pin, steam_pin):
        self.brew_pin = brew_pin
        self.steam_pin = steam_pin
        self.is_brew = 0
        self.is_steam = 0
        self.was_brew = 0
        self.was_steam = 0
        self.update()
    
    def __call__(self):
        return self.is_brew, self.was_brew, self.is_steam, self.was_steam

    def update(self):
        self.was_brew = self.is_brew
        self.was_steam = self.is_steam
        self.is_brew = self.brew_pin()
        self.is_steam = self.steam_pin()
    
    def unchanged(self):
        self.update()
        return self.was_brew == self.is_brew and self.was_steam == self.is_steam

sw = switches(brew_pin, steam_pin)

# Events #
switched = aio.Event()

# Coroutines #
# heating control loop
async def heater_control():
    global brewtemp
    global steamtemp
    while True:
        if sw.is_steam:
            pid.setpoint = steamtemp
        else:
            pid.setpoint = brewtemp
        heater_on(pid(temp_sens.ReadTemp_c()))
        await aio.sleep(1)

# brew control loop for standard controls
async def dumb_brew():
    while True:
        if sw.is_brew:
            if not sw.is_steam:
                valve_on()
            else:
                valve_off()
            pump_on()
        else:
            pump_off()
            valve_off()
        await aio.sleep(0)

async def timed_brew(brewtime = 25):
    brewtime = brewtime*1000
    brew_timer = timer()
    brew_timer.start()
    if sw()[2]:
        valve_on()
    else:
        valve_off()
    pump_on()
    while not switched.is_set() and brew_timer.current() <= brewtime:
        await aio.sleep(0)
    pump_off()
    valve_off()
    
async def weigh_brew(target_weight = 30):
    await aio.create_task(scale.tare_async())
    brew_timer = timer()
    brew_timer.start()
    if sw()[2]:
        valve_on()
    else:
        valve_off()
    pump_on()
    while not switched.is_set() and scale.get_value() <= target_weight:
        await aio.sleep(0)
    pump_off()
    valve_off()
    
        
# display loop
async def display(debug = False):
    while True:
        if debug:
            print("temperature: " + str(round(temp_sens.ReadTemp_c(),1)) + "°C; "
                  + "pressure: " + str(round(press_adc.read(),1)) + "bar; "
                  + "weight: " + str(round(scale.get_value(),1)) + "g; "
                  + "heater-duty: " + str(round(heater_duty()/1023*100)) + "%; "
                  + "pid-goal: " + str(round(pid.setpoint,0)) + "°C; "
                  + "brew/steam: " + str(sw()[0]), str(sw()[2]) + "; "
                  + "light/valve/pump: " + str(is_light()), str(is_valve()), str(is_pump())
                  , end = "           \r")
        else:
            print("temperature: " + str(temp_sens.ReadTemp_c()) + "°; "
                  + "pressure: " + str(round(press_adc.read(),1)) + "bar; "
                  + "weight: " + str(round(scale.get_value(),1)) + "g"
                  , end = "           \r")
        await aio.sleep(.5)

# switch watcher
async def switch_watcher():
    while sw.unchanged():
        await aio.sleep(.01)
    switched.set()

async def switch_watcher_dumb():
    while True:
        sw.update()
        await aio.sleep(.01)

# main routines #
# pid heating + standard gaggia classic brewing
async def main_dumb(debug = False):
    loop = aio.get_event_loop()
    heater_task = aio.create_task(heater_control())
    brew_task = aio.create_task(dumb_brew())
    display_task = aio.create_task(display(debug))
    switches_task = aio.create_task(switch_watcher_dumb())
    loop.run_forever()

# pid heating + smart brewing
async def main(debug = False):
    heater_task = aio.create_task(heater_control())
    display_task = aio.create_task(display(debug))
    while True:
        switched.clear()
        if sw()[0] and not sw()[1]:
            switches_task = aio.create_task(switch_watcher())
            brew_task = aio.create_task(weigh_brew())
            await switches_task
            await brew_task
        else:
            switches_task = await aio.create_task(switch_watcher())

if sw.is_steam:
    aio.run(main_dumb(debug = True))
    pass
else:
    aio.run(main(debug = True))
all_off()


