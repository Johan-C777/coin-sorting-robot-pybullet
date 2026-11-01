#pragma once
// Pulsador del operador (opcional, NA a GND en PIN_BOTON). Interrupción por flanco con
// antirrebote en la ISR; loop() consulta pulsacion(): corta = marcha/pausa, larga = paro.
#include <Arduino.h>
#include <esp_timer.h>
#include <soc/gpio_reg.h>
#include <soc/soc.h>

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
  static void IRAM_ATTR isr(void *arg) {
    Boton *b = static_cast<Boton *>(arg);
    const uint32_t t = (uint32_t)esp_timer_get_time();
    if (t - b->ultimo_us_ < ANTIRREBOTE_US) return;
    b->ultimo_us_ = t;
    if (!((REG_READ(GPIO_IN_REG) >> PIN_BOTON) & 1))   // registro: seguro en IRAM
      { b->bajada_us_ = t; b->soltado_ = false; }
    else if (b->bajada_us_) b->soltado_ = true;
  }
  volatile uint32_t ultimo_us_ = 0, bajada_us_ = 0;
  volatile bool soltado_ = false;
};

}  // namespace hal
