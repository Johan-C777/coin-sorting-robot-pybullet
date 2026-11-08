#pragma once
// Parámetros del sistema (no dependen de la moneda). Los marcados [CAL-xx] se ajustan
// con el prototipo armado; ver include/calibracion.h y README.md#calibración.
#include <stdint.h>

#include "Secuenciador.h"

#ifndef FW_VERSION
#define FW_VERSION "0.8.0-dev"
#endif

// ---- Barreras IR: modo de lectura ------------------------------------------------------
// BARRERAS_ADC      Timer por hardware a FS_BARRERAS_HZ -> ISR -> tarea que lee el ADC con
//                   base adaptativa e histéresis. Funciona con cualquier fototransistor.
// BARRERAS_DIGITAL  Interrupción por flanco en el GPIO (resolución de 1 µs). Requiere que el
//                   fototransistor sature (o una etapa 2N3904/LM393). Verificar con 'm'.
#define BARRERAS_ADC 0
#define BARRERAS_DIGITAL 1
#ifndef BARRERAS_MODO
#define BARRERAS_MODO BARRERAS_ADC   // [CAL-07] >>> pasar a DIGITAL si 'm' muestra niveles limpios
#endif
constexpr uint32_t FS_BARRERAS_HZ = 4000;      // 250 µs entre muestras: 0,12 mm a 500 mm/s
constexpr float UMBRAL_OCUPADA = 0.50f;        // [CAL-08] < 50 % de la base = haz cortado
constexpr float UMBRAL_LIBRE = 0.70f;          // [CAL-08] > 70 % = libre (histéresis)
constexpr float SEGUIMIENTO_BASE = 0.0005f;    // la base sigue la luz ambiente con el haz libre
constexpr uint32_t ANTIRREBOTE_US = 300;       // modo digital

// ---- Tolva: 28BYJ-48 en paso completo, 2 bobinas (máximo par) -------------------------
// Reductora real 63,68395:1 -> 2037,8868 pasos/vuelta. Se acumula la fracción.
constexpr float TOLVA_PASOS_VUELTA = 2037.8868f;
constexpr int BOLSILLOS = 5;                  // disco H02e (5 bolsillos Ø40)
constexpr int8_t TOLVA_SENTIDO = 1;            // [CAL-09] -1 si el disco gira al revés
constexpr float TOLVA_V0 = 180;                // [CAL-09] pasos/s de arranque (pull-in)
constexpr float TOLVA_VMAX = 800;              // [CAL-09] >>> barrido 't' con carga; usar 75 % del límite
constexpr float TOLVA_ACC = 2500;              // [CAL-09] pasos/s²
constexpr uint16_t TOLVA_PRE_MS = 15;          // bobinas energizadas antes del 1.er paso
constexpr uint16_t TOLVA_POST_MS = 60;         // reposo antes de soltar bobinas

// ---- Compuerta SG90 ---------------------------------------------------------------------
constexpr int SERVO_CERRADA = 0;               // [CAL-10] >>> paleta G02 horizontal
constexpr int SERVO_ABIERTA = 60;              // [CAL-10] >>> 60° abajo, la moneda cae derecho
constexpr int SERVO_US_MIN = 500, SERVO_US_MAX = 2400;

// ---- Banda (etapa 2) --------------------------------------------------------------------
#ifndef HABILITAR_BANDA
#define HABILITAR_BANDA 0                      // 1 cuando la banda esté montada
#endif
constexpr float BANDA_PASOS_MM = 33.3f;        // A4988 1/16 + NEMA17, cadena de tablillas (banda v3)
constexpr float BANDA_V0 = 400, BANDA_VMAX = 3300, BANDA_ACC = 20000;   // pasos/s, pasos/s²
constexpr float BANDA_PASO_VASO_MM = 40.0f;    // [CAL-11] >>> medir entre centros de V01 en C01
constexpr float BANDA_RECHAZO_MM = 342.0f;     // [CAL-11] posición de la rampa C02 (diseño de la banda)

// ---- Ciclo (ms) ---------------------------------------------------------------------------
constexpr seq::Temporizacion TEMPORIZACION = {
    /* espera_moneda        */ 1800,   // tras avanzar un bolsillo
    /* medicion_max         */ 1500,   // B1 entra -> B2 sale; más = atasco
    /* ventana_color        */ 150,    // muestreo del TCS3200 tras la medición
    /* llegada_compuerta    */ 500,    // [CAL-12] >>> fin de pista -> moneda quieta en G02 (video a 240 fps)
    /* compuerta_abierta    */ 350,    // [CAL-10]
    /* compuerta_cierre     */ 250,
    /* pausa_ciclo          */ 150,
    /* vacios_para_parar    */ 6,      // una vuelta del disco sin monedas
    /* reintentos_desatasco */ 1,
    /* retroceso_bolsillos  */ 0.25f,
};

// ---- TCS3200 ----------------------------------------------------------------------------
constexpr uint16_t TCS_VENTANA_MS = 4;         // conteo por filtro (R, G, B)
