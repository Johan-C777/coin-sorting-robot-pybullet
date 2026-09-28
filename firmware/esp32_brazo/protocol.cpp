#include "protocol.h"

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

namespace {
int16_t redondear(float v) { return (int16_t)lroundf(v); }
}  // namespace

namespace Protocolo {

void angulosServo(const float q[N_JUNTAS], float pinzaMm, int16_t salida[N_CANALES]) {
  salida[0] = redondear(q[0] + 90.0f);
  salida[1] = redondear(q[1]);
  salida[2] = redondear(-q[2]);            // montaje invertido
  salida[3] = redondear(q[3] + 120.0f);
  salida[4] = redondear(q[4] + 90.0f);
  salida[5] = redondear(pinzaMm / PINZA_MAX_MM * 90.0f);
}

uint16_t microsegundos(float anguloServo) {
  if (anguloServo < 0.0f) anguloServo = 0.0f;
  if (anguloServo > 180.0f) anguloServo = 180.0f;
  return (uint16_t)lroundf(PWM_MIN_US + anguloServo / 180.0f * (PWM_MAX_US - PWM_MIN_US));
}

uint8_t armarTrama(const float q[N_JUNTAS], float pinzaMm, char *destino, uint8_t capacidad) {
  int16_t s[N_CANALES];
  angulosServo(q, pinzaMm, s);
  const int n = snprintf(destino, capacidad, "S:%d,%d,%d,%d,%d,%d",
                         s[0], s[1], s[2], s[3], s[4], s[5]);
  return (n < 0) ? 0 : (uint8_t)n;
}

bool leerTrama(const char *linea, int16_t salida[N_CANALES]) {
  if (linea == nullptr || linea[0] != 'S' || linea[1] != ':') return false;
  const char *p = linea + 2;
  for (uint8_t i = 0; i < N_CANALES; i++) {
    if (*p == '\0') return false;
    char *fin = nullptr;
    const long v = strtol(p, &fin, 10);
    if (fin == p) return false;
    salida[i] = (int16_t)v;
    p = (*fin == ',') ? fin + 1 : fin;
  }
  return true;
}

}  // namespace Protocolo
