#pragma once
// Barreras infrarrojas: una por ducto de salida (nueve). Cada flanco
// FLANCO_MONEDA es una moneda, y la estación dice de qué denominación y familia es.
// El conteo se hace en interrupción y se consume en el bucle principal.
#include "conteo.h"

namespace Sensores {

void iniciar();
// Pasa al objeto de conteo las monedas detectadas desde la última llamada.
// Devuelve la estación de la última moneda vista, o -1 si no hubo ninguna.
int8_t atender(Conteo &conteo);
uint16_t pulsos(uint8_t estacion);

}  // namespace Sensores
