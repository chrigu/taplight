import uasyncio
import machine

from leds_client import leds_client
from leds_server import led_server


async def main():
    input = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_DOWN)
    print(input.value())

    if input.value() == 0:
        print('Client mode')
        await leds_client()
    else:
        print('Server mode')
        await led_server()


if __name__ == "__main__":
    uasyncio.run(main())
