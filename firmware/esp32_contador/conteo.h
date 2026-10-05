#pragma once
// Estado de conteo de la etapa: monedas por canal, valor, peso y tramas.
// No depende de Arduino, por eso se puede probar en el PC (firmware/tests).
#include <stddef.h>
#include <stdint.h>
#include "config.h"

class Conteo {
 public:
  void reiniciar();
  void sumar(uint8_t canal, uint16_t n = 1);

  uint16_t monedas(uint8_t canal) const;
  uint32_t valor(uint8_t canal) const;
  float pesoG(uint8_t canal) const;            // incluye los 18 g del vaso vacío

  uint16_t monedasTotal() const;
  uint32_t valorTotal() const;
  float pesoTotal() const;
  bool vasoLleno() const;                      // algún canal llegó a la capacidad

  // "VASOS:50x24,100x20,200x18,500x14,1000x12" para el ESP32 del brazo
  uint8_t trama(char *destino, uint8_t capacidad) const;
  // cuerpo JSON de POST /api/vasos
  size_t json(char *destino, size_t capacidad) const;

 private:
  uint16_t n_[N_CANALES] = {0, 0, 0, 0, 0};
};
