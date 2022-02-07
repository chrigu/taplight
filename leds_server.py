# This example demonstrates a simple temperature sensor peripheral.
#
# The sensor's local value updates every second, and it will notify
# any connected central every 10 seconds.

import bluetooth
import struct
import time
import uasyncio
from ble_advertising import advertising_payload

from micropython import const
import machine
import gc
from leds import Leds

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_INDICATE_DONE = const(20)
_IRQ_GATTS_WRITE = const(3)

_FLAG_WRITE = const(0x0008)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

# org.bluetooth.service.environmental_sensing
_LEDS_UUID = bluetooth.UUID('f281c95f-3947-4879-b851-08c11d22f085')
# org.bluetooth.characteristic.temperature
_LEDS_CHAR = (
    bluetooth.UUID('3c110d21-b7a4-4115-889a-77a03fdbcda3'),
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)

_LEDS_SERVICE = (
    _LEDS_UUID,
    (_LEDS_CHAR,),
)

# org.bluetooth.characteristic.gap.appearance.xml


class BLELeds:
    def __init__(self, ble, number_of_leds, led_pin, name='lightpi'):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle,),) = self._ble.gatts_register_services((_LEDS_SERVICE,))
        self._connections = set()
        self._payload = advertising_payload(
            name=name, services=[_LEDS_UUID]
        )
        self._write_callback = None

        self.light = Leds(number_of_leds, led_pin)
        self.status = 0

        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
            print('client connected')
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            print('got event', value)
            if value_handle == self._handle and self._write_callback:
                self._write_callback(value)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
            print('client disconnected')
        elif event == _IRQ_GATTS_INDICATE_DONE:
            conn_handle, value_handle, status = data

    def on_write(self, callback):
        self._write_callback = callback

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)


async def demo():
    ble = bluetooth.BLE()
    leds = BLELeds(ble, 60, 27)
    print(gc.mem_free())

    def led_cb(_cycle):
        return leds.status

    def handle_write(data):
        if data == b'0':
            status = 0
        elif data == b'1':
            fn = leds.light.do_rainbow
            status = 1
        elif data == b'2':
            fn = leds.light.do_pulse
            status = 1
        leds.status = status

        if status > 0:
            uasyncio.create_task(fn(callback=led_cb))
        gc.collect()
        print(gc.mem_free())

    leds.on_write(callback=handle_write)

    while True:
        await uasyncio.sleep_ms(1000)

if __name__ == "__main__":
    uasyncio.run(demo())
