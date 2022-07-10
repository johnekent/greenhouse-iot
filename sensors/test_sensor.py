import pytest

from sensor import Sensor

## setup
class MySensor(Sensor):
    def __connect__(self):
        pass

    def __read__(self):
        pass
class MyConnection:
    pass

def mock_none_connection(*args, **kwargs):
    return None

def mock_raises_connection(*args, **kwargs):
    raise RuntimeError("Got an error connecting")

def mock_good_connection(*args, **kwargs):
    return MyConnection()

def mock_read_good_message(*args, **kwargs):
    return {"key": "value"}

def mock_raises_read(*args, **kwargs):
    raise RuntimeError("Got an error reading")

### tests
def test_connect_none_on_none(monkeypatch):
    monkeypatch.setattr(MySensor, "__connect__", mock_none_connection)
    s = MySensor()
    assert not s.connection

def test_connect_none_on_fail(monkeypatch):
    monkeypatch.setattr(MySensor, "__connect__", mock_raises_connection)
    s = MySensor()
    assert not s.connection

def test_connect_not_none_on_good_connection(monkeypatch):
    monkeypatch.setattr(MySensor, "__connect__", mock_good_connection)
    s = MySensor()
    assert s.connection

def test_read_returns_on_good_connection(monkeypatch):
    monkeypatch.setattr(MySensor, "__connect__", mock_good_connection)
    monkeypatch.setattr(MySensor, "__read__", mock_read_good_message)
    s = MySensor()
    assert s.read()

def test_read_returns_none_on_bad_connection(monkeypatch):
    monkeypatch.setattr(MySensor, "__connect__", mock_raises_connection)
    monkeypatch.setattr(MySensor, "__read__", mock_read_good_message)
    s = MySensor()
    assert not s.read()

def test_read_returns_none_on_none_connection(monkeypatch):
    monkeypatch.setattr(MySensor, "__connect__", mock_none_connection)
    monkeypatch.setattr(MySensor, "__read__", mock_read_good_message)
    s = MySensor()
    assert not s.read()

def test_read_returns_none_and_connection_none_on_raises_connection(monkeypatch):
    monkeypatch.setattr(MySensor, "__connect__", mock_raises_connection)
    monkeypatch.setattr(MySensor, "__read__", mock_read_good_message)
    s = MySensor()
    assert not s.read()
    assert not s.connection

def test_connect_returns_none_on_bad_but_read_works_after_good(monkeypatch):
    monkeypatch.setattr(MySensor, "__connect__", mock_none_connection)
    s = MySensor()
    assert not s.connection

    monkeypatch.setattr(MySensor, "__connect__", mock_good_connection)
    monkeypatch.setattr(MySensor, "__read__", mock_read_good_message)
    assert s.read()

def test_connect_returns_none_on_bad_and_none_first_read_but_then_read_works_after_good(monkeypatch):
    monkeypatch.setattr(MySensor, "__connect__", mock_raises_connection)
    s = MySensor()
    assert not s.connection

    monkeypatch.setattr(MySensor, "__read__", mock_read_good_message)
    assert not s.read()

    monkeypatch.setattr(MySensor, "__connect__", mock_good_connection)
    assert s.read()

def test_connect_returns_none_on_bad_and_none_first_read_but_then_read_works_after_good_and_then_read_raises_sets_connect_to_none(monkeypatch):
    monkeypatch.setattr(MySensor, "__connect__", mock_raises_connection)
    s = MySensor()
    assert not s.connection, "Connection was good but should be bad"
    monkeypatch.setattr(MySensor, "__read__", mock_read_good_message)
    assert not s.read(), "Read was good even with bad connection"

    monkeypatch.setattr(MySensor, "__connect__", mock_good_connection)
    assert s.read(), "Read wasn't good even with good connection"

    monkeypatch.setattr(MySensor, "__read__", mock_raises_read)
    assert not s.read(), "Read was good on exception raising read"
    assert not s.connection, "Connection was not reset to none after raising read"

def test_connect_returns_none_on_bad_and_none_first_read_but_then_read_works_after_good_and_then_read_raises_sets_connect_to_none_then_read_is_good(monkeypatch):
    monkeypatch.setattr(MySensor, "__connect__", mock_raises_connection)
    s = MySensor()
    assert not s.connection, "Connection was good but should be bad"
    monkeypatch.setattr(MySensor, "__read__", mock_read_good_message)
    assert not s.read(), "Read was good even with bad connection"

    monkeypatch.setattr(MySensor, "__connect__", mock_good_connection)
    assert s.read(), "Read wasn't good even with good connection"

    monkeypatch.setattr(MySensor, "__read__", mock_raises_read)
    assert not s.read(), "Read was good on exception raising read"
    assert not s.connection, "Connection was not reset to none after raising read"

    monkeypatch.setattr(MySensor, "__connect__", mock_raises_connection)
    s = MySensor()
    assert not s.connection, "Connection was good but should be bad"
    monkeypatch.setattr(MySensor, "__read__", mock_read_good_message)
    assert not s.read(), "Read was good even with bad connection"

    monkeypatch.setattr(MySensor, "__connect__", mock_good_connection)
    assert s.read(), "Read wasn't good even with good connection"

    monkeypatch.setattr(MySensor, "__read__", mock_raises_read)
    assert not s.read(), "Read was good on exception raising read"
    assert not s.connection, "Connection was not reset to none after raising read"

    monkeypatch.setattr(MySensor, "__read__", mock_read_good_message)
    assert s.read(), "Read expected good but was not"
    assert s.connection, "Connection expected good but was not"
