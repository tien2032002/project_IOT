print("Sensors and Actuators")                                                                                                                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                                                                                                            
import time                                                                                                                                                                                                                                                                                                                                                                                 
import serial.tools.list_ports
import serial as s
import datetime
import json

relay_ON = [                                                                                                                                                                                                                                                                                                                                                                                
      None,                                                                                                                                                                                                                                                                                                                                                                                 
      [1, 6, 0, 0, 0, 255, 201, 138],  # Relay 1 ON                                                                                                                                                                                                                                                                                                                                         
      [2, 6, 0, 0, 0, 255, 201, 185],  # Relay 2 ON                                                                                                                                                                                                                                                                                                                                         
      [3, 6, 0, 0, 0, 255, 200, 104],  # Relay 3 ON                                                                                                                                                                                                                                                                                                                                         
      [4, 6, 0, 0, 0, 255, 201, 223],  # Relay 4 ON                                                                                                                                                                                                                                                                                                                                         
      [5, 6, 0, 0, 0, 255, 200, 14],   # Relay 5 ON                                                                                                                                                                                                                                                                                                                                         
      [6, 6, 0, 0, 0, 255, 200, 61],   # Relay 6 ON                                                                                                                                                                                                                                                                                                                                         
      [7, 6, 0, 0, 0, 255, 201, 236],  # Relay 7 ON                                                                                                                                                                                                                                                                                                                                         
      [8, 6, 0, 0, 0, 255, 201, 19],    # Relay 8 ON,                                                                                                                                                                                                                                                                                                                                       
    ]                                                                                                                                                                                                                                                                                                                                                                                       

relay_OFF = [                                                                                                                                                                                                                                                                                                                                                                               
      None,                                                                                                                                                                                                                                                                                                                                                                                 
      [1, 6, 0, 0, 0, 0, 137, 202],    # Relay 1 OFF                                                                                                                                                                                                                                                                                                                                        
      [2, 6, 0, 0, 0, 0, 137, 249],    # Relay 2 OFF                                                                                                                                                                                                                                                                                                                                        
      [3, 6, 0, 0, 0, 0, 136, 40],     # Relay 3 OFF                                                                                                                                                                                                                                                                                                                                        
      [4, 6, 0, 0, 0, 0, 137, 159],    # Relay 4 OFF                                                                                                                                                                                                                                                                                                                                        
      [5, 6, 0, 0, 0, 0, 136, 78],     # Relay 5 OFF                                                                                                                                                                                                                                                                                                                                        
      [6, 6, 0, 0, 0, 0, 136, 125],    # Relay 6 OFF                                                                                                                                                                                                                                                                                                                                        
      [7, 6, 0, 0, 0, 0, 137, 172],    # Relay 7 OFF                                                                                                                                                                                                                                                                                                                                        
      [8, 6, 0, 0, 0, 0, 137, 83]      # Relay 8 OFF                                                                                                                                                                                                                                                                                                                                        
          ]
soil_temperature =[10, 3, 0, 6, 0, 1, 101, 112]
soil_moisture = [10, 3, 0, 7, 0, 1, 52, 176]
                
