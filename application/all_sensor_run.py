"""  This is a quick connection / integration test to be run on an active environment.
Does not work in builds or on windows development machine.
Run through test of known sensors.
"""
import logging

from app.sensor import TempHumiditySensor
from app.sensor import TempHumiditySensorI2C
from app.sensor import LightSensor
from app.sensor import LightSensorUV
from app.sensor import WaterProbe
from app.sensor import FloatSwitchSensor


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

    sensors = [TempHumiditySensor(), TempHumiditySensorI2C(), LightSensor(), LightSensorUV(), WaterProbe(), FloatSwitchSensor()]

    for sensor in sensors:
        print(f"Read {sensor.read()} from {sensor}")

