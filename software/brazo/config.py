"""Parámetros del brazo clasificador y de la celda de trabajo.

Dos perfiles de medidas:
  SIMULACION  geometría con la que se hicieron las simulaciones y los cálculos
  CAD         medidas del brazo real (PLANOS_BRACITO), ver docs/06-medidas-cad.md

Se elige con la variable de entorno BRAZO_PERFIL o cambiando PERFIL abajo.
Longitudes en centímetros y ángulos en grados.
"""
import os
from dataclasses import dataclass

# --- perfiles de medidas -----------------------------------------------------
PERFILES = {
    "simulacion": {
        "d1": 11.0, "l1": 16.0, "l2": 15.0, "l3": 8.0,
        "r_arco": 23.0,
        "limites": [(-90.0, 90.0), (0.0, 180.0), (-150.0, 0.0),
                    (-120.0, 60.0), (-90.0, 90.0)],
    },
    "cad": {                      # lectura de los planos; confirmar con el modelo
        "d1": 8.7,                # 50 mm de base + 36,61 mm del hombro
        "l1": 10.0,               # brazo: 140 mm totales - cubos R17,5 y R22,5
        "l2": 9.5,                # POR MEDIR entre ejes codo-muñeca
        "l3": 6.0,                # POR MEDIR entre eje de muñeca y TCP
        "r_arco": 9.7,            # calculado con scripts/verificar_alcance.py
        "limites": [(-90.0, 90.0), (0.0, 180.0), (-150.0, 0.0),
                    (-120.0, 60.0), (-90.0, 90.0)],
    },
}
PERFIL = os.environ.get("BRAZO_PERFIL", "simulacion")
if PERFIL not in PERFILES:
    raise ValueError(f"perfil desconocido: {PERFIL}")
_P = PERFILES[PERFIL]

# --- geometría del brazo -----------------------------------------------------
D1 = _P["d1"]          # altura del eje del hombro sobre la mesa
L1 = _P["l1"]          # hombro -> codo
L2 = _P["l2"]          # codo -> muñeca
L3 = _P["l3"]          # muñeca -> TCP
ALCANCE_MAX = L1 + L2 + L3

# --- articulaciones ----------------------------------------------------------
LIMITES = _P["limites"]
NOMBRES_JUNTAS = ["J1 base", "J2 hombro", "J3 codo", "J4 cabeceo", "J5 giro"]
HOME = [0.0, 90.0, -90.0, -90.0, 0.0]

# --- pinza -------------------------------------------------------------------
PINZA_MAX_MM = 70.0
PINZA_ABIERTA_MM = 66.0
PINZA_CERRADA_MM = 49.0        # 3 mm de interferencia sobre el vaso de 52 mm
VASO_ANCHO_MM = 52.0

# --- celda de trabajo --------------------------------------------------------
SUPERFICIE = 0.6
Z_AGARRE = 6.8                 # altura del TCP al tomar o soltar el vaso
Z_SEGURA = 17.0                # altura de traslado
R_ARCO = _P["r_arco"]          # radio del arco de puestos
YAW_ENTRADA = [-86.0, -70.5, -55.0, -39.5, -24.0]
YAW_RACK = [24.0, 39.5, 55.0, 70.5, 86.0]
CABECEO_AGARRE = -90.0

# --- vasos y monedas (serie 2012 del Banco de la República) ------------------
MASA_VASO_G = 18.0
MASA_MONEDA_G = {50: 2.00, 100: 3.34, 200: 4.61, 500: 7.14, 1000: 9.95}
DENOMINACIONES = [50, 100, 200, 500, 1000]

# --- movimiento --------------------------------------------------------------
VEL_ARTICULAR = 75.0           # grados/s promedio
VEL_LINEAL = 11.0              # cm/s promedio
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


def resumen() -> str:
    return (f"perfil {PERFIL}: d1={D1} L1={L1} L2={L2} L3={L3} cm, "
            f"alcance {ALCANCE_MAX} cm, arco {R_ARCO} cm")
