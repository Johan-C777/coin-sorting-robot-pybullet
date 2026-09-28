"""Orquestador del brazo: junta planificador, trayectorias y protocolo.

Es el mismo flujo que corre el ESP32 en firmware/esp32_brazo/sequencer.cpp,
pero del lado del PC sirve para probar sin hardware y para alimentar la
simulación y el dashboard.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence

from .config import HOME, PINZA_ABIERTA_MM
from .cups import Vaso, lote_demo
from .kinematics import fk
from .links import EnlaceNulo
from .planner import Movimiento, planificar
from .protocol import estado_json, trama
from .trajectory import Tramo, ciclo_pick_place, duracion_total, muestrear


class Controlador:
    """Mantiene el estado del brazo y ejecuta órdenes de clasificación."""

    def __init__(self, vasos: Optional[List[Vaso]] = None, enlace=None,
                 velocidad: float = 1.0, dt: float = 0.02):
        self.vasos = vasos if vasos is not None else lote_demo()
        self.enlace = enlace if enlace is not None else EnlaceNulo()
        self.velocidad = velocidad
        self.dt = dt
        self.q: List[float] = list(HOME)
        self.pinza = PINZA_ABIERTA_MM
        self.estado = "listo"
        self.paso = 0
        self.total = 0
        self.criterio = "valor"
        self.sentido = "asc"

    # --- ejecución ----------------------------------------------------------
    def ejecutar_tramos(self, tramos: List[Tramo],
                        al_avanzar: Optional[Callable[[float, Sequence[float], float], None]] = None) -> float:
        for t, q, pinza in muestrear(tramos, self.dt):
            self.q, self.pinza = list(q), pinza
            self.enlace.enviar(trama(q, pinza))
            if al_avanzar:
                al_avanzar(t, q, pinza)
        return duracion_total(tramos)

    def ordenar(self, criterio: str = "valor", sentido: str = "asc",
                al_avanzar: Optional[Callable] = None) -> Dict:
        """Planifica y ejecuta la clasificación completa."""
        self.criterio, self.sentido = criterio, sentido
        movimientos: List[Movimiento] = planificar(self.vasos, criterio, sentido)
        self.total, self.paso, self.estado = len(movimientos), 0, "moviendo"
        tiempo = 0.0
        registro = []
        for i, m in enumerate(movimientos, start=1):
            self.paso = i
            tramos = ciclo_pick_place(m.origen, m.destino, self.q, self.velocidad)
            tiempo += self.ejecutar_tramos(tramos, al_avanzar)
            self.vasos[m.vaso].puesto = m.destino
            registro.append(m.describir(self.vasos))
        from .trajectory import tramo_articular          # regreso al reposo
        tramos = [tramo_articular(self.q, list(HOME), self.pinza, self.velocidad, "regreso a reposo")]
        tiempo += self.ejecutar_tramos(tramos, al_avanzar)
        self.estado = "listo"
        return {"movimientos": registro, "segundos": round(tiempo, 2),
                "tramas": len(getattr(self.enlace, "tramas", []))}

    # --- consulta -----------------------------------------------------------
    def pose_tcp(self):
        return fk(self.q)

    def estado_actual(self) -> Dict:
        return estado_json(self.q, self.pinza, self.vasos, self.estado,
                           self.paso, self.total, self.criterio, self.sentido)
