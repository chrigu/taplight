import uasyncio
import bluetooth


async def main():
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
    uasyncio.run(main())