#pragma once
// Barreras infrarrojas: una por estación. Cada flanco de bajada es una moneda.
// El conteo se hace en interrupción y se consume en el bucle principal.
#include "conteo.h"

namespace Sensores {

void iniciar();
// Pasa al objeto de conteo las monedas detectadas desde la última llamada.
// Devuelve el canal de la última moneda vista, o -1 si no hubo ninguna.
int8_t atender(Conteo &conteo);
uint16_t pulsos(uint8_t canal);

}  // namespace Sensores
