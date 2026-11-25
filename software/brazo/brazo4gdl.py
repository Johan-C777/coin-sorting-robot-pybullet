"""Cinemática del brazo construido: 4 GDL con doble paralelogramo.

Geometría tomada del CAD (hardware/etapa3-brazo/brazo/generadores/generar_brazo_step.py):

  * J1 gira la torreta alrededor del eje vertical.
  * J2 mueve el brazo principal L1 (O1 -> E1). theta2 es su ángulo absoluto
    medido desde la horizontal.
  * J3 mueve la palanca 002; por el paralelogramo inferior el antebrazo L2
    (E1 -> W1) copia ese giro, así que theta3 también es absoluto desde la
    horizontal (no relativo a L1, como en un brazo serie).
  * El paralelogramo superior mantiene el soporte de muñeca 020 siempre
    horizontal: de W1 al eje de cabeceo hay L_PITCH en horizontal.
  * El SG90 de cabeceo inclina la garra un ángulo phi respecto a la
    horizontal (0 = al frente, -90 = hacia abajo). De ese eje a la punta de los
    dedos hay L3.

Unidades: milímetros y grados. z se mide desde la cara inferior de la base 010.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

# ---- medidas del CAD (mm) ----------------------------------------------------
Z_HOMBRO = 197.0      # eje O1 sobre la cara inferior de la base
L1 = 155.0            # brazo principal 004: O1 -> E1
L2 = 130.0            # antebrazo 005: E1 -> W1
L_PITCH = 28.0        # soporte de muñeca 020: W1 -> eje de cabeceo
L3 = 90.0             # eje de cabeceo -> punta de los dedos
R_PALANCA = 50.0      # palanca 002 y extensión trasera de 005

# ---- transmisión -------------------------------------------------------------
PASOS_MOTOR = 200            # NEMA 17 de 1,8°
MICROPASOS = 16              # A4984 de la RAMBo
REDUCCION = 16.0             # planetaria de dos etapas 4:1 x 4:1 (corona 30, planetas 10, sol 10)
PASOS_POR_GRADO = PASOS_MOTOR * MICROPASOS * REDUCCION / 360.0   # 142,22

# ---- límites (estimados del CAD; se fijan con la calibración física) ---------
LIM_J1 = (-135.0, 135.0)
LIM_J2 = (15.0, 165.0)               # brazo principal
LIM_J3 = (-75.0, 60.0)               # antebrazo
LIM_ANGULO_CODO = (20.0, 165.0)      # theta2 - theta3: el paralelogramo no se cruza
LIM_CABECEO = (-90.0, 45.0)


@dataclass(frozen=True)
class Pose:
    """Pose de la punta de los dedos (TCP)."""
    x: float
    y: float
    z: float
    cabeceo: float      # phi, grados

    @property
    def radio(self) -> float:
        return math.hypot(self.x, self.y)


@dataclass(frozen=True)
class Juntas:
    j1: float           # base
    j2: float           # theta2, brazo principal desde la horizontal
    j3: float           # theta3, antebrazo desde la horizontal
    cabeceo: float      # phi

    @property
    def angulo_codo(self) -> float:
        return self.j2 - self.j3


def directa(q: Juntas) -> Pose:
    """Cinemática directa: ángulos -> posición de la punta."""
    t1, t2, t3, ph = (math.radians(a) for a in (q.j1, q.j2, q.j3, q.cabeceo))
    rho = L1 * math.cos(t2) + L2 * math.cos(t3) + L_PITCH + L3 * math.cos(ph)
    z = Z_HOMBRO + L1 * math.sin(t2) + L2 * math.sin(t3) + L3 * math.sin(ph)
    return Pose(rho * math.cos(t1), rho * math.sin(t1), z, q.cabeceo)


def muneca(p: Pose) -> Tuple[float, float]:
    """Punto W1 (radio, altura) relativo al hombro O1."""
    ph = math.radians(p.cabeceo)
    rw = p.radio - L_PITCH - L3 * math.cos(ph)
    zw = p.z - Z_HOMBRO - L3 * math.sin(ph)
    return rw, zw


def inversa(p: Pose, verificar: bool = True) -> Juntas:
    """Cinemática inversa cerrada (codo arriba, la única que permite el paralelogramo)."""
    rw, zw = muneca(p)
    d2 = rw * rw + zw * zw
    c = (d2 - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    if not -1.0 <= c <= 1.0:
        raise ValueError(f"fuera de alcance: la muñeca queda a {math.sqrt(d2):.1f} mm del hombro "
                         f"(máximo {L1 + L2:.0f} mm, mínimo {abs(L1 - L2):.0f} mm)")
    q = math.acos(c)                                   # ángulo entre L1 y la prolongación de L2
    t2 = math.atan2(zw, rw) + math.atan2(L2 * math.sin(q), L1 + L2 * math.cos(q))
    t3 = t2 - q
    t1 = math.degrees(math.atan2(p.y, p.x))
    j = Juntas(t1, math.degrees(t2), math.degrees(t3), p.cabeceo)
    if verificar:
        problema = fuera_de_limites(j)
        if problema:
            raise ValueError(problema)
    return j


def fuera_de_limites(j: Juntas) -> Optional[str]:
    for nombre, valor, (lo, hi) in (("J1", j.j1, LIM_J1), ("J2", j.j2, LIM_J2),
                                    ("J3", j.j3, LIM_J3), ("cabeceo", j.cabeceo, LIM_CABECEO),
                                    ("ángulo del codo", j.angulo_codo, LIM_ANGULO_CODO)):
        if not lo - 1e-9 <= valor <= hi + 1e-9:
            return f"{nombre} = {valor:.1f}° fuera de [{lo:.0f}, {hi:.0f}]"
    return None


def alcanzable(p: Pose) -> bool:
    try:
        inversa(p)
        return True
    except ValueError:
        return False


# ---- G-code para la RAMBo (Marlin) --------------------------------------------
# Ejes de Marlin 2.1 (EXTRUDERS 0): X = banda (mm), Y = J1, Z = J2 y A = J3 (en el
# driver E0). Con los pasos por
# unidad en pasos/grado, una coordenada de Marlin es directamente un ángulo.
# CERO_* es el ángulo real del eslabón cuando Marlin marca 0 (G92 en la pose
# de arranque); se miden con la calibración.
CERO_J1 = 0.0
CERO_J2 = 90.0        # brazo principal vertical al encender
CERO_J3 = 0.0         # antebrazo horizontal al encender


def a_marlin(j: Juntas) -> Tuple[float, float, float]:
    return j.j1 - CERO_J1, j.j2 - CERO_J2, j.j3 - CERO_J3


def gcode_mover(j: Juntas, avance: float = 1200.0) -> str:
    y, z, e = a_marlin(j)
    return f"G1 Y{y:.2f} Z{z:.2f} A{e:.2f} F{avance:.0f}"


def gcode_secuencia(poses: Iterable[Pose], avance: float = 1200.0) -> List[str]:
    """Bloque de G-code que lleva la punta por las poses dadas y espera a terminar."""
    lineas = ["G90"]                      # coordenadas absolutas
    for p in poses:
        lineas.append(gcode_mover(inversa(p), avance))
    lineas.append("M400")
    return lineas


def alcance_horizontal(z: float, cabeceo: float = 0.0, paso: float = 1.0) -> Tuple[float, float]:
    """Radio mínimo y máximo de la punta a una altura z, respetando los límites."""
    radios = [r for r in (i * paso for i in range(0, int(600 / paso)))
              if alcanzable(Pose(r, 0.0, z, cabeceo))]
    if not radios:
        return (math.nan, math.nan)
    return (min(radios), max(radios))


if __name__ == "__main__":
    print(f"Pasos por grado: {PASOS_POR_GRADO:.2f}")
    for z in (60, 100, 150, 200):
        for ph in (0, -90):
            lo, hi = alcance_horizontal(z, ph)
            print(f"z = {z:3d} mm, cabeceo {ph:4d}°: radio de la punta {lo:.0f} a {hi:.0f} mm")
