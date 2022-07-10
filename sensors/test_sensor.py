import pytest

from sensor import Sensor

def test_connect_none_on_fail():

    class MySensor(Sensor):

        def __connect__(self):
            raise RuntimeError("error")

        def __read__(self):
            pass

    
    s = MySensor()

    assert not s.connection 