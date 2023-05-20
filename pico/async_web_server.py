# Referenced from https://gist.github.com/aallan/3d45a062f26bc425b22a17ec9c81e3b6
import network
import socket
import time

from machine import Pin

import uasyncio as asyncio

from status_display import StatusDisplay

class AsyncWebServer:
    
    def __init__(self, temp_sensor, light_sensor, wlan, background_task, background_interval_sec, status_display, port=80):
        """
        wlan isn't used directly but can be queried for status on failure
        """
        
        self.onboard = Pin("LED", Pin.OUT, value=0)
        
        self.temp_sensor = temp_sensor
        self.light_sensor = light_sensor
        
        self.wlan = wlan
        
        self.background_task = background_task
        self.background_interval_sec = background_interval_sec
        
        self.status_display = status_display
        
        self.port = port
        
        self.host='0.0.0.0'
        
        self.template = self.read_page_template()
        
        print(f"Server will run on wlan address {self.wlan.ifconfig()[0]} and on port {self.port}")
        print(f"Startup page params are {self.get_page_params()}")
    
    def read_page_template(self, template="index.html"):
        template = "<html>Error reading page.</html>"
        
        with open('index.html', 'r') as file:
            template = file.read()
            
        return template
    
    def web_page(self, params: dict):
        
        temperature = params['temperature']
        light = params['light']
        time = params['time']
            
        html = self.template.format(temperature=temperature, light=light, time=time)
        return html
    
    def get_page_params(self):
        
        temperature = self.temp_sensor.take_measurement()
        light = self.light_sensor.take_measurement()
        lt = time.localtime()
        timestamp = f"{lt[0]}/{lt[1]}/{lt[2]} {lt[3]}:{lt[4]}:{lt[5]}"
                                
        params = {'temperature': temperature, 'light': light, 'time': timestamp}
        
        return params        

    async def serve_client(self, reader, writer):
        print("Client connected")
        request_line = await reader.readline()
        print("Request:", request_line)
        # We are not interested in HTTP request headers, skip them
        while await reader.readline() != b"\r\n":
            pass
        
        params = self.get_page_params()            
        response = self.web_page(params)

        writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        writer.write(response)

        await writer.drain()
        await writer.wait_closed()
        print("Client disconnected")

    """
    I hereby acknowledge the hacky arrangement of the background task hosting here
    """	
    async def run_server(self):

        print('Setting up webserver...')
        asyncio.create_task(asyncio.start_server(self.serve_client, self.host, self.port))
        while True:
            print("Webserver executing background task")
            await self.background_task()
            print("Background task completed")
            self.status_display.flash_all(0.25)
            await asyncio.sleep(self.background_interval_sec)
            
if __name__ == "__main__":
    # local test

    import main
    wlan = main.connect_wifi()
    status_display = StatusDisplay(main.led_config)
    
    class MockSensor:
        def take_measurement(self):
            return {"temperature": 83.1, "humidity": 38}
        
    temp_sensor = MockSensor()
    light_sensor = MockSensor()
    
    async def say_hello():
        print("Hello from the background")
    
    ws = AsyncWebServer(temp_sensor=temp_sensor, light_sensor=light_sensor, wlan=wlan, background_task=say_hello, status_display=status_display, background_interval_sec=10)
        
    try:
        asyncio.run(ws.run_server())	
    finally:
        print("Shutting it down...")
        asyncio.new_event_loop()