#pragma once
// Disco de 4 cavidades de la tolva: cada cuarto de vuelta suelta UNA moneda.
// Por defecto lo mueve un 28BYJ-48 (ULN2003) a medio paso, sin bloquear el loop.
// Definir TOLVA_SG90_CONTINUO para usar un SG90 modificado a rotación continua.
#include "config.h"

class Dosificador {
 public:
  void iniciar();
  void ritmo(float monedasPorSegundo);   // 0 detiene; 1/PERIODO_MONEDA_S es lo nominal
  void actualizar();                     // llamar en cada vuelta de loop()
  bool activo() const { return ritmo_ > 0.01f; }

 private:
  void bobinas(uint8_t fase);
  float ritmo_ = 0.0f;
  uint32_t periodoPasoUs_ = 0;
  uint32_t ultimoPasoUs_ = 0;
  uint8_t fase_ = 0;
};
