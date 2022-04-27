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

# initiate heater PWM and PID-controller #
brewtemp = 95
steamtemp = 145

from machine import PWM
heater = PWM(heater_pin, freq=1, duty=0)

from PID import PID
pid = PID(14.3, 2, 613, setpoint=brewtemp, scale='s')
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
        self.is_brew = False
        self.is_steam = False
        self.was_brew = False
        self.was_steam = False
        self.update()

    def update(self):
        self.was_brew = self.is_brew
        self.was_steam = self.is_brew
        self.is_brew = self.brew_pin()
        self.is_steam = self.steam_pin()

sw = switches(brew_pin, steam_pin)
    
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
        await uasyncio.sleep(1)

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
        await uasyncio.sleep(0)
        
# display loop
async def display(debug = False):
    while True:
        if debug:
            print("temperature: " + str(round(temp_sens.ReadTemp_c(),1)) + "°C; "
                  + "pressure: " + str(round(press_adc.read(),1)) + "bar; "
                  + "weight: " + str(round(scale.get_value(),1)) + "g; "
                  + "heater-duty: " + str(round(heater_duty()/1023*100,0)) + "%; "
                  + "pid-goal: " + str(round(pid.setpoint,0)) + "°C;"
                  + "is_steam: " + str(sw.is_steam) + "; "
                  + "is_brew: " + str(sw.is_brew) + "; "
                  + "is_light: " + str(is_light()) + "; "
                  + "is_valve: " + str(is_valve()) + "; "
                  + "is_pump: " + str(is_pump()) + "; "
                  , end = "           \r")
        else:
            print("temperature: " + str(round(temp_sens.ReadTemp_c(),1)) + "°; "
                  + "pressure: " + str(round(press_adc.read(),1)) + "bar; "
                  + "weight: " + str(round(scale.get_value(),1)) + "g"
                  , end = "           \r")
        await uasyncio.sleep(.5)

# switch supervisor
async def switches():
    while True:
        sw.update()
        await uasyncio.sleep(.01)

# main routines #
# standard gaggia classic behaviour
async def main_dumb(debug = False):
    heater_task = uasyncio.create_task(heater_control())
    brew_task = uasyncio.create_task(dumb_brew())
    display_task = uasyncio.create_task(display(debug))
    switches_task = uasyncio.create_task(switches())
    #while True:
    await uasyncio.sleep(100)

import uasyncio
from timing import timer

if sw.is_steam:
    uasyncio.run(main_dumb(debug = True))
    pass
else:
    pass
all_off()


