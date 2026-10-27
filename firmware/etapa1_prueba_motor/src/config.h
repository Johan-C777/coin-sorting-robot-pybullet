#pragma once
// Etapa 1 (tolva + clasificador v5) y banda (etapa 2) en ESP32-S3 DevKitC-1.
// Pines que NO se usan: 0,3,45,46 (strapping), 19,20 (USB), 26-37 (flash/PSRAM octal),
// 43,44 (UART0), 48 (LED RGB de la placa).
#include <Arduino.h>

// ---- Pines ----------------------------------------------------------------
constexpr uint8_t PIN_TOLVA[4] = {4, 5, 6, 7};  // ULN2003 IN1..IN4
constexpr uint8_t PIN_SERVO    = 15;            // SG90 compuerta (5 V externos)
constexpr uint8_t PIN_IR1      = 1;             // fototransistor barrera 1 (ADC1_CH0)
constexpr uint8_t PIN_IR2      = 2;             // fototransistor barrera 2 (ADC1_CH1)
constexpr uint8_t PIN_IR_REF   = 13;            // haz de referencia de la banda
constexpr uint8_t PIN_SDA      = 8;             // TCS34725
constexpr uint8_t PIN_SCL      = 9;
constexpr uint8_t PIN_STEP     = 10;            // A4988 (banda)
constexpr uint8_t PIN_DIR      = 11;
constexpr uint8_t PIN_EN       = 12;            // activo en bajo
// libres si hacen falta: 14, 16, 17, 18, 21, 38, 39, 40, 41, 42, 47

// ---- Tolva: 28BYJ-48 en PASO COMPLETO, 2 bobinas (máx. torque y velocidad) -----
// Reductora real 63,68395:1 -> 2037,8868 pasos/vuelta (no 2048). Se acumula la
// fracción para que el disco no se desfase tras muchas vueltas.
constexpr float  TOLVA_PASOS_VUELTA = 2037.8868f;
constexpr int    BOLSILLOS          = 8;
constexpr int8_t TOLVA_SENTIDO      = 1;        // -1 si el disco gira al revés
constexpr float  TOLVA_V0   = 180;               // pasos/s de arranque/parada (pull-in)
constexpr float  TOLVA_VMAX = 800;               // pasos/s de crucero; sube con 'v'
constexpr float  TOLVA_ACC  = 2500;              // pasos/s²
constexpr uint16_t TOLVA_PRE_MS  = 15;           // bobinas energizadas antes del 1er paso
constexpr uint16_t TOLVA_POST_MS = 60;           // reposo antes de soltar bobinas

// ---- Compuerta SG90 ---------------------------------------------------------
constexpr int SERVO_CERRADA = 0;                 // paleta horizontal
constexpr int SERVO_ABIERTA = 60;                // 60° hacia abajo
constexpr int SERVO_US_MIN = 500, SERVO_US_MAX = 2400;
constexpr uint16_t COMPUERTA_ABIERTA_MS = 350;   // tiempo abierta para soltar la moneda
constexpr uint16_t LLEGADA_MONEDA_MS = 500;      // fin de la pista -> moneda sobre la compuerta

// ---- Barreras IR y medición ---------------------------------------------------
constexpr float SEP_BARRERAS_MM = 24.0f;         // 105 -> 129 mm sobre la pista
constexpr float UMBRAL_OCUPADA = 0.50f;          // < 50 % de la base = haz cortado
constexpr float UMBRAL_LIBRE   = 0.70f;          // > 70 % = haz libre (histéresis)
constexpr uint32_t T_PUENTE_MAX_US = 400000;      // máx. entre salida B1 y entrada B2

// ---- Monedas: [nombre, diámetro, vaso 0..8 según orden del cartucho] ----------
struct Tipo { const char *nombre; float cuerda_mm; };
// Cuerda medida = diámetro * K_CUERDA (calibrar con 'c' y monedas reales).
constexpr float K_CUERDA = 1.0f;
constexpr Tipo TIPOS[9] = {                       // índice = vaso en el cartucho
    {"$50 N", 17.0f},  {"$100 N", 20.3f}, {"$50 A", 21.5f},
    {"$200 N", 22.4f}, {"$100 A", 23.0f}, {"$500 A", 23.7f},
    {"$500 N", 23.7f}, {"$200 A", 24.4f}, {"$1000 N", 26.7f}};
constexpr int V_500A = 5, V_500N = 6;
constexpr float TOLERANCIA_MM = 0.6f;            // fuera de esto -> rechazo
constexpr float UMBRAL_DORADO = 1.30f;           // (R+G)/2B > umbral = dorado (calibrar)
constexpr int   VASO_RECHAZO = -1;

// ---- Ciclo -----------------------------------------------------------------
constexpr uint16_t ESPERA_MONEDA_MS = 1800;      // tras avanzar un bolsillo
constexpr uint8_t  VACIOS_PARA_PARAR = 8;        // una vuelta sin monedas = tolva vacía

// ---- Banda (A4988 1/16 + NEMA17). Desactivada por defecto. ------------------------
#define HABILITAR_BANDA 0
constexpr float BANDA_PASOS_MM = 33.3f;          // cadena de tablillas (ESTADO)
constexpr float BANDA_V0 = 400, BANDA_VMAX = 3300, BANDA_ACC = 20000;  // pasos/s, /s²
constexpr float BANDA_PITCH_MM = 40.0f;          // PROVISIONAL: separación entre vasos
constexpr float BANDA_RECHAZO_MM = 342.0f;       // ESTADO: posición de la rampa C02
