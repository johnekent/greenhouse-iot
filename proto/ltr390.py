import board
import busio
import adafruit_ltr390

i2c = busio.I2C(board.SCL, board.SDA)

ltr = adafruit_ltr390.LTR390(i2c)
print(f"UV: {ltr.uvs}  Ambient: {ltr.light}  UVI: {ltr.uvi} Lux: {ltr.lux}")
