// Prueba del disco de la tolva (28BYJ-48 + ULN2003) en ESP32-S3.
// Avanza un bolsillo (512 pasos en medio paso) cada segundo.
// Serial: 'f' un bolsillo adelante, 'b' atras, 's' stop/continuar.
#include <Arduino.h>
#include <AccelStepper.h>

constexpr int IN1 = 4, IN2 = 5, IN3 = 6, IN4 = 7;
constexpr long PASOS_BOLSILLO = 512;  // 4096 pasos/vuelta / 8 bolsillos

// Orden IN1, IN3, IN2, IN4 (si se pone IN1..IN4 en orden, el motor vibra).
AccelStepper motor(AccelStepper::HALF4WIRE, IN1, IN3, IN2, IN4);
bool auto_avance = true;
unsigned long t_espera = 0;

void setup() {
  Serial.begin(115200);
  motor.setMaxSpeed(1100);
  motor.setAcceleration(2000);
  Serial.println("Prueba tolva: f/b = 1 bolsillo, s = auto on/off");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'f') motor.move(PASOS_BOLSILLO);
    if (c == 'b') motor.move(-PASOS_BOLSILLO);
    if (c == 's') auto_avance = !auto_avance;
  }
  if (motor.distanceToGo() == 0) {
    motor.disableOutputs();  // evita calentar las bobinas
    if (auto_avance && millis() - t_espera > 1000) {
      motor.move(PASOS_BOLSILLO);
      t_espera = millis();
    }
  }
  motor.run();
}
