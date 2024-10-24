from dataclasses import dataclass
from math import sqrt
import os
import time
from svgoutline import svg_to_outlines
import turtle
import constants
import user_setup as user_settings
import xml.etree.ElementTree as ET
from progress.bar import ChargingBar
import cv2
import actuators
import ArduinoInterface
from Stepper import StepperDirection
from Servo import ServoConnectionType, ServoActuationType, ServoInverted

# =========================================== WARNINGS =========================================== #
# Make sure user isn't accidentally starting from a point other than 0
if user_settings.START_FROM_POINT > 0:
    warning = f"NOTE: Starting from point {user_settings.START_FROM_POINT}. Press Enter to continue."
    input(warning)

# Minimum recommended padding values
min_lp = 5
min_rp = 5
min_tp = 10
min_bp = 5

# Check the padding values and warn the user if they are below the recommended minimums
lp_warning = user_settings.LEFT_PADDING < min_lp
rp_warning = user_settings.RIGHT_PADDING < min_rp
tp_warning = user_settings.TOP_PADDING < min_tp
bp_warning = user_settings.BOTTOM_PADDING < min_bp

if lp_warning or rp_warning or tp_warning or bp_warning:
    print(
        f"WARNING: Padding values are " +
        f"left: {user_settings.LEFT_PADDING}, " +
        f"right: {user_settings.RIGHT_PADDING}, " +
        f"top: {user_settings.TOP_PADDING}, " +
        f"bottom: {user_settings.BOTTOM_PADDING}.\n " +
        "Recommended minimum values are " +
        f"{min_lp}, {min_rp}, {min_tp}, {min_bp}. "
        "Make sure the pen holder fits within the canvas.")
    input("Press Enter to acknowledge.")

# ===================================== Classes and Instances ==================================== #

# Create the steppers and servo that control the physical plotter
TopLeftStepper = ArduinoInterface.Stepper(0, StepperDirection.NORMAL)
TopRightStepper = ArduinoInterface.Stepper(1, StepperDirection.INVERTED)
MarkerToggleServo = ArduinoInterface.Servo(0,
                                           ServoConnectionType.PWM,
                                           ServoActuationType.POSITION,
                                           (500, 1500),
                                           (0, 180),
                                           ServoInverted.NORMAL)
SteppersFinishedSensor = ArduinoInterface.Sensor(0)
Arduino = ArduinoInterface.Arduino(user_settings.ARDUINO_USB_PORT,
                                   [MarkerToggleServo],
                                   [TopLeftStepper, TopRightStepper],
                                   [SteppersFinishedSensor])


@dataclass
class PointInstruction:
    """Represents a point in the drawing with instructions for the motors and pen.
    x_cm and y_cm are the coordinates of the point in cm, where the bottom left of the canvas is (0,0).
    motor_left_position and motor_right_position are the number of steps each motor needs to take to reach that point.
    pen_down_after is a boolean value that determines whether the pen should be down after reaching that point.
    """
    x_cm: float
    y_cm: float
    # Map the x and y cm to the position of each motor (in steps) to reach that point.
    # Note, steps are relative to start, not current position.
    motor_left_position: int
    motor_right_position: int
    # Put the pen down after this point or not
    pen_down_after: bool


class PenController:
    def __init__(self, ArdI: ArduinoInterface.Arduino):
        self.ArdI = ArdI

        self.pen_down = True  # Initial pen state
        self.prev_instruction = None

    def raise_pen(self):
        if self.pen_down:
            self.ArdI.set_servo(MarkerToggleServo, constants.PEN_UP_SERVO_ANGLE)
            # Wait for the steppers to finish moving before continuing
            time.sleep(0.5)
            self.pen_down = False

    def lower_pen(self):
        if not self.pen_down:
            self.ArdI.set_servo(MarkerToggleServo, constants.PEN_DOWN_SERVO_ANGLE)
            # Wait for the steppers to finish moving before continuing
            time.sleep(0.5)
            self.pen_down = True
            
    def done_moving(self):
        return self.ArdI.poll_sensor(SteppersFinishedSensor)

    def follow_instruction(self, instruction: PointInstruction):
        # Move the motors to the correct position
        self.ArdI.set_stepper(TopLeftStepper, instruction.motor_left_position)
        self.ArdI.set_stepper(TopRightStepper, instruction.motor_right_position)

        # Wait for the steppers to finish moving before continuing
        while not self.done_moving():
            print("Debug: Waiting for steppers to finish moving.")
            time.sleep(0.1)

        if instruction.pen_down_after:
            self.lower_pen()
        else:
            self.raise_pen()

        # Update the previous instruction
        self.prev_instruction = instruction


