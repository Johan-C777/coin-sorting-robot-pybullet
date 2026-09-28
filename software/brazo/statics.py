"""Pares estáticos en cada articulación y factores de seguridad de los servos.

El modelo de masas es el de la memoria de cálculo: son estimaciones de piezas
en PETG al 35 % de relleno más servos de catálogo. Cuando esté el CAD, se
reemplazan aquí y todo lo demás (README, figuras) se recalcula solo.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Sequence

from .config import D1, L1, L2, L3, MASA_MONEDA_G, MASA_VASO_G

G = 9.81
KGCM = 0.0980665          # 1 kg·cm en N·m

# masa (kg) y posición del centro de masa
MASA_ESLABON_1 = 0.045    # PETG + tornillería, a L1/2 del hombro
MASA_SERVO_CODO = 0.060   # en el eje del codo
MASA_ESLABON_2 = 0.035    # a L2/2 del codo
MASA_SERVO_MUNECA = 0.055  # en el eje de la muñeca
MASA_PINZA = 0.0568       # dos MG90S y los dedos, a 4 cm de la muñeca
BRAZO_PINZA = 4.0

# par de bloqueo a 6 V, en kg·cm
SERVOS: Dict[str, Dict[str, float]] = {
    "J1": {"modelo": "MG996R", "par": 11.0},
    "J2": {"modelo": "DS3235MG", "par": 32.0},
    "J3": {"modelo": "DS3218MG", "par": 20.4},
    "J4": {"modelo": "MG996R", "par": 11.0},
    "J5": {"modelo": "MG90S", "par": 2.2},
    "pinza": {"modelo": "MG90S", "par": 2.2},
}

ACEL_BASE = 3.295         # rad/s^2, pico del giro más largo (172 grados en 2,29 s)
MU_TPU = 0.5              # fricción de las almohadillas contra el vaso
FS_AGARRE = 1.5
RADIO_PINON = 0.01        # m, radio primitivo del engranaje de los dedos


def carga_vaso_kg(denominacion: int = 1000, monedas: int = 40) -> float:
    """Masa del vaso lleno, en kg. El caso de diseño son 40 monedas de $1.000."""
    return (MASA_VASO_G + monedas * MASA_MONEDA_G[denominacion]) / 1000.0


def _elementos(q: Sequence[float], carga: float):
    a2 = math.radians(q[1])
    a3 = a2 + math.radians(q[2])
    a4 = a3 + math.radians(q[3])
    xe = L1 * math.cos(a2)
    xw = xe + L2 * math.cos(a3)
    xt = xw + L3 * math.cos(a4)
    xa = xw + BRAZO_PINZA * math.cos(a4)
    return [
        (MASA_ESLABON_1, L1 / 2 * math.cos(a2)),
        (MASA_SERVO_CODO, xe),
        (MASA_ESLABON_2, xe + L2 / 2 * math.cos(a3)),
        (MASA_SERVO_MUNECA, xw),
        (MASA_PINZA, xa),
        (carga, xt),
    ], xe, xw


@dataclass
class Pares:
    """Pares requeridos en kg·cm."""
    base: float
    hombro: float
    codo: float
    muneca: float
    pinza: float

    def como_dict(self) -> Dict[str, float]:
        return {"J1": self.base, "J2": self.hombro, "J3": self.codo,
                "J4": self.muneca, "pinza": self.pinza}


def pares(q: Sequence[float], carga: float = None) -> Pares:
    """Par estático en cada articulación para la pose y la carga dadas."""
    carga = carga_vaso_kg() if carga is None else carga
    items, xe, xw = _elementos(q, carga)

    def momento(desde: int, x0: float) -> float:
        return sum(m * (x - x0) for m, x in items[desde:]) * G / 100 / KGCM

    inercia = sum(m * (x / 100) ** 2 for m, x in items)          # kg·m^2 sobre el eje vertical
    par_base = inercia * ACEL_BASE / KGCM
    fuerza = carga * G * FS_AGARRE / (2 * MU_TPU)                # N por dedo
    par_pinza = 2 * fuerza * RADIO_PINON / KGCM
    return Pares(par_base, momento(0, 0.0), momento(2, xe), abs(momento(4, xw)), par_pinza)


def factores_seguridad(q: Sequence[float], carga: float = None) -> Dict[str, float]:
    """Par de catálogo dividido por el par requerido, articulación por articulación."""
    p = pares(q, carga).como_dict()
    return {k: (SERVOS[k]["par"] / v if v > 0.01 else math.inf) for k, v in p.items()}


def momento_de_vuelco(q: Sequence[float], carga: float = None) -> float:
    """Momento sobre la base, en N·m. Sirve para dimensionar el anclaje."""
    return pares(q, carga).hombro * KGCM
