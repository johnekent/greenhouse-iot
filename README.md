# greenhouse-iot
# Details for pico w
Please see only the pico folder

# Details below are for Pi zero, etc.
## General Pi Setup
Enable I2C - go through the Preferences - Interfaces UI<br>
Enable SSH - go through the Preferences - Interfaces UI<br>
Make sure WIFI is setup in /etc/wpa_supplicant/wpa_supplicant.conf<br>
Static IP - Eero Settings - Network Settings - Reservations & port forwarding -- set a static IP for the device.  Verify with ifconfig -a.<br>

## Libraries for I2C and IoT
sudo apt-get update<br>
sudo apt-get install i2c-tools<br>

### Note:  This page has setup from AWS with additional steps
https://docs.aws.amazon.com/iot/latest/developerguide/connecting-to-existing-device.html

## Install through this tutorial https://docs.aws.amazon.com/iot/latest/developerguide/iot-quick-start.html
installed Linux Python IoT SDK to <br>
pi@raspberrypi:/iot<br>

And successfully ran the ./start.sh to validate communication.<br>

## check the wireless strength and options using command:
iwlist wlan0 scan | egrep "Cell|ESSID|Signal|Rates|Frequency"
