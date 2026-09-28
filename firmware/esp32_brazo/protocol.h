#pragma once
// Conversión de ángulos a servo y armado o lectura de la trama "S:...".
// Sin dependencias de Arduino para poder probarlo en el PC.
#include <stdint.h>
#include "config.h"

namespace Protocolo {

// Ángulo articular -> ángulo de servo (0 a 180). J3 va montado invertido.
void angulosServo(const float q[N_JUNTAS], float pinzaMm, int16_t salida[N_CANALES]);

// Ancho de pulso en microsegundos: 500 + s/180 * 2000.
uint16_t microsegundos(float anguloServo);

// Escribe "S:j1,j2,j3,j4,j5,pinza" en destino. Devuelve los caracteres escritos.
uint8_t armarTrama(const float q[N_JUNTAS], float pinzaMm, char *destino, uint8_t capacidad);

// Lee una trama recibida. Devuelve false si el formato no cuadra.
bool leerTrama(const char *linea, int16_t salida[N_CANALES]);

}  // namespace Protocolo
