import json
import os
import threading
import random
import datetime

from dotenv import load_dotenv
from model.mqtt.mqtt_topic import MqttTopic
from model.mqtt.schedule import Schedule, ScheduleType
from model.mqtt.sensor_data import SensorData, SensorDataType
from services.mqtt import Mqtt
from services.my_firestore import MyFirestore, sendMessage
from utils.time_manager import TimeManager
from scheduler.scheduler2 import Scheduler2, ScheduleTask
from scheduler.scheduler1 import Scheduler1, Task, TaskArgument
from services.uart import Uart


class MyMqtt:
    def __init__(self, broker, username, password):
        # Save credential
        self.broker = broker
        self.username = username
        self.password = password

        # Initializing...
        self.mqtt = Mqtt()

        # Set Callback
        self.mqtt.setCallback(onConnect=self.onConnect)

    def onConnect(self, isSuccessful):
        # After connect is successful.
        if isSuccessful:
            # Subscribe all topics we list before
            self.subscribeTopics()
        else:
            print("[ERROR] Connection failed!")

    def subscribeTopics(self):
        for topic in MqttTopic.subscriptionList:
            self.mqtt.subscribe(topic=topic)

    def reconnectToMqttBroker(self):
        self.mqtt.connect(self.broker, 1883, self.username, self.password)

    def addOnMessage(self, onMessage):
        self.mqtt.setCallback(onMessage=onMessage)

    def connect(self):
        self.mqtt.connect(self.broker, 1883, self.username, self.password)

    def publish(self, topic, payload):
        self.mqtt.publish(topic, payload)


