#pragma once
// Genera los cuatro instantes de las barreras para una moneda que rueda con MRUA.
// Lo comparten las pruebas del clasificador y de la máquina de estados.
#include <math.h>
#include <stdint.h>

#include "Clasificador.h"

namespace sintetico {

// Instante (s) en que el borde delantero ha recorrido x mm desde B1.
inline double instante(double x, double v0, double a) {
  if (fabs(a) < 1e-9) return x / v0;
  return (-v0 + sqrt(v0 * v0 + 2 * a * x)) / a;
}

// D: diámetro real; h: altura del haz; w: ancho del haz; L: separación entre barreras.
inline clasif::Tiempos moneda(double D, double h = 10.0, double w = 0.0, double L = 24.0,
                              double v0 = 300.0, double a = 2450.0, uint32_t t0_us = 1000000) {
  const double c = clasif::cuerdaDesdeDiametro((float)D, (float)h) + w;
  auto us = [&](double x) { return t0_us + (uint32_t)lround(instante(x, v0, a) * 1e6); };
  return {t0_us, us(c), us(L), us(L + c)};
}

}  // namespace sintetico
