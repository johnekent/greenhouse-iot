"""float_switch_sensor
"""
from ast import Import
import logging

## this is realated to the TODO in the ignore_sensor_modules.py testing script.  Please direct your attention elsewhere.
try:
    from RPi import GPIO as GPIO
except ImportError as ie:
    logging.warning(f"The import of RPi.GPIO failed.  This may not work properly.  Try to install it.")
    
from . sensor import Sensor

class FloatSwitchSensor(Sensor):
    """ Class for reading the state of the float switch.
    Initially hardcoded to use GPIO 27 (Physical 13).
    """

    def _connect(self):

        connection = None
        self.switch_pin = 27
        
        try:
            GPIO.setwarnings(False)

            ## this number is the "GPIO #" - e.g. physical 13 = GPIO 27
            GPIO.setmode(GPIO.BCM)
                
            GPIO.setup(self.switch_pin, GPIO.IN, GPIO.PUD_UP)
            # set connection to a non-None value - the GPIO channel (~pin) setup above doesn't return a handle.
            # however the Sensor retry / error handling logic works based on the existence of a connection
            # in this case there is no connection but this will give it a value
            connection = True
        except Exception as e:
            raise RuntimeError(f"Failed to setup GPIO for pin {self.switch_pin} with exception {e}")

        logging.debug(f"FloatSwitchSensor created connection={connection} on pin {self.switch_pin}")
        return connection


    def _read(self):
        """ Read the state of the sensor.

        Returns:
            dict:  { "float_switch": [HIGH (floating up) | LOW (water level low; not floating)] }
        """
        metrics = None
        logging.debug(f"FloatSwitchSensor._read() initiating")

        try:
            float_switch_state = "HIGH" if GPIO.input(self.switch_pin) == GPIO.HIGH else "LOW"
            metrics = {"float_switch_state": float_switch_state}
            logging.debug(f"Got metrics {float_switch_state} from the float switch")
        except Exception as e:
            raise RuntimeError(f"Failed to get the input button state with exception {e}")
            
        logging.debug(f"FloatSwitchSensor.read() returning {metrics}")
        return metrics


    def _name(self):
        return "float_switch"

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
    sensor = FloatSwitchSensor()
    print(sensor.read())
