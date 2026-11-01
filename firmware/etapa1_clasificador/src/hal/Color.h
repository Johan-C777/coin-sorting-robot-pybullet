#pragma once
// TCS3200: la salida es una onda cuadrada cuya frecuencia crece con la luz del filtro
// elegido por S2/S3. Se cuenta con el periférico PCNT del ESP32-S3 (contador por hardware,
// sin una interrupción por flanco: a 100 % de escala la salida llega a ~600 kHz).
#include <Arduino.h>
#include <driver/pcnt.h>

#include "Planta.h"
#include "config.h"
#include "pines.h"

namespace hal {

class Color {
 public:
  void iniciar() {
    for (uint8_t p : {PIN_TCS_S0, PIN_TCS_S1, PIN_TCS_S2, PIN_TCS_S3}) pinMode(p, OUTPUT);
    digitalWrite(PIN_TCS_S0, HIGH);   // escala 100 %
    digitalWrite(PIN_TCS_S1, HIGH);
    pcnt_config_t cfg = {};
    cfg.pulse_gpio_num = PIN_TCS_OUT;
    cfg.ctrl_gpio_num = PCNT_PIN_NOT_USED;
    cfg.channel = PCNT_CHANNEL_0;
    cfg.unit = U;
    cfg.pos_mode = PCNT_COUNT_INC;
    cfg.neg_mode = PCNT_COUNT_DIS;
    cfg.lctrl_mode = PCNT_MODE_KEEP;
    cfg.hctrl_mode = PCNT_MODE_KEEP;
    cfg.counter_h_lim = 32767;
    cfg.counter_l_lim = -32768;
    pcnt_unit_config(&cfg);
    pcnt_filter_disable(U);
    pcnt_counter_pause(U);
  }

  // Pulsos en TCS_VENTANA_MS con el filtro (s2, s3).
  uint32_t canal(bool s2, bool s3) {
    digitalWrite(PIN_TCS_S2, s2);
    digitalWrite(PIN_TCS_S3, s3);
    delayMicroseconds(300);           // asentamiento del filtro
    pcnt_counter_clear(U);
    pcnt_counter_resume(U);
    delayMicroseconds(TCS_VENTANA_MS * 1000UL);
    pcnt_counter_pause(U);
    int16_t n = 0;
    pcnt_get_counter_value(U, &n);
    return (uint32_t)(uint16_t)n;
  }

  // Una muestra: razón (R+G)/2B y brillo total.
  seq::LecturaColor leer() {
    const uint32_t r = canal(0, 0), g = canal(1, 1), b = canal(0, 1);
    ultimo_ = {(r + g) / (2.0f * (b ? b : 1)), r + g + b};
    r_ = r; g_ = g; b_ = b;
    return ultimo_;
  }
  void crudo(uint32_t &r, uint32_t &g, uint32_t &b) const { r = r_; g = g_; b = b_; }

 private:
  static constexpr pcnt_unit_t U = PCNT_UNIT_0;
  seq::LecturaColor ultimo_{0, 0};
  uint32_t r_ = 0, g_ = 0, b_ = 0;
};

}  // namespace hal
