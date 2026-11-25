#include "Actuadores.h"

#include <ESP32Servo.h>

#include "config.h"
#include "pines.h"

namespace hal {
namespace {

#if HABILITAR_BANDA && BANDA_RAMBO
// ---- Enlace serie con la RAMBo ----------------------------------------------------------
volatile int oks_pendientes = 0;

// Una línea que respondió la RAMBo: cuenta los "ok" y muestra lo demás.
void ramboLineaRx(const char *l) {
  if (l[0] == 'o' && l[1] == 'k') { if (oks_pendientes > 0) oks_pendientes--; }
  else if (l[0] && strncmp(l, "echo:busy", 9) != 0) Serial.printf("RAMBO: %s\n", l);
}

#if BANDA_PUENTE_PC
// La RAMBo va por USB al PC y el panel web hace de puente: cada línea de G-code sale por la
// consola con el prefijo '@', y las respuestas de la RAMBo llegan por la consola como "@ok".
void ramboLeer() {}
void ramboEnviar(const char *g, int oks) {
  oks_pendientes += oks;
  const char *p = g;
  while (*p) {
    const char *f = strchr(p, '\n');
    const int n = f ? (int)(f - p) : (int)strlen(p);
    if (n) Serial.printf("@%.*s\n", n, p);
    p += n + (f ? 1 : 0);
  }
}
void ramboIniciar() {}                  // Marlin ya trae pasos/mm, sin límites y sin apagado por inactividad
#else
HardwareSerial rambo(1);
char rx_buf[64];
uint8_t rx_n = 0;

void ramboLeer() {
  while (rambo.available()) {
    char c = rambo.read();
    if (c == '\n' || c == '\r') {
      rx_buf[rx_n] = 0;
      ramboLineaRx(rx_buf);
      rx_n = 0;
    } else if (rx_n < sizeof rx_buf - 1) {
      rx_buf[rx_n++] = c;
    }
  }
}
void ramboEnviar(const char *g, int oks) {
  ramboLeer();
  oks_pendientes += oks;
  rambo.print(g);
}
void ramboIniciar() {
  rambo.begin(RAMBO_BAUD, SERIAL_8N1, PIN_RAMBO_RX, PIN_RAMBO_TX);
  delay(2500);                          // por si la RAMBo todavía está arrancando
  while (rambo.available()) rambo.read();
  char cfg[160];
  snprintf(cfg, sizeof cfg,
           "M84 S0\nM92 X%.2f\nM201 X%d\nM203 X%d\nM204 T%d\nM211 S0\nG90\nG92 X0\n",
           BANDA_PASOS_MM, (int)(BANDA_ACC / BANDA_PASOS_MM),
           (int)(BANDA_VMAX / BANDA_PASOS_MM), (int)(BANDA_ACC / BANDA_PASOS_MM));
  ramboEnviar(cfg, 8);                  // sin motor apagado por inactividad, pasos/mm, rampa, cero aquí
}
#endif
bool ramboOcupada() { ramboLeer(); return oks_pendientes > 0; }
#endif


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

#if HABILITAR_BANDA && !BANDA_RAMBO
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
#if HABILITAR_BANDA && !BANDA_RAMBO
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

#if HABILITAR_BANDA && BANDA_RAMBO
  ramboIniciar();
#elif HABILITAR_BANDA
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

#if HABILITAR_BANDA && BANDA_RAMBO
// La RAMBo (Marlin) mueve la banda; el ESP32 le manda G-code por UART1 y espera el "ok"
// de M400, que Marlin solo envía cuando el movimiento terminó. Así la compuerta nunca abre
// con el cartucho en movimiento.
void bandaMm(float mm) {
  char linea[48];
  snprintf(linea, sizeof linea, "G1 X%.2f F%d\nM400\n", mm, (int)RAMBO_F_MM_MIN);
  ramboEnviar(linea, 2);
}
void bandaVaso(int8_t v) { bandaMm(v < 0 ? BANDA_RECHAZO_MM : (8 - v) * BANDA_PASO_VASO_MM); }
bool bandaOcupada() { return ramboOcupada(); }
void bandaRespuesta(const char *linea) { ramboLineaRx(linea); }
void bandaReiniciarEnlace() { oks_pendientes = 0; }
void bandaParar() { ramboEnviar("M410\n", 1); }      // parada rápida
#elif HABILITAR_BANDA
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
