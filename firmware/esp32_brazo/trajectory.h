#pragma once
// Perfil quíntico y duración de los tramos. Mismos criterios que el PC.
#include "config.h"

namespace Trayectoria {

// s(tau) = 10 tau^3 - 15 tau^4 + 6 tau^5
float quintico(float tau);

// Picos del perfil: 1,875*d/T y 5,7735*d/T^2
float velocidadPico(float delta, float T);
float aceleracionPico(float delta, float T);

float duracionArticular(const float q0[N_JUNTAS], const float q1[N_JUNTAS], float vel);
float duracionLineal(const float p0[3], const float p1[3], float vel);

void interpolarArticular(const float q0[N_JUNTAS], const float q1[N_JUNTAS],
                         float s, float salida[N_JUNTAS]);
void interpolarLineal(const float p0[3], const float p1[3], float s, float salida[3]);

}  // namespace Trayectoria
