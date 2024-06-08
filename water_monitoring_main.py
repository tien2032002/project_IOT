import PrivateTasks.task_1
import PrivateTasks.task_2
from protocol.rs485 import Rs485
# from protocol.mqtt import MQTT
from Scheduler.scheduler import  *
import time

# mqtt = MQTT()
# rs485 = Rs485()

def testTask1():
    print ("task1")
    
def testTask2():
    print ("task2")
    
scheduler = Scheduler()
scheduler.SCH_Init()
scheduler.SCH_Add_Task(testTask1, 0, 1000)
scheduler.SCH_Add_Task(testTask2, 500, 1000)

while (1):
    scheduler.SCH_Update()
    scheduler.SCH_Dispatch_Tasks()

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