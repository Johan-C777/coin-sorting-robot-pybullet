/*
  Brazo clasificador de vasos de monedas, 5 GDL + pinza.
  Módulo 6 del Sistema de Logística de Monedas Inteligentes (UMNG).

  Hardware: ESP32 DevKit V1 + PCA9685 (I2C 0x40) + 6 servos a 6 V.
  Librería externa: Adafruit PWM Servo Driver.

  Puerto serie a 115200, comandos:
    S:114,49,83,64,90,85     pose directa (ángulos de servo)
    VASOS:500x12,100x30,...  carga el lote de la entrada
    ORDEN:valor,asc          clasifica (valor | peso | cantidad | denominacion)
    ESTADO | HOME | STOP | PAUSA | SIGUE | TORQUE0 | TORQUE1

  Con Wi-Fi levanta además GET /api/estado, POST /api/ordenar, /api/vasos y /api/pose.
*/
#include "comms.h"
#include "config.h"
#include "cups.h"
#include "sequencer.h"
#include "servo_bus.h"

#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets_example.h"
#endif

BusServos bus;
Secuenciador secuenciador;

// Lote por defecto: se sobrescribe con VASOS: o con POST /api/vasos.
Vaso vasos[N_PUESTOS] = {
    {500, 12, ZONA_ENTRADA, 0},
    {100, 30, ZONA_ENTRADA, 1},
    {1000, 8, ZONA_ENTRADA, 2},
    {50, 25, ZONA_ENTRADA, 3},
    {200, 17, ZONA_ENTRADA, 4},
};

Comms comms(bus, secuenciador, vasos);
uint32_t tPrevio = 0;

void setup() {
  comms.iniciarSerie(115200);

  if (!bus.iniciar()) {
    Serial.println(F("no responde el PCA9685: revisa I2C y alimentacion"));
  }
  bus.comandar(Q_HOME, PINZA_ABIERTA_MM);

  comms.iniciarWifi(WIFI_SSID, WIFI_PASS);
  tPrevio = millis();
}

void loop() {
  comms.atender();

  const uint32_t ahora = millis();
  if (ahora - tPrevio < (uint32_t)(DT_CONTROL * 1000.0f)) return;

  const float dt = (ahora - tPrevio) / 1000.0f;
  tPrevio = ahora;

  secuenciador.actualizar(dt, bus);   // genera la pose siguiente
  bus.actualizar(dt);                 // rampa y PWM a los seis servos
}
