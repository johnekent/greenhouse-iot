""" water_actuator.py

Simple wrapper around melnor_bluetooth for a subset of relevant functionality to this project.
"""
import asyncio
import logging
import time

## this is realated to the TODO in the ignore_sensor_modules.py testing script.  Please direct your attention elsewhere.
try:
    from melnor_bluetooth.constants import BATTERY_UUID
    from melnor_bluetooth.device import Device
except ImportError as ie:
    logging.warning(f"The import of melnor_bluetooth failed.  This may not work properly.  Try to install it.")

class WaterActuator:
    """Perform functions such as manual watering based on commands.
    Rather than getting all fancy with asyncio, including event loop inconsistencies between windows
    and linux, this keeps it simple by connecting, acting, and disconnecting each time.
    Also, since these commands will be infrequent and connections can fail between, it just makes sense.
    """
    def __init__(self, address, validate_connection=False):
        self.address = address # this is the melnor greenhouse address as seen in the app but separated by colons -- e.g. '38:23:C8:A1:21:36'

        if validate_connection:
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
        if not device.is_connected:
            logging.info(f"The device is not connected so skipping remainder of request to validate connection.")
            return None

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
        device._valve_count = 4

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

    @staticmethod
    def get_device_status(device):
        valves = [ device.zone1, device.zone2, device.zone3, device.zone4 ]

        status = { 
            'battery_level': device.battery_level,
            'valves': { f'valve{i+1}': { 
                    'id': valves[i].id,
                    'is_watering': valves[i].is_watering,
                    'manual_watering_minutes': valves[i].manual_watering_minutes,
                    'watering_end_time': valves[i].watering_end_time }
                for i in range(0,len(valves)) }
        }

        return status

    @staticmethod
    def is_watering(valve):
        return valve.is_watering

    async def water_zone(self, zone: int, minutes: int):
        """Water the specified zone

        Args:
            zone (int): The integer form of the zone (1,2,3 or 4)
            minutes (int): Duration of watering
        """

        logging.info(f"Connecting to device address {self.address} to water zone {zone}.")
        device = Device(mac=self.address)
        await device.connect()
        if not device.is_connected:
            logging.info(f"The device is not connected so skipping remainder of request to water.")
            return None

        await device.fetch_state()

        device_zone = WaterActuator.zone_map(device, zone)  #aka valve
        logging.info(f"The device zone valve {device_zone} will be used for any watering requests.")

        device_status = WaterActuator.get_device_status(device)
        logging.info(f"The device status in water request is {device_status}")

        if not WaterActuator.is_watering(device_zone):
            device_zone.manual_watering_minutes = minutes
            device_zone.is_watering = True
            await device.push_state()
            await device.fetch_state()
            logging.info(f"Device After Zone Watering Set = {device}")
            await device.disconnect()
            logging.info(f"The device was issued a request to water zone {zone} for {minutes}, which was successfully executed.")
        else:
            logging.warning(f"The device was issued a request to water zone {zone} for {minutes}.  However, it is already watering so this command was ignored.")

        return device_status

    async def check_battery(self):
        """Get the battery status

        Returns:
            battery (int): 0-100 range of battery percent remaining
        """

        device = Device(mac=self.address)

        battery = None
        await device.connect()
        if not device.is_connected:
            logging.info(f"The device is not connected so skipping remainder of request to check water.")
            return battery
        
        await device.fetch_state()
        logging.info(f"Device in battery check = {device}")

        battery = device.battery_level
        await device.disconnect()

        return battery   


if __name__ == "__main__":

    import sys
    if len(sys.argv) == 2:
        address = sys.argv[1]
    else:
        logging.error("Please enter the bluetooth device address as an argument.")
        exit()
    
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
    logging.info("B----Validating actuator constructor...")
    wa = WaterActuator(address, validate_connection=True)
    logging.info("E----Validated  actuator constructor...")

    logging.info("B-----------Checking water zone")
    status = asyncio.run(wa.water_zone(zone=1, minutes=1))
    logging.info("E-----------Checked water zone and got status of {status}")

    logging.info("B-------Checking battery with return value")
    battery = asyncio.run(wa.check_battery())
    logging.info(f"Battery is {battery}")
    logging.info("E-------Checking battery with return value")

    logging.info("B-----------------Rerunning validation after usage-----")
    asyncio.run(wa.validate_connection())
    logging.info("B-----------------Reran     validation after usage-----")

    logging.info("B-----------Checking re-execute of water zone")
    status = asyncio.run(wa.water_zone(zone=3, minutes=1))
    logging.info("E-----------Completed re-check of water zone function with status = {status}")