# This is how we will control moving the pen across the board and raising/lowering it (on/off the surface)
Pen = PenController(Arduino)

# ======================================= PRIMARY FUNCTIONS ====================================== #


def add_strokes_to_svg(input_file: str, output_file: str):
    """Add stroke and stroke-width attributes to all elements in an SVG file.
    This is necessary for the svgoutline library to work properly.

    Args:
        input_file (str): The path to the input SVG file.
        output_file (str): The path to the output SVG file.
    """
    # Parse the SVG file
    tree = ET.parse(input_file)
    root = tree.getroot()

    # Iterate over all elements in the SVG
    for elem in root.iter():
        # Add stroke and stroke-width attributes to each element
        # The color and width are arbitrary as far as this program is concerned. All that matters is that they are there.
        elem.set('stroke', 'red')
        elem.set('stroke-width', '2')

    # Write the updated SVG to a new file
    tree.write(output_file)


def svg_to_instructions(svg_path: str):
    """Generate a list of PointInstructions from an SVG file.

    Args:
        svg_path (str): The path to the SVG file that will be converted to instructions.
    """

    # ====================================== GET STARTING POINTS ===================================== #

    frame_width = user_settings.CANVAS_WIDTH - user_settings.LEFT_PADDING - user_settings.RIGHT_PADDING
    frame_height = user_settings.CANVAS_HEIGHT - user_settings.TOP_PADDING - user_settings.BOTTOM_PADDING

    # Get raw points. These will later be scaled to the canvas size, but may have any range of values right now.
    tree = ET.parse(svg_path)
    root = tree.getroot()
    outlines = svg_to_outlines(root)
    # List of lists of points. Each sublist is a disconnected section of the drawing.
    raw_sections = [line[2] for line in outlines]

    raw_all_points = [point for section in raw_sections for point in section]

    # Determine the minimum and maximum x and y values of the drawing
    # These will be used to scale the drawing to the canvas size
    min_x = min([point[0] for point in raw_all_points])
    max_x = max([point[0] for point in raw_all_points])
    min_y = min([point[1] for point in raw_all_points])
    max_y = max([point[1] for point in raw_all_points])

    # ============================================ SCALING =========================================== #
    # Scale all points to fit in the frame

    # Calculate the scale factor to fit the drawing to the canvas
    x_scale_factor = frame_width / (max_x - min_x)
    y_scale_factor = frame_height / (max_y - min_y)

    # Maintain aspect ratio by using the smaller scale factor
    scale_factor = min(x_scale_factor, y_scale_factor)

    # Calculate the center offset to keep the drawing centered
    x_center_offset = (frame_width - (max_x - min_x) * scale_factor) / 2
    y_center_offset = (frame_height - (max_y - min_y) * scale_factor) / 2

    def scale_raw_xy(x, y):
        """Take in a raw x and y value and scale it to the canvas size. Only used in svg_to_instructions."""
        scaled_x = (x - min_x) * scale_factor + user_settings.LEFT_PADDING + x_center_offset
        scaled_y = (y - min_y) * scale_factor + y_center_offset
        scaled_y = user_settings.CANVAS_HEIGHT - user_settings.TOP_PADDING - scaled_y
        return scaled_x, scaled_y

    sections = []

    for raw_section in raw_sections:
        section = [scale_raw_xy(x, y) for x, y in raw_section]
        sections.append(section)

    # ====================================== INTERMEDIATE POINTS ===================================== #
    # Add intermediate points in the drawing. Necessary to avoid arcs when drawing straight lines.

    def add_intermediate_points(section):
        """Add intermediate points to the sections to smooth out the drawing.

        Args:
            section (list): List of points [(x1, y1), (x2, y2), ...]

        Returns:
            list: New section with intermediate points.
        """
        new_section = []
        for i in range(len(section) - 1):
            x1, y1 = section[i]
            x2, y2 = section[i + 1]
            new_section.append((x1, y1))
            distance = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            num_points = int(distance // user_settings.MAX_CM_BETWEEN_POINTS)
            for j in range(1, num_points + 1):
                new_x = x1 + j * (x2 - x1) / (num_points + 1)
                new_y = y1 + j * (y2 - y1) / (num_points + 1)
                new_section.append((new_x, new_y))
        new_section.append(section[-1])
        return new_section

    interpolated_sections = [add_intermediate_points(section) for section in sections]

    # ======================================== MOTOR DISTANCES ======================================= #

    def xy_to_motor_position(x, y):
        steps_per_cm = constants.STEPS_PER_REVOLUTION * constants.REVOLUTIONS_PER_CM
        cm_from_top = user_settings.CANVAS_HEIGHT - y - constants.PEN_VERTICAL_OFFSET
        cm_from_right = user_settings.CANVAS_WIDTH - x + constants.PEN_HOLDER_WIDTH
        cm_from_left = x + constants.PEN_HOLDER_WIDTH
        top_left_motor_position = steps_per_cm * sqrt(cm_from_top ** 2 + cm_from_left ** 2)
        top_right_motor_position = steps_per_cm * sqrt(cm_from_top ** 2 + cm_from_right ** 2)
        return top_left_motor_position, top_right_motor_position

    instructions = []

    for section in interpolated_sections:
        for x, y in section:
            motor_left_position, motor_right_position = xy_to_motor_position(x, y)
            instructions.append(PointInstruction(x, y, motor_left_position, motor_right_position, True))

        # At the end of each section, lift the pen up
        instructions[-1].pen_down_after = False

    return instructions


def prep_background(input: str, output: str, width: int, height: int):
    """Helper function for draw().
    Resizes the input image that will be the background of the drawing.
    Also adds a rectangle to the turtle screen to represent the area inside the canvas padding.

    Args:
        input (str): The path to the input image.
        output (str): The path to the output image.
        width (int): The desired width of the image in pixels.
        height (int): The desired height of the image in pixels.
    """
    # Used to draw the rectangle representing the canvas padding
    width_scale = width / user_settings.CANVAS_WIDTH
    height_scale = height / user_settings.CANVAS_HEIGHT

    line_thickness = 2

    # cv2 rectangle origin is top left. Positive x is right, positive y is down
    # The +- 10 offsets adjust for some small rounding issues. It will ONLY affect the preview, not the actual drawing.
    x0 = int(user_settings.LEFT_PADDING * width_scale) - line_thickness * 2 - 10
    y0 = int((user_settings.TOP_PADDING) * height_scale) + line_thickness * 2 + 10

    x1 = int((user_settings.CANVAS_WIDTH - user_settings.RIGHT_PADDING) * width_scale) + line_thickness * 2 - 10
    y1 = int((user_settings.CANVAS_HEIGHT - user_settings.BOTTOM_PADDING) * height_scale) - line_thickness * 2 + 10

    img = cv2.imread(input)
    resized = cv2.resize(img, (width, height))
    cv2.rectangle(resized,
                  (x0, y0),
                  (x1, y1),
                  (0, 0, 0),
                  line_thickness,
                  lineType=cv2.LINE_AA)
    cv2.imwrite(output, resized)


def draw(instructions: list[PointInstruction], only_preview=False):
    """Draw the given instructions on the canvas. Show a digital preview of the drawing as well

    Args:
        instructions (list[PointInstruction]): The list of instructions to draw.
        only_preview (bool, optional): Whether to only show a preview of the drawing. Defaults to False.
    """

    # ================================ TURTLE, CANVAS, AND BACKGROUND ================================ #
    screen = turtle.Screen()

    # Get starting screen width and height of the window
    screen_width, screen_height = screen.window_width(), screen.window_height()
    # Scale the window / screen to the canvas size, maintaining aspect ratio
    if screen_width / user_settings.CANVAS_WIDTH < screen_height / user_settings.CANVAS_HEIGHT:
        screen_height = int(screen_width * user_settings.CANVAS_HEIGHT / user_settings.CANVAS_WIDTH)
    else:
        screen_width = int(screen_height * user_settings.CANVAS_WIDTH / user_settings.CANVAS_HEIGHT)
    screen.setup(width=screen_width, height=screen_height)

    # Configure how coordinates are interpreted. (0,0) will be bottom left, (CANVAS_WIDTH, CANVAS_HEIGHT) will be top right
    screen.setworldcoordinates(0, 0, user_settings.CANVAS_WIDTH, user_settings.CANVAS_HEIGHT)

    turtle_canvas = screen.getcanvas()

    # Add the background image if it exists
    if user_settings.BACKGROUND_IMG_FILE_PATH:
        prep_background(user_settings.BACKGROUND_IMG_FILE_PATH,
                        "temp/ResizedBackground.png",
                        screen_width, screen_height)
        # Set the background image to be the resized image and make sure its aligned properly
        screen.bgpic("temp/ResizedBackground.png")
        turtle_canvas.itemconfig(screen._bgpic, anchor="sw")

    root = turtle_canvas.winfo_toplevel()
    root.resizable(False, False)
    root.title("Drawing Preview")

    # Bug-fixing line that allows us to recreate the turtle window if this function is called multiple times.
    turtle.TurtleScreen._RUNNING = True

    t = turtle.Turtle()
    t.pensize(user_settings.TURTLE_PENSIZE)
    t.color("green") if only_preview else t.color("blue")
    t.setheading(90)  # Point the turtle up

    t.penup()

    # Progress bar to show how many points have been drawn. Will be shown in the console.
    bar = ChargingBar('Drawing', max=len(instructions))

    # ====================================== DRAWING THE POINTS ====================================== #
    for i, instruction in enumerate(instructions):
        # Skip to the starting point
        if i < user_settings.START_FROM_POINT:
            bar.next()
            continue

        t.goto(instruction.x_cm, instruction.y_cm)
        t.pendown() if instruction.pen_down_after else t.penup()

        # If we are actually drawing and not just previewing, follow the instructions
        if not only_preview:
            Pen.follow_instruction(instruction)
            save_progress(i)

        bar.next()

    print("\n")

    # If the actual drawing is complete, remove the progress file
    if not only_preview:
        os.remove("progress.txt")

    print("Click window to exit.")
    turtle.exitonclick()
    print("Drawing complete.")


def save_progress(total_points_drawn: int):
    try:  # Save progress in case of interruption
        with open("progress.txt", "w") as f:
            f.write(str(total_points_drawn))
    except PermissionError:
        print("Could not save progress. Make sure progress.txt is not open.")


if __name__ == "__main__":
    # Always raise the pen to start. This is to prevent the pen from drawing when it shouldn't.
    print("Raising pen...")
    Pen.raise_pen()

    print("Preprocessing SVG file...")
    add_strokes_to_svg(user_settings.INPUT_IMG_FILE_PATH, 'temp/output.svg')
    print("Converting SVG to instructions...")
    instructions = svg_to_instructions('temp/output.svg')

    if user_settings.SHOW_PREVIEW:
        print("Showing preview...")
        draw(instructions, only_preview=True)
        input("Press Enter to confirm preview and start drawing.")

    print("Drawing...")
    draw(instructions)
