"""Construye la celda de trabajo en PyBullet: mesa, bandejas y vasos."""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "software"))

import pybullet as p                                    # noqa: E402

from brazo.config import (MASA_MONEDA_G, MASA_VASO_G, R_ARCO, SUPERFICIE,
                          YAW_ENTRADA, YAW_RACK)         # noqa: E402
from brazo.cups import Vaso                              # noqa: E402

COLOR_DEN = {50: [0.31, 0.49, 0.69, 0.75], 100: [0.23, 0.58, 0.40, 0.75],
             200: [0.52, 0.35, 0.69, 0.75], 500: [0.82, 0.60, 0.07, 0.75],
             1000: [0.77, 0.25, 0.18, 0.75]}
RADIO_VASO = 0.026      # m
ALTO_VASO = 0.08        # m


def xy_puesto(yaw_grados: float, radio: float = R_ARCO) -> List[float]:
    """Centro de un puesto, en metros."""
    r = radio / 100.0
    return [r * math.cos(math.radians(yaw_grados)), r * math.sin(math.radians(yaw_grados))]


def crear_bandejas() -> List[int]:
    """Discos delgados que marcan los diez puestos."""
    ids = []
    grosor = SUPERFICIE / 100.0
    for zona, yaws in (("entrada", YAW_ENTRADA), ("rack", YAW_RACK)):
        color = [0.20, 0.35, 0.48, 1] if zona == "rack" else [0.35, 0.37, 0.36, 1]
        for yaw in yaws:
            x, y = xy_puesto(yaw)
            vis = p.createVisualShape(p.GEOM_CYLINDER, radius=0.042, length=grosor,
                                      rgbaColor=color)
            col = p.createCollisionShape(p.GEOM_CYLINDER, radius=0.042, height=grosor)
            ids.append(p.createMultiBody(0, col, vis, [x, y, grosor / 2]))
    return ids


def crear_vaso(vaso: Vaso) -> int:
    """Un vaso con la masa real de su contenido, en su puesto de entrada."""
    masa = (MASA_VASO_G + vaso.monedas * MASA_MONEDA_G[vaso.denominacion]) / 1000.0
    x, y = xy_puesto(vaso.puesto.yaw)
    z = SUPERFICIE / 100.0 + ALTO_VASO / 2
    vis = p.createVisualShape(p.GEOM_CYLINDER, radius=RADIO_VASO, length=ALTO_VASO,
                              rgbaColor=COLOR_DEN[vaso.denominacion])
    col = p.createCollisionShape(p.GEOM_CYLINDER, radius=RADIO_VASO, height=ALTO_VASO)
    cuerpo = p.createMultiBody(masa, col, vis, [x, y, z])
    p.changeDynamics(cuerpo, -1, lateralFriction=0.9, spinningFriction=0.01)
    return cuerpo


def crear_celda(vasos: List[Vaso]) -> Dict[int, int]:
    """Devuelve el mapa índice de vaso -> id del cuerpo en PyBullet."""
    crear_bandejas()
    return {i: crear_vaso(v) for i, v in enumerate(vasos)}
