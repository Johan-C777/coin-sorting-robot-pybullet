#include "conteo.h"

#include <stdio.h>

void Conteo::reiniciar() {
  for (uint8_t i = 0; i < N_ESTACIONES; i++) n_[i] = 0;
}

void Conteo::sumar(uint8_t estacion, uint16_t n) {
  if (estacion < N_ESTACIONES) n_[estacion] += n;
}

uint16_t Conteo::monedasEstacion(uint8_t estacion) const {
  return estacion < N_ESTACIONES ? n_[estacion] : 0;
}

uint16_t Conteo::monedas(uint8_t vaso) const {
  uint16_t s = 0;
  for (uint8_t e = 0; e < N_ESTACIONES; e++)
    if (VASO_DE_ESTACION[e] == vaso) s += n_[e];
  return s;
}

uint16_t Conteo::antiguas(uint8_t vaso) const {
  uint16_t s = 0;
  for (uint8_t e = 0; e < N_ESTACIONES; e++)
    if (VASO_DE_ESTACION[e] == vaso && FAMILIA[e] == ANTIGUA) s += n_[e];
  return s;
}

uint32_t Conteo::valor(uint8_t vaso) const {
  return vaso < N_VASOS ? (uint32_t)DENOMINACION_VASO[vaso] * monedas(vaso) : 0;
}

float Conteo::pesoG(uint8_t vaso) const {
  if (vaso >= N_VASOS || monedas(vaso) == 0) return 0.0f;
  float m = MASA_VASO_G;
  for (uint8_t e = 0; e < N_ESTACIONES; e++)
    if (VASO_DE_ESTACION[e] == vaso) m += n_[e] * MASA_MONEDA_G[e];
  return m;
}

uint16_t Conteo::monedasTotal() const {
  uint16_t s = 0;
  for (uint8_t e = 0; e < N_ESTACIONES; e++) s += n_[e];
  return s;
}

uint16_t Conteo::antiguasTotal() const {
  uint16_t s = 0;
  for (uint8_t v = 0; v < N_VASOS; v++) s += antiguas(v);
  return s;
}

uint32_t Conteo::valorTotal() const {
  uint32_t s = 0;
  for (uint8_t v = 0; v < N_VASOS; v++) s += valor(v);
  return s;
}

float Conteo::pesoTotal() const {
  float s = 0.0f;
  for (uint8_t v = 0; v < N_VASOS; v++) s += pesoG(v);
  return s;
}

bool Conteo::vasoLleno() const {
  for (uint8_t v = 0; v < N_VASOS; v++)
    if (monedas(v) >= MONEDAS_POR_VASO) return true;
  return false;
}

uint8_t Conteo::trama(char *destino, uint8_t capacidad) const {
  int n = snprintf(destino, capacidad, "VASOS:");
  for (uint8_t v = 0; v < N_VASOS && n > 0 && (uint8_t)n < capacidad; v++) {
    n += snprintf(destino + n, capacidad - n, "%s%ux%u",
                  v ? "," : "", DENOMINACION_VASO[v], monedas(v));
    if (antiguas(v) && (uint8_t)n < capacidad)
      n += snprintf(destino + n, capacidad - n, "a%u", antiguas(v));
  }
  return (n < 0) ? 0 : (uint8_t)n;
}

size_t Conteo::json(char *destino, size_t capacidad) const {
  int n = snprintf(destino, capacidad, "{\"entrada\":[");
  for (uint8_t v = 0; v < N_VASOS && n > 0 && (size_t)n < capacidad; v++)
    n += snprintf(destino + n, capacidad - n,
                  "%s{\"puesto\":%u,\"den\":%u,\"familia\":\"%s\",\"n\":%u,\"antiguas\":%u,"
                  "\"valor\":%lu,\"peso_g\":%.1f}",
                  v ? "," : "", v + 1, DENOMINACION_VASO[v],
                  antiguas(v) && antiguas(v) == monedas(v) ? "antigua" : "nueva", monedas(v), antiguas(v),
                  (unsigned long)valor(v), pesoG(v));
  if (n > 0 && (size_t)n < capacidad)
    n += snprintf(destino + n, capacidad - n,
                  "],\"totales\":{\"monedas\":%u,\"antiguas\":%u,\"valor\":%lu,"
                  "\"peso_g\":%.1f}}",
                  monedasTotal(), antiguasTotal(), (unsigned long)valorTotal(), pesoTotal());
  return (n < 0) ? 0 : (size_t)n;
}
