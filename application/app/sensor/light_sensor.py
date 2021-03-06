""" Light_Sensor.py
An abstraction of a light sensor.
"""
import logging
import SI1145.SI1145 as SI1145_probe

from . sensor import Sensor

class LightSensor(Sensor):
    """ LightSensor class
    """
    def __init__(self, name="light_sensor"):
        self.name = name
        super().__init__()

    def _connect(self):
        """Implement the connection method

        Raises:
            RuntimeError: on any exception

        Returns:
            object: connection reference
        """

        connection = None

        try:
            connection = SI1145_probe.SI1145()
        except Exception as e:
            raise RuntimeError(f"On creation of SI1145 received error {e}")

        return connection

    def _read(self):
        """Take readings from sensor

        Returns:
            dict: visible, IR, UV, UV_index
        """
        sensor = self.connection
        metrics = None

        try:
            visible_light = sensor.readVisible()
            infra_red = sensor.readIR()
            ultra_violet = sensor.readUV()
            uv_index = ultra_violet / 100.0

            metrics = {"visible": visible_light, "IR": infra_red, "UV": ultra_violet, "UV_index": uv_index}

        except Exception as e:  # can be RuntimeError or OSError -- both take the same path
            raise RuntimeError(f"The attempt to read the light sensor failed with {e}")

        logging.debug(f"LightSensor.read() returning {metrics}")
        return metrics
    
    def _name(self):
        return self.name

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
    sensor = LightSensor()
    print(sensor.read())