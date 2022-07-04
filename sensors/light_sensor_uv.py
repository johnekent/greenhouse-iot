""" Light_Sensor.py
An abstraction of a light sensor.
"""
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
            print(f"The attempt to read the light sensor uv failed with {rte}")
        except OSError as ose:
            print(f"The attempt to read the light sensor uv failed with {ose}")

        return metrics
