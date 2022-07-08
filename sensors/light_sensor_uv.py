""" Light_Sensor.py
An abstraction of a light sensor.
"""
import logging

import board
import busio
import adafruit_ltr390

class LightSensorUV:
    """ LightSensorUV class
    """
    def __init__(self):

        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_ltr390.LTR390(i2c)

    def read(self):
        """Take readings from sensor

        Returns:
            dict: UV, ambient, UVI, lux
        """
        sensor = self.sensor
        metrics = None

        try:

            metrics = {"UV": sensor.uvs, "ambient": sensor.light, "UVI": sensor.uvi, "lux": sensor.lux}

        except RuntimeError as rte:
            logging.error(f"The attempt to read the light sensor uv failed with {rte}")
        except OSError as ose:
            logging.error(f"The attempt to read the light sensor uv failed with {ose}")

        logging.debug(f"LightSensorUV.read() returning {metrics}")
        return metrics

if __name__ == "__main__":
    sensor = LightSensorUV()
    print(sensor.read())