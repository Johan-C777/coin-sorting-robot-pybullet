#include "conteo.h"

#include <stdio.h>

void Conteo::reiniciar() {
  for (uint8_t i = 0; i < N_CANALES; i++) n_[i] = 0;
}

void Conteo::sumar(uint8_t canal, uint16_t n) {
  if (canal < N_CANALES) n_[canal] += n;
}

uint16_t Conteo::monedas(uint8_t canal) const {
  return canal < N_CANALES ? n_[canal] : 0;
}

uint32_t Conteo::valor(uint8_t canal) const {
  return canal < N_CANALES ? (uint32_t)DENOMINACION[canal] * n_[canal] : 0;
}

float Conteo::pesoG(uint8_t canal) const {
  if (canal >= N_CANALES) return 0.0f;
  return n_[canal] ? MASA_VASO_G + n_[canal] * MASA_MONEDA_G[canal] : 0.0f;
}

uint16_t Conteo::monedasTotal() const {
  uint16_t s = 0;
  for (uint8_t i = 0; i < N_CANALES; i++) s += n_[i];
  return s;
}

uint32_t Conteo::valorTotal() const {
  uint32_t s = 0;
  for (uint8_t i = 0; i < N_CANALES; i++) s += valor(i);
  return s;
}

float Conteo::pesoTotal() const {
  float s = 0.0f;
  for (uint8_t i = 0; i < N_CANALES; i++) s += pesoG(i);
  return s;
}

bool Conteo::vasoLleno() const {
  for (uint8_t i = 0; i < N_CANALES; i++)
    if (n_[i] >= MONEDAS_POR_VASO) return true;
  return false;
}

uint8_t Conteo::trama(char *destino, uint8_t capacidad) const {
  int n = snprintf(destino, capacidad, "VASOS:");
  for (uint8_t i = 0; i < N_CANALES && n > 0 && (uint8_t)n < capacidad; i++)
    n += snprintf(destino + n, capacidad - n, "%s%ux%u",
                  i ? "," : "", DENOMINACION[i], n_[i]);
  return (n < 0) ? 0 : (uint8_t)n;
}

size_t Conteo::json(char *destino, size_t capacidad) const {
  int n = snprintf(destino, capacidad, "{\"entrada\":[");
  for (uint8_t i = 0; i < N_CANALES && n > 0 && (size_t)n < capacidad; i++)
    n += snprintf(destino + n, capacidad - n,
                  "%s{\"puesto\":%u,\"den\":%u,\"n\":%u,\"valor\":%lu,\"peso_g\":%.1f}",
                  i ? "," : "", i + 1, DENOMINACION[i], n_[i],
                  (unsigned long)valor(i), pesoG(i));
  n += snprintf(destino + n, capacidad - n,
                "],\"totales\":{\"monedas\":%u,\"valor\":%lu,\"peso_g\":%.1f}}",
                monedasTotal(), (unsigned long)valorTotal(), pesoTotal());
  return (n < 0) ? 0 : (size_t)n;
}
