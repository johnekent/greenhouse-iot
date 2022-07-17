""" test_mqtt_connection
"""

import pytest

from ..context import app

from app.communication import MQTTConnection

def test_create():
    connection = MQTTConnection(endpoint=None, port=None, topic=None, control_topic=None, cert=None, key=None, root_ca=None, client_id=None)
