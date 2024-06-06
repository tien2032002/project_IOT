import json
from typing import List


class ScheduleType:
    ADD = "add"
    DELETE = "delete"
    UPDATE = "update"


class Schedule:
    def __init__(
            self,
            scheduleId: str = "",
            email: str = "",
            type: str = "",
            name: str = "",
            volume: str = "",
            ratio: str = "[]",
            date: str = "",
            weekday: str = "[]",
            time: str = "",
            isOn: int = 1,
            error: str = ""
    ):
        self.scheduleId = scheduleId
        self.email = email
        self.type = type
        self.name = name
        self.volume = volume
        self.ratio = eval(ratio)
        self.date = date
        self.weekday = eval(weekday)
        self.time = time
        self.isOn = isOn
        self.error = error

    def setId(self, scheduleId: str):
        self.scheduleId = scheduleId

    @classmethod
    def importFromJsonString(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)

    def toJsonString(self):
        # Exclude bytes attributes from serialization
        data = {key: value for key, value in self.__dict__.items() if not isinstance(value, bytes)}
        return json.dumps(data)
