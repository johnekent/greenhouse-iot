import pytest

from tests import ignore_sensor_modules

from sensor_publisher import SensorPublisher

all_known_sensors = "TempHumiditySensor, TempHumiditySensorI2C, LightSensor, LightSensorUV, WaterProbe, FloatSwitchSensor"

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

def test_measure_environment(monkeypatch):
    """This tests that the class really loads and that it can generally operate without interacting with the environment

    Args:
        monkeypatch (_type_): _description_
    """

    def mock_create_connection(self, endpoint, port, cert, key, root_ca, client_id):
        return None

    # don't try to make a connection as it will not work
    monkeypatch.setattr(SensorPublisher, "create_connection", mock_create_connection)
    
    sp = SensorPublisher(endpoint=None, port=None, topic=None, control_topic=None, cert=None, key=None, root_ca=None, client_id=None, thing_name=None, active_sensors="")

    message = sp.measure_environment()
    assert isinstance(message, dict)
