#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PWMServoDriver.h>
#include <AccelStepper.h>
#include "Steppers.h"
#include "Servos.h"
#include "Sensors.h"

// The absolute maximum microseconds for a servo pulse.
// This is a backup safety limit to avoid breaking servos.
#define MAX_SERVO_MICROS 3000
#define MIN_SERVO_MICROS 0
// Constants
#define SERVO_FREQ 50 // Analog servos run at ~50 Hz updates

// Initialize PWM servo driver
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Enumeration for command types
enum class CommandType : char
{
    ShieldServo = 's',
    Stepper = 't',
    Sensor = 'i',
    LooseServo = 'l',
    Unknown = 'X'
};

// Structure to represent a parsed command
struct Command
{
    CommandType type;
    int index;
    long value;   // For set commands
    bool isQuery; // True for query commands like 'i2?'

    Command() : type(CommandType::Unknown), index(-1), value(0), isQuery(false) {}
};

// Example commands:
// "s0=1500;" - Set shield servo 0 to 1500 microseconds
// "t0=100;" - Move stepper 0 to position 100
// "i2?;" - Query sensor 2
// "l1=2000;" - Set loose servo 1 to 2000 microseconds (of 50Hz PWM)
// "s2=1000;t1=200;i0?;" - Set shield servo 2 to 1000, move stepper 1 to 200, query sensor 0

// Function Prototypes
void runAllSteppers();
bool parseCommand(const String &input, Command &cmd);
void processCommands(const String &input);
void executeCommand(const Command &cmd);

void setup()
{
    // Initialize Serial communication
    Serial.begin(115200);
    Serial.setTimeout(100); // Set timeout for Serial.readString()
    Serial.println("Initializing...");

    // Initialize PWM servo driver
    pwm.begin();
    pwm.setOscillatorFrequency(27000000);
    pwm.setPWMFreq(SERVO_FREQ);

    // Initialize peripherals
    setupSteppers();
    setupServos();
    setupSensors();
}

void loop()
{
    // Check if data is available on Serial
    if (Serial.available())
    {
        String incomingData = Serial.readString();
        incomingData.trim(); // Remove leading and trailing whitespace

        // Serial.println(incomingData);

        if (incomingData.length() > 0)
        {
            processCommands(incomingData);
        }
    }

    // Continuously run steppers
    runAllSteppers();
}

/**
 * @brief Processes all commands in the input string separated by ';'
 * @param input String containing one or multiple commands
 */
void processCommands(const String &input)
{
    int start = 0;
    int end = input.indexOf(';');

    while (end != -1)
    {
        runAllSteppers(); // Ensure steppers are updated regularly

        String commandStr = input.substring(start, end);
        commandStr.trim(); // Clean up the command string

        if (commandStr.length() > 0)
        {
            Command cmd;
            if (parseCommand(commandStr, cmd))
            {
                executeCommand(cmd);
            }
        }

        start = end + 1;
        end = input.indexOf(';', start);
    }
}

/**
 * @brief Parses a single command string into a Command object
 * @param input The command string (e.g., "s0=1500" or "i2?")
 * @param cmd Reference to a Command object to populate
 * @return True if parsing is successful, else False
 */
bool parseCommand(const String &input, Command &cmd)
{
    if (input.length() < 2)
    {
        Serial.println("!Error: Command too short.");
        return false;
    }

    // Determine command type
    char typeChar = input.charAt(0);
    cmd.type = static_cast<CommandType>(typeChar);

    // Handle query commands (ending with '?')
    int queryPos = input.indexOf('?');
    if (queryPos != -1)
    {
        String indexStr = input.substring(1, queryPos);
        cmd.index = indexStr.toInt();
        cmd.isQuery = true;
        return true;
    }

    // Handle set commands (containing '=')
    int equalsPos = input.indexOf('=');
    if (equalsPos == -1)
    {
        Serial.println("!Error: Invalid command format. Missing '=' or '?'");
        return false;
    }

    String indexStr = input.substring(1, equalsPos);
    String valueStr = input.substring(equalsPos + 1);

    cmd.index = indexStr.toInt();
    cmd.value = valueStr.toInt();
    cmd.isQuery = false;

    return true;
}

/**
 * @brief Executes a parsed Command
 * @param cmd The Command to execute
 */
void executeCommand(const Command &cmd)
{
    switch (cmd.type)
    {
    case CommandType::ShieldServo:
        if (cmd.index >= 0 && cmd.index < 16)
        {
            int servoValue = constrain(cmd.value, 0, MAX_SERVO_MICROS);
            pwm.writeMicroseconds(cmd.index, servoValue);
        }
        else
        {
            Serial.println("!Error: Invalid shield servo index.");
        }
        break;

    case CommandType::Stepper:
        if (cmd.index >= 0 && cmd.index < steppersCount)
        {
            steppers[cmd.index].moveTo(cmd.value);
        }
        else
        {
            Serial.println("!Error: Invalid stepper index.");
        }
        break;

    case CommandType::Sensor:
        if (cmd.isQuery)
        {
            if (cmd.index >= 0 && cmd.index < sensorsCount)
            {
                int sensorValue = sensors[cmd.index]->read();
                // Format: "i{index}={value}"
                // Example: "i2=1000"
                Serial.print("i");
                Serial.print(cmd.index);
                Serial.print("=");
                Serial.println(sensorValue);
            }
            else
            {
                Serial.println("!{Error: Invalid sensor index.}");
            }
        }
        else
        {
            Serial.println("!{Error: Sensor command should be a query (e.g., 'i2?').}");
        }
        break;

    case CommandType::LooseServo:
        if (cmd.index >= 0 && cmd.index < looseServosCount)
        {
            int servoValue = constrain(cmd.value, 0, MAX_SERVO_MICROS);
            looseServos[cmd.index].writeMicroseconds(servoValue);
        }
        else
        {
            Serial.println("!{Error: Invalid loose servo index.}");
        }
        break;

    default:
        Serial.println("!{Error: Unknown command type.}");
        break;
    }
}

/**
 * @brief Runs all steppers that need stepping. Must be called as frequently as possible!
 */
void runAllSteppers()
{
    // static unsigned long lastStepTime = 0;
    // unsigned long currentTime = micros();
    // unsigned long timeElapsed = currentTime - lastStepTime;
    // lastStepTime = currentTime;

    // Optional: Debugging lag in stepper updates
    // if (timeElapsed > 500) {
    //     Serial.printf("Stepper update lag: %lu microseconds\n", timeElapsed);
    // }

    for (int i = 0; i < steppersCount; ++i)
    {
        steppers[i].run();
    }
}
