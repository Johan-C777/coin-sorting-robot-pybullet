"""Brazo clasificador de vasos de monedas (módulo 6 del proyecto).

Paquete con la cinemática, la planificación de orden, la generación de
trayectorias y el protocolo de comunicación con el ESP32.
"""
from . import config  # noqa: F401
from .kinematics import fk, ik, t05, jacobiano, det_jacobiano, pose_puesto  # noqa: F401
from .cups import Vaso, lote_aleatorio  # noqa: F401
from .planner import planificar, Movimiento  # noqa: F401
from .trajectory import quintico, perfil, tramo_articular, tramo_lineal  # noqa: F401
from .protocol import angulos_servo, trama, pwm_us, estado_json  # noqa: F401

__version__ = "0.2.0"
