// Note: this file only defines "loose" servos. The shield servos are defined in the Adafruit_PWMServoDriver library.

#ifndef SERVOS_H
#define SERVOS_H

#include <Servo.h>

Servo penServo = Servo();
Servo looseServos[] = {penServo};

void setupServos()
{
    penServo.attach(10);
}

// Number of loose servos (0 if none)
int looseServosCount = sizeof(looseServos) ? sizeof(looseServos) / sizeof(looseServos[0]) : 0;

#endif