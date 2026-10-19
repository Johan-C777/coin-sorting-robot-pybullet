#pragma once
// Etapa 1: selección y conteo de monedas. La geometría sale de
// scripts/generar_clasificador.py (hardware/stl/); si se cambia una ranura allá,
// se cambia aquí.
#include <stdint.h>

// El riel separa por diámetro en siete ranuras y un extremo abierto. La ranura 6
// recibe las dos monedas de $500 y la bifurcación activa (sensor de color + aguja
// SG90) las reparte en dos ductos. Total: nueve ductos de salida, cada uno con su
// barrera infrarroja y una sola combinación de denominación y familia. Los
// ductos de la misma denominación descargan en el mismo vaso.
constexpr uint8_t N_ESTACIONES = 9;            // ductos de salida con barrera IR
constexpr uint8_t N_VASOS = 5;

enum Familia : uint8_t { NUEVA = 0, ANTIGUA = 1 };

// un vaso por denominación, en este orden
constexpr uint16_t DENOMINACION_VASO[N_VASOS] = {50, 100, 200, 500, 1000};

// ducto:                         1      2      3      4      5      6      7      8      9
//                               N50   N100    A50   N200   A100   A500   N500   A200  N1000
// ranura del riel:               1      2      3      4      5      6      6      7    final
constexpr uint8_t VASO_DE_ESTACION[N_ESTACIONES] = {0, 1, 0, 2, 1, 3, 3, 2, 4};
constexpr Familia FAMILIA[N_ESTACIONES] = {NUEVA, NUEVA, ANTIGUA, NUEVA, ANTIGUA,
                                           ANTIGUA, NUEVA, ANTIGUA, NUEVA};
constexpr float DIAMETRO_MM[N_ESTACIONES] = {17.00f, 20.30f, 21.00f, 22.40f, 23.00f,
                                             23.50f, 23.70f, 24.40f, 26.70f};
constexpr uint8_t RANURA_DE_ESTACION[N_ESTACIONES] = {0, 1, 2, 3, 4, 5, 5, 6, 7};
constexpr uint8_t N_RANURAS = 8;               // 7 ranuras + extremo abierto
constexpr float RANURA_MM[N_RANURAS] = {17.5f, 20.8f, 21.5f, 22.9f, 23.4f,
                                        24.1f, 24.9f, 0.0f};   // 0 = extremo abierto
constexpr float MASA_MONEDA_G[N_ESTACIONES] = {2.00f, 3.34f, 4.50f, 4.61f, 5.31f,
                                               7.43f, 7.14f, 7.08f, 9.95f};
constexpr float MASA_VASO_G = 18.0f;
constexpr uint8_t ESTACION_A500 = 5;
constexpr uint8_t ESTACION_N500 = 6;

// ---------------------------------------------------------------------------
// Pines (ESP32 DevKit V1, 30 pines). Se evitan los de arranque 0, 2, 5, 12 y 15.
// Barreras IR: LED IR + fototransistor a través del ducto, salida con pull-up
// EXTERNO de 10 k a 3,3 V (34-39 no tienen pull-up interno). Haz libre = bajo,
// moneda = alto -> flanco de SUBIDA. Con módulos TCRT5000/LM393 usar FALLING.
// 36 y 39 dan pulsos falsos si el Wi-Fi duerme: el .ino apaga el modem-sleep.
// ---------------------------------------------------------------------------
constexpr uint8_t PIN_SENSOR[N_ESTACIONES] = {34, 35, 36, 39, 32, 33, 25, 26, 27};
constexpr int FLANCO_MONEDA = 0x01;            // RISING (0x02 = FALLING)
constexpr uint32_t REBOTE_US = 25000;          // 25 ms entre monedas del mismo ducto

// I2C del sensor de color TCS34725 (dirección 0x29)
constexpr uint8_t PIN_SDA = 21;
constexpr uint8_t PIN_SCL = 22;

// tolva: 28BYJ-48 por ULN2003 (IN1..IN4). Con TOLVA_SG90_CONTINUO se usa un
// SG90 modificado a rotación continua en PIN_TOLVA_SG90.
constexpr uint8_t PIN_TOLVA[4] = {16, 17, 18, 19};
constexpr uint8_t PIN_TOLVA_SG90 = 18;
constexpr uint8_t CAVIDADES_DISCO = 4;
constexpr uint16_t PASOS_VUELTA_28BYJ = 4076;  // medio paso, reductora 63,68:1
constexpr int8_t SENTIDO_TOLVA = 1;            // -1 si el disco gira al revés
constexpr float PERIODO_MONEDA_S = 1.5f;       // una moneda cada 1,5 s
constexpr float RITMO_MAX = 0.9f;              // monedas/s que aguanta el 28BYJ-48
constexpr uint8_t CANAL_TOLVA = 0;
constexpr uint16_t TOLVA_SG90_PARADO_US = 1500;
constexpr uint16_t TOLVA_SG90_US_POR_RPM = 4;  // calibrar: µs sobre el neutro por rpm

// aguja de la bifurcación de $500: SG90 por LEDC
constexpr uint8_t PIN_AGUJA = 13;
constexpr uint8_t CANAL_AGUJA = 2;
constexpr uint8_t AGUJA_A500_GRADOS = 55;      // plato inclinado hacia -X: $500 antigua
constexpr uint8_t AGUJA_N500_GRADOS = 125;     // plato inclinado hacia +X: $500 nueva
constexpr uint16_t AGUJA_RETORNO_MS = 600;     // vuelve a la posición antigua si no llega la moneda

// banda: puente H L298N (19 y 21 quedaron para la tolva y el I2C)
constexpr uint8_t PIN_BANDA_A = 14;
constexpr uint8_t PIN_BANDA_B = 4;
constexpr uint8_t PIN_BANDA_PWM = 23;
constexpr uint8_t CANAL_BANDA = 1;
constexpr uint16_t BANDA_PWM_MIN = 120;        // de 0 a 255, por debajo no arranca

// celda
constexpr float VASOS_POR_TANDA = 5;
constexpr uint16_t MONEDAS_POR_VASO = 40;      // capacidad de un vaso lleno
