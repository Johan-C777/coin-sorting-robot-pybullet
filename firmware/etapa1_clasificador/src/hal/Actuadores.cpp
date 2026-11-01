#include "Actuadores.h"

#include <ESP32Servo.h>

#include "config.h"
#include "pines.h"

namespace hal {
namespace {

// ---- 28BYJ-48 en paso completo, 2 bobinas: IN1..IN4 = 1100, 0110, 0011, 1001 ---------------
constexpr uint8_t FASES[4] = {0b0011, 0b0110, 0b1100, 0b1001};   // bit0 = IN1
uint8_t fase = 0;

void escribir(uint8_t m) {
  for (int i = 0; i < 4; i++) digitalWrite(PIN_TOLVA[i], (m >> i) & 1);
}
void tolvaPaso(int dir) { fase = (fase + dir) & 3; escribir(FASES[fase]); }
void tolvaEnergizar() { escribir(FASES[fase]); }
void tolvaSoltar() { escribir(0); }     // sin corriente: el motor no se calienta en reposo

Rampa rampa_tolva(tolvaPaso, tolvaSoltar);
float bolsillo_acum = 0;                // posición exacta del disco, en bolsillos
Servo servo;

#if HABILITAR_BANDA
void bandaPaso(int dir) {
  digitalWrite(PIN_DIR, dir > 0);
  digitalWrite(PIN_STEP, HIGH);
  delayMicroseconds(2);                 // A4988 pide >= 1 µs
  digitalWrite(PIN_STEP, LOW);
}
Rampa rampa_banda(bandaPaso);
#endif

void tareaPasos(void *) {
  for (;;) {
    rampa_tolva.run();
#if HABILITAR_BANDA
    rampa_banda.run();
#endif
    taskYIELD();
  }
}

}  // namespace

void actuadoresIniciar() {
  for (uint8_t p : PIN_TOLVA) { pinMode(p, OUTPUT); digitalWrite(p, LOW); }
  rampa_tolva.v0 = TOLVA_V0;
  rampa_tolva.vmax = TOLVA_VMAX;
  rampa_tolva.acc = TOLVA_ACC;
  rampa_tolva.pre_us = TOLVA_PRE_MS * 1000UL;
  rampa_tolva.post_us = TOLVA_POST_MS * 1000UL;
  rampa_tolva.alEnergizar(tolvaEnergizar);

  servo.setPeriodHertz(50);
  servo.attach(PIN_SERVO, SERVO_US_MIN, SERVO_US_MAX);
  servo.write(SERVO_CERRADA);

#if HABILITAR_BANDA
  pinMode(PIN_STEP, OUTPUT);
  pinMode(PIN_DIR, OUTPUT);
  pinMode(PIN_EN, OUTPUT);
  digitalWrite(PIN_EN, LOW);            // habilitado
  rampa_banda.v0 = BANDA_V0;
  rampa_banda.vmax = BANDA_VMAX;
  rampa_banda.acc = BANDA_ACC;
#endif

#if ESP_ARDUINO_VERSION_MAJOR < 3
  disableCore0WDT();                    // la tarea de pasos no duerme: el IDLE0 no alimenta el WDT
#endif
  xTaskCreatePinnedToCore(tareaPasos, "pasos", 4096, nullptr, 2, nullptr, 0);
}

void tolvaBolsillos(float n) {
  bolsillo_acum += n;
  rampa_tolva.ir(lroundf(bolsillo_acum * TOLVA_PASOS_VUELTA / BOLSILLOS) * TOLVA_SENTIDO);
}
bool tolvaOcupada() { return rampa_tolva.ocupado(); }
void tolvaParar() { rampa_tolva.parar(); }
Rampa &tolva() { return rampa_tolva; }

void compuerta(bool abierta) { servo.write(abierta ? SERVO_ABIERTA : SERVO_CERRADA); }
void compuertaAngulo(int g) { servo.write(constrain(g, 0, 180)); }

#if HABILITAR_BANDA
// El cero de la banda es el vaso 8 bajo el embudo (referencia por el haz PIN_IR_REF).
void bandaMm(float mm) { rampa_banda.ir(lroundf(mm * BANDA_PASOS_MM)); }
void bandaVaso(int8_t v) { bandaMm(v < 0 ? BANDA_RECHAZO_MM : (8 - v) * BANDA_PASO_VASO_MM); }
bool bandaOcupada() { return rampa_banda.ocupado(); }
void bandaParar() { rampa_banda.parar(); }
#else
void bandaMm(float) {}
void bandaVaso(int8_t) {}
bool bandaOcupada() { return false; }
void bandaParar() {}
#endif

}  // namespace hal
