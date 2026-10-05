#include "dosificador.h"

#include <Arduino.h>

void Dosificador::escribir(uint16_t us) {
  // LEDC a 50 Hz y 16 bits: el ancho de pulso se traduce a cuentas
  const uint32_t cuentas = (uint32_t)((float)us / 20000.0f * 65535.0f);
  ledcWrite(CANAL_SERVO, cuentas);
}

void Dosificador::iniciar() {
  ledcSetup(CANAL_SERVO, 50, 16);
  ledcAttachPin(PIN_SERVO, CANAL_SERVO);
  escribir(SERVO_CERRADO_US);
}

void Dosificador::ritmo(float monedasPorSegundo) {
  ritmo_ = monedasPorSegundo < 0 ? 0 : monedasPorSegundo;
  proximo_ = millis();
}

void Dosificador::actualizar() {
  const uint32_t ahora = millis();
  if (abierto_ && ahora >= cierra_) {
    escribir(SERVO_CERRADO_US);
    abierto_ = false;
  }
  if (!activo() || abierto_ || ahora < proximo_) return;
  escribir(SERVO_ABIERTO_US);
  abierto_ = true;
  cierra_ = ahora + SERVO_MS_ABIERTO;
  proximo_ = ahora + (uint32_t)(1000.0f / ritmo_);
}
