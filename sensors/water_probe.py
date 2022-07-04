"""Water_Probe
Class for reading from the probe's output.
"""
import os
import glob
import time
from pathlib import Path

class WaterProbe:
    """Class to represent a DS18b20 one wire probe for reading.
    Works well when connected to GPIO4 input.
    Has internal retry within read() to connect if initial connection fails
    """

    def __init__(self):
        """Initializes and checks environment

        Raises RuntimeError if the device file is not found
        """

        try:
            self.connect_sensor()
        except RuntimeError as rte:
            print(f"Failed to get connection in constructor.  Reads will retry.  Error: {rte}")


    def connect_sensor(self):
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
            print(f"The device file is {self.device_file}")
        else:
            raise RuntimeError(f"Device file {self.device_file} is not a found file")

    def read_temp_raw(self):
        """Read the raw contents

        Returns:
            lines: raw lines read from device file
        """
        lines = []

        if not self.device_file:  # if it's not been connected try to connect
            try:
                self.connect_sensor()
            except RuntimeError as rte:
                print(f"Failed to get connection in read process.  Will continue to retry.  Error: {rte}")            
        
        if self.device_file:  # if we now or did have the file get the contents
            with open(self.device_file, 'r', encoding='ascii') as file:
                lines = file.readlines()

        return lines

    def read(self):
        """Read the temperature values from the file

        Returns:
            dict:  {"temp_celsius": temp_c, "temp_fahrenheit": temp_f}
        """
        message = None
        lines = self.read_temp_raw()

        if lines:  # don't try to process empty content
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = self.read_temp_raw()
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                temp_f = temp_c * 9.0 / 5.0 + 32.0

                message = {"temp_celsius": temp_c, "temp_fahrenheit": temp_f}

        return message