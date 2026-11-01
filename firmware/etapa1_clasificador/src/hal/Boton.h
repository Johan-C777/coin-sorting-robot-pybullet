#pragma once
// Pulsador del operador (opcional, NA a GND en PIN_BOTON). Interrupción por flanco con
// antirrebote en la ISR; loop() consulta pulsacion(): corta = marcha/pausa, larga = paro.
#include <Arduino.h>
#include <esp_timer.h>

#include "pines.h"

namespace hal {

enum class Pulsacion : uint8_t { Ninguna, Corta, Larga };

class Boton {
 public:
  void iniciar() {
    pinMode(PIN_BOTON, INPUT_PULLUP);
    attachInterruptArg(PIN_BOTON, isr, this, CHANGE);
  }
  Pulsacion pulsacion() {
    if (bajada_us_ && !soltado_ && (uint32_t)esp_timer_get_time() - bajada_us_ > LARGA_US) {
      bajada_us_ = 0;                       // larga: se dispara sin esperar a soltar
      return Pulsacion::Larga;
    }
    if (!soltado_) return Pulsacion::Ninguna;
    soltado_ = false;
    const bool corta = bajada_us_ != 0;
    bajada_us_ = 0;
    return corta ? Pulsacion::Corta : Pulsacion::Ninguna;
  }

 private:
  static constexpr uint32_t ANTIRREBOTE_US = 30000, LARGA_US = 2000000;
  static void isr(void *arg);   // en Boton.cpp: IRAM_ATTR fuera del header evita el error de literales l32r
  volatile uint32_t ultimo_us_ = 0, bajada_us_ = 0;
  volatile bool soltado_ = false;
};

}  // namespace hal
