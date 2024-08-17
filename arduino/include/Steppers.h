#include <AccelStepper.h>
// #include <MultiStepper.h>

// Define steppers
AccelStepper topLeftStepper = AccelStepper(AccelStepper::DRIVER, 2, 3);
AccelStepper topRightStepper = AccelStepper(AccelStepper::DRIVER, 6, 7);
AccelStepper steppers[] = {topLeftStepper, topRightStepper};

// // Define stepper groups
// MultiStepper topSteppers = MultiStepper();
// MultiStepper stepperGroups[] = {topSteppers};

void setupSteppers()
// Call this in the setup() function to set up the steppers and groups
{
    // Set up steppers with max speed and acceleration
    steppers[0].setMaxSpeed(500);
    steppers[0].setAcceleration(5000);

    steppers[1].setMaxSpeed(500);
    steppers[1].setAcceleration(5000);

    // // Add steppers to respective groups
    // topSteppers.addStepper(topLeftStepper);
    // topSteppers.addStepper(topRightStepper);
}

int steppers_count = sizeof(steppers) / sizeof(steppers[0]);
// int groups_count = sizeof(stepperGroups) / sizeof(stepperGroups[0]);