#pragma once
// Conversión de ángulos a servo y armado o lectura de la trama "S:...".
// Sin dependencias de Arduino para poder probarlo en el PC.
#include <stdint.h>
#include "config.h"
#include "cups.h"

namespace Protocolo {

// Ángulo articular -> ángulo de servo (0 a 180). J3 va montado invertido.
void angulosServo(const float q[N_JUNTAS], float pinzaMm, int16_t salida[N_CANALES]);

// Ancho de pulso en microsegundos: 500 + s/180 * 2000.
uint16_t microsegundos(float anguloServo);

// Escribe "S:j1,j2,j3,j4,j5,pinza" en destino. Devuelve los caracteres escritos.
uint8_t armarTrama(const float q[N_JUNTAS], float pinzaMm, char *destino, uint8_t capacidad);

// Lee una trama recibida. Devuelve false si el formato no cuadra.
bool leerTrama(const char *linea, int16_t salida[N_CANALES]);

// Lee el lote que manda el contador: "VASOS:50x30a9,100x20,..." donde
// "a9" (opcional) dice cuántas de las monedas son antiguas. Llena los vasos en
// la zona de entrada y devuelve cuántos leyó (0 si el formato no cuadra).
uint8_t leerVasos(const char *linea, Vaso vasos[N_PUESTOS]);

// Criterio de orden a partir de su nombre: "valor", "peso", "cantidad",
// "denominacion" o "antiguas". Si no lo reconoce devuelve POR_VALOR.
uint8_t criterioDeTexto(const char *texto);

}  // namespace Protocolo
