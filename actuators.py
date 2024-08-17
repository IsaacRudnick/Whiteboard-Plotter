from abc import ABC
import serial
import time


class Servo:
    def __init__(self,
                 arduino_index: int,
                 lower_microseconds_limit: int,
                 upper_microseconds_limit: int,
                 total_degrees: int,
                 inverted: bool):

        # The index of this servo in the Arduino's array of servos
        # See ./Arduino/include/Servos.h for the array of servos
        self.arduino_index = arduino_index
        self.lower_microseconds_limit = lower_microseconds_limit
        self.upper_microseconds_limit = upper_microseconds_limit
        self.total_degrees = total_degrees
        self.inverted = inverted

        self.degrees_set_to = None


class StepperMotor:
    def __init__(self, arduino_index: int, inverted: bool):

        # The index of this stepper in the Arduino's array of steppers
        # See ./Arduino/include/Steppers.h for the array of steppers
        self.arduino_index = arduino_index
        self.inverted = inverted

        self.position_set_to = None


class Command(ABC):
    pass


class ServoCommand(Command):
    def __init__(self, servo: Servo, degrees: int):
        self.servo = servo
        self.degrees = degrees

        servo.degrees_set_to = degrees

    def __str__(self):
        return f"s{self.servo.arduino_index}={int(self.degrees)};"


class StepperCommand(Command):
    def __init__(self, stepper: StepperMotor, position: int):
        self.stepper = stepper
        self.position = position

        stepper.position_set_to = position

    def __str__(self):
        return f"m{self.stepper.arduino_index}={int(self.position)};"


class ActuatorController:

    def __init__(self, port: str, show_serial: bool = False):
        """Initializes the ServoController class. The port will be the port the Arduino is connected to.
        On windows, this will be COM3, COM4, etc. On Linux, this will be /dev/ttyUSB0, /dev/ttyUSB1, etc.


        Args:
            port (str): The USB port the Arduino is connected to.
        """
        self.arduino = serial.Serial(port, 115200, timeout=.1)
        self.commands_to_send = []
        self.show_serial = show_serial
        # Wait for the Arduino to initialize the serial connection
        time.sleep(1)

    def send_queue(self):
        """Take all queued commands and send them to the Arduino."""
        # Convert the list of commands to a string and send it to the Arduino
        self._write_read(''.join([str(command) for command in self.commands_to_send]))
        self.commands_to_send = []

    def _queue_command(self, command: Command) -> None:
        """Queue a command to be sent to the Arduino."""
        self.commands_to_send.append(command)

    def _write_read(self, message: str):
        """Send a message to the Arduino and return the response."""

        # Send outgoing message
        self.arduino.write(bytes(message, 'utf-8'))

        # Receive incoming message
        response = self.arduino.readall().decode()
        if self.show_serial:
            print(f"{message=}")
            print(f"{response=}")

        return response

    def _clamp(self, num: float, min_value: float, max_value: float) -> float:
        """Clamp a number between a minimum and maximum value, to protect from setting (e.g.,) degrees beyond safe ranges.
        Private function, not intended to be called from outside the class."""
        return max(min(num, max_value), min_value)

    def _map(self, value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
        """Map a value from one range to another. Useful for converting (e.g.,) degrees to pulse widths.
        Assumes the input value is within the input range. If it is not, use the clamp function to ensure it is.
        Private function, not intended to be called from outside the class."""
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    # ========================================= SERVO METHODS ======================================== #

    def queue_set_degrees(self, servo: Servo, degrees: float) -> None:

        half_degrees = servo.total_degrees / 2
        degrees = self._clamp(degrees, -half_degrees, half_degrees)
        # Invert the degrees if the servo is inverted
        degrees *= -1 if servo.inverted else 1

        microSeconds = int(self._map(
            degrees,
            -half_degrees, half_degrees,
            servo.lower_microseconds_limit, servo.upper_microseconds_limit))

        self._queue_command(ServoCommand(servo, microSeconds))

    def queue_turn_off(self, servo: Servo) -> None:
        """Turn off the servo."""
        self._queue_command(ServoCommand(servo, 0))

    # ========================================= STEPPER MOTOR METHODS ======================================== #

    def queue_set_stepper(self, stepper: StepperMotor, position: int) -> None:
        """Set the position of a stepper motor."""

        # Invert the position if the motor is inverted
        position *= -1 if stepper.inverted else 1
        # Send the position to the Arduino
        self._queue_command(StepperCommand(stepper, position))
