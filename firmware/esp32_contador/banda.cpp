#include "banda.h"

#include <Arduino.h>

void Banda::iniciar() {
  pinMode(PIN_BANDA_A, OUTPUT);
  pinMode(PIN_BANDA_B, OUTPUT);
  ledcSetup(CANAL_BANDA, 1000, 8);
  ledcAttachPin(PIN_BANDA_PWM, CANAL_BANDA);
  detener();
}

void Banda::avanzar(float velocidad) {
  if (velocidad <= 0.01f) { detener(); return; }
  if (velocidad > 1.0f) velocidad = 1.0f;
  digitalWrite(PIN_BANDA_A, HIGH);
  digitalWrite(PIN_BANDA_B, LOW);
  const uint16_t pwm = BANDA_PWM_MIN + (uint16_t)((255 - BANDA_PWM_MIN) * velocidad);
  ledcWrite(CANAL_BANDA, pwm);
  marcha_ = true;
}

void Banda::detener() {
  ledcWrite(CANAL_BANDA, 0);
  digitalWrite(PIN_BANDA_A, LOW);
  digitalWrite(PIN_BANDA_B, LOW);
  marcha_ = false;
}
