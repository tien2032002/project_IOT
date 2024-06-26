from Scheduler.task import *


class Scheduler:
    TICK = 1000
    SCH_MAX_TASKS = 40
    SCH_tasks_G = []
    current_index_task = 0

    def __init__(self):
        return

    def SCH_Init(self):
        self.current_index_task = 0

    def SCH_Add_Task(self, pFunction, DELAY, PERIOD):
        if self.current_index_task == 0:
            aTask = Task(pFunction, DELAY * self.TICK, PERIOD * self.TICK)
            self.SCH_tasks_G.append(aTask)
            self.current_index_task += 1
            return True

        if self.current_index_task < self.SCH_MAX_TASKS:
            total = 0
            
            for index in range(self.current_index_task):
                if total + self.SCH_tasks_G[index].Delay >= DELAY*self.TICK:
                    aTask = Task(pFunction, DELAY * self.TICK - total, PERIOD * self.TICK)
                    self.SCH_tasks_G[index].Delay-=DELAY * self.TICK - total
                    self.SCH_tasks_G.insert(index, aTask)
                    break
                total+=self.SCH_tasks_G[index].Delay
                if index == self.current_index_task - 1:
                    aTask = Task(pFunction, DELAY * self.TICK - total, PERIOD * self.TICK)
                    self.SCH_tasks_G.append(aTask)
            self.current_index_task += 1
            # print(f"add task with delay = {DELAY}, period = {PERIOD}")
            return True
        else:
            print("PrivateTasks are full!!!")
            return False

    def SCH_Update(self):
        if self.current_index_task > 0:
            self.SCH_tasks_G[0].Delay -= 1

    def SCH_Dispatch_Tasks(self):
        if self.current_index_task <=0:
            return
        if self.SCH_tasks_G[0].Delay <=0:
            self.SCH_tasks_G[0].pTask()
            new_pTask = self.SCH_tasks_G[0].pTask
            new_delay = self.SCH_tasks_G[0].Period/self.TICK
            new_period = self.SCH_tasks_G[0].Period/self.TICK
            self.SCH_tasks_G.pop(0)
            self.current_index_task = self.current_index_task - 1
            if new_period > 0:
                self.SCH_Add_Task(new_pTask, new_delay, new_period)
                # self.print_delay_list()

           

    def print_delay_list(self):
        for i in range(self.current_index_task):
            print (self.SCH_tasks_G[i].Delay)
    
    def SCH_Delete_all(self):
        self.SCH_tasks_G = []
        self.current_index_task = 0
        return

    def SCH_GenerateID(self):
        return -1

