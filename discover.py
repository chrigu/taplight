import asyncio
from bleak import BleakScanner

def detection_callback(device, advertisement_data):
    print(device.details)
    print(device.metadata)
    print(device.address, "RSSI:", device.rssi, advertisement_data)
    print(advertisement_data.manufacturer_data)

async def main():
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)
    await scanner.start()
    await asyncio.sleep(10.0)
    await scanner.stop()

    for d in scanner.discovered_devices:
        print(d)

asyncio.run(main())

# a495bb70c5b14b44b5121370f02d74de
# -5.8P, 19.4C
# HCI Event:
#     code:
#         3e
#     length:
#         42
#     LE Meta:
#         code:
#             02
#         Adv Report:
#             num reports:
#                 1
#             ev type:
#                 no connection adv
#             addr type:
#                 random
#             peer:
#                 f3:f0:e4:06:d5:e5
#             length:
#                 30
#             flags:
#                 Simul LE - BR/EDR (Host): False
#                 Simul LE - BR/EDR (Control.): False
#                 BR/EDR Not Supported: False
#                 LE General Disc.: True
#                 LE Limited Disc.: False
#             Payload for mfg_specific_data:
#                 4c:00:02:15:a4:95:bb:70:c5:b1:4b:44:b5:12:13:70:f0:2d:74:de:00:43:03:d2:c5
#             rssi:
#                 -40

# 00 43	67 °F
# 2	03 D2	978 sg