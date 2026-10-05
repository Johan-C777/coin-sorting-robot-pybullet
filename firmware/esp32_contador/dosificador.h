#pragma once
// Paleta del servo que deja caer una moneda por ciclo.
#include "config.h"

class Dosificador {
 public:
  void iniciar();
  void ritmo(float monedasPorSegundo);   // 0 detiene la alimentación
  void actualizar();                     // llamar en cada vuelta de loop()
  bool activo() const { return ritmo_ > 0.01f; }

 private:
  void escribir(uint16_t microsegundos);
  float ritmo_ = 0.0f;
  uint32_t proximo_ = 0;
  uint32_t cierra_ = 0;
  bool abierto_ = false;
};
