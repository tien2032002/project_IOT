import time
import serial.tools.list_ports

ser = serial.Serial(port="COM3", baudrate=115200)

mixer1_ON = [1, 6, 0, 0, 0, 255, 201, 138]
mixer1_OFF = [1, 6, 0, 0, 0, 0, 137, 202]
mixer2_ON = [2, 6, 0, 0, 0, 255, 201, 185]
mixer2_OFF = [2, 6, 0, 0, 0, 0, 137, 249]
mixer3_ON = [3, 6, 0, 0, 0, 255, 200, 104]
mixer3_OFF = [3, 6, 0, 0, 0, 0, 136, 40]
selector1_ON = [4, 6, 0, 0, 0, 255, 201, 223]
selector1_OFF = [4, 6, 0, 0, 0, 0, 137, 159]
selector2_ON = [5, 6, 0, 0, 0, 255, 200, 14]
selector2_OFF = [5, 6, 0, 0, 0, 0, 136, 78]
selector3_ON = [6, 6, 0, 0, 0, 255, 200, 61]
selector3_OFF = [6, 6, 0, 0, 0, 0, 136, 125]
pumpIn_ON = [7, 6, 0, 0, 0, 255, 201, 236]
pumpIn_OFF = [7, 6, 0, 0, 0, 0, 137, 172]
pumpOut_ON = [8, 6, 0, 0, 0, 255, 201, 19]
pumpOut_OFF = [8, 6, 0, 0, 0, 0, 137, 83]
soil_temperature = [1, 3, 0, 6, 0, 1, 100, 11]
soil_moisture = [1, 3, 0, 7, 0, 1, 53, 203]


def decodeModbus(data_array):
    if len(data_array) >= 7:
        array_size = len(data_array)
        value = data_array[array_size - 4] * 256 + data_array[array_size - 3]
        return value
    else:
        return -1


def test(cmd):
    if cmd == mixer1_ON:
        print("MIXER 1: ON")
    elif cmd == mixer2_ON:
        print("MIXER 2: ON")
    elif cmd == mixer3_ON:
        print("MIXER 3: ON")
    elif cmd == pumpIn_ON:
        print("PUMP IN: ON")
    elif cmd == mixer1_OFF:
        print("MIXER 1: OFF")
    elif cmd == mixer2_OFF:
        print("MIXER 2: OFF")
    elif cmd == mixer3_OFF:
        print("MIXER 3: OFF")
    elif cmd == pumpIn_OFF:
        print("PUMP IN: OFF")
    elif cmd == pumpOut_ON:
        print("PUMP OUT: ON")
    elif cmd == selector1_ON:
        print("SELECTOR 1: ON")
    elif cmd == selector2_ON:
        print("SELECTOR 2: ON")
    elif cmd == selector3_ON:
        print("SELECTOR 3: ON")
    elif cmd == pumpOut_OFF:
        print("PUMP OUT: OFF")
    elif cmd == selector1_OFF:
        print("SELECTOR 1: OFF")
    elif cmd == selector2_OFF:
        print("SELECTOR 2: OFF")
    elif cmd == selector3_OFF:
        print("SELECTOR 3: OFF")
    elif cmd == soil_temperature:
        pass
    elif cmd == soil_moisture:
        pass
    else:
        print("UNKNOWN MESSAGE!")


while True:
    numByte = ser.inWaiting()
    if numByte >= 8:
        payload = [b for b in ser.read(8)]
        test(payload)
        ser.write(payload)
    else:
        time.sleep(0.2)
