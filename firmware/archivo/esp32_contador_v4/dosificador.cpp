#include "dosificador.h"

#include <Arduino.h>

namespace {
// medio paso del 28BYJ-48: IN1..IN4
const uint8_t SECUENCIA[8] = {0b0001, 0b0011, 0b0010, 0b0110,
                              0b0100, 0b1100, 0b1000, 0b1001};
constexpr float PASOS_POR_MONEDA = (float)PASOS_VUELTA_28BYJ / CAVIDADES_DISCO;  // ≈1019
}  // namespace

void Dosificador::bobinas(uint8_t fase) {
  const uint8_t b = fase == 0xFF ? 0 : SECUENCIA[fase & 7];
  for (uint8_t i = 0; i < 4; i++) digitalWrite(PIN_TOLVA[i], (b >> i) & 1);
}

void Dosificador::iniciar() {
#ifdef TOLVA_SG90_CONTINUO
  ledcSetup(CANAL_TOLVA, 50, 16);
  ledcAttachPin(PIN_TOLVA_SG90, CANAL_TOLVA);
  ledcWrite(CANAL_TOLVA, (uint32_t)(TOLVA_SG90_PARADO_US / 20000.0f * 65535.0f));
#else
  for (uint8_t i = 0; i < 4; i++) pinMode(PIN_TOLVA[i], OUTPUT);
  bobinas(0xFF);
#endif
}

void Dosificador::ritmo(float monedasPorSegundo) {
  if (monedasPorSegundo < 0) monedasPorSegundo = 0;
  if (monedasPorSegundo > RITMO_MAX) monedasPorSegundo = RITMO_MAX;
  ritmo_ = monedasPorSegundo;
#ifdef TOLVA_SG90_CONTINUO
  // rpm = ritmo * 60 / cavidades; el neutro y la ganancia se calibran en banco
  const float rpm = ritmo_ * 60.0f / CAVIDADES_DISCO;
  const uint16_t us = TOLVA_SG90_PARADO_US + SENTIDO_TOLVA * (int16_t)(rpm * TOLVA_SG90_US_POR_RPM);
  ledcWrite(CANAL_TOLVA, (uint32_t)(us / 20000.0f * 65535.0f));
#else
  periodoPasoUs_ = activo() ? (uint32_t)(1e6f / (ritmo_ * PASOS_POR_MONEDA)) : 0;
  if (!activo()) bobinas(0xFF);                  // sin corriente en reposo
#endif
}

void Dosificador::actualizar() {
#ifndef TOLVA_SG90_CONTINUO
  if (!activo()) return;
  const uint32_t ahora = micros();
  if (ahora - ultimoPasoUs_ < periodoPasoUs_) return;
  ultimoPasoUs_ = ahora;
  fase_ = (uint8_t)(fase_ + SENTIDO_TOLVA) & 7;
  bobinas(fase_);
#endif
}
