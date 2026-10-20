#pragma once
// Clasificación del anillo de la moneda de $500 a partir de lecturas RGBC del
// TCS34725. Sin Arduino: se prueba en el PC (firmware/tests/test_conteo.cpp).
//
// La moneda rueda de canto frente a la ventana del sensor (ranura en PLA negro).
// Con la ranura vacía el canal C queda en la línea base; al pasar la moneda sube
// y la razón (R+G)/2B separa el anillo dorado (latón/bronce) del plateado (níquel).
#include <stdint.h>

struct LecturaColor {
  uint16_t c, r, g, b;
};

enum class Anillo : uint8_t { NINGUNO = 0, PLATEADO = 1, DORADO = 2 };

class Clasificador500 {
 public:
  // parámetros calibrables en banco (imprimir razon() con monedas conocidas)
  float factorPresencia = 1.6f;   // C > base*factor + margen => hay moneda
  uint16_t margenPresencia = 40;
  float umbralDorado = 1.30f;     // (R+G)/2B por encima => dorado
  uint8_t muestrasDecision = 3;   // a 2,4 ms por lectura: ~7 ms tras ver la moneda

  // Devuelve PLATEADO o DORADO una sola vez por moneda; NINGUNO el resto del tiempo.
  Anillo alimentar(const LecturaColor &l) {
    const bool hay = base_ > 0 && l.c > base_ * factorPresencia + margenPresencia;
    if (!hay) {
      if (presente_) presente_ = false;            // la moneda terminó de pasar
      base_ = base_ <= 0 ? l.c : base_ * 0.95f + l.c * 0.05f;
      n_ = 0;
      suma_ = 0;
      return Anillo::NINGUNO;
    }
    presente_ = true;
    if (n_ == 0xFF) return Anillo::NINGUNO;        // ya se decidió esta moneda
    suma_ += (l.r + l.g) / (2.0f * (l.b ? l.b : 1));
    if (++n_ < muestrasDecision) return Anillo::NINGUNO;
    razon_ = suma_ / n_;
    n_ = 0xFF;
    return razon_ > umbralDorado ? Anillo::DORADO : Anillo::PLATEADO;
  }

  float razon() const { return razon_; }
  float base() const { return base_; }

 private:
  float base_ = 0;
  float suma_ = 0;
  float razon_ = 0;
  uint8_t n_ = 0;
  bool presente_ = false;
};
