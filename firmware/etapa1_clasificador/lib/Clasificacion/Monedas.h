#pragma once
// Catálogo de monedas colombianas que clasifica la etapa 1 (Banco de la República).
// Fuente única para el firmware; la prueba software/tests/test_firmware_clasificador.py
// verifica que coincide con software/brazo/monedas.py.
//
// El índice de TIPOS es el número de vaso dentro del cartucho (C01 x 3), en el orden
// en que la banda los pasa bajo el embudo. VASO_RECHAZO = rampa C02.
#include <stdint.h>

namespace monedas {

enum class Familia : uint8_t { Nueva, Antigua };

struct Tipo {
  const char *codigo;   // N = nueva (2012), A = antigua (1989-1996)
  const char *nombre;
  uint16_t valor;       // COP
  Familia familia;
  float diametro_mm;    // oficial
  float espesor_mm;     // referencia (no interviene en la decisión)
  float masa_g;
};

constexpr uint8_t N_VASOS = 9;
constexpr int8_t VASO_RECHAZO = -1;

constexpr Tipo TIPOS[N_VASOS] = {
    {"N50", "$50 nueva", 50, Familia::Nueva, 17.00f, 1.30f, 2.00f},
    {"N100", "$100 nueva", 100, Familia::Nueva, 20.30f, 1.50f, 3.34f},
    {"A50", "$50 antigua", 50, Familia::Antigua, 21.50f, 1.40f, 4.50f},
    {"N200", "$200 nueva", 200, Familia::Nueva, 22.40f, 1.70f, 4.61f},
    {"A100", "$100 antigua", 100, Familia::Antigua, 23.00f, 1.55f, 5.31f},
    {"A500", "$500 antigua", 500, Familia::Antigua, 23.70f, 2.05f, 7.14f},
    {"N500", "$500 nueva", 500, Familia::Nueva, 23.70f, 2.20f, 7.14f},
    {"A200", "$200 antigua", 200, Familia::Antigua, 24.40f, 1.70f, 7.08f},
    {"N1000", "$1.000 nueva", 1000, Familia::Nueva, 26.70f, 2.30f, 9.95f},
};

constexpr uint8_t V_N50 = 0, V_N100 = 1, V_A50 = 2, V_N200 = 3, V_A100 = 4, V_A500 = 5, V_N500 = 6,
                  V_A200 = 7, V_N1000 = 8;

// $1.000 de 1996 (fuera de circulación): 21,67 mm, a 0,17 mm de la $50 antigua.
// Se distingue por color (dorada, CuAlNi) y va a rechazo.
constexpr float DIAMETRO_A1000_MM = 21.67f;

// Capacidad útil de un vaso V01 (Ø34 x 60) con la moneda más gruesa ($1.000 nueva).
constexpr uint16_t CAPACIDAD_VASO = 26;

}  // namespace monedas
