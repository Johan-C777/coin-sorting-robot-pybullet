// Implementación de BusServos sin hardware, para probar el secuenciador en el PC.
// Guarda la última pose comandada en lugar de escribir PWM.
#include "../esp32_brazo/servo_bus.h"

bool BusServos::iniciar() { listo_ = true; return true; }

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
  const float paso = VEL_SERVO_MAX * dt;
  for (uint8_t i = 0; i < N_CANALES; i++) {
    const float error = objetivo_[i] - actual_[i];
    if (error > paso) actual_[i] += paso;
    else if (error < -paso) actual_[i] -= paso;
    else actual_[i] = objetivo_[i];
  }
}

void BusServos::habilitar(bool activo) { habilitado_ = activo; }
void BusServos::escribir() {}
void BusServos::trama(char *destino, uint8_t capacidad) const {
  Protocolo::armarTrama(q_, pinzaMm_, destino, capacidad);
}
