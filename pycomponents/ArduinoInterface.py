import serial
from Sensor import *
from Stepper import *
from Servo import *
from enum import Enum

# ====================================== VALID COMMAND TYPES ===================================== #


class CommandType(Enum):
    ShieldServo = 's'
    Stepper = 't'
    Sensor = 'i'
    LooseServo = 'l'


class Command:
    """This class allows standardization of the commands sent to the Arduino.
    When the ArduinoInterface class (below) sends a command, it will create a Command object and send it to the Arduino.
    This class handles the string-formatting of the command and the conversion of the value to the proper format.
    """

    def __init__(self, type: CommandType, index: int, value: int = None):
        if type not in CommandType:
            raise ValueError("Invalid command type. ")

        self.type = type
        self.index = index
        self.value = value

    def __str__(self) -> str:
        # Return the properly-formatted command depending on the type
        if self.type == CommandType.Sensor:
            return f"{self.type.value}{self.index}?;"  # E.g. "i0?" for sensor 0
        else:
            val = str(int(self.value)) if self.value else ""
            # Force the value to be an int. "1000.0" is not a valid value for the arduino, but "1000" is.
            return f"{self.type.value}{self.index}={val};"  # E.g. "s0=90" for shield servo 0 to 90 degrees


class ArduinoInterface:
    """This class is the interface between the Python code and the Arduino. It handles all communication between the two.
    It is responsible for sending commands to the Arduino and receiving responses.
    """

    def __init__(self, port: str, servos: list[Servo], steppers: list[Stepper], sensors: list[Sensor]):
        self.port = port
        self.arduino = serial.Serial(port, 115200)

        self.servos = servos
        self.steppers = steppers
        self.sensors = sensors

        self.arduino.read_all()
        time.sleep(2)  # Wait for the Arduino to initialize before sending commands

    def _send_command(self, command: Command):
        """Send a message to the Arduino and return the response. For private use only."""
        message = str(command).encode('utf-8')
        # print(f"{message=}")
        self.arduino.write(message)

    def _read(self):
        """Read one line from the Arduino and return it. For private use only."""
        response = self.arduino.readline().decode()
        # print(f"{response=}")
        return response

    def poll_sensor(self, sensor: Sensor):
        """Poll a single sensor, update its value, and return the response."""
        # Create query, e.g.  "i0?" for sensor 0, and send it
        query = Command(CommandType.Sensor, sensor.index)
        self._send_command(query)
        # Wait for the correct response, e.g. "i0=100" for sensor 0
        response = ""
        while f"i{sensor.index}=" not in response:
            response = self._read()

        response_value = int(response.split('=')[1])
        sensor.mark_latest_reading(response_value)
        return response_value

    def poll_all_sensors(self):
        """Poll all sensors and update their values."""
        for sensor in self.sensors:
            self.poll_sensor(sensor)

    def set_servo(self, servo: Servo, value: int):
        """Set the given servo to the given value."""
        # Determine the command type based on the servo's connection type
        commandtype = CommandType.ShieldServo if servo.connection_type == ServoConnectionType.SHIELD else CommandType.LooseServo
        # Map the value from the actuation range to the microsecond range
        arduino_value = servo.actuation_value_to_arduino_value(value)
        # Create the command and send it
        command = Command(commandtype, servo.pin_or_index, arduino_value)
        self._send_command(command)
        # Update the servo's actuation value
        servo.mark_actuation_value(arduino_value)

    def set_stepper(self, stepper: Stepper, value: int):
        """Set the given stepper to the given value."""
        arduino_value = stepper.steps_to_arduino_value(value)
        command = Command(CommandType.Stepper, stepper.index, arduino_value)
        self._send_command(command)
        # Update the stepper's steps using the initial value,
        # not the arduino value.
        # The arduino value is only for communication.
        stepper.mark_stepper_steps(value)

    def close(self):
        """Close the serial connection to the Arduino. Note that this will make the object unusable."""
        self.arduino.close()
