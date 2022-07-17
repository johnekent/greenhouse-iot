# ignore these as not needed for tests and not installable on dev machine
# may wish to put an "if windows" around this or other dynamic import failure try/catch
import sys

sys.modules['adafruit_dht'] = ()
sys.modules['adafruit_ahtx0'] = ()
sys.modules['adafruit_ltr390'] = ()
sys.modules['SI1145.SI1145'] = ()
sys.modules['board'] = ()
sys.modules['busio'] = ()
sys.modules['melnor_bluetooth'] = {'constants': True}
sys.modules['melnor_bluetooth.constants'] = ()

sys.modules['RPi.GPIO'] = ()  #TODO:  make this work so can more clealy include this in tests
