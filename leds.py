import machine, neopixel
import time
import uasyncio

T_STEP = 10

T_DELTA = 900
C1 = [145, 105, 0]
C2 = [255, 230, 164]


class Leds:
    def __init__(self, number_of_lights, pin):
        self._lights = number_of_lights
        self._pin = machine.Pin(pin)
        self._np = neopixel.NeoPixel(self._pin, self._lights)
        self._on = True

        self.set_color(0, 255, 0)
        time.sleep(2)
        self.set_color(0, 0, 0)

    def wheel(self, pos):
        if pos < 0 or pos > 255:
            return (0, 0, 0)
        if pos < 85:
            return (255 - pos * 3, pos * 3, 0)
        if pos < 170:
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

    def set_color(self, r, g, b):
        for i in range(self._lights):
            self._np[i] = (r, g, b)
        self._np.write()

    def calc_new_color(self, C1, C2, step, steps):
        if C1 - C2 == 0:
            return C1
        new_color = ((C2 - C1) * step // steps) + C1

        if new_color > 255:
            return new_color
        elif new_color < 0:
            return 0
        return new_color

    # https://randomnerdtutorials.com/micropython-ws2812b-addressable-rgb-leds-neopixel-esp32-esp8266/
    async def _rainbow_cycle(self, cycle, callback):
        for i in range(self._lights):
            rc_index = (i * 256 // self._lights) + cycle
            self._np[i] = self.wheel(rc_index & 255)
        self._np.write()
        await uasyncio.sleep_ms(T_STEP)
        if callback:
            # return cycle and step
            self._on = callback(cycle)

    async def do_one_cycle(self, C1, C2, steps, cycle, callback):
        # input step and cycle
        for i in range(1, steps + 1):
            if not self._on:
                break

            new_color = [0, 0, 0]
            for j in range(3):
                new_color[j] = self.calc_new_color(C1[j], C2[j], i, steps)
            self.set_color(*new_color)
            await uasyncio.sleep_ms(T_STEP)
            if callback:
                # return cycle and step
                self._on = callback(cycle)

    async def _do_pulse(self, C1, C2, callback):
        steps = T_DELTA // T_STEP
        cycle = 0
        #do cycle in controller
        while self._on:
            await self.do_one_cycle(C1, C2, steps, cycle, callback)
            C2, C1 = C1, C2
            cycle += 1
        self.set_color(0, 0, 0)
        self._on = True

    async def do_rainbow(self, callback=None):
        for i in range(254):
            if not self._on:
                break
            await self._rainbow_cycle(i, callback)

        self.set_color(0, 0, 0)
        self._on = True

    async def do_pulse(self, callback=None):
        await self._do_pulse(C1, C2, callback)

    def stop(self):
        self._on = False


if __name__ == "__main__":

    def cb(cycle):
        return False if cycle > 200 else True

    leds = Leds(60, 27)
    #uasyncio.run(light.do_pulse(callback=cb))
    uasyncio.run(leds.do_rainbow(callback=cb))
