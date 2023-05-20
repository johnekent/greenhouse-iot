"""
Custom class based on this simple example:
https://pythonforundergradengineers.com/micropython-temp-sensor.html

"""

import machine

class MCP9808:
    
    def __init__(self, i2c):
        self.i2c = i2c
        
    def get_temperature(self):
        
        byte_data = bytearray(2)
        self.i2c.readfrom_mem_into(24, 5, byte_data)
        value = byte_data[0] << 8 | byte_data[1]
        temp = (value & 0xFFF) / 16.0
        if value & 0x1000:
            temp -= 256.0
        
        # C to F
        return (temp * 1.8)+32
    
    def take_measurement(self):
        
        return {"temperature": self.get_temperature()}
    

if __name__ == "__main__":
    
    from machine import Pin, I2C

    #setup i2c bus
    i2c = machine.I2C(0, scl=machine.Pin(17), sda=machine.Pin(16))
    
    s = MCP9808(i2c=i2c)
    
    print(s.take_measurement())
    print(s.take_measurement())
