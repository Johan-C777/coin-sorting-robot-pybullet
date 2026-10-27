#pragma once
// Barreras IR (fototransistor: colector a 3V3, emisor a GPIO + 10 k a GND; haz libre = alto)
// y color TCS34725. La base de cada barrera sigue lentamente la luz ambiente.
#include <Adafruit_TCS34725.h>
#include <Wire.h>
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

struct Color {
  Adafruit_TCS34725 tcs{TCS34725_INTEGRATIONTIME_2_4MS, TCS34725_GAIN_16X};
  bool ok = false;
  bool iniciar() {
    Wire.begin(PIN_SDA, PIN_SCL, 400000);
    ok = tcs.begin();
    return ok;
  }
  // Muestrea `ms` y devuelve la razón (R+G)/2B de la lectura con más luz (moneda centrada).
  float razonMax(uint16_t ms, uint16_t *cmax = nullptr) {
    if (!ok) return 0;
    uint16_t r, g, b, c, mejor_c = 0;
    float razon = 0;
    for (uint32_t t0 = millis(); millis() - t0 < ms;) {
      tcs.getRawData(&r, &g, &b, &c);
      if (c > mejor_c) { mejor_c = c; razon = (r + g) / (2.0f * (b ? b : 1)); }
    }
    if (cmax) *cmax = mejor_c;
    return razon;
  }
};
