import threading
from utils.time_manager import TimeManager


class TaskArgument:
    def __init__(self, **kwargs):
        self.payload = kwargs


class Task:
    def __init__(
            self,
            pTask,
            delay,
            period,
            args: TaskArgument = None
    ):
        self.pTask = pTask
        self.args = args
        self.delay = int(delay / Scheduler1.TIMER_CYCLE)
        self.period = int(period / Scheduler1.TIMER_CYCLE)
        self.taskId = 0

    def setTaskId(self, newId: int):
        self.taskId = newId

    # Renew delay then check if delay is negative, return false.
    # Otherwise true.
    def canContinue(self):
        return self._renewDelay()

    def _renewDelay(self):
        if self.period > 0:
            self.delay = self.period
            return True
        else:
            return False

    def doTask(self):
        if self.pTask:
            if self.args:
                self.pTask(self.args)
            else:
                self.pTask()
        else:
            print("[ERROR] No task to run!")


# 2 Threads: LoopInfinity and Timer.
# SCH_Update and SCH_Dispatch run concurrently by using lock.
# We try to make SCH_Update, SCH_AddTask, SCH_DeleteTask has higher priority to run than SCH_Dispatch.
class Scheduler1:
    TIMER_CYCLE = 0.05
    IDLE_SLEEP = 0.1
    PRIORITY_WAIT = 0.02
    MAX_TASK = 40

    def __init__(self):
        # Tracking task ID
        self._taskIds = list(range(self.MAX_TASK))

        # List of tasks.
        self._taskList = []

        # Lock
        self._lock = threading.Lock()

        # For delay
        self._time = TimeManager()

        self.numTaskRunning = 0

        # Number for priority.
        # This is the number show the scheduler function need to be done.
        # Assume we have SCH_Dispatch always acquire lock of SCH_Update, make starvation.
        # We prior SCH_Update, SCH_AddTask, SCH_DeleteTask than SCH_Dispatch.
        self._priorityFunc = 0

        # For SCH_Update()
        self._runUpdate = 0

        # In irrigation process
        self.inProcess = False

        # Notify no task, loopInfinity thread can be sleep
        self.isNoTask = 0

        # Start timer
        thread = threading.Thread(target=self.TIMER)
        thread.daemon = True
        thread.start()

        # Start loop
        thread = threading.Thread(target=self.LoopInfinity)
        thread.daemon = True
        thread.start()

    def SCH_AddTask(self, task: Task) -> int:
        self._priorityFunc += 1
        # Critical section !!!
        with self._lock:
            self.numTaskRunning += 1
            task.setTaskId(self._taskIds.pop())
            self._addTaskSortedByDelay(task)
        # End critical section !!!
        self._priorityFunc -= 1
        return task.taskId

    def _addTaskSortedByDelay(self, newTask: Task):
        idx = 0
        for task in self._taskList:
            delay_diff = newTask.delay - task.delay
            if delay_diff > 0:
                newTask.delay = delay_diff
            else:
                task.delay = -delay_diff
                self._taskList.insert(idx, newTask)
                return
            idx += 1
        self._taskList.append(newTask)

    def SCH_DeleteTask(self, taskId: int):
        self._priorityFunc += 1
        # Critical section !!!
        with self._lock:
            self.numTaskRunning += -1
            res = self.deleteTask(taskId)
        # End critical section !!!
        self._priorityFunc -= 1
        return res

    def deleteTask(self, taskId: int):
        idx = 0
        for task in self._taskList:
            if task.taskId == taskId:
                if idx + 1 < len(self._taskList):
                    self._taskList[idx + 1].delay += self._taskList[idx].delay
                self._taskIds.append(task.taskId)
                self._taskList.remove(task)
                return True
            idx += 1
        return False

    def isReady(self):
        if self._taskList:
            return self._taskList[0].delay <= 0
        return False

    def SCH_Dispatch(self):
        if self._priorityFunc > 0:
            # Sleep about = 16ms
            TimeManager.sleep(self.PRIORITY_WAIT)
            return

        self.isNoTask = False
        # Critical section !!!
        with self._lock:
            if self._taskList and self.isReady():
                task = self._taskList.pop(0)
                self._taskIds.append(task.taskId)
            else:
                self.isNoTask = True
                return

        # End critical section !!!

        if task and task.delay <= 0:
            # Execute
            task.doTask()
            # Check if the task has period.
            # If true will reset new delay then add task again.
            if task.canContinue():
                self.SCH_AddTask(task)

    def SCH_Update(self):
        self._priorityFunc += 1
        # Critical section !!!
        with self._lock:
            if self._taskList:
                if self._taskList[0].delay > 0:
                    self._taskList[0].delay -= 1
        # End critical section !!!
        self._priorityFunc -= 1

    def TIMER(self):
        self._time.start()
        while True:
            self.SCH_Update()
            self._time.waitUntil(self.TIMER_CYCLE)
            self._time.moveStartPoint(self.TIMER_CYCLE)

    def LoopInfinity(self):
        while True:
            self.SCH_Dispatch()

            if self.isNoTask:
                TimeManager.sleep(self.IDLE_SLEEP)
