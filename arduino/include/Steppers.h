#ifndef STEPPERS_H
#define STEPPERS_H

#include <AccelStepper.h>

// Define steppers
AccelStepper topLeftStepper = AccelStepper(AccelStepper::DRIVER, 2, 3);
AccelStepper topRightStepper = AccelStepper(AccelStepper::DRIVER, 6, 7);
AccelStepper steppers[] = {topLeftStepper, topRightStepper};

void setupSteppers()
// Call this in the setup() function to set up the steppers and groups
{
    // Set up steppers with max speed and acceleration
    steppers[0].setMaxSpeed(500);
    steppers[0].setAcceleration(5000);

    steppers[1].setMaxSpeed(500);
    steppers[1].setAcceleration(5000);
}

// Number of steppers (0 if none)
int steppersCount = sizeof(steppers) ? sizeof(steppers) / sizeof(steppers[0]) : 0;

#endif