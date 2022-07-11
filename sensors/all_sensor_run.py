"""  To be run on a given environment.  Does not work in builds or on windows development machine.
Run through test of known sensors.
"""

from temp_humidity_sensor import TempHumiditySensor
from temp_humidity_sensor_i2c import TempHumiditySensorI2C
from light_sensor import LightSensor
from light_sensor_uv import LightSensorUV
from water_probe import WaterProbe

if __name__ == "__main__":

    sensors = [TempHumiditySensor(), TempHumiditySensorI2C(), LightSensor(), LightSensorUV(), WaterProbe()]

    for sensor in sensors:
        print(f"Read {sensor.read()} from {sensor}")

