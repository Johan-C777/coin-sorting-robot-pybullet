#pragma once
// Motor de la tolva (28BYJ-48 + ULN2003), compuerta SG90 y banda (A4988).
#include "config.h"
#include "rampa.h"

// ---- 28BYJ-48 en paso completo con 2 bobinas ON: IN1..IN4 = 1100, 0110, 0011, 1001 ----
namespace tolva_hw {
constexpr uint8_t FASES[4] = {0b0011, 0b0110, 0b1100, 0b1001};   // bit0 = IN1
volatile uint8_t fase = 0;
inline void escribir(uint8_t m) {
  for (int i = 0; i < 4; i++) digitalWrite(PIN_TOLVA[i], (m >> i) & 1);
}
void paso(int dir) { fase = (fase + dir) & 3; escribir(FASES[fase]); }
void energizar() { escribir(FASES[fase]); }
void soltar() { escribir(0); }                    // sin corriente: no calienta
}  // namespace tolva_hw

Rampa tolva(tolva_hw::paso, tolva_hw::soltar);
float bolsillo_acum = 0;                           // posición exacta en bolsillos (fracción)

inline void tolvaIniciar() {
  for (uint8_t p : PIN_TOLVA) { pinMode(p, OUTPUT); digitalWrite(p, LOW); }
  tolva.v0 = TOLVA_V0; tolva.vmax = TOLVA_VMAX; tolva.acc = TOLVA_ACC;
  tolva.pre_us = TOLVA_PRE_MS * 1000UL; tolva.post_us = TOLVA_POST_MS * 1000UL;
  tolva.alEnergizar(tolva_hw::energizar);
}
// Avanza n bolsillos (negativo = atrás) sin acumular el error de 2037,89 vs 2048.
inline void tolvaBolsillos(float n) {
  bolsillo_acum += n;
  tolva.ir(lroundf(bolsillo_acum * TOLVA_PASOS_VUELTA / BOLSILLOS) * TOLVA_SENTIDO);
}

// ---- Compuerta: SG90 por LEDC directo (50 Hz, 14 bits) ----
inline void servoGrados(int g) {
  const uint32_t us = SERVO_US_MIN + (uint32_t)constrain(g, 0, 180) * (SERVO_US_MAX - SERVO_US_MIN) / 180;
  ledcWrite(PIN_SERVO, us * 16383UL / 20000UL);
}
inline void compuertaIniciar() {
  ledcAttach(PIN_SERVO, 50, 14);
  servoGrados(SERVO_CERRADA);
}

// ---- Banda: A4988 STEP/DIR/EN ----
#if HABILITAR_BANDA
namespace banda_hw {
void paso(int dir) {
  digitalWrite(PIN_DIR, dir > 0);
  digitalWrite(PIN_STEP, HIGH);
  delayMicroseconds(2);                           // A4988 pide >= 1 µs
  digitalWrite(PIN_STEP, LOW);
}
}  // namespace banda_hw
Rampa banda(banda_hw::paso);
inline void bandaIniciar() {
  pinMode(PIN_STEP, OUTPUT); pinMode(PIN_DIR, OUTPUT); pinMode(PIN_EN, OUTPUT);
  digitalWrite(PIN_EN, LOW);                      // habilitado
  banda.v0 = BANDA_V0; banda.vmax = BANDA_VMAX; banda.acc = BANDA_ACC;
}
inline void bandaA(float mm) { banda.ir(lroundf(mm * BANDA_PASOS_MM)); }
// vaso 0..8; el cero de la banda es el vaso 8 (ESTADO). PROVISIONAL.
inline float bandaPosVaso(int v) { return (8 - v) * BANDA_PITCH_MM; }
#endif

// ---- Tarea de pasos en el núcleo 0 (el loop queda libre para sensores y lógica) ----
inline void tareaPasos(void *) {
  for (;;) {
    tolva.run();
#if HABILITAR_BANDA
    banda.run();
#endif
    bool trabajando = tolva.ocupado();
#if HABILITAR_BANDA
    trabajando = trabajando || banda.ocupado();
#endif
    if (trabajando) taskYIELD(); else vTaskDelay(1);   // en reposo deja correr IDLE0
  }
}
inline void iniciarTareaPasos() {
  // Prioridad 0 (= IDLE): taskYIELD() alterna con IDLE0 y el watchdog queda contento sin desactivarlo.
  xTaskCreatePinnedToCore(tareaPasos, "pasos", 4096, nullptr, tskIDLE_PRIORITY, nullptr, 0);
}
