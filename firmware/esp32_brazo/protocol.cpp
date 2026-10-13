#include "protocol.h"

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

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

uint8_t leerVasos(const char *linea, Vaso vasos[N_PUESTOS]) {
  if (linea == nullptr || strncmp(linea, "VASOS:", 6) != 0) return 0;
  const char *p = linea + 6;
  uint8_t leidos = 0;
  while (leidos < N_PUESTOS && *p) {
    char *fin = nullptr;
    const long den = strtol(p, &fin, 10);
    if (fin == p || *fin != 'x') return 0;
    p = fin + 1;
    const long n = strtol(p, &fin, 10);
    if (fin == p || n < 0 || n > 255) return 0;
    p = fin;
    long antiguas = 0;
    if (*p == 'a') {
      antiguas = strtol(p + 1, &fin, 10);
      if (fin == p + 1 || antiguas < 0 || antiguas > n) return 0;
      p = fin;
    }
    Vaso &v = vasos[leidos++];
    v.denominacion = (uint16_t)den;
    v.monedas = (uint8_t)n;
    v.antiguas = (uint8_t)antiguas;
    v.zona = ZONA_ENTRADA;
    v.puesto = (int8_t)(leidos - 1);
    if (*p == ',') p++;
    else if (*p != '\0') return 0;
  }
  return leidos;
}

uint8_t criterioDeTexto(const char *t) {
  if (t == nullptr) return POR_VALOR;
  if (strncmp(t, "den", 3) == 0) return POR_DENOMINACION;
  if (strncmp(t, "can", 3) == 0) return POR_CANTIDAD;
  if (strncmp(t, "pes", 3) == 0) return POR_PESO;
  if (strncmp(t, "ant", 3) == 0) return POR_ANTIGUAS;
  return POR_VALOR;
}

}  // namespace Protocolo
