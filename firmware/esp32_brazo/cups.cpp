#include "cups.h"

namespace Vasos {

float masaMonedaG(uint16_t denominacion) {
  switch (denominacion) {
    case 50: return 2.00f;
    case 100: return 3.34f;
    case 200: return 4.61f;
    case 500: return 7.14f;
    case 1000: return 9.95f;
    default: return 0.0f;
  }
}

float masaMonedaAntiguaG(uint16_t denominacion) {
  switch (denominacion) {
    case 50: return 4.50f;
    case 100: return 5.31f;
    case 200: return 7.08f;
    case 500: return 7.14f;           // igual a la nueva: el selector no las distingue
    default: return 0.0f;             // la $1.000 de 1996 no la admite el riel
  }
}

uint32_t valor(const Vaso &v) {
  return (uint32_t)v.denominacion * (uint32_t)v.monedas;
}

float pesoG(const Vaso &v) {
  const uint8_t antiguas = (v.antiguas <= v.monedas) ? v.antiguas : v.monedas;
  return 18.0f                                             // vaso vacío
       + (v.monedas - antiguas) * masaMonedaG(v.denominacion)
       + antiguas * masaMonedaAntiguaG(v.denominacion);
}

float clave(const Vaso &v, uint8_t criterio) {
  switch (criterio) {
    case POR_DENOMINACION: return (float)v.denominacion;
    case POR_CANTIDAD: return (float)v.monedas;
    case POR_PESO: return pesoG(v);
    case POR_ANTIGUAS: return (float)v.antiguas;
    case POR_VALOR:
    default: return (float)valor(v);
  }
}

float yawDe(int8_t zona, int8_t puesto) {
  if (puesto < 0 || puesto >= (int8_t)N_PUESTOS) return 0.0f;
  return (zona == ZONA_RACK) ? YAW_RACK[puesto] : YAW_ENTRADA[puesto];
}

}  // namespace Vasos
