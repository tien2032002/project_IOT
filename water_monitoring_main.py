import PrivateTasks.task_1
import PrivateTasks.task_2
from protocol.rs485 import Rs485
from protocol.mqtt import MQTT
from Scheduler.scheduler import  *
import time
import json
import schedule
import random
from datetime import datetime

# timeout, in dict

routine = {
    "cycle": 2,
    'MIXER1': 2,
    'MIXER2': 2,
    'MIXER3': 2,
    'PUMP_IN': 2,
    'SELECTOR1': 2,
    'SELECTOR2': 2,
    'SELECTOR3': 2,
    'PUMP_OUT': 2,
    "is_active": True,
    "name": "schedule 1",
    "start": "18:30",
    "stop": "18:40"
}

scheduler = Scheduler()
scheduler.SCH_Init()

def message(client , feed_id , payload):
    if feed_id == "routine":
        global routine
        routine = json.loads(payload)
        stop_routine()
        if routine["is_active"]:
            schedule.every().day.at(routine["start"]).do(start_routine)
            schedule.every().day.at(routine["stop"]).do(stop_routine)
            
mqtt = MQTT(message)
rs485 = Rs485()

cycle = 0

def mixer1():
    print (f"mixer1: {routine['MIXER1']}")
    rs485.turn_off_relay(8, mqtt)
    rs485.turn_on_relay(1, mqtt)
    scheduler.SCH_Add_Task(mixer2, routine["MIXER2"], 0)
    
def mixer2():
    print (f"mixer2: {routine['MIXER2']}")
    rs485.turn_off_relay(1, mqtt)
    rs485.turn_on_relay(2, mqtt)
    scheduler.SCH_Add_Task(mixer3, routine["MIXER3"], 0)
    
def mixer3():
    print (f"mixer3: {routine['MIXER3']}")
    rs485.turn_off_relay(2, mqtt)
    rs485.turn_on_relay(3, mqtt)
    scheduler.SCH_Add_Task(pump_in, routine['PUMP_IN'], 0)
    
def pump_in():
    print (f"pump in: {routine['PUMP_IN']}")
    rs485.turn_off_relay(3, mqtt)
    rs485.turn_on_relay(4, mqtt)
    scheduler.SCH_Add_Task(selector1, routine["SELECTOR1"], 0)
    
def selector1():
    print (f"selector1: {routine['SELECTOR1']}")
    rs485.turn_off_relay(4, mqtt)
    rs485.turn_on_relay(5, mqtt)
    scheduler.SCH_Add_Task(selector2, routine["SELECTOR2"], 0)
    
def selector2():
    print (f"selector2: {routine['SELECTOR2']}")
    rs485.turn_off_relay(5, mqtt)
    rs485.turn_on_relay(6, mqtt)
    scheduler.SCH_Add_Task(selector3, routine["SELECTOR3"], 0)
    
def selector3():
    print (f"selector3: {routine['SELECTOR3']}")
    rs485.turn_off_relay(6, mqtt)
    rs485.turn_on_relay(7, mqtt)
    scheduler.SCH_Add_Task(pump_out, routine["PUMP_OUT"], 0)
    
def pump_out():
    print (f"pump out: {routine['PUMP_OUT']}")
    rs485.turn_off_relay(7, mqtt)
    rs485.turn_on_relay(8, mqtt)
    global cycle
    
    if cycle > 0:
        cycle+=1
        scheduler.SCH_Add_Task(mixer1, routine["MIXER1"], 0)
    else:
        scheduler.SCH_Dispatch_Tasks()
        
def start_routine():
    global cycle
    cycle = 1
    print("start irrigation process")
    print(routine)
    scheduler.SCH_Add_Task(mixer1, routine["MIXER1"], 0)

def stop_routine():
    print("stop irrigation process")
    scheduler.SCH_Delete_all
    scheduler.SCH_Add_Task(temp_dummy, 1, 10)
    scheduler.SCH_Add_Task(humid_dummy, 2, 10)

def temp_dummy():
    temp = random.random()*(30-27) + 27
    print(f"Nhiet do hien tai la: {temp}")
    mqtt.client.publish("temp", temp)
    
def humid_dummy():
    humid = random.random()*(90-70) + 70
    print(f"Do am hien tai la: {humid}")
    mqtt.client.publish("humid", humid)
    
scheduler.SCH_Add_Task(temp_dummy, 1, 10)
scheduler.SCH_Add_Task(humid_dummy, 2, 10)

# start_routine()
while (1):
    scheduler.SCH_Update()
    scheduler.SCH_Dispatch_Tasks()
    schedule.run_pending()

    time.sleep(0.001)

# scheduler = Scheduler()
# scheduler.SCH_Init()
# soft_timer = softwaretimer()

# task1 = PrivateTasks.private_task_1.Task1()
# task2 = PrivateTasks.private_task_2.Task2()

# ledblink = PrivateTasks.led_blinky_task.LedBlinkyTask(soft_timer)

# watermonitoring = PrivateTasks.water_monitoring_task.WaterMonitoringTask(watermonitoring_timer, m485)
# main_ui = PrivateTasks.main_ui_task.Main_UI(watermonitoring)
# rapidoserver = PrivateTasks.rapido_server_task.RapidoServerTask()

# #scheduler.SCH_Add_Task(task1.Task1_Run, 1000,2000)
# #scheduler.SCH_Add_Task(task2.Task2_Run, 1000,4000)
# # scheduler.SCH_Add_Task(soft_timer.Timer_Run, 1, 1)
# # scheduler.SCH_Add_Task(ledblink.LedBlinkyTask_Run, 1, 1)


# scheduler.SCH_Add_Task(main_ui.UI_Refresh, 1, 100)

# scheduler.SCH_Add_Task(watermonitoring_timer.Timer_Run, 1, 100)
# #scheduler.SCH_Add_Task(rapidoserver.uploadData, 1, 1000)
# scheduler.SCH_Add_Task(watermonitoring.WaterMonitoringTask_Run, 1, 1)

# while True:
#     scheduler.SCH_Update()
#     scheduler.SCH_Dispatch_Tasks()

#     time.sleep(0.1)