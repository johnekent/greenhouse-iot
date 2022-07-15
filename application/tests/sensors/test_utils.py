import pytest

from ..context import app

from app.sensor import Sensor
from app.sensor import SensorUtils as su

def test_instance_from_string():

    name = "LightSensor"

    instance = su.instance_from_string(name)

    assert isinstance(instance, Sensor)

def test_instance_from_string_invalid_class():

    name = "TheGreatestOfAllNonexistentSensors"

    with pytest.raises(ValueError):
        su.instance_from_string(name)
