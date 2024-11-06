from enum import Enum
from pycomponents.utils import map, clamp


class ServoConnectionType(Enum):
    SHIELD = 's'
    LOOSE = 'l'


class ServoActuationType(Enum):
    POSITION = 'p'
    VELOCITY = 'v'


class ServoInverted(Enum):
    NORMAL = 1
    INVERTED = -1


class Servo:
    def __init__(self,
                 pin_or_index: int,
                 connection_type: ServoConnectionType,
                 actuation_type: ServoActuationType,
                 microsecond_range: tuple[int, int],
                 actuation_range: tuple[int, int],
                 inverted: ServoInverted):
        """Creates a servo object with the given parameters

        Args:
            pin_or_index (int): The index of the servo in the arduino Servos.h header file OR the pin the servo is connected to (if SHIELD)
            connection_type (ServoConnectionType): The connection type of the servo
            actuation_type (ServoActuationType): The actuation type of the servo
            microsecond_range (tuple[int, int]): The range of microsecond values that the servo can be set to. Format: (lower, upper)
            actuation_range (tuple[int, int]): The range of actuation values that the servo can be set to. Format: (lower, upper). Likely degrees or velocities.

        Raises: 
            ValueError: If the pin is greater than 15 and the connection type is SHIELD
            ValueError: If the microsecond ranges are not positive

        Example usage:
            ServoType(ServoConnectionType.SHIELD, ServoActuationType.POSITION, (1000, 2000), (0, 180), ServoInverted.NORMAL) 
            represents a servo that is connected to the shield, is position controlled, can be set to a range of 1000-2000 microseconds, and can be set to a range of 0-180 degrees.
            Degrees could alternatively be (-90, 90) for a servo that can only rotate 180 degrees. How you wish to set this will be up to you.
        """

        if pin_or_index > 15 and connection_type == ServoConnectionType.SHIELD:
            raise ValueError("Shield-connected servos' pins must be less than or equal to 15. ")

        if microsecond_range[0] < 0 or microsecond_range[1] < 0:
            raise ValueError("Microsecond ranges must be positive.")

        self.pin_or_index = pin_or_index
        self.connection_type = connection_type
        self.actuation_type = actuation_type
        self.microsecond_range = microsecond_range
        self.actuation_range = actuation_range
        self.inverted = inverted

        self.actuation_value = None

    def mark_actuation_value(self, value: int):
        """Updates the actuation value (degrees or velocity) of the servo.

        Args:
            value (int): The new actuation value of the servo
        """
        self.actuation_value = value

    def actuation_value_to_arduino_value(self, value: int) -> int:
        """Converts the actuation value to a microsecond value.

        Args:
            value (int): The actuation value to convert to microseconds

        Returns:
            int: The actuation value converted to microseconds
        """

        # Clamp the value to the actuation range to prevent out-of-range values
        value = clamp(self.actuation_range[0], value, self.actuation_range[1])

        # Map the value from the actuation range to the microsecond range
        in_min, in_max = self.actuation_range
        out_min, out_max = self.microsecond_range

        # If the servo is inverted, invert the value before mapping
        # When working with this code, remember that the servo's actuation range may not be equal about 0.
        # E.g. it could be -20 to 100 degrees.
        if self.inverted == ServoInverted.INVERTED:
            value = self.actuation_range[1] - value

        return int(map(value, in_min, in_max, out_min, out_max))
