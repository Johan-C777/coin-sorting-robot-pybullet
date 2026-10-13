"""Brazo clasificador de vasos de monedas (módulo 6 del proyecto).

Paquete con el catálogo de monedas de las dos familias y el diseño del riel
selector, la cinemática, la ruta de A a B entre obstáculos, la planificación
de orden, la generación de trayectorias y el protocolo con el ESP32.
"""
from . import config  # noqa: F401
from .kinematics import fk, ik, t05, jacobiano, det_jacobiano, pose_puesto  # noqa: F401
from .cups import Vaso, lote_aleatorio  # noqa: F401
from .planner import planificar, Movimiento  # noqa: F401
from .trajectory import quintico, perfil, tramo_articular, tramo_lineal  # noqa: F401
from .protocol import angulos_servo, trama, pwm_us, estado_json, trama_vasos  # noqa: F401
from . import monedas, obstaculos  # noqa: F401

__version__ = "0.3.0"
