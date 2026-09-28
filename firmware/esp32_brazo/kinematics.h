#pragma once
// Cinemática directa e inversa, idéntica a software/brazo/kinematics.py.
#include <stdint.h>
#include "config.h"

struct ResultadoIK {
  bool ok;              // hay solución y respeta los límites
  int8_t junta;         // articulación que se sale (-1 si el fallo es de alcance)
  float q[N_JUNTAS];
};

namespace Cinematica {

// Devuelve la posición del TCP y el cabeceo absoluto de la pinza.
void fk(const float q[N_JUNTAS], float &x, float &y, float &z, float &phi);

// Solución cerrada de codo arriba. yawPrevio se usa si el punto cae sobre el eje.
ResultadoIK ik(float x, float y, float z, float phi = CABECEO,
               float psi = 0.0f, float yawPrevio = 0.0f);

// Centro de un puesto del arco, a la altura pedida.
void posePuesto(float yaw, float z, float &x, float &y);

// det(J) = L1*L2*sen(theta3): sirve para vigilar la singularidad del brazo estirado.
float detJacobiano(const float q[N_JUNTAS]);

}  // namespace Cinematica
