# https://github.com/blafois/MicroPython-WaterSensor

import machine
import network
import time
import json
import sys
import uasyncio

# Global Variables

led = None  # Status led pin
SENSOR_PIN = 15
STATUS_LED = 12

last_update_status = 0
last_update_pulses = 0
last_update_litres = 0
sensor = {}

'''
Setup pins (GPIO)
'''


def setupPins():
    global sensor, led

    s = machine.Pin(SENSOR_PIN, machine.Pin.IN)

    sensor['m3'] = 0
    sensor['pulses'] = 0
    sensor['litres'] = 0

    s.irq(trigger=machine.Pin.IRQ_FALLING, handler=water_tick_handler)

    led = machine.Pin(STATUS_LED, machine.Pin.OUT)
    print('pins setup')


# ------------------------------------------------------------------

'''
Status led toggling
'''


def toggleLed():
    global led
    if led is not None:
        led.value(led.value() ^ 1)


# ------------------------------------------------------------------

def water_tick_handler(p):
    global sensor
    id = str(p)[4:-1]
    sensor['pulses'] += 1

    toggleLed()



def save():
    global sensor
    print("[+] Saving State")

    f = open('state.json', 'w')
    json.dump(sensors, f)
    f.close()


# ------------------------------------------------------------------

def restore():
    global sensors
    try:
        f = open('state.json', 'r')
        print("[+] Restoring State")
        sensors = json.load(f)
        f.close()
    except OSError:
        return False


# ------------------------------------------------------------------

async def flow(handle_data):
    setupPins()

    while True:
        # toggleLed()
        await uasyncio.sleep(1)
        # if time.time() % 5 == 0:
        handle_data(sensor['pulses'])

def print_pulses(pulses):
    print(f'pulses {pulses}')


# Main Program
def main():
    uasyncio.run(flow(print_pulses))

if __name__ == "__main__":
    main()