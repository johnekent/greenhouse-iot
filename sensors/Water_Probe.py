"""Water_Probe
Class for reading from the probe's output.
"""
import os
import glob
import time
from pathlib import Path

class WaterProbe:
    """Class to represent a DS18b20 one wire probe for reading.
    Works well when connected to GPIO4 input
    """

    def __init__(self):
        """Initializes and checks environment

        Raises RuntimeError if the device file is not found
        """
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'

        if Path(self.device_file).is_file():
            print(f"The device file is {self.device_file}")
        else:
            raise RuntimeError(f"Device file {self.device_file} is not a found file")

    def read_temp_raw(self):
        """Read the raw contents

        Returns:
            lines: raw lines read from device file
        """
        lines = []
        with open(self.device_file, 'r', encoding='ascii') as file:
            lines = file.readlines()

        return lines

    def read(self):
        """Read the temperature values from the file

        Returns:
            dict:  {"temp_celsius": temp_c, "temp_fahrenheit": temp_f}
        """
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0

            return {"temp_celsius": temp_c, "temp_fahrenheit": temp_f}