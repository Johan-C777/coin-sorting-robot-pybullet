#pragma once
// Planificador de orden: mismos cinco pasos que software/brazo/planner.py.
#include "cups.h"

struct Movimiento {
  uint8_t vaso;          // índice en el arreglo de vasos
  int8_t zonaOrigen;
  int8_t puestoOrigen;
  int8_t zonaDestino;
  int8_t puestoDestino;
  bool liberar;          // true si solo se está despejando un puesto del rack
};

namespace Planificador {

// Llena movs (máximo 10) y devuelve cuántos movimientos hacen falta.
uint8_t planificar(const Vaso vasos[N_PUESTOS], uint8_t criterio, int8_t sentido,
                   Movimiento movs[10]);

}  // namespace Planificador
