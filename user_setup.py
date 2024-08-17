# =================================== SET INPUT PARAMETERS HERE ================================== #
# This is the file you want the program to draw.
INPUT_IMG_FILE_PATH = f"user/SVGs/DefaultDrawing.svg"

# If the process crashes (e.g., from a power outage), you can see the recorded progress in the progress.txt file.
# To start from that point, change this to that value.
START_FROM_POINT = 0

# Max distance between two points.
# Higher value = faster drawing, but less accurate
# Lower value = slower drawing, but more accurate
# Recommended range = (0, 2]
MAX_CM_BETWEEN_POINTS = .2

# The USB port the Arduino is connected to. If you aren't sure, run list_usb_ports.py
# The name will likely have "Serial" or "Arduino" in it.
ARDUINO_USB_PORT = "COM13"

# Whether or not to show a preview of the drawing first
SHOW_PREVIEW = True
# Turtle configuration
TURTLE_PENSIZE = 5

# ====================================== CANVAS AND PADDING ====================================== #
# A cropped, keystoned picture of the background you intend to draw on. Set this to None if you don't have a background.
BACKGROUND_IMG_FILE_PATH = "user/backgrounds/DefaultBackground.png"

# SEE documentation/SoftwareSetup.md FOR EXPLANATION OF THESE VALUES.
CANVAS_WIDTH = 51  # cm
CANVAS_HEIGHT = 31  # cm

TOP_PADDING = 5  # cm
LEFT_PADDING = 2  # cm
RIGHT_PADDING = 2  # cm
BOTTOM_PADDING = 5  # cm

# RUN main.py TO START PROGRAM.
