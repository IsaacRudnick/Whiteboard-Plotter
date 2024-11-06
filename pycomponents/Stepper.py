from enum import Enum


class StepperDirection(Enum):
    NORMAL = 1
    INVERTED = -1


class Stepper:
    def __init__(self,
                 index: int,
                 inverted: StepperDirection):
        """Creates a stepper object with the given parameters

        Args:
            index (int): The index of the stepper in the arduino Steppers.h header file
            inverted (StepperInverted): Whether the stepper is inverted or not
        """

        self.index = index
        self.inverted = inverted
        self.steps = 0

    def mark_stepper_steps(self, steps: int):
        """Updates the steps of the stepper

        Args:
            steps (int): The new steps of the stepper
        """
        self.steps = steps

    def steps_to_arduino_value(self, steps: int) -> int:
        """Converts the steps to account for inversion. 
        Eventually, this function could handle other adjustments as well, such 
        as adjusting for the number of steps per revolution.

        Args:
            steps (int): The number of steps to convert to microseconds

        Returns:
            int: The equivalent microsecond value
        """
        return steps * self.inverted.value
