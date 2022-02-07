import asyncio
from bleak import BleakClient

address = "CBC59304-2DE7-4A5B-BF0E-120BC9AA429B"
LIGHT_CHAR = "3c110d21-b7a4-4115-889a-77a03fdbcda3"
LIGHT_SERVICES = "f281c95f-3947-4879-b851-08c11d22f085"

async def main(address):
    async with BleakClient(address) as client:
        services = await client.get_services()
        print('services', services.get_characteristic(LIGHT_CHAR))
        print('char', services.characteristics[20].service_uuid)
        print('servicehandle', services.characteristics[20].service_handle)
        print('serviceuuid', services.characteristics[20].service_uuid)
        print('charuuid', services.characteristics[20].uuid)
        print('charhandle', services.characteristics[20].handle)
        print('props', services.characteristics[20].properties)
        await client.write_gatt_char(services.characteristics[20], bytearray(b'0'))
        print('write done')
        await asyncio.sleep(2)

asyncio.run(main(address))