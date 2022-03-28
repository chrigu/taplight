import uasyncio
import machine

from leds_client import leds_client
from leds_server import led_server


async def main():
    input = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_DOWN)

    if input.value == 1:
        await leds_client()
    else:
        await led_server()


if __name__ == "__main__":
    uasyncio.run(main())
