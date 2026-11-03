#pragma once
// Barreras IR (fototransistor: colector a 3V3, emisor a GPIO + 10 k a GND; haz libre = alto)
// y color TCS3200 (frecuencia por PCNT). La base de cada barrera sigue lentamente la luz ambiente.
#include <driver/pulse_cnt.h>
#include "config.h"

struct Barrera {
  explicit Barrera(uint8_t p) : pin(p) {}
  uint8_t pin;
  float base = 0;
  int raw = 0;
  bool ocupada = false;
  uint32_t t_ent = 0, t_sal = 0;   // µs del último corte y de la última liberación
  bool nueva_ent = false, nueva_sal = false;

  void iniciar() {
    pinMode(pin, INPUT);
    analogSetPinAttenuation(pin, ADC_11db);
    float s = 0;
    for (int i = 0; i < 64; i++) { s += analogRead(pin); delay(1); }
    base = s / 64;
  }
  void leer() {
    raw = analogRead(pin);
    const uint32_t t = micros();
    if (!ocupada) {
      base += (raw - base) * 0.0005f;                  // sigue la luz ambiente
      if (raw < base * UMBRAL_OCUPADA) { ocupada = true; t_ent = t; nueva_ent = true; }
    } else if (raw > base * UMBRAL_LIBRE) {
      ocupada = false; t_sal = t; nueva_sal = true;
    }
  }
  void borrar() { nueva_ent = nueva_sal = false; }
};

// TCS3200: la salida es una onda cuadrada cuya frecuencia crece con la luz del filtro
// elegido por S2/S3. Se cuenta con el PCNT del ESP32-S3 (sin interrupciones por flanco).
struct Color {
  pcnt_unit_handle_t u = nullptr;
  void iniciar() {
    for (uint8_t p : {PIN_TCS_S0, PIN_TCS_S1, PIN_TCS_S2, PIN_TCS_S3}) pinMode(p, OUTPUT);
    digitalWrite(PIN_TCS_S0, HIGH);                 // escala 100 %
    digitalWrite(PIN_TCS_S1, HIGH);
    pcnt_unit_config_t uc = {};
    uc.low_limit = -1;
    uc.high_limit = 32767;
    pcnt_new_unit(&uc, &u);
    pcnt_chan_config_t cc = {};
    cc.edge_gpio_num = PIN_TCS_OUT;
    cc.level_gpio_num = -1;
    pcnt_channel_handle_t ch;
    pcnt_new_channel(u, &cc, &ch);
    pcnt_channel_set_edge_action(ch, PCNT_CHANNEL_EDGE_ACTION_INCREASE, PCNT_CHANNEL_EDGE_ACTION_HOLD);
    pcnt_unit_enable(u);
    pcnt_unit_start(u);
  }
  // Pulsos contados en TCS_VENTANA_MS con el filtro (s2, s3): R=(0,0) B=(0,1) C=(1,0) G=(1,1).
  uint32_t canal(bool s2, bool s3) {
    digitalWrite(PIN_TCS_S2, s2);
    digitalWrite(PIN_TCS_S3, s3);
    delayMicroseconds(300);                         // asentamiento del filtro
    pcnt_unit_clear_count(u);
    delayMicroseconds(TCS_VENTANA_MS * 1000UL);
    int n = 0;
    pcnt_unit_get_count(u, &n);
    return n > 0 ? n : 0;
  }
  // Muestrea `ms` y devuelve la razón (R+G)/2B de la lectura con más luz (moneda centrada).
  float razonMax(uint16_t ms, uint32_t *total = nullptr) {
    uint32_t mejor = 0;
    float razon = 0;
    for (uint32_t t0 = millis(); millis() - t0 < ms;) {
      const uint32_t r = canal(0, 0), g = canal(1, 1), b = canal(0, 1);
      if (r + g + b > mejor) { mejor = r + g + b; razon = (r + g) / (2.0f * (b ? b : 1)); }
    }
    if (total) *total = mejor;
    return razon;
  }
};
