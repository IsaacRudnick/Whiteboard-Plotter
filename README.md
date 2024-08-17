# VectorPlotter

:pushpin: If the system is set up and you just want to have it draw something, follow [these steps](/documentation/DrawSomething.md).

TODO: Picture of system on whiteboard

## Overview

This repository has everything necessary to assemble your own robot capable of plotting of SVG files on a whiteboard (or other surface). The existing code automatically handles outlining, scaling, and positioning of any SVG file along with commanding the robot to draw the image.

## Hardware

The VectorPlotter robot is built using an Arduino to handle implementation of the abstracted commands sent by the Python script. The robot is controlled by two stepper motors, one at each upper corner of the canvas. The pen is attached to a 3D-printed pen-holder assembly which uses a servo to raise and lower the pen, allowing noncontinuous lines to be drawn.

See the [Hardware Guide](/documentation/HardwareGuide.md) for a list of all necessary components and assembly instructions.

## Software

The VectorPlotter software is split into two parts: the Arduino code and the Python code. The Arduino code is responsible for interfacing with the hardware and executing the commands sent by the Python code. The Python code is responsible for reading the SVG file, scaling and positioning it on the canvas, and sending the commands to the Arduino to draw the image.

See the [Software Setup Guide](/documentation/SoftwareSetup.md) for a list of all necessary software and setup instructions.

## Usage

See the [How to Use](/documentation/DrawSomething.md) for instructions on how to use the software once everything is set up.

## Troubleshooting

See the [Troubleshooting Guide](/documentation/Troubleshooting.md) for common issues and solutions.
