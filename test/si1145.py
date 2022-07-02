import SI1145.SI1145 as SI1145


def run_single_test(sensor):
    vis = sensor.readVisible()
    IR = sensor.readIR()
    UV = sensor.readUV()
    uvIndex = UV / 100.0

    message = {"visible": vis, "IR": IR, "UV": UV, "UV_index": uvIndex}

    print(message)

if __name__ == "__main__":

    sensor = SI1145.SI1145()
    run_single_test(sensor) 
