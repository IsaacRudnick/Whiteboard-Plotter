import time


class Sensor:
    def __init__(self,
                 index: int):
        """Creates a sensor object with the given parameters

        Args:
            index (int): The index of the sensor in the arduino Sensors.h header file
        """

        self.index = index
        self.value = None
        self.timestamp = None

    def mark_latest_reading(self, value: int):
        """Updates the value of the sensor

        Args:
            value (int): The new value of the sensor
        """
        self.value = value
        self.timestamp = time.time()
