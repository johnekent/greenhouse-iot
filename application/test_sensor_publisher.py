import pytest

from tests import ignore_sensor_modules

from sensor_publisher import SensorPublisher

all_known_sensors = "TempHumiditySensor, TempHumiditySensorI2C, LightSensor, LightSensorUV, WaterProbe"

def test_load_empty_sensors_list():

    sensors = SensorPublisher.load_sensors("")

    assert isinstance(sensors, list)
    assert len(sensors) == 0

def test_load_sensors_list_spaces_ok():
    #test with a space between
    sensors = SensorPublisher.load_sensors(all_known_sensors)

    assert len(sensors) == len(all_known_sensors.split())


def test_load_sensors_mix_of_bad_and_good_throws_exception():

    with pytest.raises(ValueError):
        sensors = SensorPublisher.load_sensors(all_known_sensors + ",SomeJunkyThing")
