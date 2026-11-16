#include <Servo.h>

// SG90 signal connections: Base D9, Shoulder D10, L-Hand D11, R-Hand D6
const byte SERVO_PINS[4] = {9, 10, 11, 6};
const byte SERVO_COUNT = 4;
const byte SERVO_MIN_ANGLES[SERVO_COUNT] = {1, 0, 0, 0};
const byte SERVO_MAX_ANGLES[SERVO_COUNT] = {180, 90, 90, 90};

Servo servos[SERVO_COUNT];
int currentAngles[SERVO_COUNT] = {90, 45, 0, 90};

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(50);

  for (byte i = 0; i < SERVO_COUNT; i++) {
    servos[i].attach(SERVO_PINS[i]);
    servos[i].write(currentAngles[i]);
  }

  Serial.println("ROBOT_ARM_READY");
}

void loop() {
  if (!Serial.available()) return;

  String command = Serial.readStringUntil('\n');
  command.trim();

  // Serial protocol examples: S1:90, S2:45, S3:0, and S4:90
  if (command.length() < 4 || command.charAt(0) != 'S') return;

  int colon = command.indexOf(':');
  if (colon < 2) return;

  int servoNumber = command.substring(1, colon).toInt();
  int angle = command.substring(colon + 1).toInt();

  if (servoNumber < 1 || servoNumber > SERVO_COUNT) return;

  byte index = servoNumber - 1;
  if (angle < SERVO_MIN_ANGLES[index] || angle > SERVO_MAX_ANGLES[index]) return;

  currentAngles[index] = angle;
  servos[index].write(angle);

  Serial.print("OK S");
  Serial.print(servoNumber);
  Serial.print(":");
  Serial.println(angle);
}
