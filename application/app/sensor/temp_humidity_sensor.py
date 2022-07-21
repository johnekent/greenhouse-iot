""" Temp_Humidity_Sensor.py
An abstraction of a sensor.
"""
import logging
import adafruit_dht
import board

from . sensor import Sensor

class TempHumiditySensor(Sensor):
    """ TempHumiditySensor class.
    """

    def __init__(self, name="temp_humidity_sensor"):
        self.name = name
        super().__init__()

    def _connect(self):
        """constructor

        Args:
            board (board, optional): The input pin.  Defaults to board.17 (GPIO 17, Physical 11).
        """

        connection = None
        input_pin = None  # this is to fix the raise error which tries to print when not set.  see TODO below
        try:
            input_pin=board.D17  #TODO:  make this as a configuration parameter in the config.ini
            connection = adafruit_dht.DHT22(input_pin, use_pulseio=False)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to DHT22 on {input_pin} with exception {e}")

        return connection

    def _read(self):
        """Take readings from sensor

        Returns:
            dict: temp_celsius, temp_fahrenheit, humidity
        """

        device = self.connection

        metrics = None
        temp_c = None
        temp_f = None
        humidity = None
        try:
            temp_c = device.temperature
            temp_f = temp_c * (9/5) + 32
            humidity = device.humidity
            metrics = {"temp_celsius": temp_c, "temp_fahrenheit": temp_f, "humidity": humidity}

        except RuntimeError as rte:
            logging.error(f"Received {rte} while obtaining temperature and humidity")
            raise rte  # let it float up

        logging.debug(f"TempHumiditySensor.read() returning {metrics}")
        return metrics

    def _name(self):
        return self.name

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
    sensor = TempHumiditySensor()
    print(sensor.read())