class Main:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.BROKER = os.getenv("BROKER")
        self.USERNAME = os.getenv("_USER")
        self.PASSWORD = os.getenv("KEY")
        print(self.BROKER, self.USERNAME, self.PASSWORD)

        # Establish Firebase Connection
        self.myFirestore = MyFirestore(self.BROKER, self.USERNAME, self.PASSWORD)
        # This is for local schedule list, always update for Firebase each 5 minutes.
        self.scheduleList = []
        self.scheduleIdRunning = ""
        # For start time history
        self.scheduleStartTime = ""

        # Gateway occur error ?
        self.isErrorOccur = False

        # Create scheduler for handling schedule from app.
        self.scheduler1 = Scheduler1()
        # Initialize Uart
        self.uart = Uart(self.scheduler1)
        self.uart.setOnProcessDone(self.onProcessDone)
        self.uart.setOnUartIsDown(self.onUartIsDown)
        # Add 2 tasks for reading sensor
        self.scheduler1.SCH_AddTask(Task(pTask=self.uart.readTemperature, delay=0, period=2))
        self.scheduler1.SCH_AddTask(Task(pTask=self.uart.readMoisture, delay=0.02, period=2))

        self.scheduler2 = Scheduler2()
        # self.scheduler2.setOnTaskDone(on_task_done=self.onTaskDone)
        # self.scheduler2.setOnSaveHistory(on_save_history=self.onSaveHistory)

        # Initialize scheduler2
        self.setOffAllScheduleInDatabase()

        # Establish MQTT services
        self.myMqtt = MyMqtt(self.BROKER, self.USERNAME, self.PASSWORD)
        self.myMqtt.addOnMessage(onMessage=self.onMessage)
        self.myMqtt.connect()

        # We need one infinity loop to maintain program
        self.loop()

    def onUartIsDown(self):
        print("<==============ERROR================>")
        print("[ERROR] Can't communication with sensors!")
        print("<==============ERROR================>")
        sendMessage(title="[ERROR] Some devices are down!", body="Please, go to check those sensors!\nWe also make "
                                                                 "the gateway"
                                                         "down, re-run gateway when those sensors work well again!")
        self.isErrorOccur = True
        TimeManager.sleep(1000)

    def onProcessDone(self, isSuccessful):
        if isSuccessful:
            print("Process ran successfully!")
            doc = self.myFirestore.getSchedule(self.scheduleIdRunning)
            self.scheduleIdRunning = ""
            if doc.exists:
                schedule = Schedule(
                    scheduleId=doc.get("scheduleId"),
                    name=doc.get("name"),
                    type="update",
                    volume=doc.get("volume"),
                    ratio=str(doc.get("ratio")),
                    date=doc.get("date"),
                    weekday=str(doc.get("weekday")),
                    time=doc.get("time"),
                    isOn=0
                )
                self.onTaskDone(schedule)
                self.onSaveHistory(schedule)
        else:
            print("<==============ERROR================>")
            print("[ERROR] Irrigation process hasn't run like expectation!")
            print("<==============ERROR================>")
            sendMessage(title="[ERROR] Irrigation process hasn't run like expectation!",
                        body="Please, talk to technician to fix this thing!")
            self.isErrorOccur = True
            TimeManager.sleep(1000)

    def onTaskDone(self, schedule: Schedule):
        schedule.isOn = 0
        schedule.type = ScheduleType.UPDATE
        js = json.loads(schedule.toJsonString())
        del js["email"]
        del js["type"]
        del js["error"]
        self.myFirestore.updateSchedule(schedule.scheduleId, js)
        self.publishSchedule(schedule)

    def onSaveHistory(self, schedule: Schedule):
        formatted_time = datetime.datetime.now().strftime("%H:%M %d-%m-%Y")
        js = {
            "name": schedule.name,
            "volume": schedule.volume,
            "ratio": schedule.ratio,
            "start_time": self.scheduleStartTime,
            "end_time": formatted_time
        }
        self.myFirestore.putHistory(js)

    def setOffAllScheduleInDatabase(self):
        col = self.myFirestore.getSchedules()
        for doc in col:
            schedule = Schedule(
                scheduleId=doc.get("scheduleId"),
                name=doc.get("name"),
                volume=doc.get("volume"),
                ratio=str(doc.get("ratio")),
                date=doc.get("date"),
                weekday=str(doc.get("weekday")),
                time=doc.get("time"),
                isOn=doc.get("isOn")
            )
            if schedule.isOn == 1:
                schedule.isOn = 0
                js = json.loads((schedule.toJsonString()))
                del js["email"]
                del js["type"]
                del js["error"]
                self.myFirestore.updateSchedule(schedule.scheduleId, js)

    def taskScheduler2(self, schedule):
        if not self.scheduleIdRunning:
            self.scheduleIdRunning = schedule.scheduleId
            self.scheduleStartTime = f"{schedule.time} {datetime.datetime.now().strftime('%d-%m-%Y')}"
            print("SCHEDULER 2 TASK RUN: " + schedule.scheduleId)
            if not self.uart.initializeIrrigationProcess(schedule):
                self.scheduleIdRunning = ""
                self.scheduleStartTime = ""

        else:
            print("[ERROR] Other tasks is running!")
            if schedule.date:
                schedule.isOn = 0
                schedule.type = ScheduleType.UPDATE
                js = json.loads(schedule.toJsonString())
                del js["email"]
                del js["type"]
                del js["error"]
                self.myFirestore.updateSchedule(schedule.scheduleId, js)
                self.publishSchedule(schedule)
            sendMessage(title="[ERROR] Other tasks is running!",
                        body="Your schedule is conflicted! Schedule just run will turn off!")

    def onMessage(self, topic, payload):
        topic = topic.split("/")[-1]
        print("Topic: " + topic + "| Payload: " + payload)

        if topic == "V2":
            thread = threading.Thread(target=self.handleScheduleRequest, args=(payload,))
            thread.daemon = True
            thread.start()

    def addScheduleRequest(self, schedule: Schedule):
        cur_time = datetime.datetime.now()
        formatted_time = cur_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        schedule.setId(formatted_time)

        # Add schedule Task here
        scheduleTask = ScheduleTask(pTask=self.taskScheduler2, schedule=schedule)
        if scheduleTask.isInTime() and scheduleTask.schedule.date:
            schedule.error = "The time set is in the past!"
        else:
            self.scheduler2.SCH_AddTask(scheduleTask)
            js = json.loads(schedule.toJsonString())
            del js["email"]
            del js["type"]
            del js["error"]
            self.myFirestore.putSchedule(formatted_time, js)

        self.publishSchedule(schedule)

    def deleteSchedule(self, schedule: Schedule):
        if schedule.scheduleId:
            if self.scheduleIdRunning == schedule.scheduleId:
                schedule.error = "This schedule is executing, you can delete until it's done"
            elif self.myFirestore.isScheduleExist(schedule.scheduleId):
                self.scheduler2.SCH_DeleteScheduleTask(schedule.scheduleId)
                self.myFirestore.deleteSchedule(schedule.scheduleId)
            else:
                schedule.error = "This schedule doesn't exist! This mean someone has already deleted before!"
            self.publishSchedule(schedule)
        else:
            print("[ERROR] deleteSchedule but scheduleId is empty!")

    def updateSchedule(self, schedule: Schedule):
        if schedule.scheduleId:
            if self.scheduleIdRunning == schedule.scheduleId:
                schedule.error = "This schedule is executing, you can delete until it's done"
            elif self.myFirestore.isScheduleExist(schedule.scheduleId):
                scheduleTask = ScheduleTask(pTask=self.taskScheduler2, schedule=schedule)
                if scheduleTask.schedule.isOn == 1 and scheduleTask.isInTime() and scheduleTask.schedule.date:
                    schedule.error = "The time set is in the past!"
                else:
                    self.scheduler2.SCH_DeleteScheduleTask(schedule.scheduleId)
                    if schedule.isOn == 1:
                        self.scheduler2.SCH_AddTask(scheduleTask)

                    js = json.loads(schedule.toJsonString())
                    del js["email"]
                    del js["type"]
                    del js["error"]
                    self.myFirestore.updateSchedule(schedule.scheduleId, js)
            else:
                schedule.error = "This schedule doesn't exist!"
            self.publishSchedule(schedule)
        else:
            print("[ERROR] updateSchedule but scheduleId is empty!")

    def handleScheduleRequest(self, payload: str):
        schedule = Schedule.importFromJsonString(payload)
        if schedule.type == ScheduleType.ADD:
            self.addScheduleRequest(schedule)
        elif schedule.type == ScheduleType.DELETE:
            self.deleteSchedule(schedule)
        elif schedule.type == ScheduleType.UPDATE:
            self.updateSchedule(schedule)

    def publishSensorData(self, sensorData: SensorData):
        self.myMqtt.publish(
            MqttTopic.sensorData,
            payload=sensorData.toStringInJsonForm()
        )

    def publishSchedule(self, schedule: Schedule):
        self.myMqtt.publish(
            MqttTopic.scheduleResponse,
            payload=schedule.toJsonString()
        )

    def publishCurrentTime(self):
        curTime = datetime.datetime.now()
        data = {
            "hour": curTime.hour,
            "minute": curTime.minute,
            "day": curTime.day,
            "month": curTime.month,
            "year": curTime.year
        }
        self.myMqtt.publish(MqttTopic.currentTime, payload=json.dumps(data))

    def loop(self):
        counter = 5
        while not self.isErrorOccur:
            counter -= 1
            if counter <= 0:
                counter = 5
                self.publishSensorData(SensorData(SensorDataType.TEMPERATURE, self.uart.tempValue))
                self.publishSensorData(SensorData(SensorDataType.SOIL_MOISTURE, self.uart.moisValue))
            TimeManager.sleep(1)


Main()




