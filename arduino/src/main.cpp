#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PWMServoDriver.h>
#include <AccelStepper.h>
#include "Steppers.h"
#include "Servos.h"

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
#define SERVO_FREQ 50 // Analog servos run at ~50 Hz updates

typedef struct
{
  long value;
  int index;
  char type; // 's' for servo, 'm' for stepper (motor)
} command;

unsigned long previous_step_time = micros();

// Function prototypes
void runAllSteppers();
command stringToCommand(String input);
void handleCommands(String input);
void executeServoCommand(command cmd);
void executeStepperCommand(command cmd);

// Steps all steppers that need to be stepped
void runAllSteppers()
{
  unsigned long difference = micros() - previous_step_time;
  previous_step_time = micros();

  if (difference > 500)
  {
    Serial.println(difference);
  }

  for (int i = 0; i < steppers_count; i++)
  {
    steppers[i].run();
  }
}

// Converts a string to a command
command stringToCommand(String input)
{
  command cmd;
  cmd.type = input.charAt(0); // First character determines the command type ('s', 'm', 'M')
  cmd.index = -1;             // Initialize index with invalid value
  cmd.value = -1;             // Initialize value with invalid value

  int equalsIndex = input.indexOf('=');
  if (equalsIndex == -1)
  {
    Serial.println("Invalid input format. Please enter the input in the correct format.");
    return cmd;
  }

  cmd.index = input.substring(1, equalsIndex).toInt();
  String valuePart = input.substring(equalsIndex + 1);
  cmd.value = valuePart.toInt();

  return cmd;
}

// Executes a servo command
void executeServoCommand(command cmd)
{
  if (cmd.index >= 0 && (unsigned)cmd.index < servos_count)
  {
    servos[cmd.index].writeMicroseconds(cmd.value);
  }
  else
  {
    Serial.println("Invalid servo index.");
  }
}

// Executes a stepper command
void executeStepperCommand(command cmd)
{
  if (cmd.index >= 0 && (unsigned)cmd.index < steppers_count)
  {
    steppers[cmd.index].moveTo(cmd.value);
  }
  else
  {
    Serial.println("Invalid stepper index.");
  }
}

// Handle all commands in an input string
void handleCommands(String input)
{
  int startIndex = 0;
  int endIndex = input.indexOf(';');

  while (endIndex != -1)
  {
    String commandString = input.substring(startIndex, endIndex);
    Serial.println(commandString);
    command cmd = stringToCommand(commandString);

    if (cmd.index != -1 && cmd.value != -1)
    {
      switch (cmd.type)
      {
      case 's':
        executeServoCommand(cmd);
        break;
      case 'm':
        executeStepperCommand(cmd);
        break;
      default:
        Serial.println("Invalid command type.");
        break;
      }
    }

    startIndex = endIndex + 1;
    endIndex = input.indexOf(';', startIndex);
  }
}

void setup()
{
  setupSteppers();
  setupServos();

  Serial.begin(115200);   // Initialize the Serial communication at a baud rate of 115200
  Serial.setTimeout(100); // Set the timeout for the Serial input (in milliseconds)
  Serial.println("Initializing...");

  pwm.begin();
  pwm.setOscillatorFrequency(27000000);
  pwm.setPWMFreq(SERVO_FREQ); // Analog servos run at ~50 Hz updates
}

void loop()
{
  if (Serial.available())
  {
    String incomingData = Serial.readString(); // Read the incoming data
    if (incomingData.length() != 0)
    {
      handleCommands(incomingData);
    }
  }

  runAllSteppers();
}
