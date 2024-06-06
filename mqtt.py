import sys
from Adafruit_IO import Client, MQTTClient
import time

AIO_FEED_IDs = ["temp", 'humid']
AIO_USERNAME = "tien2032002"
AIO_KEY = "aio_iXQC80XfQ48t1Jv74OytgQSWvtTN"

TEMP_TOPIC = "temp"
HUMID_TOPIC = "humid"


class MQTT:
    def __init__(self) -> None:
        # set callback
        self.client = MQTTClient(AIO_USERNAME , AIO_KEY)
        self.client.on_connect = self.connected
        self.client.on_disconnect = self.disconnected
        self.client.on_message = self.message
        self.client.on_subscribe = self.subscribe
        self.client.connect()
        self.client.loop_background()
        
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

client = MQTT()
        
        


