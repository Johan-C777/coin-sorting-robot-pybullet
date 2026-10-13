#include "sensores.h"

#include <Arduino.h>

namespace {
volatile uint16_t cuenta[N_ESTACIONES] = {};
volatile uint32_t ultimo[N_ESTACIONES] = {};
uint16_t entregadas[N_ESTACIONES] = {};

void IRAM_ATTR pulso(uint8_t estacion) {
  const uint32_t ahora = micros();
  if (ahora - ultimo[estacion] < REBOTE_US) return;    // filtra el rebote del haz
  ultimo[estacion] = ahora;
  cuenta[estacion]++;
}
void IRAM_ATTR isr0() { pulso(0); }
void IRAM_ATTR isr1() { pulso(1); }
void IRAM_ATTR isr2() { pulso(2); }
void IRAM_ATTR isr3() { pulso(3); }
void IRAM_ATTR isr4() { pulso(4); }
void IRAM_ATTR isr5() { pulso(5); }
void IRAM_ATTR isr6() { pulso(6); }
void IRAM_ATTR isr7() { pulso(7); }
void (*ISR[N_ESTACIONES])() = {isr0, isr1, isr2, isr3, isr4, isr5, isr6, isr7};
}  // namespace

namespace Sensores {

void iniciar() {
  for (uint8_t i = 0; i < N_ESTACIONES; i++) {
    pinMode(PIN_SENSOR[i], INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(PIN_SENSOR[i]), ISR[i], FALLING);
  }
}

int8_t atender(Conteo &conteo) {
  int8_t ultimaEstacion = -1;
  for (uint8_t i = 0; i < N_ESTACIONES; i++) {
    noInterrupts();
    const uint16_t total = cuenta[i];
    interrupts();
    if (total != entregadas[i]) {
      conteo.sumar(i, total - entregadas[i]);
      entregadas[i] = total;
      ultimaEstacion = (int8_t)i;
    }
  }
  return ultimaEstacion;
}

uint16_t pulsos(uint8_t estacion) { return estacion < N_ESTACIONES ? cuenta[estacion] : 0; }

}  // namespace Sensores
