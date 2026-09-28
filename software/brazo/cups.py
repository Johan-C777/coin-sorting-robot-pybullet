"""Modelo de los vasos de monedas que maneja el brazo."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from .config import DENOMINACIONES, MASA_MONEDA_G, MASA_VASO_G, Puesto


@dataclass
class Vaso:
    """Un vaso lleno de monedas de una sola denominación."""
    denominacion: int
    monedas: int
    puesto: Optional[Puesto] = None

    @property
    def valor(self) -> int:
        """Valor total en pesos: V = n * d."""
        return self.denominacion * self.monedas

    @property
    def peso_g(self) -> float:
        """Masa total: m = m_vaso + n * m_moneda."""
        return MASA_VASO_G + self.monedas * MASA_MONEDA_G[self.denominacion]

    def como_dict(self) -> dict:
        return {
            "puesto": self.puesto.etiqueta if self.puesto else None,
            "den": self.denominacion,
            "n": self.monedas,
            "valor": self.valor,
            "peso_g": round(self.peso_g, 1),
        }

    def __str__(self) -> str:
        return f"${self.denominacion:,} x {self.monedas}".replace(",", ".")


# Criterios de orden que expone la app: nombre -> clave de comparación
CRITERIOS: Dict[str, Callable[[Vaso], float]] = {
    "denominacion": lambda v: v.denominacion,
    "cantidad": lambda v: v.monedas,
    "valor": lambda v: v.valor,
    "peso": lambda v: v.peso_g,
}


def lote_demo() -> List[Vaso]:
    """Lote fijo usado en la documentación y en las pruebas."""
    datos = [(500, 12), (100, 30), (1000, 8), (50, 25), (200, 17)]
    return [Vaso(d, n, Puesto("entrada", i)) for i, (d, n) in enumerate(datos)]


def lote_aleatorio(semilla: Optional[int] = None) -> List[Vaso]:
    """Cinco vasos, uno por denominación, con 6 a 40 monedas cada uno."""
    rng = random.Random(semilla)
    dens = DENOMINACIONES[:]
    rng.shuffle(dens)
    return [Vaso(d, rng.randint(6, 40), Puesto("entrada", i)) for i, d in enumerate(dens)]


def totales(vasos: List[Vaso]) -> dict:
    return {
        "monedas": sum(v.monedas for v in vasos),
        "valor": sum(v.valor for v in vasos),
        "peso_g": round(sum(v.peso_g for v in vasos), 1),
    }
