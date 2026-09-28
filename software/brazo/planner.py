"""Planificador de orden: decide qué vaso va a cada puesto y cómo llegar ahí.

Regla del algoritmo (docs/01-arquitectura.md):
  1. Ordenar los vasos por la clave elegida, desempatando por denominación.
  2. Recorrer los puestos del rack del 1 al 5.
  3. Si el vaso correcto ya está en su puesto, no se toca.
  4. Si el puesto está ocupado por otro, ese otro se lleva a un hueco libre
     de la entrada.
  5. Mover el vaso correcto desde donde esté hasta el puesto.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .config import Puesto
from .cups import CRITERIOS, Vaso


@dataclass
class Movimiento:
    """Un traslado de un vaso entre dos puestos."""
    vaso: int            # índice dentro de la lista de vasos
    origen: Puesto
    destino: Puesto
    motivo: str = "orden"   # 'orden' o 'liberar'

    def describir(self, vasos: List[Vaso]) -> str:
        v = vasos[self.vaso]
        extra = " (libera el puesto)" if self.motivo == "liberar" else ""
        return f"Vaso de {v} de {self.origen} a {self.destino}{extra}"


def orden_objetivo(vasos: List[Vaso], criterio: str = "valor",
                   sentido: str = "asc") -> List[int]:
    """Índices de los vasos en el orden en que deben quedar en el rack."""
    if criterio not in CRITERIOS:
        raise ValueError(f"criterio desconocido: {criterio}")
    clave = CRITERIOS[criterio]
    signo = 1 if sentido == "asc" else -1
    return sorted(range(len(vasos)),
                  key=lambda i: (signo * clave(vasos[i]), signo * vasos[i].denominacion))


def planificar(vasos: List[Vaso], criterio: str = "valor",
               sentido: str = "asc") -> List[Movimiento]:
    """Secuencia mínima de movimientos para dejar el rack ordenado."""
    objetivo = orden_objetivo(vasos, criterio, sentido)
    pos: List[Optional[Puesto]] = [v.puesto for v in vasos]
    rack: List[Optional[int]] = [None] * 5
    entrada: List[Optional[int]] = [None] * 5
    for i, p in enumerate(pos):
        if p is None:
            continue
        (rack if p.zona == "rack" else entrada)[p.indice] = i

    movimientos: List[Movimiento] = []
    for j, idx in enumerate(objetivo):
        actual = pos[idx]
        if actual is not None and actual.zona == "rack" and actual.indice == j:
            continue
        ocupante = rack[j]
        if ocupante is not None and ocupante != idx:
            hueco = entrada.index(None)
            destino = Puesto("entrada", hueco)
            movimientos.append(Movimiento(ocupante, pos[ocupante], destino, "liberar"))
            entrada[hueco] = ocupante
            rack[j] = None
            pos[ocupante] = destino
        origen = pos[idx]
        if origen is not None:
            (rack if origen.zona == "rack" else entrada)[origen.indice] = None
        destino = Puesto("rack", j)
        movimientos.append(Movimiento(idx, origen, destino))
        rack[j] = idx
        pos[idx] = destino
    return movimientos


def aplicar(vasos: List[Vaso], movimientos: List[Movimiento]) -> None:
    """Actualiza la posición de los vasos como si el brazo ya hubiera movido."""
    for m in movimientos:
        vasos[m.vaso].puesto = m.destino
