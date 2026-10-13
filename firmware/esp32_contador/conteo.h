#pragma once
// Estado de conteo de la etapa 1: monedas por estación del riel y, a partir de
// ellas, por vaso: total, antiguas, valor y peso. También arma las tramas.
// No depende de Arduino, por eso se puede probar en el PC (firmware/tests).
#include <stddef.h>
#include <stdint.h>
#include "config.h"

class Conteo {
 public:
  void reiniciar();
  void sumar(uint8_t estacion, uint16_t n = 1);   // estación 0 a 7

  uint16_t monedasEstacion(uint8_t estacion) const;

  // por vaso (0 a 4, en el orden de DENOMINACION_VASO)
  uint16_t monedas(uint8_t vaso) const;
  uint16_t antiguas(uint8_t vaso) const;
  uint32_t valor(uint8_t vaso) const;
  float pesoG(uint8_t vaso) const;               // incluye los 18 g del vaso vacío

  uint16_t monedasTotal() const;
  uint16_t antiguasTotal() const;
  uint32_t valorTotal() const;
  float pesoTotal() const;
  bool vasoLleno() const;                        // algún vaso llegó a la capacidad

  // "VASOS:50x24a6,100x20,..." para el ESP32 del brazo; "aN" solo si hay antiguas
  uint8_t trama(char *destino, uint8_t capacidad) const;
  // cuerpo JSON de POST /api/vasos
  size_t json(char *destino, size_t capacidad) const;

 private:
  uint16_t n_[N_ESTACIONES] = {0, 0, 0, 0, 0, 0, 0, 0};
};
