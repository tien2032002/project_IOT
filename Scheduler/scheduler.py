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
            aTask = Task(pFunction, DELAY / self.TICK, PERIOD / self.TICK)
            self.SCH_tasks_G.append(aTask)
            self.current_index_task += 1
            print(f"add task with delay = {DELAY}, period = {PERIOD}")
            return True

        if self.current_index_task < self.SCH_MAX_TASKS:
            total = 0
            for index in range(self.current_index_task):
                total+=self.SCH_tasks_G[index].Delay
                if total <= DELAY/self.TICK:
                    aTask = Task(pFunction, DELAY / self.TICK - total, PERIOD / self.TICK)
                    self.SCH_tasks_G.insert(index+1, aTask)
                    break
            self.current_index_task += 1
            print(f"add task with delay = {DELAY}, period = {PERIOD}")
            return True
        else:
            print("PrivateTasks are full!!!")
            return False

    def SCH_Update(self):
        if self.current_index_task > 0:
            self.SCH_tasks_G[0].Delay -= 1

    def SCH_Dispatch_Tasks(self):
        if self.SCH_tasks_G[0].Delay <=0:
            self.SCH_tasks_G[0].pTask()
            if self.SCH_tasks_G[0].Period > 0:
                self.SCH_Add_Task(self.SCH_tasks_G[0].pTask, self.SCH_tasks_G[0].Period, self.SCH_tasks_G[0].Period)
            self.SCH_tasks_G.pop(0)

    def SCH_Delete(self, aTask):
        return

    def SCH_GenerateID(self):
        return -1

