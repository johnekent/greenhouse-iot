""" Temp_Humidity_Sensor.py
Uses the AHT10 since the DHT11 / DHT22 was inconsistent on pi zero w (worked on pi zero 2 w)
An abstraction of a sensor.
"""
import logging
import board
import adafruit_ahtx0

class TempHumiditySensorI2C:
    """ TempHumiditySensorI2C class.
    """

    def __init__(self):
        """constructor
        """
        # Create sensor object, communicating over the board's default I2C bus
        i2c = board.I2C()  # uses board.SCL and board.SDA
        self.sensor = adafruit_ahtx0.AHTx0(i2c)

    def read(self):
        """Take readings from sensor

        Returns:
            dict: temp_celsius, temp_fahrenheit, humidity
        """

        sensor = self.sensor

        metrics = None
        temp_c = None
        temp_f = None
        humidity = None
        try:
            temp_c = sensor.temperature
            temp_f = temp_c * (9/5) + 32
            humidity = sensor.relative_humidity
            metrics = {"temp_celsius": temp_c, "temp_fahrenheit": temp_f, "humidity": humidity}

        except RuntimeError as rte:
            logging.error(f"Received {rte} while obtaining temperature and humidity")

        logging.debug(f"TempHumiditySensor.read() returning {metrics}")
        return metrics

if __name__ == "__main__":
    sensor = TempHumiditySensorI2C()
    print(sensor.read())
