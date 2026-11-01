#pragma once
// Mapa de pines · ESP32-S3-DevKitC-1 (N8R8 / N16R8) con su shield.
// Esquema: hardware/etapa1-clasificador/esquematico/  ·  docs/11-electronica-etapa1.md
//
// NO usar: 0, 3, 45, 46 (strapping) · 19, 20 (USB) · 26-37 (flash/PSRAM octal)
//          43, 44 (UART0) · 48 (LED RGB de la placa, se usa como LED de estado)
#include <stdint.h>

// ---- Tolva: 28BYJ-48 por ULN2003 (5 V externos, GND común) --------------------------
constexpr uint8_t PIN_TOLVA[4] = {4, 5, 6, 7};   // IN1..IN4

// ---- Compuerta: SG90 (5 V externos, 220 µF junto al servo) -------------------------
constexpr uint8_t PIN_SERVO = 15;

// ---- Barreras IR de medición (pista L01, a 105 y 129 mm) --------------------------
// Fototransistor en seguidor de emisor: C -> 3V3, E -> GPIO + 10 kΩ -> GND.
// Haz libre = nivel alto; moneda en el haz = nivel bajo. LED IR: 5 V -> 330 Ω -> LED.
constexpr uint8_t PIN_IR1 = 1;                   // ADC1_CH0 (también entrada con interrupción)
constexpr uint8_t PIN_IR2 = 2;                   // ADC1_CH1

// ---- Sensor de color TCS3200 (adaptador A01 a 152 mm) -------------------------------
constexpr uint8_t PIN_TCS_OUT = 14;              // onda cuadrada -> contador PCNT
constexpr uint8_t PIN_TCS_S2 = 16;               // filtro: R (0,0) · B (0,1) · G (1,1)
constexpr uint8_t PIN_TCS_S3 = 17;
constexpr uint8_t PIN_TCS_S0 = 18;               // escala: S0 = S1 = 1 -> 100 %
constexpr uint8_t PIN_TCS_S1 = 21;               // OE a GND, VCC a 3V3

// ---- Banda (etapa 2): A4988 + NEMA17 y haz de referencia del cartucho ---------------
constexpr uint8_t PIN_STEP = 10;
constexpr uint8_t PIN_DIR = 11;
constexpr uint8_t PIN_EN = 12;                   // activo en bajo
constexpr uint8_t PIN_IR_REF = 13;               // mismo circuito que las barreras

// ---- Operador (opcional): pulsador NA a GND, marcha/pausa; mantener 2 s = paro --------
constexpr uint8_t PIN_BOTON = 9;

// Libres: 8, 38, 39, 40, 41, 42, 47
