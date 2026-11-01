#pragma once
// Parámetros que se ajustan con monedas reales. Los valores de fábrica están en
// include/calibracion.h; los calibrados se guardan en NVS (flash) desde la consola.

namespace clasif {

struct Calibracion {
  // Geometría de la pista L01 (scripts/generar_v5.py: B1 = 105, SEP = 24, H_BAR = 10)
  float sep_barreras_mm;   // distancia entre los dos haces a lo largo de la pista
  float h_haz_mm;          // altura del haz sobre la repisa (la moneda rueda sobre ella)
  float ancho_haz_mm;      // ancho efectivo del haz: se resta de la cuerda medida
  // Decisión
  float tolerancia_max_mm; // error máximo aceptado en diámetro
  float margen_vecino_mm;  // se resta a la mitad de la distancia al vecino más cercano
  float umbral_dorado;     // (R+G)/2B por encima = dorada
  // Física plausible (descarta lecturas con ruido o dos monedas pegadas)
  float v_min_mm_s, v_max_mm_s;
  float a_min_mm_s2, a_max_mm_s2;
};

}  // namespace clasif
