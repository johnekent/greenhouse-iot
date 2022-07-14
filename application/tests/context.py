import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ignore these as not needed for tests and not installable on dev machine
# may wish to put an "if windows" around this or other dynamic import failure try/catch
sys.modules['adafruit_dht'] = ()
sys.modules['adafruit_ahtx0'] = ()
sys.modules['adafruit_ltr390'] = ()
sys.modules['SI1145.SI1145'] = ()
sys.modules['board'] = ()
sys.modules['busio'] = ()

import app