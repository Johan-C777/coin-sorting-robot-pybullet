#pragma once
// Parámetros del brazo clasificador. Son los mismos números de
// software/brazo/config.py y de la memoria de cálculo: si cambias uno, cámbialo
// en los dos lados. Longitudes en cm, ángulos en grados.

#include <stdint.h>

// ---- geometría --------------------------------------------------------------
constexpr float D1 = 11.0f;   // altura del hombro
constexpr float L1 = 16.0f;   // hombro -> codo
constexpr float L2 = 15.0f;   // codo -> muñeca
constexpr float L3 = 8.0f;    // muñeca -> TCP

// ---- articulaciones ---------------------------------------------------------
constexpr uint8_t N_JUNTAS = 5;
constexpr uint8_t N_CANALES = 6;                  // 5 articulaciones + pinza
constexpr float Q_MIN[N_JUNTAS] = {-90.0f, 0.0f, -150.0f, -120.0f, -90.0f};
constexpr float Q_MAX[N_JUNTAS] = {90.0f, 180.0f, 0.0f, 60.0f, 90.0f};
constexpr float Q_HOME[N_JUNTAS] = {0.0f, 90.0f, -90.0f, -90.0f, 0.0f};

// ---- pinza ------------------------------------------------------------------
constexpr float PINZA_MAX_MM = 70.0f;
constexpr float PINZA_ABIERTA_MM = 66.0f;
constexpr float PINZA_CERRADA_MM = 49.0f;         // 3 mm de interferencia
constexpr float VASO_ANCHO_MM = 52.0f;

// ---- celda ------------------------------------------------------------------
constexpr float R_ARCO = 23.0f;
constexpr float Z_AGARRE = 6.8f;
constexpr float Z_SEGURA = 17.0f;
constexpr float CABECEO = -90.0f;
constexpr uint8_t N_PUESTOS = 5;
constexpr float YAW_ENTRADA[N_PUESTOS] = {-86.0f, -70.5f, -55.0f, -39.5f, -24.0f};
constexpr float YAW_RACK[N_PUESTOS] = {24.0f, 39.5f, 55.0f, 70.5f, 86.0f};
constexpr int8_t ZONA_ENTRADA = 0;
constexpr int8_t ZONA_RACK = 1;

// ---- movimiento -------------------------------------------------------------
constexpr float VEL_ARTICULAR = 75.0f;            // grados/s promedio
constexpr float VEL_LINEAL = 11.0f;               // cm/s promedio
constexpr float T_MIN_ARTICULAR = 0.45f;
constexpr float T_MIN_LINEAL = 0.30f;
constexpr float DT_CONTROL = 0.02f;               // 50 Hz, igual que el PWM

// ---- servos y PCA9685 -------------------------------------------------------
constexpr uint8_t PCA_DIR = 0x40;
constexpr uint8_t PIN_SDA = 21;
constexpr uint8_t PIN_SCL = 22;
constexpr uint16_t PWM_MIN_US = 500;
constexpr uint16_t PWM_MAX_US = 2500;
constexpr uint16_t PWM_FREQ_HZ = 50;
constexpr uint32_t PCA_OSC_HZ = 25000000UL;       // calibrar por unidad
constexpr uint8_t CANAL[N_CANALES] = {0, 1, 2, 3, 4, 5};
constexpr float VEL_SERVO_MAX = 180.0f;           // grados/s de la rampa

// ---- criterios de orden -----------------------------------------------------
enum Criterio : uint8_t { POR_DENOMINACION = 0, POR_CANTIDAD, POR_VALOR, POR_PESO };
