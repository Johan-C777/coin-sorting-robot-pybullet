"""Protocolo entre el PC, el ESP32 y la simulación.

Nivel bajo: una línea de texto por pose.
    S:j1,j2,j3,j4,j5,pinza    (ángulos de servo, grados enteros)
Lote del contador al brazo, una línea:
    VASOS:500x12,100x30a10,...  (denominación x monedas, aN = de ellas antiguas)
Nivel alto: JSON por HTTP para la app Streamlit.
"""
from __future__ import annotations

from typing import Dict, List, Sequence

from .config import (PINZA_MAX_MM, PWM_MAX_US, PWM_MIN_US, Puesto)
from .cups import Vaso, totales

# Conversión de ángulo articular a ángulo de servo (0 a 180 grados).
# J3 va montado invertido, por eso el signo negativo.
DESFASES = [
    lambda q: q + 90.0,
    lambda q: q,
    lambda q: -q,
    lambda q: q + 120.0,
    lambda q: q + 90.0,
]


def angulos_servo(q: Sequence[float], pinza_mm: float) -> List[int]:
    """Ángulos que se envían al PCA9685, redondeados a grado entero."""
    s = [round(f(v)) for f, v in zip(DESFASES, q)]
    s.append(round(pinza_mm / PINZA_MAX_MM * 90.0))
    return s


def pwm_us(angulo_servo: float) -> int:
    """Ancho de pulso: 500 us + s/180 * 2000 us."""
    a = min(max(angulo_servo, 0.0), 180.0)
    return round(PWM_MIN_US + a / 180.0 * (PWM_MAX_US - PWM_MIN_US))


def trama(q: Sequence[float], pinza_mm: float) -> str:
    return "S:" + ",".join(str(v) for v in angulos_servo(q, pinza_mm))


def parsear_trama(linea: str) -> List[int]:
    """Inversa de trama(): devuelve los seis ángulos de servo."""
    linea = linea.strip()
    if not linea.startswith("S:"):
        raise ValueError("la trama debe empezar con 'S:'")
    partes = linea[2:].split(",")
    if len(partes) != 6:
        raise ValueError("la trama debe traer seis valores")
    return [int(round(float(p))) for p in partes]


def trama_vasos(vasos: Sequence[Vaso]) -> str:
    """Lote en el orden de la entrada: "VASOS:500x12,100x30a10,..."."""
    partes = []
    for v in vasos:
        partes.append(f"{v.denominacion}x{v.monedas}" + (f"a{v.antiguas}" if v.antiguas else ""))
    return "VASOS:" + ",".join(partes)


def parsear_vasos(linea: str) -> List[Vaso]:
    """Inversa de trama_vasos(): los vasos quedan en los puestos E1 a E5."""
    linea = linea.strip()
    if not linea.startswith("VASOS:"):
        raise ValueError("el lote debe empezar con 'VASOS:'")
    vasos = []
    for i, parte in enumerate(linea[6:].split(",")):
        den, _, resto = parte.partition("x")
        n, _, antiguas = resto.partition("a")
        try:
            vasos.append(Vaso(int(den), int(n), Puesto("entrada", i),
                              int(antiguas) if antiguas else 0))
        except ValueError as e:
            raise ValueError(f"vaso mal escrito: {parte!r}") from e
    return vasos


def estado_json(q: Sequence[float], pinza_mm: float, vasos: List[Vaso],
                estado: str = "listo", paso: int = 0, total: int = 0,
                criterio: str = "valor", sentido: str = "asc") -> Dict:
    """Cuerpo de GET /api/estado, el que consume el dashboard."""
    rack = sorted((v for v in vasos if v.puesto and v.puesto.zona == "rack"),
                  key=lambda v: v.puesto.indice)
    entrada = sorted((v for v in vasos if v.puesto and v.puesto.zona == "entrada"),
                     key=lambda v: v.puesto.indice)
    return {
        "estado": estado,
        "paso": paso,
        "total": total,
        "criterio": criterio,
        "sentido": sentido,
        "q": [round(v, 2) for v in q],
        "pinza_mm": round(pinza_mm, 1),
        "servos": angulos_servo(q, pinza_mm),
        "rack": [v.como_dict() for v in rack],
        "entrada": [v.como_dict() for v in entrada],
        "totales": totales(vasos),
    }
