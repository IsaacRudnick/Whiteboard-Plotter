#include <Servo.h>

Servo penServo = Servo();
Servo servos[] = {penServo};

void setupServos()
{
    penServo.attach(10);
}

int servos_count = sizeof(servos) / sizeof(servos[0]);