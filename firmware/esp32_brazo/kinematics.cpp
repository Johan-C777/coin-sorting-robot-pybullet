#include "kinematics.h"

#include <math.h>

namespace {
constexpr float GRADOS = 180.0f / (float)M_PI;
constexpr float RAD = (float)M_PI / 180.0f;

float envolver(float a) {
  while (a > 180.0f) a -= 360.0f;
  while (a < -180.0f) a += 360.0f;
  return a;
}
}  // namespace

namespace Cinematica {

void fk(const float q[N_JUNTAS], float &x, float &y, float &z, float &phi) {
  const float a2 = q[1] * RAD;
  const float a3 = a2 + q[2] * RAD;
  const float a4 = a3 + q[3] * RAD;
  const float rho = L1 * cosf(a2) + L2 * cosf(a3) + L3 * cosf(a4);
  x = rho * cosf(q[0] * RAD);
  y = rho * sinf(q[0] * RAD);
  z = D1 + L1 * sinf(a2) + L2 * sinf(a3) + L3 * sinf(a4);
  phi = a4 * GRADOS;
}

ResultadoIK ik(float x, float y, float z, float phi, float psi, float yawPrevio) {
  ResultadoIK r;
  r.ok = false;
  r.junta = -1;
  for (uint8_t i = 0; i < N_JUNTAS; i++) r.q[i] = 0.0f;

  const float radio = sqrtf(x * x + y * y);
  const float t1 = (radio < 1e-4f) ? yawPrevio : atan2f(y, x) * GRADOS;
  const float p = phi * RAD;
  const float rw = radio - L3 * cosf(p);            // centro de muñeca
  const float hw = z - D1 - L3 * sinf(p);
  const float d = (rw * rw + hw * hw - L1 * L1 - L2 * L2) / (2.0f * L1 * L2);
  if (d > 1.0f || d < -1.0f) return r;              // fuera del alcance

  const float t3 = -acosf(d);                       // codo arriba
  const float t2 = atan2f(hw, rw) - atan2f(L2 * sinf(t3), L1 + L2 * cosf(t3));
  r.q[0] = t1;
  r.q[1] = t2 * GRADOS;
  r.q[2] = t3 * GRADOS;
  r.q[3] = envolver(phi - r.q[1] - r.q[2]);
  r.q[4] = psi;

  for (uint8_t i = 0; i < N_JUNTAS; i++) {
    if (r.q[i] < Q_MIN[i] - 0.05f || r.q[i] > Q_MAX[i] + 0.05f) {
      r.junta = (int8_t)i;
      return r;
    }
    if (r.q[i] < Q_MIN[i]) r.q[i] = Q_MIN[i];
    if (r.q[i] > Q_MAX[i]) r.q[i] = Q_MAX[i];
  }
  r.ok = true;
  return r;
}

void posePuesto(float yaw, float z, float &x, float &y) {
  x = R_ARCO * cosf(yaw * RAD);
  y = R_ARCO * sinf(yaw * RAD);
  (void)z;
}

float detJacobiano(const float q[N_JUNTAS]) {
  return L1 * L2 * sinf(q[2] * RAD);
}

}  // namespace Cinematica
