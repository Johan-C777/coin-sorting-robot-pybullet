"""Cinemática directa e inversa del brazo de 5 GDL.

Convención (ver docs/02-cinematica.md):
  * theta1 gira alrededor del eje vertical, positivo hacia el rack.
  * theta2 se mide desde la horizontal, positivo levantando el brazo.
  * theta3 y theta4 son relativos al eslabón anterior.
  * phi = theta2 + theta3 + theta4 es el cabeceo absoluto de la pinza
    (-90 grados = apuntando hacia abajo).
"""
from __future__ import annotations

import math
from typing import List, Sequence, Tuple

from .config import (CABECEO_AGARRE, D1, L1, L2, L3, LIMITES, NOMBRES_JUNTAS,
                     R_ARCO)


class FueraDeAlcance(ValueError):
    """El punto pedido no tiene solución geométrica."""


class FueraDeLimite(ValueError):
    """Hay solución, pero alguna articulación se sale de su rango."""


def _envolver(a: float) -> float:
    return (a + 180.0) % 360.0 - 180.0


def dh_matrix(theta: float, d: float, a: float, alpha: float) -> List[List[float]]:
    """Matriz homogénea de un renglón de la tabla Denavit-Hartenberg estándar."""
    ct, st = math.cos(theta), math.sin(theta)
    ca, sa = math.cos(alpha), math.sin(alpha)
    return [
        [ct, -st * ca, st * sa, a * ct],
        [st, ct * ca, -ct * sa, a * st],
        [0.0, sa, ca, d],
        [0.0, 0.0, 0.0, 1.0],
    ]


def _mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def t05(q: Sequence[float]) -> List[List[float]]:
    """Matriz de transformación del TCP, por producto de las cinco matrices DH."""
    r = [math.radians(v) for v in q]
    tabla = [
        (r[0], D1, 0.0, math.pi / 2),
        (r[1], 0.0, L1, 0.0),
        (r[2], 0.0, L2, 0.0),
        (r[3] + math.pi / 2, 0.0, 0.0, math.pi / 2),
        (r[4], L3, 0.0, 0.0),
    ]
    T = dh_matrix(*tabla[0])
    for fila in tabla[1:]:
        T = _mul(T, dh_matrix(*fila))
    return T


def fk(q: Sequence[float]) -> Tuple[float, float, float, float]:
    """Cinemática directa cerrada. Devuelve (X, Y, Z, phi) del TCP."""
    q1, q2, q3, q4 = (math.radians(v) for v in q[:4])
    a3, a4 = q2 + q3, q2 + q3 + q4
    rho = L1 * math.cos(q2) + L2 * math.cos(a3) + L3 * math.cos(a4)
    z = D1 + L1 * math.sin(q2) + L2 * math.sin(a3) + L3 * math.sin(a4)
    return rho * math.cos(q1), rho * math.sin(q1), z, math.degrees(a4)


def puntos(q: Sequence[float]) -> dict:
    """Hombro, codo, muñeca y TCP en el plano (rho, z) del brazo."""
    q2, q3, q4 = (math.radians(v) for v in q[1:4])
    a3, a4 = q2 + q3, q2 + q3 + q4
    hombro = (0.0, D1)
    codo = (L1 * math.cos(q2), D1 + L1 * math.sin(q2))
    muneca = (codo[0] + L2 * math.cos(a3), codo[1] + L2 * math.sin(a3))
    tcp = (muneca[0] + L3 * math.cos(a4), muneca[1] + L3 * math.sin(a4))
    return {"hombro": hombro, "codo": codo, "muneca": muneca, "tcp": tcp}


def ik(x: float, y: float, z: float, phi: float = CABECEO_AGARRE,
       psi: float = 0.0, yaw_previo: float = 0.0) -> List[float]:
    """Cinemática inversa cerrada, solución de codo arriba.

    Lanza FueraDeAlcance o FueraDeLimite si la pose no es ejecutable.
    """
    r = math.hypot(x, y)
    q1 = yaw_previo if r < 1e-9 else math.degrees(math.atan2(y, x))
    p = math.radians(phi)
    rw = r - L3 * math.cos(p)          # centro de muñeca
    hw = z - D1 - L3 * math.sin(p)
    d = (rw * rw + hw * hw - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    if abs(d) > 1.0:
        raise FueraDeAlcance(f"punto ({x:.2f}, {y:.2f}, {z:.2f}) fuera del alcance")
    q3 = -math.acos(d)                 # raíz negativa: codo arriba
    q2 = math.atan2(hw, rw) - math.atan2(L2 * math.sin(q3), L1 + L2 * math.cos(q3))
    q = [q1, math.degrees(q2), math.degrees(q3),
         _envolver(phi - math.degrees(q2 + q3)), psi]
    for i, (lo, hi) in enumerate(LIMITES):
        if not lo - 1e-6 <= q[i] <= hi + 1e-6:
            raise FueraDeLimite(f"{NOMBRES_JUNTAS[i]} fuera de límite: {q[i]:.2f} grados")
        q[i] = min(max(q[i], lo), hi)
    return q


def alcanzable(x: float, y: float, z: float, phi: float = CABECEO_AGARRE) -> bool:
    try:
        ik(x, y, z, phi)
        return True
    except (FueraDeAlcance, FueraDeLimite):
        return False


def jacobiano(q: Sequence[float]) -> List[List[float]]:
    """Jacobiano plano de (rho, z, phi) respecto a (theta2, theta3, theta4)."""
    q2, q3, q4 = (math.radians(v) for v in q[1:4])
    a3, a4 = q2 + q3, q2 + q3 + q4
    s2, c2 = math.sin(q2), math.cos(q2)
    s23, c23 = math.sin(a3), math.cos(a3)
    s234, c234 = math.sin(a4), math.cos(a4)
    return [
        [-L1 * s2 - L2 * s23 - L3 * s234, -L2 * s23 - L3 * s234, -L3 * s234],
        [L1 * c2 + L2 * c23 + L3 * c234, L2 * c23 + L3 * c234, L3 * c234],
        [1.0, 1.0, 1.0],
    ]


def det_jacobiano(q: Sequence[float]) -> float:
    """det(J) = L1 * L2 * sen(theta3): se anula solo con el brazo estirado."""
    return L1 * L2 * math.sin(math.radians(q[2]))


def pose_puesto(yaw: float, z: float, radio: float = R_ARCO) -> Tuple[float, float, float]:
    """Coordenadas del TCP sobre el arco de puestos, a la altura indicada."""
    return (radio * math.cos(math.radians(yaw)),
            radio * math.sin(math.radians(yaw)), z)
