#pragma once
// Tolva (28BYJ-48 + ULN2003), compuerta (SG90) y banda (A4988 + NEMA17, etapa 2).
// Los pasos se generan en una tarea dedicada en el núcleo 0; loop() y la máquina de estados
// corren en el núcleo 1 y nunca esperan a un motor.
#include <Arduino.h>

#include "Rampa.h"

namespace hal {

void actuadoresIniciar();              // pines, servo y tarea de pasos

// Tolva
void tolvaBolsillos(float n);          // avanza n bolsillos sin acumular el error 2037,89 vs 2048
bool tolvaOcupada();
void tolvaParar();
Rampa &tolva();                        // para ajustar v0, vmax y acc desde la consola

// Compuerta
void compuerta(bool abierta);
void compuertaAngulo(int grados);      // calibración [CAL-10]

// Banda (no hace nada si HABILITAR_BANDA = 0)
void bandaVaso(int8_t vaso);           // 0..8 o -1 (rampa de rechazo)
void bandaMm(float mm);
bool bandaOcupada();
void bandaParar();

}  // namespace hal
