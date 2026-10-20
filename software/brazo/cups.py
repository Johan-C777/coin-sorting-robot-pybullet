"""Modelo de los vasos de monedas que maneja el brazo."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from .config import (MASA_MONEDA_ANTIGUA_G, MASA_MONEDA_G, MASA_VASO_G, TIPOS_VASO,
                     Puesto)


@dataclass
class Vaso:
    """Un vaso con monedas de una sola denominación.

    Desde la etapa 1 física cada vaso recibe un solo tipo de moneda (por
    ejemplo, $200 antigua), así que ``antiguas`` vale 0 o ``monedas``. El
    modelo admite mezclas porque el peso depende de ello: una $200 antigua
    pesa 7,08 g y una nueva 4,61 g.
    """
    denominacion: int
    monedas: int
    puesto: Optional[Puesto] = None
    antiguas: int = 0

    def __post_init__(self):
        if not 0 <= self.antiguas <= self.monedas:
            raise ValueError("las antiguas no pueden superar el total del vaso")
        if self.antiguas and self.denominacion not in MASA_MONEDA_ANTIGUA_G:
            raise ValueError(f"la ${self.denominacion} antigua no la admite el selector")

    @property
    def nuevas(self) -> int:
        return self.monedas - self.antiguas

    @property
    def valor(self) -> int:
        """Valor total en pesos: V = n * d."""
        return self.denominacion * self.monedas

    @property
    def peso_g(self) -> float:
        """Masa total: m = m_vaso + n_nuevas * m_nueva + n_antiguas * m_antigua."""
        antigua = MASA_MONEDA_ANTIGUA_G.get(self.denominacion, 0.0)
        return (MASA_VASO_G + self.nuevas * MASA_MONEDA_G[self.denominacion]
                + self.antiguas * antigua)

    def como_dict(self) -> dict:
        return {
            "puesto": self.puesto.etiqueta if self.puesto else None,
            "den": self.denominacion,
            "n": self.monedas,
            "nuevas": self.nuevas,
            "antiguas": self.antiguas,
            "valor": self.valor,
            "peso_g": round(self.peso_g, 1),
        }

    def __str__(self) -> str:
        texto = f"${self.denominacion:,} x {self.monedas}".replace(",", ".")
        return texto + (f" ({self.antiguas} antiguas)" if self.antiguas else "")


# Criterios de orden que expone la app: nombre -> clave de comparación
CRITERIOS: Dict[str, Callable[[Vaso], float]] = {
    "denominacion": lambda v: v.denominacion,
    "cantidad": lambda v: v.monedas,
    "valor": lambda v: v.valor,
    "peso": lambda v: v.peso_g,
    "antiguas": lambda v: v.antiguas,
}


def lote_demo() -> List[Vaso]:
    """Lote fijo usado en la documentación y en las pruebas: los nueve vasos.

    (denominación, monedas, de ellas antiguas). Un vaso por tipo de moneda; la
    $1.000 antigua no se admite en el riel.
    """
    datos = [(500, 12, 12), (100, 30, 0), (1000, 8, 0), (50, 25, 0), (200, 17, 0),
             (100, 10, 10), (50, 9, 9), (500, 8, 0), (200, 6, 6)]
    return [Vaso(d, n, Puesto("entrada", i), a) for i, (d, n, a) in enumerate(datos)]


def lote_aleatorio(semilla: Optional[int] = None) -> List[Vaso]:
    """Nueve vasos, uno por tipo de moneda, con 6 a 40 monedas cada uno."""
    rng = random.Random(semilla)
    tipos = TIPOS_VASO[:]
    rng.shuffle(tipos)
    vasos = []
    for i, (d, antigua) in enumerate(tipos):
        n = rng.randint(6, 40)
        vasos.append(Vaso(d, n, Puesto("entrada", i), n if antigua else 0))
    return vasos


def totales(vasos: List[Vaso]) -> dict:
    return {
        "monedas": sum(v.monedas for v in vasos),
        "antiguas": sum(v.antiguas for v in vasos),
        "valor": sum(v.valor for v in vasos),
        "peso_g": round(sum(v.peso_g for v in vasos), 1),
    }
