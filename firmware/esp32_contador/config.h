#pragma once
// Etapa 1: selección y conteo de monedas. Los números son los mismos de
// scripts/generar_stl.py y de la simulación HTML.
#include <stdint.h>

// El riel recibe monedas de las dos familias del Banco de la República: la
// nueva (2012) y la anterior (1989-1996). Ordenadas por diámetro quedan ocho
// estaciones; cada una recibe una sola combinación de denominación y familia,
// así que su barrera infrarroja cuenta también la familia. Las estaciones de
// la misma denominación descargan, por un colector, en el mismo vaso.
// Diseño y verificación en software/brazo/monedas.py y docs/07-monedas.md.
constexpr uint8_t N_ESTACIONES = 8;
constexpr uint8_t N_VASOS = 5;

enum Familia : uint8_t { NUEVA = 0, ANTIGUA = 1, AMBAS = 2 };

// un vaso por denominación, en este orden
constexpr uint16_t DENOMINACION_VASO[N_VASOS] = {50, 100, 200, 500, 1000};

// estación:                         1      2      3      4      5      6      7      8
//                                  N50   N100    A50   N200   A100   500    A200   N1000
constexpr uint8_t VASO_DE_ESTACION[N_ESTACIONES] = {0, 1, 0, 2, 1, 3, 2, 4};
constexpr Familia FAMILIA[N_ESTACIONES] = {NUEVA, NUEVA, ANTIGUA, NUEVA, ANTIGUA,
                                           AMBAS, ANTIGUA, NUEVA};
constexpr float DIAMETRO_MM[N_ESTACIONES] = {17.00f, 20.30f, 21.50f, 22.40f,
                                             23.00f, 23.70f, 24.40f, 26.70f};
constexpr float LUZ_MM[N_ESTACIONES] = {17.60f, 20.90f, 21.95f, 22.70f,
                                        23.35f, 24.05f, 25.00f, 27.30f};
constexpr float MASA_MONEDA_G[N_ESTACIONES] = {2.00f, 3.34f, 4.50f, 4.61f,
                                               5.31f, 7.14f, 7.08f, 9.95f};
constexpr float MASA_VASO_G = 18.0f;

// pines de las barreras infrarrojas, una por estación. Se evitan los pines de
// arranque (0, 2, 5, 12 y 15) y los de solo entrada (34 a 39, sin pull-up).
constexpr uint8_t PIN_SENSOR[N_ESTACIONES] = {32, 33, 25, 26, 27, 14, 13, 4};
constexpr uint32_t REBOTE_US = 25000;          // 25 ms entre monedas de la misma estación

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
constexpr float PASO_ESTACION_MM = 50.0f;     // 8 estaciones en 440 mm de riel
constexpr float VASOS_POR_TANDA = 5;
constexpr uint16_t MONEDAS_POR_VASO = 40;      // capacidad de un vaso lleno
