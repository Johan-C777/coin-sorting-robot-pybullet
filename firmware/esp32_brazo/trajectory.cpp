#include "trajectory.h"

#include <math.h>

namespace Trayectoria {

float quintico(float tau) {
  if (tau <= 0.0f) return 0.0f;
  if (tau >= 1.0f) return 1.0f;
  return tau * tau * tau * (10.0f + tau * (-15.0f + 6.0f * tau));
}

float velocidadPico(float delta, float T) { return 1.875f * fabsf(delta) / T; }

float aceleracionPico(float delta, float T) { return 5.7735f * fabsf(delta) / (T * T); }

float duracionArticular(const float q0[N_JUNTAS], const float q1[N_JUNTAS], float vel) {
  float dq = 0.0f;
  for (uint8_t i = 0; i < N_JUNTAS; i++) {
    const float d = fabsf(q1[i] - q0[i]);
    if (d > dq) dq = d;
  }
  const float T = dq / (VEL_ARTICULAR * vel);
  return T > T_MIN_ARTICULAR ? T : T_MIN_ARTICULAR;
}

float duracionLineal(const float p0[3], const float p1[3], float vel) {
  const float dx = p1[0] - p0[0], dy = p1[1] - p0[1], dz = p1[2] - p0[2];
  const float T = sqrtf(dx * dx + dy * dy + dz * dz) / (VEL_LINEAL * vel);
  return T > T_MIN_LINEAL ? T : T_MIN_LINEAL;
}

void interpolarArticular(const float q0[N_JUNTAS], const float q1[N_JUNTAS],
                         float s, float salida[N_JUNTAS]) {
  for (uint8_t i = 0; i < N_JUNTAS; i++) salida[i] = q0[i] + (q1[i] - q0[i]) * s;
}

void interpolarLineal(const float p0[3], const float p1[3], float s, float salida[3]) {
  for (uint8_t i = 0; i < 3; i++) salida[i] = p0[i] + (p1[i] - p0[i]) * s;
}

}  // namespace Trayectoria
