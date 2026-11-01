#pragma once
// Medición del diámetro por tiempo de vuelo entre dos barreras IR y decisión del vaso.
// Código portable (sin Arduino): se compila igual en el ESP32-S3 y en el PC (pio test -e native).
//
// Modelo (el mismo de sim/mujoco/rodar.py, error simulado 0,03 mm):
//   La moneda rueda de canto con aceleración constante a (MRUA). El haz está a una altura h
//   sobre la repisa, así que la moneda lo tapa mientras recorre la CUERDA c = 2·sqrt(h·(D − h)).
//   Con los cuatro instantes (entra/sale en B1 y B2) se resuelven v0, a y c:
//     v0·T        + a·T²/2        = L        (borde delantero de B1 a B2)
//     v0·τ1       + a·τ1²/2  − c  = 0        (la moneda tapa B1 durante τ1)
//     v0·(T+τ2)   + a·(T+τ2)²/2 − c = L      (borde trasero sale de B2)
//   y el diámetro es D = h + c²/(4h).
#include <stdint.h>
#include "Calibracion.h"
#include "Monedas.h"

namespace clasif {

enum class Motivo : uint8_t {
  Ok = 0,
  OrdenTiempos,      // los flancos no llegaron en el orden físico posible
  Velocidad,         // fuera de [v_min, v_max]
  Aceleracion,       // fuera de [a_min, a_max]: rebote, dos monedas o ruido
  Cuerda,            // cuerda imposible para la altura del haz
  SinCoincidencia,   // diámetro lejos de todas las monedas
  FueraCirculacion,  // $1.000 de 1996 (diámetro de $50 antigua pero dorada)
  DobleMoneda,       // una segunda moneda entró antes de terminar la medición
  Atasco,            // la moneda no terminó de pasar las barreras a tiempo
};

const char *texto(Motivo m);

struct Tiempos {
  uint32_t ent1_us, sal1_us, ent2_us, sal2_us;  // reloj de micros() / esp_timer
};

struct Medicion {
  Motivo motivo;
  float v0_mm_s;     // velocidad del borde delantero al entrar a B1
  float a_mm_s2;     // aceleración a lo largo de la pista
  float cuerda_mm;   // cuerda corregida (sin el ancho del haz)
  float diametro_mm;
};

struct Decision {
  int8_t vaso;           // 0..8 o monedas::VASO_RECHAZO
  Motivo motivo;
  float error_mm;        // |D − D_nominal| del candidato
  float tolerancia_mm;   // tolerancia del candidato
  bool requiere_color;   // $500 (antigua/nueva) y $50 antigua (descartar $1.000 de 1996)
};

// Conversión cuerda <-> diámetro para una altura de haz dada.
float diametroDesdeCuerda(float cuerda_mm, float h_mm);
float cuerdaDesdeDiametro(float diametro_mm, float h_mm);

// Tiempos -> velocidad, aceleración, cuerda y diámetro.
Medicion medir(const Tiempos &t, const Calibracion &cal);

// Tolerancia propia de cada vaso: min(tol_max, distancia al vecino/2 − margen).
float tolerancia(uint8_t vaso, const Calibracion &cal);

// Diámetro -> vaso (vecino más cercano con tolerancia por clase).
Decision decidirPorDiametro(float diametro_mm, const Calibracion &cal);

// Completa la decisión con la razón de color (R+G)/2B del TCS3200.
Decision decidirConColor(Decision d, float razon, const Calibracion &cal);

}  // namespace clasif
