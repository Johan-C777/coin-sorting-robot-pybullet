#include "Barreras.h"

#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#include <soc/gpio_reg.h>
#include <soc/soc.h>

#include "config.h"
#include "pines.h"

namespace hal {
namespace {

QueueHandle_t cola = nullptr;
#if UNA_BARRERA
volatile uint8_t canal_unico = 0;                      // 0 = GPIO 1, 1 = GPIO 2
volatile uint32_t dt_virtual_us = (uint32_t)(24.0f / UNA_BARRERA_V_MM_S * 1e6f);
bool hay_virtual = false;
seq::EventoBarrera ev_virtual;
#endif
volatile uint32_t perdidos = 0;
volatile uint32_t ref_corte_us = 0;

inline void IRAM_ATTR publicarDesdeISR(seq::Barrera b, seq::Flanco f, uint32_t t, BaseType_t *despertar) {
  const seq::EventoBarrera ev{b, f, t};
  if (xQueueSendFromISR(cola, &ev, despertar) != pdTRUE) perdidos = perdidos + 1;
}

struct Canal {
  uint8_t pin;
  seq::Barrera id;
  float base;
  int crudo;
  bool ocupada;
  volatile uint32_t ultimo_us;
  volatile uint8_t nivel;
};
Canal canales[2] = {{PIN_IR1, seq::Barrera::Primera, 0, 0, false, 0, 1}, {PIN_IR2, seq::Barrera::Segunda, 0, 0, false, 0, 1}};

// ---- Haz de referencia de la banda: siempre por flanco ---------------------------------
void IRAM_ATTR isrReferencia() { ref_corte_us = (uint32_t)esp_timer_get_time(); }

#if BARRERAS_MODO == BARRERAS_DIGITAL
// ---- Modo digital: una ISR por flanco en cada barrera ---------------------------------
void IRAM_ATTR isrBarrera(void *arg) {
  Canal *c = static_cast<Canal *>(arg);
  const uint32_t t = (uint32_t)esp_timer_get_time();
  const uint8_t nivel = (REG_READ(GPIO_IN_REG) >> c->pin) & 1;   // lectura de registro: segura en IRAM
  if (nivel == c->nivel) return;                                  // rebote sin cambio neto
  if (t - c->ultimo_us < ANTIRREBOTE_US) return;
  c->nivel = nivel;
  c->ultimo_us = t;
  BaseType_t despertar = pdFALSE;
  publicarDesdeISR(c->id, nivel ? seq::Flanco::Sale : seq::Flanco::Entra, t, &despertar);
  if (despertar) portYIELD_FROM_ISR();
}

void iniciarModo() {
  for (Canal &c : canales) {
    pinMode(c.pin, INPUT);
    c.nivel = digitalRead(c.pin);
    c.ocupada = !c.nivel;
    attachInterruptArg(c.pin, isrBarrera, &c, CHANGE);
  }
}
void diagModo(Canal &c) { c.crudo = c.nivel ? 4095 : 0; c.ocupada = !c.nivel; }

#else
// ---- Modo ADC: timer por hardware -> ISR -> tarea de muestreo --------------------------
hw_timer_t *timer = nullptr;
TaskHandle_t tarea = nullptr;
volatile uint32_t t_muestra = 0;

void IRAM_ATTR isrMuestreo() {
  t_muestra = (uint32_t)esp_timer_get_time();       // instante exacto del muestreo
  BaseType_t despertar = pdFALSE;
  vTaskNotifyGiveFromISR(tarea, &despertar);
  if (despertar) portYIELD_FROM_ISR();
}

void procesar(Canal &c, int crudo, uint32_t t) {
  c.crudo = crudo;
  if (!c.ocupada) {
    c.base += (crudo - c.base) * SEGUIMIENTO_BASE;   // sigue la luz ambiente
    if (crudo < c.base * UMBRAL_OCUPADA) {
      c.ocupada = true;
      const seq::EventoBarrera ev{c.id, seq::Flanco::Entra, t};
      if (xQueueSend(cola, &ev, 0) != pdTRUE) perdidos = perdidos + 1;
    }
  } else if (crudo > c.base * UMBRAL_LIBRE) {
    c.ocupada = false;
    const seq::EventoBarrera ev{c.id, seq::Flanco::Sale, t};
    if (xQueueSend(cola, &ev, 0) != pdTRUE) perdidos = perdidos + 1;
  }
}

void tareaMuestreo(void *) {
  for (;;) {
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
    const uint32_t t = t_muestra;
#if UNA_BARRERA
    Canal &c = canales[canal_unico];
    procesar(c, analogRead(c.pin), t);
#else
    for (Canal &c : canales) procesar(c, analogRead(c.pin), t);
#endif
  }
}

void iniciarModo() {
  for (Canal &c : canales) {
    pinMode(c.pin, INPUT);
    analogSetPinAttenuation(c.pin, ADC_11db);
    float s = 0;
    for (int i = 0; i < 64; i++) { s += analogRead(c.pin); delay(1); }
    c.base = s / 64;                                  // haz libre al arrancar (pista vacía)
  }
  // Núcleo 1, por encima de loop() (prioridad 1) y por debajo de nada crítico.
  xTaskCreatePinnedToCore(tareaMuestreo, "barreras", 3072, nullptr, 5, &tarea, 1);
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  timer = timerBegin(1000000);                        // 1 MHz
  timerAttachInterrupt(timer, &isrMuestreo);
  timerAlarm(timer, 1000000 / FS_BARRERAS_HZ, true, 0);
#else
  timer = timerBegin(0, 80, true);                    // 80 MHz / 80 = 1 MHz
  timerAttachInterrupt(timer, &isrMuestreo, true);
  timerAlarmWrite(timer, 1000000 / FS_BARRERAS_HZ, true);
  timerAlarmEnable(timer);
#endif
}
void diagModo(Canal &) {}
#endif

}  // namespace

void barrerasIniciar() {
  cola = xQueueCreate(32, sizeof(seq::EventoBarrera));
  iniciarModo();
  pinMode(PIN_IR_REF, INPUT);
  attachInterrupt(PIN_IR_REF, isrReferencia, FALLING);
}

#if UNA_BARRERA
// Con una sola barrera, cada flanco real genera el de una segunda barrera "virtual" situada a
// sep_barreras_mm aguas abajo y desfasada dt = sep / v. El medidor de dos barreras queda con
// velocidad constante v y la cuerda sale de v × tiempo de oclusión.
bool barrerasEvento(seq::EventoBarrera &ev) {
  if (hay_virtual) { ev = ev_virtual; hay_virtual = false; return true; }
  const seq::Barrera fisica = canal_unico ? seq::Barrera::Segunda : seq::Barrera::Primera;
  do {
    if (xQueueReceive(cola, &ev, 0) != pdTRUE) return false;
  } while (ev.barrera != fisica);                     // el otro haz se ignora
  ev.barrera = seq::Barrera::Primera;
  ev_virtual = {seq::Barrera::Segunda, ev.flanco, ev.t_us + dt_virtual_us};
  hay_virtual = true;
  return true;
}
void barreraUnicaCanal(uint8_t canal) { canal_unico = canal & 1; xQueueReset(cola); }
uint8_t barreraUnicaCanal() { return canal_unico; }
void barreraUnicaVelocidad(float v_mm_s, float sep_mm) { dt_virtual_us = (uint32_t)(sep_mm / v_mm_s * 1e6f); }
float barreraUnicaVelocidad(float sep_mm) { return sep_mm / (dt_virtual_us * 1e-6f); }
#else
bool barrerasEvento(seq::EventoBarrera &ev) { return xQueueReceive(cola, &ev, 0) == pdTRUE; }
#endif
void barrerasDescartar() {
  xQueueReset(cola);
#if UNA_BARRERA
  hay_virtual = false;
#endif
}
uint32_t barrerasPerdidos() { return perdidos; }

DiagBarrera barrerasDiag(uint8_t i) {
  Canal &c = canales[i & 1];
  diagModo(c);
  return {c.crudo, c.base, c.ocupada};
}

uint32_t referenciaUltimoCorte() { return ref_corte_us; }
void referenciaBorrar() { ref_corte_us = 0; }

}  // namespace hal
