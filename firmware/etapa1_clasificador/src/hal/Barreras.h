#pragma once
// Barreras IR de medición (B1, B2) y haz de referencia de la banda.
// Los flancos se marcan con esp_timer_get_time() DENTRO de una ISR y viajan a la máquina de
// estados por una cola de FreeRTOS: la medición no depende de lo que esté haciendo loop().
#include <Arduino.h>

#include "Planta.h"

namespace hal {

struct DiagBarrera {
  int crudo;       // última lectura ADC (o 4095/0 en modo digital)
  float base;      // nivel con el haz libre
  bool ocupada;
};

void barrerasIniciar();
bool barrerasEvento(seq::EventoBarrera &ev);
void barrerasDescartar();
DiagBarrera barrerasDiag(uint8_t i);
uint32_t barrerasPerdidos();        // eventos que no cupieron en la cola

// Haz de referencia del cartucho (banda): instante del último corte, 0 si no hubo.
uint32_t referenciaUltimoCorte();
void referenciaBorrar();

}  // namespace hal
