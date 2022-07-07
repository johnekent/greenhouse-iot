import asyncio

from melnor_bluetooth.constants import BATTERY_UUID
from melnor_bluetooth.device import Device

#address = '00:00:00:00:00' # fill with your device mac address
address = '58:93:D8:AC:81:26' # fill with your device mac address

async def test():
    device = Device(mac=address)
    print(f"Device = {device}")
    await device.connect()

    print(device.battery_level())

    await device.disconnect();

asyncio.run(test())
