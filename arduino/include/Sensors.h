#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h> // Required for Arduino-specific functions like pinMode()
#include <Steppers.h>

// Base Sensor class to handle any number of pins
class Sensor
{
protected:
    int *pins;    // Array to hold pins
    int pinCount; // Number of pins

public:
    Sensor(int pinArray[], int count)
    {
        pinCount = count;
        pins = new int[pinCount];
        for (int i = 0; i < pinCount; i++)
        {
            pins[i] = pinArray[i];
        }
    }

    // Default setup for sensors: Set all pins as INPUT (can be overridden)
    virtual void setup()
    {
        for (int i = 0; i < pinCount; i++)
        {
            pinMode(pins[i], INPUT);
        }
    }

    // Virtual read function to be implemented by each sensor
    virtual int read() = 0;
};

// Sensor to check if all steppers have finished moving.
class SteppersFinishedSensor : public Sensor
{
public:
    SteppersFinishedSensor() : Sensor(NULL, 0) {}

    void setup() override
    {
        return;
    }

    int read() override
    {
        // Check if all steppers have finished moving
        for (int i = 0; i < steppers_count; i++)
        {
            if (steppers[i].distanceToGo() != 0)
            {
                return false;
            }
        }
        return true;
    }
};

// Sensor array to store multiple sensors
Sensor *sensors[] = {
    new SteppersFinishedSensor(),
};

const int sensorsCount = sizeof(sensors) / sizeof(sensors[0]);

// Setup all sensors
void setupSensors()
{
    for (int i = 0; i < sensorsCount; i++)
    {
        sensors[i]->setup();
    }
}

#endif