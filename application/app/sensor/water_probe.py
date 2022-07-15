"""Water_Probe
Class for reading from the probe's output.
"""
import glob
import logging
import os
import time
from pathlib import Path

from . sensor import Sensor

class WaterProbe(Sensor):
    """Class to represent a DS18b20 one wire probe for reading.
    Works well when connected to GPIO4 input.
    """

    def _connect(self):

        connection = None

        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        base_dir = '/sys/bus/w1/devices/'
        
        device_folders = glob.glob(base_dir + '28*')

        self.device_file = None

        if device_folders:
            self.device_file = device_folders[0] + '/w1_slave'
        else:
            raise RuntimeError(f"The device file was not found in expected location: {base_dir}")

        if Path(self.device_file).is_file():
            logging.info(f"The device file is {self.device_file}")
            connection = self.device_file
        else:
            raise RuntimeError(f"Device file {self.device_file} is not a found file")


        return connection

    def read_temp_raw(self, connection):
        """Read the raw contents

        Returns:
            lines: raw lines read from device file
        """
        lines = []

        device_file = connection

        try:
            if device_file:  # if we now or did have the file get the contents
                with open(device_file, 'r', encoding='ascii') as file:
                    lines = file.readlines()
        except Exception as e:
            raise RuntimeError(f"Reading from the device file {device_file} resulted in this error {e}")

        return lines

    def _read(self):
        """Read the temperature values from the file

        Returns:
            dict:  {"temp_celsius": temp_c, "temp_fahrenheit": temp_f}
        """
        metrics = None
        lines = self.read_temp_raw(self.connection)

        if lines:  # don't try to process empty content
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = self.read_temp_raw()
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                temp_f = temp_c * 9.0 / 5.0 + 32.0

                metrics = {"temp_celsius": temp_c, "temp_fahrenheit": temp_f}

        logging.debug(f"WaterProbe.read() returning {metrics}")
        return metrics

    def _name(self):
        return "water_probe"

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
    sensor = WaterProbe()
    print(sensor.read())
