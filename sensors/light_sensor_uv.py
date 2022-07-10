""" Light_Sensor.py
An abstraction of a light sensor.
"""
import logging

import board
import busio
import adafruit_ltr390

from sensor import Sensor

class LightSensorUV:
    """ LightSensorUV class
    """
    def __connect__(self):

        connection = None

        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            connection = adafruit_ltr390.LTR390(i2c)
        except Exception as e:
            raise RuntimeError(f"Failed to create connection to LTR390 I2C with {e}")

        return connection

    def __read__(self):
        """Take readings from sensor

        Returns:
            dict: UV, ambient, UVI, lux
        """
        sensor = self.connection
        metrics = None

        try:
            metrics = {"UV": sensor.uvs, "ambient": sensor.light, "UVI": sensor.uvi, "lux": sensor.lux}
        except Exception as e:  # can be RuntimeError or OSError -- both result in the same path
            err_msg = f"The attempt to read the light sensor uv failed with {e}"
            raise RuntimeError(err_msg)

        logging.debug(f"LightSensorUV.read() returning {metrics}")
        return metrics

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
    sensor = LightSensorUV()
    print(sensor.read())