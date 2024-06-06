from enum import Enum


class SensorDataType(Enum):
    TEMPERATURE = "temp"
    SOIL_MOISTURE = "mois"


class SensorData:
    def __init__(self, sensorDataType: SensorDataType, value: int):
        self.sensorDataType = sensorDataType
        self.value = value

    def toStringInJsonForm(self):
        data = {
            "type": self.sensorDataType.value,
            "value": self.value
        }
        return str(data)
