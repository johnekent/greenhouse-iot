"""  To be run on a given environment.  Does not work in builds or on windows development machine.
Run through test of known sensors.
"""

from app.sensor import TempHumiditySensor
from app.sensor import TempHumiditySensorI2C
from app.sensor import LightSensor
from app.sensor import LightSensorUV
from app.sensor import WaterProbe


if __name__ == "__main__":

    sensors = [TempHumiditySensor(), TempHumiditySensorI2C(), LightSensor(), LightSensorUV(), WaterProbe()]

    for sensor in sensors:
        print(f"Read {sensor.read()} from {sensor}")

