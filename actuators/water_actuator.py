""" water_actuator.py

Simple wrapper around melnor_bluetooth for a subset of relevant functionality to this project.
"""
import asyncio
import logging
import time

from melnor_bluetooth.constants import BATTERY_UUID
from melnor_bluetooth.device import Device

class WaterActuator:
    """Perform functions such as manual watering based on commands.
    Rather than getting all fancy with asyncio, including event loop inconsistencies between windows
    and linux, this keeps it simple by connecting, acting, and disconnecting each time.
    Also, since these commands will be infrequent and connections can fail between, it just makes sense.
    """
    def __init__(self):
        self.address = '58:93:D8:AC:81:26' # this is the melnor greenhouse address
        try:
            # check and use this to instantiate to prevent calling methods on an inaccessible connection
            asyncio.run(self.validate_connection())
        except Exception as e:
            logging.critical(f"Failed to successfully connect to device on address {self.address} with exception {e}")

    async def validate_connection(self):
        """Make sure the connection can be established and is good through a basic test.

        Args:
            address (str): the mac address address of the watering device
        """

        device = Device(mac=self.address)
        await device.connect()
        await device.fetch_state()
        logging.info(f"Device = {device}")

        await device.disconnect()
        logging.info(f"Device disconnected")
        ## let any exceptions float up

    @staticmethod
    def zone_map(device, zone: int):
        """Map the id to the zone on the device.

        Args:
            zone (int): Integer form of the zone

        Returns:
            device_zone: The devices corresponding zone
        """

        # hackiness due to error:  'AttributeError: 'Device' object has no attribute '_valve_count''
        device.__value_count = 4

        if zone == 1:
            return device.zone1
        elif zone == 2:
            return device.zone2
        elif zone == 3:
            return device.zone3
        elif zone == 4:
            return device.zone4
        else:
            raise ValueError(f"The provided zone was {zone} but must be in range between 1 and 4 inclusive.")

    async def water_zone(self, zone: int, minutes: int):
        """Water the specified zone

        Args:
            zone (int): The integer form of the zone (1,2,3 or 4)
            minutes (int): Duration of watering
        """
        device = Device(mac=self.address)
        device_zone = self.zone_map(device, zone)

        await device.connect()
        await device.fetch_state()
        logging.info(f"Device before setting watering zone {zone} to minutes {minutes} = {device}")

        device_zone.manual_watering_minutes = minutes
        device_zone.is_watering = True
        await device.push_state()
        await device.fetch_state()
        logging.info(f"Device After Zone Watering Set = {device}")
        await device.disconnect()

    async def check_battery(self):

        device = Device(mac=self.address)

        await device.connect()
        await device.fetch_state()
        logging.info(f"Device in battery check = {device}")

        battery = device.battery_level
        await device.disconnect()

        return battery    
     

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
    logging.info("B----Validating actuator constructor...")
    wa = WaterActuator()
    logging.info("E----Validated  actuator constructor...")
    
    logging.info("B-----------Checking water zone")
    asyncio.run(wa.water_zone(zone=1, minutes=1))
    logging.info("E-----------Checked water zone")

    logging.info("B-------Checking battery with return value")
    battery = asyncio.run(wa.check_battery())
    logging.info(f"Battery is {battery}")
    logging.info("E-------Checking battery with return value")

    logging.info("B-----------------Rerunning validation after usage-----")
    asyncio.run(wa.validate_connection())
    logging.info("B-----------------Reran     validation after usage-----")
    
    logging.info("B-----------Checking re-execute of water zone")
    asyncio.run(wa.water_zone(zone=3, minutes=1))
    logging.info("E-----------Completed re-check of water zone function")
