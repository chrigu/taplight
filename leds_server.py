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

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_INDICATE_DONE = const(20)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTC_WRITE_DONE = const(17)

_FLAG_WRITE = const(0x0008)
_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

# org.bluetooth.service.environmental_sensing
_LEDS_UUID = bluetooth.UUID('f281c95f-3947-4879-b851-08c11d22f085')
# org.bluetooth.characteristic.temperature
_LEDS_CHAR = (
    bluetooth.UUID('3c110d21-b7a4-4115-889a-77a03fdbcda3'),
    _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,
)

_LEDS_SERVICE = (
    _LEDS_UUID,
    (_LEDS_CHAR,),
)

# org.bluetooth.characteristic.gap.appearance.xml


class BLELeds:
    def __init__(self, ble, name='lightpi'):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle,),) = self._ble.gatts_register_services((_LEDS_SERVICE,))
        self._connections = set()
        self._payload = advertising_payload(
            name=name, services=[_LEDS_UUID]
        )

        self.status = 0

        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == _IRQ_GATTS_WRITE:
            # A client has written to this characteristic or descriptor.
            conn_handle, attr_handle = data
        elif event == _IRQ_GATTC_WRITE_DONE:
            # A gattc_write() has completed.
            # Note: The value_handle will be zero on btstack (but present on NimBLE).
            # Note: Status will be zero on success, implementation-specific value otherwise.
            conn_handle, value_handle, status = data
            if conn_handle in self._connections and value_handle == self._handle:
                self.status = self._ble.gatts_read(self._handle)
                if self._handle:
                    self._handle()
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_INDICATE_DONE:
            conn_handle, value_handle, status = data

    def set_flow(self, flow, notify=False, indicate=False):
        # Data is sint16 in degrees Celsius with a resolution of 0.01 degrees Celsius.
        # Write the local value, ready for a central to read.
        self._ble.gatts_write(self._handle, struct.pack("<h", int(flow * 100)))
        if notify or indicate:
            for conn_handle in self._connections:
                if notify:
                    # Notify connected centrals.
                    self._ble.gatts_notify(conn_handle, self._handle)
                if indicate:
                    # Indicate connected centrals.
                    self._ble.gatts_indicate(conn_handle, self._handle)

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)


async def demo():
    ble = bluetooth.BLE()
    leds = BLELeds(ble)

    while True:
        await uasyncio.sleep_ms(1000)

if __name__ == "__main__":
    uasyncio.run(demo())
