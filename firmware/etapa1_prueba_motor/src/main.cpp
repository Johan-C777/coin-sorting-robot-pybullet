// Prueba del disco de la tolva (28BYJ-48 + ULN2003) en ESP32-S3.
// Paso completo: 2048 pasos/vuelta, 256 por bolsillo (mas rapido que medio paso).
// Serial: f/b = 1 bolsillo, s = auto on/off, + / - = velocidad +-100 pasos/s.
#include <Arduino.h>
#include <AccelStepper.h>

constexpr int IN1 = 4, IN2 = 5, IN3 = 6, IN4 = 7;
constexpr long PASOS_BOLSILLO = 256;  // 2048 pasos/vuelta / 8 bolsillos

// Orden IN1, IN3, IN2, IN4 (si se pone IN1..IN4 en orden, el motor vibra).
AccelStepper motor(AccelStepper::FULL4WIRE, IN1, IN3, IN2, IN4);
float vel = 700;  // pasos/s; si pierde pasos, baja con '-'
bool auto_avance = true;
unsigned long t_espera = 0;

void aplicarVel() {
  motor.setMaxSpeed(vel);
  motor.setAcceleration(vel * 4);
  Serial.printf("vel=%.0f pasos/s (%.1f rpm)\n", vel, vel * 60 / 2048);
}

void setup() {
  Serial.begin(115200);
  aplicarVel();
  Serial.println("f/b = bolsillo, s = auto, +/- = velocidad");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'f') motor.move(PASOS_BOLSILLO);
    if (c == 'b') motor.move(-PASOS_BOLSILLO);
    if (c == 's') auto_avance = !auto_avance;
    if (c == '+') { vel += 100; aplicarVel(); }
    if (c == '-') { vel = max(100.0f, vel - 100); aplicarVel(); }
  }
  if (motor.distanceToGo() == 0) {
    motor.disableOutputs();  // evita calentar las bobinas
    if (auto_avance && millis() - t_espera > 300) {
      motor.move(PASOS_BOLSILLO);
      t_espera = millis();
    }
  }
  motor.run();
}
