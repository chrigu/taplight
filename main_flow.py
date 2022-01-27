# This example demonstrates a simple temperature sensor peripheral.
#
# The sensor's local value updates every second, and it will notify
# any connected central every 10 seconds.

import bluetooth
import struct
import time
from ble_advertising import advertising_payload

from micropython import const
import machine

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_INDICATE_DONE = const(20)

_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

# org.bluetooth.service.environmental_sensing
_FLOW_UUID = bluetooth.UUID('cfdee137-c64e-4701-9b2d-b6b323d4d0e3')
# org.bluetooth.characteristic.temperature
_FLOW_CHAR = (
    bluetooth.UUID('f05e45d2-3352-4839-8f7a-cf950ae1f09e'),
    _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,
)

_FLOW_SERVICE = (
    _FLOW_UUID,
    (_FLOW_CHAR,),
)

# org.bluetooth.characteristic.gap.appearance.xml


class BLEBeerFlow:
    def __init__(self, ble, name="pibeerflow"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle,),) = self._ble.gatts_register_services((_FLOW_SERVICE,))
        self._connections = set()
        self._payload = advertising_payload(
            name=name, services=[_FLOW_UUID]
        )
        self._advertise()

        self.switch = machine.Pin(27, machine.Pin.IN, machine.Pin.PULL_DOWN)

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
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


def demo():
    ble = bluetooth.BLE()
    flow = BLEBeerFlow(ble)

    while True:
        j = flow.switch.value()
        flow.set_flow(j, notify=True, indicate=False)
        # Random walk the temperature.
        time.sleep_ms(1000)

if __name__ == "__main__":
    demo()
