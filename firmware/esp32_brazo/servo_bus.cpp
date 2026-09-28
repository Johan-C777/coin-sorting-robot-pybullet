#include "servo_bus.h"

#include <Adafruit_PWMServoDriver.h>
#include <Arduino.h>
#include <Wire.h>

namespace {
Adafruit_PWMServoDriver pca(PCA_DIR);
}

bool BusServos::iniciar() {
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(400000);
  listo_ = pca.begin();
  if (!listo_) return false;
  pca.setOscillatorFrequency(PCA_OSC_HZ);
  pca.setPWMFreq(PWM_FREQ_HZ);
  escribir();
  return true;
}

void BusServos::comandar(const float q[N_JUNTAS], float pinzaMm) {
  for (uint8_t i = 0; i < N_JUNTAS; i++) {
    float v = q[i];
    if (v < Q_MIN[i]) v = Q_MIN[i];
    if (v > Q_MAX[i]) v = Q_MAX[i];
    q_[i] = v;
  }
  if (pinzaMm < 0.0f) pinzaMm = 0.0f;
  if (pinzaMm > PINZA_MAX_MM) pinzaMm = PINZA_MAX_MM;
  pinzaMm_ = pinzaMm;

  int16_t s[N_CANALES];
  Protocolo::angulosServo(q_, pinzaMm_, s);
  for (uint8_t i = 0; i < N_CANALES; i++) objetivo_[i] = (float)s[i];
}

void BusServos::actualizar(float dt) {
  const float paso = VEL_SERVO_MAX * dt;            // rampa: evita tirones
  for (uint8_t i = 0; i < N_CANALES; i++) {
    const float error = objetivo_[i] - actual_[i];
    if (error > paso) actual_[i] += paso;
    else if (error < -paso) actual_[i] -= paso;
    else actual_[i] = objetivo_[i];
  }
  escribir();
}

void BusServos::habilitar(bool activo) {
  habilitado_ = activo;
  if (!listo_) return;
  if (!activo) for (uint8_t i = 0; i < N_CANALES; i++) pca.setPWM(CANAL[i], 0, 0);
  else escribir();
}

void BusServos::escribir() {
  if (!listo_ || !habilitado_) return;
  for (uint8_t i = 0; i < N_CANALES; i++)
    pca.writeMicroseconds(CANAL[i], Protocolo::microsegundos(actual_[i]));
}

void BusServos::trama(char *destino, uint8_t capacidad) const {
  Protocolo::armarTrama(q_, pinzaMm_, destino, capacidad);
}
