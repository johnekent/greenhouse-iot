""" Temp_Humidity_Sensor.py
An abstraction of a sensor.
"""
import logging
import adafruit_dht
import board

class TempHumiditySensor:
    """ TempHumiditySensor class.
    """

    def __init__(self, input_pin=board.D17):
        """constructor

        Args:
            board (board, optional): The input pin.  Defaults to board.17 (GPIO 17, Physical 11).
        """
        self.dht_device = adafruit_dht.DHT22(input_pin, use_pulseio=False)

    def read(self):
        """Take readings from sensor

        Returns:
            dict: temp_celsius, temp_fahrenheit, humidity
        """

        device = self.dht_device

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

        logging.debug(f"TempHumiditySensor.read() returning {metrics}")
        return metrics

if __name__ == "__main__":
    sensor = TempHumiditySensor()
    print(sensor.read())