"""Generación de trayectorias con perfil quíntico.

Un movimiento se parte en tramos. Cada tramo sabe cuánto dura y qué pose
entregar en cada instante, de modo que el ejecutor solo muestrea a 50 Hz.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence, Tuple

from .config import (CABECEO_AGARRE, PINZA_ABIERTA_MM, PINZA_CERRADA_MM,
                     T_MINIMA_ARTICULAR, T_MINIMA_LINEAL, VEL_ARTICULAR,
                     VEL_LINEAL, Z_AGARRE, Z_SEGURA, Puesto)
from .kinematics import ik, pose_puesto


def quintico(tau: float) -> float:
    """s(tau) = 10*tau^3 - 15*tau^4 + 6*tau^5, con velocidad y aceleración nulas en los extremos."""
    tau = min(max(tau, 0.0), 1.0)
    return tau ** 3 * (10 + tau * (-15 + 6 * tau))


def perfil(delta: float, T: float, t: float) -> Tuple[float, float, float]:
    """Posición, velocidad y aceleración del perfil quíntico en el instante t."""
    tau = min(max(t / T, 0.0), 1.0)
    pos = delta * quintico(tau)
    vel = delta / T * (30 * tau ** 2 - 60 * tau ** 3 + 30 * tau ** 4)
    acc = delta / T ** 2 * (60 * tau - 180 * tau ** 2 + 120 * tau ** 3)
    return pos, vel, acc


def picos(delta: float, T: float) -> Tuple[float, float]:
    """Velocidad y aceleración máximas del perfil: 1,875*d/T y 5,7735*d/T^2."""
    return 1.875 * abs(delta) / T, 5.7735 * abs(delta) / T ** 2


@dataclass
class Tramo:
    """Un tramo de movimiento evaluable en el tiempo."""
    tipo: str                      # 'articular', 'lineal' o 'pinza'
    duracion: float
    descripcion: str
    evaluar: Callable[[float], Tuple[List[float], float]] = field(repr=False)

    def fin(self) -> Tuple[List[float], float]:
        return self.evaluar(self.duracion)


def duracion_articular(q0: Sequence[float], q1: Sequence[float], vel: float = 1.0) -> float:
    dq = max(abs(b - a) for a, b in zip(q0, q1))
    return max(T_MINIMA_ARTICULAR, dq / (VEL_ARTICULAR * vel))


def duracion_lineal(p0: Sequence[float], p1: Sequence[float], vel: float = 1.0) -> float:
    d = math.dist(p0, p1)
    return max(T_MINIMA_LINEAL, d / (VEL_LINEAL * vel))


def tramo_articular(q0: Sequence[float], q1: Sequence[float], pinza: float,
                    vel: float = 1.0, descripcion: str = "movimiento articular") -> Tramo:
    T = duracion_articular(q0, q1, vel)

    def evaluar(t: float):
        s = quintico(t / T)
        return [a + (b - a) * s for a, b in zip(q0, q1)], pinza

    return Tramo("articular", T, descripcion, evaluar)


def tramo_lineal(p0: Sequence[float], p1: Sequence[float], pinza: float,
                 phi: float = CABECEO_AGARRE, vel: float = 1.0,
                 descripcion: str = "movimiento lineal") -> Tramo:
    """Interpolación recta del TCP; la pose articular sale de la inversa."""
    T = duracion_lineal(p0, p1, vel)

    def evaluar(t: float):
        s = quintico(t / T)
        p = [a + (b - a) * s for a, b in zip(p0, p1)]
        return ik(p[0], p[1], p[2], phi), pinza

    return Tramo("lineal", T, descripcion, evaluar)


def tramo_pinza(q: Sequence[float], desde: float, hasta: float,
                vel: float = 1.0, descripcion: str = "pinza") -> Tramo:
    T = max(0.25, abs(hasta - desde) / (90.0 * vel))

    def evaluar(t: float):
        return list(q), desde + (hasta - desde) * quintico(t / T)

    return Tramo("pinza", T, descripcion, evaluar)


def ciclo_pick_place(origen: Puesto, destino: Puesto, q_inicial: Sequence[float],
                     vel: float = 1.0) -> List[Tramo]:
    """Los ocho tramos que mueven un vaso de un puesto a otro."""
    p_alto_o = pose_puesto(origen.yaw, Z_SEGURA)
    p_bajo_o = pose_puesto(origen.yaw, Z_AGARRE)
    p_alto_d = pose_puesto(destino.yaw, Z_SEGURA)
    p_bajo_d = pose_puesto(destino.yaw, Z_AGARRE + 0.25)   # holgura al soltar

    q_alto_o = ik(*p_alto_o)
    q_alto_d = ik(*p_alto_d)
    q_bajo_o = ik(*p_bajo_o)
    q_bajo_d = ik(*p_bajo_d)

    return [
        tramo_articular(q_inicial, q_alto_o, PINZA_ABIERTA_MM, vel,
                        f"ir sobre {origen}"),
        tramo_lineal(p_alto_o, p_bajo_o, PINZA_ABIERTA_MM, vel=vel,
                     descripcion="bajar al vaso"),
        tramo_pinza(q_bajo_o, PINZA_ABIERTA_MM, PINZA_CERRADA_MM, vel, "cerrar pinza"),
        tramo_lineal(p_bajo_o, p_alto_o, PINZA_CERRADA_MM, vel=vel,
                     descripcion="subir con el vaso"),
        tramo_articular(q_alto_o, q_alto_d, PINZA_CERRADA_MM, vel,
                        f"trasladar a {destino}"),
        tramo_lineal(p_alto_d, p_bajo_d, PINZA_CERRADA_MM, vel=vel,
                     descripcion="bajar al puesto"),
        tramo_pinza(q_bajo_d, PINZA_CERRADA_MM, PINZA_ABIERTA_MM, vel, "abrir pinza"),
        tramo_lineal(p_bajo_d, p_alto_d, PINZA_ABIERTA_MM, vel=vel,
                     descripcion="subir libre"),
    ]


def muestrear(tramos: List[Tramo], dt: float = 0.02):
    """Recorre los tramos y entrega (t_global, q, pinza_mm) cada dt segundos."""
    t_global = 0.0
    for tr in tramos:
        n = max(1, int(round(tr.duracion / dt)))
        for k in range(1, n + 1):
            t = tr.duracion * k / n
            q, pinza = tr.evaluar(t)
            yield t_global + t, q, pinza
        t_global += tr.duracion


def duracion_total(tramos: List[Tramo]) -> float:
    return sum(tr.duracion for tr in tramos)
