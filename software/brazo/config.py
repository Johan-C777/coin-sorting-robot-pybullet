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
PINZA_CERRADA_MM = 31.0        # 3 mm de interferencia sobre el vaso de 34 mm
VASO_ANCHO_MM = 34.0           # los vasos de la etapa 1 (Ø34 x 60 mm) son los que viajan

# --- celda de trabajo --------------------------------------------------------
SUPERFICIE = 0.6
VASO_ALTO = 6.0                # cm; vaso de la etapa 1
GRASP_DZ = 4.2                 # cm del TCP a la base del vaso (se toma a 42 mm de abajo)
Z_AGARRE = SUPERFICIE + GRASP_DZ   # altura del TCP al tomar o soltar el vaso (4,8 cm)
Z_SEGURA = 17.0                # altura de traslado
R_ARCO = _P["r_arco"]          # radio del arco de puestos
# Nueve puestos por zona, a 9,5° (3,8 cm de cuerda sobre el arco de 23 cm: entre vasos
# de 34 mm quedan 4 mm). La pinza toma con las mordazas abiertas en sentido radial.
N_PUESTOS = 9
YAW_ENTRADA = [-88.0 + 9.5 * i for i in range(N_PUESTOS)]      # -88 a -12
YAW_RACK = [12.0 + 9.5 * i for i in range(N_PUESTOS)]          # 12 a 88
CABECEO_AGARRE = -90.0

# --- vasos y monedas (Banco de la República) ---------------------------------
# Familia nueva (2012) y familia anterior (1989-1996). El catálogo completo,
# con diámetros, fuentes y el diseño del selector, está en brazo/monedas.py.
MASA_VASO_G = 18.0
MASA_MONEDA_G = {50: 2.00, 100: 3.34, 200: 4.61, 500: 7.14, 1000: 9.95}
MASA_MONEDA_ANTIGUA_G = {50: 4.50, 100: 5.31, 200: 7.08, 500: 7.14}
DENOMINACIONES = [50, 100, 200, 500, 1000]
# Los nueve vasos, uno por ducto del riel (etapa 1): (denominación, antigua)
TIPOS_VASO = [(50, False), (100, False), (50, True), (200, False), (100, True),
              (500, True), (500, False), (200, True), (1000, False)]
MONEDAS_POR_VASO = 40          # capacidad de un vaso lleno

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
    """Un puesto de la celda: zona ('entrada' o 'rack') e índice 0..N_PUESTOS-1."""
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
