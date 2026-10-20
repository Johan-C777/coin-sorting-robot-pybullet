#include "bifurcacion.h"

#include <Arduino.h>
#include <Wire.h>

namespace {
constexpr uint8_t TCS_DIR = 0x29;
constexpr uint8_t CMD = 0x80, AUTO_INC = 0x20;
constexpr uint8_t R_ENABLE = 0x00, R_ATIME = 0x01, R_CONTROL = 0x0F, R_ID = 0x12, R_CDATAL = 0x14;
constexpr uint8_t PON = 0x01, AEN = 0x02;
constexpr uint8_t ATIME_2_4MS = 0xFF;          // 1 ciclo de integración = 2,4 ms
constexpr uint8_t GANANCIA_4X = 0x01;
constexpr uint32_t PERIODO_LECTURA_US = 2500;

void escribir(uint8_t reg, uint8_t valor) {
  Wire.beginTransmission(TCS_DIR);
  Wire.write(CMD | reg);
  Wire.write(valor);
  Wire.endTransmission();
}

uint32_t usServo(uint8_t grados) {             // SG90: 0° = 500 µs, 180° = 2400 µs
  const uint32_t us = 500 + (uint32_t)grados * 1900 / 180;
  return us * 65535 / 20000;                   // LEDC a 50 Hz, 16 bits
}
}  // namespace

bool Bifurcacion::iniciar() {
  ledcSetup(CANAL_AGUJA, 50, 16);
  ledcAttachPin(PIN_AGUJA, CANAL_AGUJA);
  aguja(AGUJA_A500_GRADOS);

  Wire.beginTransmission(TCS_DIR);
  Wire.write(CMD | R_ID);
  if (Wire.endTransmission() != 0 || Wire.requestFrom(TCS_DIR, (uint8_t)1) != 1) return ok_ = false;
  const uint8_t id = Wire.read();
  if (id != 0x44 && id != 0x4D) return ok_ = false;   // TCS34725 / TCS34727
  escribir(R_ATIME, ATIME_2_4MS);
  escribir(R_CONTROL, GANANCIA_4X);
  escribir(R_ENABLE, PON);
  delay(3);
  escribir(R_ENABLE, PON | AEN);
  return ok_ = true;
}

bool Bifurcacion::leer(LecturaColor &l) {
  Wire.beginTransmission(TCS_DIR);
  Wire.write(CMD | AUTO_INC | R_CDATAL);
  if (Wire.endTransmission(false) != 0 || Wire.requestFrom(TCS_DIR, (uint8_t)8) != 8) return false;
  uint16_t v[4];
  for (uint8_t i = 0; i < 4; i++) {
    const uint8_t bajo = Wire.read();          // orden de lectura explícito
    v[i] = bajo | (uint16_t)(Wire.read() << 8);
  }
  l = {v[0], v[1], v[2], v[3]};               // C, R, G, B
  return true;
}

void Bifurcacion::aguja(uint8_t grados) { ledcWrite(CANAL_AGUJA, usServo(grados)); }

void Bifurcacion::actualizar() {
  const uint32_t ahora = micros();
  if (abajo_ && (ahora - tAbajo_) / 1000 > AGUJA_RETORNO_MS) {
    aguja(AGUJA_A500_GRADOS);                  // la moneda nunca llegó: posición segura
    abajo_ = false;
  }
  if (!ok_ || ahora - tLectura_ < PERIODO_LECTURA_US) return;
  tLectura_ = ahora;
  LecturaColor l;
  if (!leer(l)) return;
  const Anillo a = clas_.alimentar(l);
  if (a == Anillo::NINGUNO) return;
  ultimo_ = a;
  if (a == Anillo::DORADO) {
    aguja(AGUJA_N500_GRADOS);
    abajo_ = true;
    tAbajo_ = ahora;
  } else {
    aguja(AGUJA_A500_GRADOS);
  }
  Serial.printf("C500:%s,%.2f\n", a == Anillo::DORADO ? "dorado" : "plateado", clas_.razon());
}

void Bifurcacion::monedaContada(int8_t estacion) {
  if (estacion == ESTACION_N500 && abajo_) {
    aguja(AGUJA_A500_GRADOS);
    abajo_ = false;
  }
}
