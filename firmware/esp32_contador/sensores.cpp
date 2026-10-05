#include "sensores.h"

#include <Arduino.h>

namespace {
volatile uint16_t cuenta[N_CANALES] = {0, 0, 0, 0, 0};
volatile uint32_t ultimo[N_CANALES] = {0, 0, 0, 0, 0};
uint16_t entregadas[N_CANALES] = {0, 0, 0, 0, 0};

void IRAM_ATTR pulso(uint8_t canal) {
  const uint32_t ahora = micros();
  if (ahora - ultimo[canal] < REBOTE_US) return;    // filtra el rebote del haz
  ultimo[canal] = ahora;
  cuenta[canal]++;
}
void IRAM_ATTR isr0() { pulso(0); }
void IRAM_ATTR isr1() { pulso(1); }
void IRAM_ATTR isr2() { pulso(2); }
void IRAM_ATTR isr3() { pulso(3); }
void IRAM_ATTR isr4() { pulso(4); }
void (*ISR[N_CANALES])() = {isr0, isr1, isr2, isr3, isr4};
}  // namespace

namespace Sensores {

void iniciar() {
  for (uint8_t i = 0; i < N_CANALES; i++) {
    pinMode(PIN_SENSOR[i], INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(PIN_SENSOR[i]), ISR[i], FALLING);
  }
}

int8_t atender(Conteo &conteo) {
  int8_t ultimoCanal = -1;
  for (uint8_t i = 0; i < N_CANALES; i++) {
    noInterrupts();
    const uint16_t total = cuenta[i];
    interrupts();
    if (total != entregadas[i]) {
      conteo.sumar(i, total - entregadas[i]);
      entregadas[i] = total;
      ultimoCanal = (int8_t)i;
    }
  }
  return ultimoCanal;
}

uint16_t pulsos(uint8_t canal) { return canal < N_CANALES ? cuenta[canal] : 0; }

}  // namespace Sensores
