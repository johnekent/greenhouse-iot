import asyncio
import time

from melnor_bluetooth.constants import BATTERY_UUID
from melnor_bluetooth.device import Device

#address = '00:00:00:00:00' # fill with your device mac address
address = '58:93:D8:AC:81:26' # this is the melnor greenhouse address
#address = '59:93:D8:AC:81:26' # this is the wrong address -- does not connect when this is used

async def test():
    device = Device(mac=address)
    print(f"Device before connect = {device}")
    await device.connect()
    print(f"Device Connected = {device}")
    await device.fetch_state()
    print(f"Device after fetching state = {device}")

    print(device.battery_level)

    manual_minutes = 2
    zones = [device.zone1, device.zone2, device.zone3, device.zone4]
    for zone in zones:
        zone.manual_watering_minutes = manual_minutes
        zone.is_watering = True

    await device.push_state()
    await device.fetch_state()
    print(f"Device After Zone Watering Set = {device}")

    start_seconds = time.time()
    to_sleep = 10
    remain = manual_minutes * 60 + 30
    while remain > 0:
        remain -= to_sleep
        time.sleep(to_sleep)
        await device.fetch_state()
        now = time.time()
        print(f"Device with {now - start_seconds} elapsed fetching state = {device}")
        print(f"Zone 1 Watering end time (aka seconds_left) minus now is {device.zone1.watering_end_time - now}")
        print(f"Zone 3 Watering end time (aka seconds_left) minus now is {device.zone3.watering_end_time - now}")

    await device.disconnect()

asyncio.run(test())
