#pragma once
// Ajuste de la altura y el ancho efectivos del haz con monedas conocidas.
// Uso (consola): "c<vaso>" + pasar varias monedas de ese tipo, repetir con otros tipos,
// "C" calcula, "g" guarda en NVS. Portable: se prueba en el PC.
//
// Modelo:  c_medida = w + 2·sqrt(h·(D − h))   -> se buscan h y w por mínimos cuadrados
// (barrido fino de h; para cada h, w óptimo es el promedio de los residuos).
#include <stdint.h>
#include "Calibracion.h"

namespace clasif {

class Calibrador {
 public:
  static constexpr uint8_t MAX_MUESTRAS = 96;

  void reiniciar() { n_ = 0; }
  // c_bruta_mm: cuerda SIN restar el ancho del haz; diametro_real_mm: el de la moneda puesta.
  bool agregar(float c_bruta_mm, float diametro_real_mm);
  uint8_t muestras() const { return n_; }
  uint8_t tiposDistintos() const;

  struct Ajuste {
    bool valido;
    float h_mm, ancho_mm;
    float rms_diametro_mm;   // error RMS del diámetro con el ajuste
    float max_diametro_mm;   // peor muestra
  };
  // Requiere >= 6 muestras de >= 2 diámetros distintos.
  Ajuste ajustar(float h_min = 6.0f, float h_max = 14.0f, float paso = 0.005f) const;
  // Aplica el ajuste sobre una calibración existente.
  static void aplicar(const Ajuste &a, Calibracion &cal);

 private:
  float c_[MAX_MUESTRAS] = {};
  float d_[MAX_MUESTRAS] = {};
  uint8_t n_ = 0;
};

}  // namespace clasif