class Rs485:
    def __init__(self):
        self.portName = self.getPort()
        self.rate = 9600
        self.connect()
                                                                                                                                                                                                                                                                                                                                   
    def getPort(self):                                                                                                                                                                                                                                                                                                                                                                              
        ports = serial.tools.list_ports.comports()                                                                                                                                                                                                                                                                                                                                              
        N = len(ports)                                                                                                                                                                                                                                                                                                                                                                          
        commPort = "None"                                                                                                                                                                                                                                                                                                                                                                       
        for i in range(0, N):                                                                                                                                                                                                                                                                                                                                                                   
            port = ports[i]                                                                                                                                                                                                                                                                                                                                                                     
            strPort = str(port)                                                                                                                                                                                                                                                                                                                                                                 
            if "USB" in strPort:                                                                                                                                                                                                                                                                                                                                                                
                splitPort = strPort.split(" ")                                                                                                                                                                                                                                                                                                                                                  
                commPort = (splitPort[0])                                                                                                                                                                                                                                                                                                                                                       
        return commPort                                                                                                                                                                                                                                                                                                                                                                         
        # return "/dev/ttyUSB1"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
    def connect(self):                                                                                                                                                                                                                                                                                                                                               
        try:                                                                                                                                                                                                                                                                                                                                                                                        
            self.ser = serial.Serial(port=self.portName, baudrate=self.rate)                                                                                                                                                                                                                                                                                                                                       
            print("Open successfully")                                                                                                                                                                                                                                                                                                                                                              
        except:                                                                                                                                                                                                                                                                                                                                                                                     
            print("Can not open the port")                                                                                                                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                                                                                                            
    def serial_read_data(self):                                                                                                                                                                                                                                                                                                                                                                  
        bytesToRead = self.ser.inWaiting()                                                                                                                                                                                                                                                                                                                                                           
        if bytesToRead > 0:                                                                                                                                                                                                                                                                                                                                                                     
            out = self.ser.read(bytesToRead)                                                                                                                                                                                                                                                                                                                                                         
            data_array = [b for b in out]                                                                                                                                                                                                                                                                                                                                                       
            print("Array: ",data_array)                                                                                                                                                                                                                                                                                                                                                         
            if len(data_array) >= 7:                                                                                                                                                                                                                                                                                                                                                            
                array_size = len(data_array)                                                                                                                                                                                                                                                                                                                                                    
                value = data_array[array_size - 4] * 256 + data_array[array_size - 3]                                                                                                                                                                                                                                                                                                           
                return value                                                                                                                                                                                                                                                                                                                                                                    
            else:                                                                                                                                                                                                                                                                                                                                                                               
                return -1                                                                                                                                                                                                                                                                                                                                                                       
        return 0                                                                                                                                                                                                                                                                                                                                                                               
 
    def setDevice(self, id, state):                                                                                                                                                                                                                                                                                                                                                                   
        print("RELAY ", id)                                                                                                                                                                                                                                                                                                                                                                     
        if state == True:                                                                                                                                                                                                                                                                                                                                                                       
            print(relay_ON[id], "--------")                                                                                                                                                                                                                                                                                                                                                     
            self.ser.write(relay_ON[id])                                                                                                                                                                                                                                                                                                                                                             
        else:                                                                                                                                                                                                                                                                                                                                                                                   
            print(relay_OFF[id], "--------")                                                                                                                                                                                                                                                                                                                                                    
            self.ser.write(relay_OFF[id])                                                                                                                                                                                                                                                                                                                                                            
        time.sleep(1)                                                                                                                                                                                                                                                                                                                                                                           
        print("Result: ", self.serial_read_data())                                                                                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                                                                                                            
#while True:                                                                                                                                                                                                                                                                                                                                                                                
#    for i in range(1,8):                                                                                                                                                                                                                                                                                                                                                                   
#        setDevice(i, True)                                                                                                                                                                                                                                                                                                                                                                 
#        time.sleep(2)                                                                                                                                                                                                                                                                                                                                                                      
#        setDevice(i, False)                                                                                                                                                                                                                                                                                                                                                                
#        time.sleep(2)                                                                                                                                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                                                                                                            

    def readTemperature(self):                                                                                                                                                                                                                                                                                                                                                                      
        self.serial_read_data()
        self.clear_buffer()                                                                                                                                                                                                                                                                                                                                              
        self.ser.write(s.to_bytes(soil_temperature))                                                                                                                                                                                                                                                                                                                                                             
        time.sleep(1)                                                                                                                                                                                                                                                                                                                                                                           
        return self.serial_read_data()                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                

    def readMoisture(self):                                                                                                                                                                                                                                                                                                                                                                         
        self.serial_read_data()
        self.clear_buffer()
        self.ser.write(s.to_bytes(soil_moisture))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
        time.sleep(1)                                                                                                                                                                                                                                                                                                                                                                           
        return self.serial_read_data()                                                                                                                                                                                                                                                                                                                                                            
    
    def clear_buffer(self):
        bytesToRead = self.ser.inWaiting()
        if bytesToRead > 0:
            out = self.ser.read(bytesToRead)
            print ("buffer: ", out)
            
    def turn_on_relay(self, id, mqtt):
        record = {
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "id": id,
            "status": "on"
        }
        mqtt.client.publish("history", json.dumps(record))
        
        print(f"turn on relay id {id}")
        self.serial_read_data()
        self.clear_buffer()
        self.ser.write(s.to_bytes(relay_ON[id]))
        return True
    
    def turn_off_relay(self, id, mqtt):
        record = {
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "id": id,
            "status": "on"
        }
        mqtt.client.publish("history", json.dumps(record))
        
        print(f"turn off relay id {id}")
        self.serial_read_data()
        self.clear_buffer()
        self.ser.write(s.to_bytes(relay_OFF[id]))  