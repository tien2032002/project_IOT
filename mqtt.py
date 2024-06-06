import sys
from Adafruit_IO import Client, MQTTClient
from datetime import datetime
import requests


AIO_FEED_IDs = ["temp", 'humid', 'light', 'light-button', 'ac-button', "user-datetime"]
AIO_USERNAME = "tien2032002"
AIO_KEY = "aio_vfuA18wC1N6tdh5fT8lnv8OrkvkN"
MODEL_PATH = "IOT/keras_model.h5"
CLASS_NAME_PATH = "IOT/labels.txt"

TEMP_TOPIC = "temp"
HUMID_TOPIC = "humid"
LIGHT_TOPIC = "light"

LED_BUTTON = "light-button"
AC_BUTTON = "ac-button" #air conditional 


class MQTT:
    def __init__(self) -> None:
        # set callback
        self.client = MQTTClient(AIO_USERNAME , AIO_KEY)
        self.client2 = Client(AIO_USERNAME , AIO_KEY)
        self.client.on_connect = self.connected
        self.client.on_disconnect = self.disconnected
        self.client.on_message = self.message
        self.client.on_subscribe = self.subscribe
        self.client.connect()
        self.client.loop_background()
        
        # sensor data
        self.temp = self.getCurrentTopicData(TEMP_TOPIC)
        self.humid = self.getCurrentTopicData(HUMID_TOPIC)
        self.light = self.getCurrentTopicData(LIGHT_TOPIC)

        
        
    def getCurrentTopicData(self, topic_name):
        url = f'https://io.adafruit.com/api/v2/{AIO_USERNAME}/feeds/{topic_name}'
        # print(requests.get(url).json())
        return requests.get(url).json()["last_value"]
    
    def connected(self, client):
        print("Ket noi thanh cong ...")
        for topic in AIO_FEED_IDs:
            client.subscribe(topic)

    def subscribe(self, client , userdata , mid , granted_qos):
        print("Subscribe thanh cong ...")

    def disconnected(self, client):
        print("Ngat ket noi ...")
        sys.exit (1)

    def message(self, client , feed_id , payload):
        if (feed_id == HUMID_TOPIC):
            self.humid = payload
        elif (feed_id == TEMP_TOPIC):
            self.temp = payload
        elif (feed_id == LIGHT_TOPIC):
            self.light = payload
        elif (feed_id == LED_BUTTON):
            self.led_button = payload
        elif (feed_id == AC_BUTTON):
            self.ac_button = payload

    
    def get_history(self, topic, limit):
        return self.client2.data(topic, max_results=limit)
    
    def user_scheduler(self):
        self.client.publish(LED_BUTTON, 0)
        
client = MQTT()

