#pragma once
// Etapa 1: selección y conteo de monedas. Los números son los mismos de
// scripts/generar_stl.py y de la simulación HTML.
#include <stdint.h>

constexpr uint8_t N_CANALES = 5;

// denominaciones y masa de cada moneda (serie 2012 del Banco de la República)
constexpr uint16_t DENOMINACION[N_CANALES] = {50, 100, 200, 500, 1000};
constexpr float MASA_MONEDA_G[N_CANALES] = {2.00f, 3.34f, 4.61f, 7.14f, 9.95f};
constexpr float DIAMETRO_MM[N_CANALES] = {17.0f, 20.3f, 22.4f, 23.7f, 26.7f};
constexpr float LUZ_MM[N_CANALES] = {17.6f, 20.9f, 23.0f, 24.3f, 27.3f};
constexpr float MASA_VASO_G = 18.0f;

// pines de las barreras infrarrojas, una por estación
constexpr uint8_t PIN_SENSOR[N_CANALES] = {32, 33, 25, 26, 27};
constexpr uint32_t REBOTE_US = 25000;          // 25 ms entre monedas del mismo canal

// dosificador: servo SG90 por LEDC
constexpr uint8_t PIN_SERVO = 18;
constexpr uint8_t CANAL_SERVO = 0;
constexpr uint16_t SERVO_CERRADO_US = 1200;
constexpr uint16_t SERVO_ABIERTO_US = 1750;
constexpr uint16_t SERVO_MS_ABIERTO = 120;     // tiempo con la paleta abierta

// banda: puente H L298N
constexpr uint8_t PIN_BANDA_A = 19;
constexpr uint8_t PIN_BANDA_B = 21;
constexpr uint8_t PIN_BANDA_PWM = 23;
constexpr uint8_t CANAL_BANDA = 1;
constexpr uint16_t BANDA_PWM_MIN = 120;        // de 0 a 255, por debajo no arranca

// celda
constexpr float PASO_ESTACION_MM = 65.0f;
constexpr float VASOS_POR_TANDA = 5;
constexpr uint16_t MONEDAS_POR_VASO = 40;      // capacidad de un vaso lleno
