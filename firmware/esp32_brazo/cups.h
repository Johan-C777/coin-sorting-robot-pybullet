#pragma once
// Vasos de monedas: datos que llegan del módulo contador.
#include <stdint.h>
#include "config.h"

struct Vaso {
  uint16_t denominacion;   // 50, 100, 200, 500 o 1000
  uint8_t monedas;         // total del vaso, de las dos familias
  int8_t zona;             // ZONA_ENTRADA o ZONA_RACK
  int8_t puesto;           // 0 a 4, -1 si está en la pinza
  uint8_t antiguas;        // cuántas de las monedas son de la familia anterior
};

namespace Vasos {

float masaMonedaG(uint16_t denominacion);          // familia nueva (2012)
float masaMonedaAntiguaG(uint16_t denominacion);   // familia anterior; 0 si no se admite
uint32_t valor(const Vaso &v);
float pesoG(const Vaso &v);
float clave(const Vaso &v, uint8_t criterio);
float yawDe(int8_t zona, int8_t puesto);

}  // namespace Vasos
