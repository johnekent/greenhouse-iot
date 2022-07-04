""" Light_Sensor.py
An abstraction of a light sensor.
"""
import logging
import SI1145.SI1145 as SI1145_probe

class LightSensor:
    """ LightSensor class
    """
    def __init__(self):
        self.sensor = SI1145_probe.SI1145()

    def read(self):
        """Take readings from sensor

        Returns:
            dict: visible, IR, UV, UV_index
        """
        sensor = self.sensor
        metrics = None

        try:
            visible_light = sensor.readVisible()
            infra_red = sensor.readIR()
            ultra_violet = sensor.readUV()
            uv_index = ultra_violet / 100.0

            metrics = {"visible": visible_light, "IR": infra_red, "UV": ultra_violet, "UV_index": uv_index}

        except RuntimeError as rte:
            logging.error(f"The attempt to read the light sensor failed with {rte}")
        except OSError as ose:
            logging.error(f"The attempt to read the light sensor failed with {ose}")

        logging.debug(f"LightSensor.read() returning {metrics}")
        return metrics
