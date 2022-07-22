""" test_mqtt_connection
"""

import pytest

from ..context import app

from app.communication import MQTTConnection

def test_create(monkeypatch):
    def mock_create_connection(selfy):
        pass

    # don't try to make a connection as it will not work
    monkeypatch.setattr(MQTTConnection, "create_connection", mock_create_connection)    

    connection = MQTTConnection(endpoint=None, port=None, cert=None, key=None, root_ca=None, client_id=None)

    assert connection
