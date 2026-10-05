#pragma once
// Banda transportadora sobre puente H. La velocidad se da de 0 a 1.
#include "config.h"

class Banda {
 public:
  void iniciar();
  void avanzar(float velocidad);   // 0 a 1
  void detener();
  bool enMarcha() const { return marcha_; }

 private:
  bool marcha_ = false;
};
