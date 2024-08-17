# ====================================== PRELOADED CONSTANTS ===================================== #
# Distance between belt ends in the holder.
PEN_HOLDER_WIDTH = 2.5  # cm
# How high above the belt the pen is.
PEN_VERTICAL_OFFSET = 2  # cm

# ====================================== STEPPERS AND SERVOS ===================================== #
STEPS_PER_REVOLUTION = 400  # Turning the motor 400 steps = one revolution
REVOLUTIONS_PER_CM = 0.25  # From testing, Driving the belt 1 cm requires 0.25 revolutions.

# Index in Arduino steppers list
TOP_LEFT_MOTOR_INDEX = 0
TOP_RIGHT_MOTOR_INDEX = 1
# Index in Arduino servos list
SERVO_INDEX = 0

PEN_DOWN_SERVO_ANGLE = 30
PEN_UP_SERVO_ANGLE = -90
