import pytest

import asyncio

from ..context import app

from app.handler import handle_greenhouse_action



tests = [ 
    ({'float_switch_left': {'float_switch_state': 'LOW'}}, "float_switch_left", "LOW"),
    ({'float_switch_right': {'float_switch_state': 'HIGH'}}, "float_switch_right", "HIGH"),
    ({'float_xyz_right': {'float_switch_state': 'HIGH'}}, "float_switch_right", "UNKNOWN"),
    ({'float_switch_right': {'float_switch_xxx': 'HIGH'}}, "float_switch_right", "UNKNOWN"),
 ]
@pytest.mark.parametrize('sensor_metrics, float_name, expected', tests)
def test__get_float_state(sensor_metrics, float_name, expected):

    state = handle_greenhouse_action._get_float_state(sensor_metrics=sensor_metrics, float_name=float_name)

    assert expected == state