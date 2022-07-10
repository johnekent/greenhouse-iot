import asyncio
import logging
import time

from melnor_bluetooth.constants import BATTERY_UUID
from melnor_bluetooth.device import Device

class WaterActuator:

    def __init__(self):
        address = '58:93:D8:AC:81:26' # this is the melnor greenhouse address
        self.device = Device(mac=address)
        asyncio.run(self.__connect__())
        logging.info(f"Device Connected = {self.device}")

    async def __connect__(self):
        """Connect to the bluetooth device and fetch the current state
        """
        await self.device.connect()   
        await self.device.fetch_state()

    def zone_map(self, zone: int):
        """_summary_

        Args:
            zone (int): Integer form of the zone

        Returns:
            device_zone: The devices corresponding zone
        """

        if zone == 1:
            return self.device.zone1
        elif zone == 2:
            return self.device.zone2
        elif zone == 3:
            return self.device.zone3
        elif zone == 4:
            return self.device.zone4
        else:
            raise ValueError(f"The provided zone was {zone} but must be in range between 1 and 4 inclusive.")

    
    def water_zone(self, zone: int, minutes: int):
        """Water the specified zone

        Args:
            zone (int): The integer form of the zone (1,2,3 or 4)
            minutes (int): Duration of watering
        """

        device_zone = self.zone_map(zone)

        asyncio.run(self.__water_zone__(device_zone, minutes))

    async def __water_zone__(self, zone, minutes):
        """ Begin watering the specific zone for the specific interval

        Args:
            zone (melnor_bluetooth.device.zone) : The zone to water
            minutes (int): The duration of the watering
        """
        zone.manual_watering_minutes = minutes
        zone.is_watering = True
        await self.device.push_state()
        await self.device.fetch_state()
        print(f"Device After Zone Watering Set = {self.device}")

    def disconnect(self):
        asyncio.run(self.__disconnect__())

    async def __disconnect__(self):
        await self.device.disconnect()


if __name__ == "__main__":
    wa = WaterActuator()
    wa.water_zone(zone=1, minutes=1)
    wa.disconnect()
