#include "planner.h"

namespace Planificador {

uint8_t planificar(const Vaso vasos[N_PUESTOS], uint8_t criterio, int8_t sentido,
                   Movimiento movs[10]) {
  // 1. orden objetivo por la clave elegida, desempatando por denominación
  uint8_t orden[N_PUESTOS];
  for (uint8_t i = 0; i < N_PUESTOS; i++) orden[i] = i;
  for (uint8_t i = 1; i < N_PUESTOS; i++) {          // inserción: n = 5
    const uint8_t actual = orden[i];
    int8_t j = (int8_t)i - 1;
    while (j >= 0) {
      const float a = Vasos::clave(vasos[orden[j]], criterio) * sentido;
      const float b = Vasos::clave(vasos[actual], criterio) * sentido;
      const bool mayor = (a > b) || (a == b &&
          vasos[orden[j]].denominacion * sentido > vasos[actual].denominacion * sentido);
      if (!mayor) break;
      orden[j + 1] = orden[j];
      j--;
    }
    orden[j + 1] = actual;
  }

  // 2. estado actual de los puestos
  int8_t rack[N_PUESTOS], entrada[N_PUESTOS];
  int8_t zona[N_PUESTOS], puesto[N_PUESTOS];
  for (uint8_t i = 0; i < N_PUESTOS; i++) { rack[i] = -1; entrada[i] = -1; }
  for (uint8_t i = 0; i < N_PUESTOS; i++) {
    zona[i] = vasos[i].zona;
    puesto[i] = vasos[i].puesto;
    if (puesto[i] < 0) continue;
    if (zona[i] == ZONA_RACK) rack[puesto[i]] = (int8_t)i;
    else entrada[puesto[i]] = (int8_t)i;
  }

  uint8_t n = 0;
  for (uint8_t j = 0; j < N_PUESTOS && n < 10; j++) {
    const uint8_t idx = orden[j];
    if (zona[idx] == ZONA_RACK && puesto[idx] == (int8_t)j) continue;   // ya está

    const int8_t ocupante = rack[j];
    if (ocupante >= 0 && ocupante != (int8_t)idx) {                     // liberar
      int8_t hueco = -1;
      for (uint8_t k = 0; k < N_PUESTOS; k++) if (entrada[k] < 0) { hueco = (int8_t)k; break; }
      if (hueco < 0) break;                                            // no debería pasar
      movs[n++] = {(uint8_t)ocupante, zona[ocupante], puesto[ocupante],
                   ZONA_ENTRADA, hueco, true};
      entrada[hueco] = ocupante;
      rack[j] = -1;
      zona[ocupante] = ZONA_ENTRADA;
      puesto[ocupante] = hueco;
    }

    if (puesto[idx] >= 0) {
      if (zona[idx] == ZONA_RACK) rack[puesto[idx]] = -1;
      else entrada[puesto[idx]] = -1;
    }
    movs[n++] = {idx, zona[idx], puesto[idx], ZONA_RACK, (int8_t)j, false};
    rack[j] = (int8_t)idx;
    zona[idx] = ZONA_RACK;
    puesto[idx] = (int8_t)j;
  }
  return n;
}

}  // namespace Planificador
