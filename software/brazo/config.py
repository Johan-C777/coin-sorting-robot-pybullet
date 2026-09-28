"""Parámetros del brazo clasificador y de la celda de trabajo.

Longitudes en centímetros y ángulos en grados, igual que en la memoria de
cálculo (docs/02-cinematica.md) y en la simulación 3D. Este módulo es la única
fuente de verdad del lado del PC: firmware/esp32_brazo/config.h replica los
mismos números para el hardware.
"""
from dataclasses import dataclass

# --- geometría del brazo -----------------------------------------------------
D1 = 11.0   # altura del eje del hombro sobre la mesa
L1 = 16.0   # hombro -> codo
L2 = 15.0   # codo -> muñeca
L3 = 8.0    # muñeca -> TCP (punto de agarre)

ALCANCE_MAX = L1 + L2 + L3          # 39 cm desde el eje del hombro

# --- límites articulares (grados) -------------------------------------------
LIMITES = [
    (-90.0, 90.0),    # J1 base
    (0.0, 180.0),     # J2 hombro
    (-150.0, 0.0),    # J3 codo
    (-120.0, 60.0),   # J4 cabeceo de muñeca
    (-90.0, 90.0),    # J5 giro de muñeca
]
NOMBRES_JUNTAS = ["J1 base", "J2 hombro", "J3 codo", "J4 cabeceo", "J5 giro"]
HOME = [0.0, 90.0, -90.0, -90.0, 0.0]

# --- pinza -------------------------------------------------------------------
PINZA_MAX_MM = 70.0
PINZA_ABIERTA_MM = 66.0
PINZA_CERRADA_MM = 49.0   # 3 mm de interferencia sobre el vaso de 52 mm
VASO_ANCHO_MM = 52.0

# --- celda de trabajo --------------------------------------------------------
SUPERFICIE = 0.6          # espesor de la bandeja
Z_AGARRE = 6.8            # altura del TCP al tomar o soltar el vaso
Z_SEGURA = 17.0           # altura de traslado
R_ARCO = 23.0             # radio del arco de puestos
YAW_ENTRADA = [-86.0, -70.5, -55.0, -39.5, -24.0]
YAW_RACK = [24.0, 39.5, 55.0, 70.5, 86.0]
CABECEO_AGARRE = -90.0    # pinza vertical

# --- vasos y monedas (serie 2012 del Banco de la República) ------------------
MASA_VASO_G = 18.0
MASA_MONEDA_G = {50: 2.00, 100: 3.34, 200: 4.61, 500: 7.14, 1000: 9.95}
DENOMINACIONES = [50, 100, 200, 500, 1000]

# --- movimiento --------------------------------------------------------------
VEL_ARTICULAR = 75.0      # grados/s promedio de un tramo articular
VEL_LINEAL = 11.0         # cm/s promedio de un tramo lineal
T_MINIMA_ARTICULAR = 0.45
T_MINIMA_LINEAL = 0.30

# --- servos ------------------------------------------------------------------
PWM_MIN_US = 500
PWM_MAX_US = 2500
PWM_FREQ_HZ = 50


@dataclass(frozen=True)
class Puesto:
    """Un puesto de la celda: zona ('entrada' o 'rack') e índice 0..4."""
    zona: str
    indice: int

    @property
    def yaw(self) -> float:
        return (YAW_ENTRADA if self.zona == "entrada" else YAW_RACK)[self.indice]

    @property
    def etiqueta(self) -> str:
        return ("E" if self.zona == "entrada" else "R") + str(self.indice + 1)

    def __str__(self) -> str:
        return f"{self.zona} {self.indice + 1}"
