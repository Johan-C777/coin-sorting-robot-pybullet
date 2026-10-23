"""Clasificador de la etapa 1, versión 5 (prototipo compacto): piezas STL y despiece.

    pip install manifold3d numpy
    python scripts/generar_v5.py              # STL de impresión, despiece y verificación
    python scripts/generar_v5.py --ensamble   # además el ensamble (STL y JSON para el visor)

Torre de pie sobre la banda, sin pared ni tornillos:
  tolva de disco inclinado (45°) -> pista inclinada (22°, placa a 20° de la vertical) con dos
  barreras IR y sensor de color -> embudo -> compuerta (SG90) -> vaso correcto del cartucho,
  que la banda pone bajo el embudo. El rechazo cae por una rampa a un vaso que se pone a mano.

Simulación que respalda las cotas (sim/mujoco):
  * disco.py: salida del disco a la pista, 1728/1728 de canto (caída de 18 a 30 mm, a <= 3 mm de la placa)
  * embudo.py: embudo rim 45, 45°, 60 mm adelante y 50 mm bajo el fin de pista, 81/81
  * rodar.py: medición del diámetro por tiempo entre dos barreras

Marco del mundo (W, mm): X a lo largo de la banda (hacia el punto A), Y hacia arriba (Y = 0 es
la mesa), Z hacia el frente. El hueco del embudo está en X = 0, Z = 0.
Cada pieza se modela en el mundo y se gira a su orientación de impresión (Z = capas).
Impresora: Creality K1C, cama 220 x 220 x 250 mm (se deja margen: 210 mm).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from manifold3d import CrossSection, FillRule, Manifold, set_circular_segments

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generar_clasificador import escribir_stl  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "hardware" / "etapa1-clasificador" / "v5"
CAMA = 210.0
set_circular_segments(64)

# ---------------------------------------------------------------- tolerancias
HOLGURA = 0.3        # por lado en encajes deslizantes (clavijas en agujeros, servo, motor)
PIN_D = 6.0          # clavija impresa Ø6
PIN_L = 20.0
PIN_H = PIN_D + 2 * HOLGURA   # agujero para la clavija

# ---------------------------------------------------------------- cotas generales
PEND, LEAN = 22.0, 20.0          # pendiente de la pista y placa respecto a la vertical
PLACA, BAJO, ALTO = 4.0, 6.0, 40.0
REPISA_E, LAB = 3.0, 11.0
S_END = 175.0                    # largo de la pista
B1, SEP, H_BAR, S_COLOR = 105.0, 24.0, 10.0, 152.0
Y_H = 150.0                      # cara inferior del hueco del embudo
FUN_RIM, FUN_HOLE, FUN_A, FUN_E = 45.0, 16.5, 45.0, 2.4
FUN_FX, FUN_FZ = 60.0, 50.0      # el hueco está 60 mm adelante y 50 mm abajo del fin de pista
Y_G = 146.0                      # eje (bisagra) de la compuerta
Z_BIS = -17.0                    # la bisagra está en el borde trasero de la paleta
G_ABRE = 60.0                    # la compuerta abre 60° hacia abajo
Y_BELT, CUP_D, CUP_H, CUP_PASO, N_VASOS = 50.0, 34.0, 60.0, 38.0, 9
SLED_E = 6.0
# disco
DISCO_INC = 45.0                 # inclinación del disco respecto a la horizontal (en el marco de la pista)
POCKET_D, R_PASO, N_BOLS, DISCO_E = 29.0, 42.0, 8, 2.4
DISCO_R = 51.0
ARO_R0, ARO_E, ARO_H = 52.0, 3.0, 40.0
BASE_E = 3.0
S_SUELTA, SUBE, FRENTE = 22.0, 22.0, 1.5   # punto donde cae la moneda (centro de una de 23 mm)
# armazón
X_CAB = (-200.0, -84.0, 70.0)    # caballetes
Z_PATA, PATA_W, CAB_E = 95.0, 16.0, 16.0
Y_VIGA1 = 165.0                  # cara superior de la viga del caballete (la brida del embudo queda a la altura del borde)
Y_VIGA0 = Y_VIGA1 - 16.0
PAT_H = 14.0                     # patín
LARG_W, LARG_H, Z_LARG = 12.0, 12.0, 60.0   # largueros sobre las vigas

p, g = math.radians(PEND), math.radians(LEAN)
SV = np.array([math.cos(p), -math.sin(p), 0.0])
TV = np.array([math.sin(p) * math.cos(g), math.cos(p) * math.cos(g), -math.sin(g)])
NV = np.array([math.sin(p) * math.sin(g), math.cos(p) * math.sin(g), math.cos(g)])
X_E, Y_E = -FUN_FX, Y_H + FUN_FZ
ORIG = np.array([X_E, Y_E, 0.0]) - S_END * SV
FUN_Y_RIM = Y_H + (FUN_RIM - FUN_HOLE) * math.tan(math.radians(FUN_A))


# ---------------------------------------------------------------- utilidades
def caja(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def cil(p0, eje, largo, r, r2=None):
    """Cilindro (o cono) de base en p0 a lo largo de eje."""
    a = np.asarray(eje, float); a = a / np.linalg.norm(a)
    aux = np.array([1.0, 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(a, aux); u /= np.linalg.norm(u); v = np.cross(a, u)
    m = Manifold.cylinder(largo, r, -1.0 if r2 is None else r2)
    return m.transform(np.column_stack([u, v, a, np.asarray(p0, float)]))


def poli(pts):
    return CrossSection([np.asarray(pts, float)], FillRule.EvenOdd)


def marco(m: Manifold, cols, orig) -> Manifold:
    """Lleva una pieza modelada en un marco local (ejes cols, origen orig) al mundo."""
    return m.transform(np.column_stack(list(cols) + [np.asarray(orig, float)]))


def a_mundo_pista(s, t, n):
    return ORIG + s * SV + t * TV + n * NV


def marco_pista(m):
    return marco(m, (SV, TV, NV), ORIG)


# disco: ejes en el marco de la pista (s, t, n)
_rel = math.radians(90 - LEAN - DISCO_INC)
UD_L = np.array([1.0, 0, 0])
WD_L = np.array([0, math.cos(_rel), -math.sin(_rel)])
ND_L = np.array([0, math.sin(_rel), math.cos(_rel)])
_d_med, _e_med = 23.0, 1.8
_R = np.array([S_SUELTA, _d_med / 2 + SUBE, (_d_med / 2) * math.sin(_rel) + _e_med / 2 + FRENTE])
_C = _R + (POCKET_D / 2 - _d_med / 2) * WD_L - R_PASO * WD_L
DISCO_O_L = _C - (_e_med / 2) * ND_L          # centro del disco sobre la cara de la base (marco pista)
L2W = np.column_stack([SV, TV, NV])
UD, WD, ND = L2W @ UD_L, L2W @ WD_L, L2W @ ND_L
DISCO_O = ORIG + L2W @ DISCO_O_L


def marco_disco(m):
    return marco(m, (UD, WD, ND), DISCO_O)


def a_mundo_disco(u, w, nd):
    return DISCO_O + u * UD + w * WD + nd * ND


def agujero_pin(p0, eje, prof=11.0):
    return cil(np.asarray(p0) - 0.5 * np.asarray(eje) / np.linalg.norm(eje), eje, prof + 0.5, PIN_H / 2)


def pin_en(p0, eje, dentro=10.0):
    """Clavija del ensamble (solo para revisar choques): mitad en cada pieza."""
    e = np.asarray(eje, float) / np.linalg.norm(eje)
    return cil(np.asarray(p0) - dentro * e, e, PIN_L, PIN_D / 2)


# ---------------------------------------------------------------- piezas
@dataclass
class Pieza:
    codigo: str
    nombre: str
    cant: int
    mundo: Manifold            # posición en el ensamble (la primera copia)
    impresion: np.ndarray      # matriz 3x4 mundo -> orientación de impresión (antes de apoyar en la cama)
    notas: str = ""
    otras: tuple = ()          # posiciones de las demás copias (matrices 3x4 mundo -> mundo)


def rot_imp(cols):
    """Matriz 3x4 que lleva los ejes cols (en el mundo) a X, Y, Z de impresión."""
    R = np.array(cols, float)
    return np.column_stack([R, np.zeros(3)])


I3 = np.column_stack([np.eye(3), np.zeros(3)])


# ================================================================= pista (L01) y porta-emisores (B01)
def s_de_x(x):
    return (x - ORIG[0]) / SV[0]


S_K = (s_de_x(X_CAB[0]), s_de_x(X_CAB[1]))


def zona_pista():
    """Volumen que ocupa la pista y todo lo que queda encima/delante (para recortar soportes)."""
    a = caja(-300, 500, -BAJO, 600, -600, 0.0)            # detrás de la cara de la placa, desde su borde inferior
    b = caja(-300, 500, -REPISA_E, 600, -1, 600)            # delante de la placa, desde la cara inferior de la repisa
    for sk in S_K:                                          # tacos bajo la repisa
        b += caja(sk - 8.3, sk + 8.3, -BAJO, 600, -1, LAB + 0.3)
    return marco_pista(a + b)


S_TOLVA = 76.0       # la placa sube a T_TOLVA en s < S_TOLVA (agarre de la tolva)
T_TOLVA = 54.0
PADS_S = (-20.0, 66.0)
PAD_T = (40.0, 52.0)


def pista_local():
    m = caja(-4, S_END, -BAJO, ALTO, -PLACA, 0)
    m += caja(-4, S_TOLVA, ALTO - 1, T_TOLVA, -PLACA, 0)
    m += caja(-4, S_END, -REPISA_E, 0, -1, LAB)                      # repisa
    m += caja(-4, 0, 0, 22, -1, 8)                                    # tope trasero
    for sb in (B1, B1 + SEP):
        m += caja(sb - 5, sb + 5, -REPISA_E, H_BAR + 8, LAB, LAB + 8)  # poste del receptor
        m -= cil((sb, H_BAR, LAB + 1.5), (0, 0, 1), 20, 5.2 / 2)        # bolsillo del receptor (Ø5)
        m -= cil((sb, H_BAR, -PLACA - 1), (0, 0, 1), LAB + 10, 1.6 / 2)  # ventana del haz
    # sensor de color (TCS34725) delante de la moneda, mirando a su cara
    m += caja(S_COLOR - 11, S_COLOR + 11, -REPISA_E, 26, LAB - 1, LAB + 4.5)
    m -= caja(S_COLOR - 10.4, S_COLOR + 10.4, 3.6, 24.4, LAB + 3.0, LAB + 5)  # rebaje de la placa del sensor
    m -= cil((S_COLOR, 14, LAB - 2), (0, 0, 1), 8, 4.0)                       # ventana del sensor
    # agujeros para las clavijas de la tolva (en la cara de la placa) y de los soportes (borde inferior)
    for sp in PADS_S:
        m -= cil((sp, (PAD_T[0] + PAD_T[1]) / 2, -PLACA - 1), (0, 0, 1), PLACA + 2, PIN_H / 2)
    return m


def pista():
    m = pista_local()
    for sk in S_K:                                    # taco bajo la repisa con agujero para la clavija del soporte
        m += caja(sk - 8, sk + 8, -BAJO, -REPISA_E + 0.01, -PLACA, LAB)
        m -= cil((sk, -BAJO - 0.5, 3.5), (0, 1, 0), 6.0, PIN_H / 2)
    return marco_pista(m)


def porta_emisor(sb):
    """B01: sujeta el emisor IR detrás de la placa; se engancha en el borde inferior."""
    m = caja(sb - 7, sb + 7, -8.5, 18, -12, -PLACA - 0.3)
    m += caja(sb - 7, sb + 7, -8.5, -BAJO - 0.3, -12, 3)
    m += caja(sb - 7, sb + 7, -8.5, -REPISA_E - 1.3, 0.3, 3)
    m -= cil((sb, H_BAR, -12.5), (0, 0, 1), 8.2, 5.2 / 2)
    return marco_pista(m)


# ================================================================= tolva de disco (H01, H02, H03)
MOTOR_OFF = 8.0          # el eje del 28BYJ-48 está 8 mm corrido del centro del cuerpo
MOTOR_D, MOTOR_L, OREJAS = 28.0, 19.0, 35.0
RASC_ANG = 150.0         # posición del rascador (grados, 0 = hacia la pista, 90 = arriba)
RASC_GAP = (2.5, 2.6, 2.8)


def zona_detras_placa():
    """Lo que está detrás de la cara de la placa de la pista (la tolva no puede entrar)."""
    return marco_pista(caja(-300, 500, -300, 600, -600, 0.3))


def base_tolva():
    r_ext = ARO_R0 + ARO_E
    m = Manifold.cylinder(BASE_E, r_ext + 3).translate((0, 0, -BASE_E))
    m += caja(-52, 70, 20, 66, -BASE_E, 0)                            # extensión hacia la placa
    aro = Manifold.cylinder(ARO_H, r_ext) - Manifold.cylinder(ARO_H + 2, ARO_R0).translate((0, 0, -1))
    m += aro
    # ranura del rascador en el aro
    a = math.radians(RASC_ANG)
    ranura = caja(-2.2, 2.2, ARO_R0 - 1, r_ext + 1, 0, ARO_H + 1)
    m -= ranura.transform(np.array([[math.cos(a - math.pi / 2), -math.sin(a - math.pi / 2), 0, 0],
                                    [math.sin(a - math.pi / 2), math.cos(a - math.pi / 2), 0, 0],
                                    [0, 0, 1, 0]]))
    # hueco de salida (arriba) y paso del eje
    m -= Manifold.cylinder(BASE_E + 2, 15.5).translate((0, R_PASO, -BASE_E - 1))
    m -= Manifold.cylinder(BASE_E + 2, 5.0).translate((0, 0, -BASE_E - 1))
    # clavijas para las orejas del motor (detrás)
    for u in (-OREJAS / 2, OREJAS / 2):
        m += Manifold.cylinder(4.5, 3.9 / 2).translate((u, -MOTOR_OFF, -BASE_E - 4.0))
    # pasos para una brida alrededor del motor
    for u in (-MOTOR_D / 2 - 4, MOTOR_D / 2 + 4):
        m += caja(u - 3, u + 3, -MOTOR_OFF - 9, -MOTOR_OFF + 9, -BASE_E - 5, -BASE_E + 0.5)
        m -= caja(u - 4, u + 4, -MOTOR_OFF - 2.5, -MOTOR_OFF + 2.5, -BASE_E - 4, -BASE_E - 0.8)
    w = marco_disco(m)
    w -= zona_detras_placa()
    # almohadillas que se apoyan en la placa de la pista, con clavija
    for sp in PADS_S:
        pad = caja(sp - 9, sp + 9, PAD_T[0] - 3, PAD_T[1], 0.3, 9.0)
        pad -= cil((sp, (PAD_T[0] + PAD_T[1]) / 2, 0), (0, 0, 1), 8.5, PIN_H / 2)
        w += marco_pista(pad)
    return w


def disco():
    m = Manifold.cylinder(DISCO_E, DISCO_R)
    for i in range(N_BOLS):
        a = 2 * math.pi * i / N_BOLS
        c = (R_PASO * math.cos(a), R_PASO * math.sin(a))
        bolsa = Manifold.cylinder(DISCO_E + 2, POCKET_D / 2).translate((c[0], c[1], -1))
        canal = caja(R_PASO, DISCO_R + 5, -POCKET_D / 2, POCKET_D / 2, -1, DISCO_E + 1)
        canal = canal.transform(np.array([[math.cos(a), -math.sin(a), 0, 0], [math.sin(a), math.cos(a), 0, 0], [0, 0, 1, 0]]))
        m -= bolsa + canal
    m += Manifold.cylinder(6.0, 7.0).translate((0, 0, DISCO_E))      # cubo hacia el frente
    m += Manifold.cylinder(DISCO_E, 12.0)
    eje = caja(-2.5 - HOLGURA / 2, 2.5 + HOLGURA / 2, -1.5 - HOLGURA / 2, 1.5 + HOLGURA / 2, -1, DISCO_E + 5)
    eje = eje ^ Manifold.cylinder(DISCO_E + 7, 2.5 + HOLGURA / 2).translate((0, 0, -1))
    m -= eje                                                           # eje en D del 28BYJ-48
    return marco_disco(m.translate((0, 0, 0.05)))


def rascador(gap):
    a = math.radians(RASC_ANG)
    r_ext = ARO_R0 + ARO_E
    m = caja(-2.0, 2.0, ARO_R0 - 0.5, r_ext + 3, 0, ARO_H + 3)          # lengüeta en la ranura del aro
    m += caja(-2.0, 2.0, ARO_R0 - 0.5, r_ext + 3, ARO_H, ARO_H + 3)
    m += caja(-2.0, 2.0, 22, ARO_R0 - 0.5 + 1e-3, gap, gap + 5)          # barra sobre el disco
    m += caja(-2.0, 2.0, ARO_R0 - 6, ARO_R0, gap, ARO_H * 0.5)          # refuerzo
    m = m.transform(np.array([[math.cos(a - math.pi / 2), -math.sin(a - math.pi / 2), 0, 0],
                              [math.sin(a - math.pi / 2), math.cos(a - math.pi / 2), 0, 0],
                              [0, 0, 1, 0]]))
    return marco_disco(m)


# ================================================================= embudo (F01, F02)
FL_Y0 = Y_VIGA1 + LARG_H
FL_Y1, FL_R = FL_Y0 + 3.0, 68.0
CAMP_R0, CAMP_E, CAMP_H = 48.0, 2.0, 60.0
VENT = 40.0                              # media apertura de la ventana de entrada (grados)
Z_R2, Z_R1 = 60.0, 74.0                  # largueros: entre caballetes 2-3 (bajo la brida) y 1-2
PINES_BRIDA = [(x, z) for x in (-15.0, 15.0) for z in (-Z_R2, Z_R2)]
PINES_G01 = [(55.0, Z_BIS - 6.0), (55.0, Z_BIS + 6.0)]


def embudo():
    dy = FUN_E / math.cos(math.radians(FUN_A))
    k = 1 / math.tan(math.radians(FUN_A))
    h = FUN_Y_RIM - Y_H
    ext = cil((0, Y_H, 0), (0, 1, 0), h, FUN_HOLE + dy * k, FUN_RIM + dy * k)
    inn = cil((0, Y_H - 0.01, 0), (0, 1, 0), h + 0.02, FUN_HOLE, FUN_RIM)
    m = ext + cil((0, FL_Y0, 0), (0, 1, 0), FL_Y1 - FL_Y0, FL_R)
    m -= cil((0, FL_Y1 - 1.2, 0), (0, 1, 0), 2, CAMP_R0 + CAMP_E + 0.3) - cil((0, FL_Y1 - 2, 0), (0, 1, 0), 3, CAMP_R0 - 0.3)   # ranura de la campana
    m -= inn + cil((0, FUN_Y_RIM - 0.02, 0), (0, 1, 0), 10, FUN_RIM)
    for x, z in PINES_BRIDA + PINES_G01:
        m -= cil((x, FL_Y0 - 1, z), (0, 1, 0), 10, PIN_H / 2)
    return m


def campana():
    y0 = FL_Y1 - 1.0
    m = cil((0, y0, 0), (0, 1, 0), CAMP_H, CAMP_R0 + CAMP_E) - cil((0, y0 - 1, 0), (0, 1, 0), CAMP_H - 2 + 1, CAMP_R0)
    # ventana hacia la pista (lado -X), también en la tapa
    r = 200
    a = math.radians(VENT)
    cuña = poli([[0, 0], [-r * math.cos(a), -r * math.sin(a)], [-r, 0], [-r * math.cos(a), r * math.sin(a)]])
    cuña = cuña.extrude(CAMP_H + 4).transform(np.array([[1, 0, 0, 0], [0, 0, 1, y0 - 1], [0, 1, 0, 0]]))
    m -= cuña - cil((0, y0 - 2, 0), (0, 1, 0), CAMP_H + 6, 30)
    return m


# ================================================================= compuerta (G01, G02, G03)
SERVO_TOP = 26.0          # cara superior de la caja del SG90 (el eje apunta a -X, sobre la bisagra)
SERVO_L, SERVO_W, SERVO_H = 22.7, 12.2, 22.5
SERVO_OFF = 5.5           # el eje está corrido 5,5 mm del centro de la caja (hacia arriba)
G01_X0, G01_X1, POSTE_X1 = 33.0, 50.0, 60.0


def soporte_servo():
    """G01: cuna del SG90 de la compuerta, colgada de la brida del embudo con dos clavijas."""
    yc = Y_G - SERVO_OFF
    y0 = yc - SERVO_H / 2 - 3
    m = caja(G01_X0, G01_X1, y0, Y_G + 8, Z_BIS - 10, Z_BIS + 14)
    m += caja(G01_X1, POSTE_X1, y0, FL_Y0, Z_BIS - 10, Z_BIS + 10)
    esc = poli([[G01_X1 + 0.01, Y_G + 8 - 0.01], [G01_X0, Y_G + 8 - 0.01], [G01_X1 + 0.01, Y_G + 8 + G01_X1 - G01_X0]]).extrude(20)
    m += esc.translate((0, 0, Z_BIS - 10))
    m -= caja(G01_X0 - 1, G01_X1 + 1, yc - SERVO_H / 2 - HOLGURA, yc + SERVO_H / 2 + HOLGURA,
              Z_BIS - SERVO_W / 2 - HOLGURA, Z_BIS + SERVO_W / 2 + HOLGURA)
    m -= caja(G01_X0 + 6, POSTE_X1 + 1, yc - 4, yc + 4, Z_BIS - 3, Z_BIS + 3)      # salida del cable
    for x, z in PINES_G01:
        m -= cil((x, FL_Y0 - 9, z), (0, 1, 0), 10, PIN_H / 2)
    return m


PAL = 17.0      # media paleta
PAL_E = 2.5


def compuerta():
    """G02: paleta con bisagra en su borde trasero (eje del servo). Cerrada sostiene la moneda bajo el hueco."""
    m = caja(-PAL, PAL, Y_G - PAL_E / 2, Y_G + PAL_E / 2, Z_BIS, PAL)
    m += cil((-PAL, Y_G, Z_BIS), (1, 0, 0), 2 * PAL, PAL_E / 2)
    m += cil((PAL - 2, Y_G, Z_BIS), (1, 0, 0), 19.0 - PAL + 2, 4.5)              # cubo del brazo del servo
    m += caja(PAL - 2, 19.0, Y_G - 3.5, Y_G + PAL_E / 2, Z_BIS, Z_BIS + 9)
    rebaje = cil((19.0 - 1.6, Y_G, Z_BIS), (1, 0, 0), 2, 3.7) + caja(19.0 - 1.6, 19.1, Y_G - 2.4, Y_G + 2.4, Z_BIS, Z_BIS + 9.5)
    return m - rebaje


# ================================================================= armazón
def caballete(xc):
    x0, x1 = xc - CAB_E / 2, xc + CAB_E / 2
    m = caja(x0, x1, Y_VIGA0, Y_VIGA1, -Z_PATA - PATA_W / 2, Z_PATA + PATA_W / 2)
    for zs in (-1, 1):
        m += caja(x0, x1, 4, Y_VIGA1, zs * Z_PATA - PATA_W / 2, zs * Z_PATA + PATA_W / 2)
        # escuadra
        zi = zs * (Z_PATA - PATA_W / 2)
        tri = poli([[0, 0], [-24 * zs, 0], [0, -24]]).extrude(CAB_E)
        m += tri.transform(np.array([[0, 0, 1, x0], [0, 1, 0, Y_VIGA0], [1, 0, 0, zi]]))
    for z in (-Z_R1, -Z_R2, -10.0, 10.0, 38.0, Z_R2, Z_R1):
        m -= cil((xc, Y_VIGA1 - 11, z), (0, 1, 0), 12, PIN_H / 2)
    return m


def patin(xa, xb, xs):
    m = caja(xa, xb, 0, PAT_H, Z_PATA - 12, Z_PATA + 12)
    for xc in xs:
        m -= caja(xc - CAB_E / 2 - HOLGURA, xc + CAB_E / 2 + HOLGURA, 4, PAT_H + 1,
                  Z_PATA - PATA_W / 2 - HOLGURA, Z_PATA + PATA_W / 2 + HOLGURA)
    return m


def larguero(xa, xb, z, xs, pines_arriba=()):
    m = caja(xa, xb, Y_VIGA1, Y_VIGA1 + LARG_H, z - LARG_W / 2, z + LARG_W / 2)
    for xc in xs:
        m -= cil((xc, Y_VIGA1 - 1, z), (0, 1, 0), 10, PIN_H / 2)
    for x in pines_arriba:
        m -= cil((x, Y_VIGA1 + LARG_H - 9, z), (0, 1, 0), 10, PIN_H / 2)
    return m


def soporte(xc, z0, z1, ytop, extra=None, pines_z=(-10.0, 10.0)):
    m = caja(xc - CAB_E / 2, xc + CAB_E / 2, Y_VIGA1, ytop, z0, z1)
    m -= zona_pista()
    if extra is not None:
        m -= extra
    for z in pines_z:
        m -= cil((xc, Y_VIGA1 - 1, z), (0, 1, 0), 10, PIN_H / 2)
    sk = s_de_x(xc)
    p0 = a_mundo_pista(sk, -BAJO, 3.5)
    m -= cil(p0 - 14.5 * TV, TV, 15, PIN_H / 2)
    return max(m.decompose(), key=lambda c: c.volume())


def zona_tolva():
    """La base de la tolva y su motor, barridos hacia la tolva (para el soporte K1)."""
    frente = marco_disco(caja(-400, 400, -400, 400, -BASE_E - 0.3, 400))
    motor = Manifold.cylinder(MOTOR_L + 40, MOTOR_D / 2 + 0.6).translate((0, -MOTOR_OFF, -BASE_E - MOTOR_L - 1))
    motor += caja(-OREJAS / 2 - 5, OREJAS / 2 + 5, -MOTOR_OFF - 7, -MOTOR_OFF + 7, -BASE_E - 6, 10)
    motor += caja(-MOTOR_D / 2 - 8, MOTOR_D / 2 + 8, -MOTOR_OFF - 10, -MOTOR_OFF + 10, -BASE_E - 6, 10)
    motor += caja(-8, 8, -MOTOR_OFF - MOTOR_D / 2 - 8, -MOTOR_OFF, -BASE_E - MOTOR_L, 10)   # cable
    return frente + marco_disco(motor)


# ================================================================= cartucho y vasos
CART_L = 3 * CUP_PASO
CART_W = 52.0


def cartucho(xc):
    y0, y1 = Y_BELT, Y_BELT + SLED_E
    m = caja(xc - CART_L / 2, xc + CART_L / 2, y0, y1, -CART_W / 2, CART_W / 2)
    for zc in (-20.0, 20.0):
        cola = poli([[0, zc - 3], [6, zc - 5], [6, zc + 5], [0, zc + 3]]).extrude(SLED_E)
        m += cola.transform(np.array([[1, 0, 0, xc + CART_L / 2 - 0.01], [0, 0, 1, y0], [0, 1, 0, 0]]))
        h = HOLGURA
        hueco = poli([[0, zc - 3 - h], [6 + h, zc - 5 - h], [6 + h, zc + 5 + h], [0, zc + 3 + h]]).extrude(SLED_E + 2)
        m -= hueco.transform(np.array([[1, 0, 0, xc - CART_L / 2 - 0.01], [0, 0, 1, y0 - 1], [0, 1, 0, 0]]))
    for i in (-1, 0, 1):
        m -= cil((xc + i * CUP_PASO, y1 - 3, 0), (0, 1, 0), 4, CUP_D / 2 + HOLGURA)
        m += caja(xc + i * CUP_PASO - 1.5, xc + i * CUP_PASO + 1.5, y1, y1 + 10, -CART_W / 2, -CART_W / 2 + 3)   # aleta de posición
    return m


RAMPA = (-5.0, 114.0, 48.0)      # z inicial, y inicial, z final de la rampa de rechazo (40°)
Z_RECHAZO = 60.0                  # donde se pone a mano el vaso de rechazo (sobre la mesa)


def cartucho_rechazo(xc):
    """C02: posición de rechazo al extremo del cartucho; una rampa a 40° lleva la moneda a un vaso al costado."""
    z0, y0, z1 = RAMPA
    k = math.tan(math.radians(40.0))
    yr = lambda z: y0 - k * (z - z0)
    perfil = poli([[-CART_W / 2, Y_BELT], [CART_W / 2, Y_BELT], [CART_W / 2, Y_BELT + SLED_E], [-CART_W / 2, Y_BELT + SLED_E]])
    perfil += poli([[z0, yr(z0)], [z1, yr(z1)], [z1, yr(z1) - 4], [z0, yr(z0) - 4]])
    perfil += poli([[z0, Y_BELT + 1], [z0 + 4, Y_BELT + 1], [z0 + 4, yr(z0 + 4) - 1], [z0, yr(z0) - 1]])
    perfil += poli([[20, Y_BELT + 1], [24, Y_BELT + 1], [24, yr(24) - 1], [20, yr(20) - 1]])
    perfil += poli([[z0 + 4, Y_BELT + SLED_E], [20, yr(20) - 3], [20, yr(20) - 9], [z0 + 4, Y_BELT + SLED_E - 0.01]])
    L = CUP_PASO
    T = lambda x0: np.array([[0, 0, 1, x0], [0, 1, 0, 0], [1, 0, 0, 0]])
    m = perfil.extrude(L).transform(T(xc - L / 2))
    for zc in (-20.0, 20.0):
        cola = poli([[0, zc - 3], [6, zc - 5], [6, zc + 5], [0, zc + 3]]).extrude(SLED_E)
        m += cola.transform(np.array([[1, 0, 0, xc + L / 2 - 0.01], [0, 0, 1, Y_BELT], [0, 1, 0, 0]]))
    return m


def vaso(x):
    y0 = Y_BELT + SLED_E - 3
    m = cil((x, y0, 0), (0, 1, 0), CUP_H, CUP_D / 2) - cil((x, y0 + 1.6, 0), (0, 1, 0), CUP_H, CUP_D / 2 - 1.6)
    return m


def clavija(largo):
    m = Manifold.cylinder(largo - 1, PIN_D / 2) + Manifold.cylinder(1, PIN_D / 2, PIN_D / 2 - 0.6).translate((0, 0, largo - 1))
    m += Manifold.cylinder(1, PIN_D / 2 - 0.6, PIN_D / 2)
    return m - Manifold.cylinder(1.0, PIN_D / 2 - 0.6)


# ================================================================= ensamble
def ensamble():
    """Diccionario código -> lista de mallas en el mundo (una por copia)."""
    xs = X_CAB
    k1_extra = zona_tolva()
    piezas = {
        "L01": [pista()],
        "B01": [porta_emisor(B1), porta_emisor(B1 + SEP)],
        "H01": [base_tolva()],
        "H02": [disco()],
        "H03": [rascador(RASC_GAP[0])],
        "K01": [soporte(xs[0], -20, 50, 330, k1_extra, pines_z=(-10.0, 10.0, 38.0))],
        "K02": [soporte(xs[1], -20, 15, 240)],
        "F01": [embudo()],
        "F02": [campana()],
        "G01": [soporte_servo()],
        "G02": [compuerta()],
        "T01": [caballete(x) for x in xs],
        "S01": [patin(xs[0] - 35, xs[1] + 35, xs[:2]).transform(np.diag([1, 1, s, 1])[:3]) for s in (1, -1)],
        "S02": [patin(xs[2] - 50, xs[2] + 50, xs[2:]).transform(np.diag([1, 1, s, 1])[:3]) for s in (1, -1)],
        "R01": [larguero(xs[0] - 8, xs[1] + 8, s * Z_R1, xs[:2]) for s in (1, -1)],
        "R02": [larguero(xs[1] - 8, xs[2] + 8, s * Z_R2, xs[1:], pines_arriba=(-15.0, 15.0)) for s in (1, -1)],
        "C01": [cartucho(i * CART_L) for i in (-1, 0, 1)],
        "C02": [cartucho_rechazo(-1.5 * CART_L - CUP_PASO / 2)],
        "V01": [vaso((i - 4) * CUP_PASO) for i in range(N_VASOS)],
    }
    return piezas


def revisar_choques(piezas):
    plano = [(k, i, m) for k, ms in piezas.items() for i, m in enumerate(ms)]
    malos = []
    for a in range(len(plano)):
        for b in range(a + 1, len(plano)):
            ka, ia, ma = plano[a]; kb, ib, mb = plano[b]
            ba, bb = ma.bounding_box(), mb.bounding_box()
            if any(ba[j] > bb[j + 3] or bb[j] > ba[j + 3] for j in range(3)):
                continue
            v = (ma ^ mb).volume()
            if v > 0.5:
                malos.append((f"{ka}#{ia}", f"{kb}#{ib}", round(v, 1)))
    return malos


# ================================================================= impresión y despiece
X_, Y_, Z_ = np.eye(3)
ARRIBA_Y = [X_, -Z_, Y_]                 # de pie como en el ensamble (Y del mundo hacia arriba)
BOCA_ABAJO = [X_, Z_, -Y_]               # al revés (lo de arriba queda sobre la cama)
X_ARRIBA = [Y_, Z_, X_]
CAB_PLANO = [-Z_, Y_, X_]

FICHAS = [
    # código, nombre, orientación, notas de impresión
    ("L01", "Pista con repisa, barreras y sensor de color", lambda: [SV, TV, NV], "Acostada sobre la espalda de la placa. Sin soportes."),
    ("B01", "Porta-emisor IR (se engancha detrás de la placa)", lambda: [TV, NV, SV], "De lado. Sin soportes."),
    ("H01", "Base de la tolva: plato inclinado, aro y soporte del motor", lambda: [UD, WD, ND], "Con la cara trasera abajo. Necesita soportes (solo bajo las clavijas del motor y las almohadillas)."),
    ("H02", "Disco de 8 bolsillos", lambda: [UD, WD, ND], "Plano, el cubo hacia arriba. Sin soportes."),
    ("H03", "Rascador (quita la moneda montada)", None, "De canto. Sin soportes. Se imprimen 3 alturas: 2,5 / 2,6 / 2,8 mm."),
    ("K01", "Soporte de la tolva y la pista (caballete 1)", lambda: X_ARRIBA, "De lado (cara plana abajo). Sin soportes."),
    ("K02", "Soporte de la pista (caballete 2)", lambda: X_ARRIBA, "De lado. Sin soportes."),
    ("F01", "Embudo con brida", lambda: BOCA_ABAJO, "Boca abajo (la brida sobre la cama). Pared a 45°, sin soportes."),
    ("F02", "Campana del embudo con ventana", lambda: BOCA_ABAJO, "Con la tapa sobre la cama. Sin soportes."),
    ("G01", "Cuna del servo de la compuerta", lambda: BOCA_ABAJO, "Boca abajo. Sin soportes."),
    ("G02", "Compuerta (paleta con bisagra)", lambda: X_ARRIBA, "De canto, el cubo arriba. Sin soportes."),
    ("T01", "Caballete (marco en forma de puente)", lambda: CAB_PLANO, "Plano. Sin soportes."),
    ("S01", "Patín largo (caballetes 1 y 2)", lambda: ARRIBA_Y, "Plano. Sin soportes."),
    ("S02", "Patín corto (caballete 3)", lambda: ARRIBA_Y, "Plano. Sin soportes."),
    ("R01", "Larguero entre caballetes 1 y 2", lambda: ARRIBA_Y, "Plano. Sin soportes."),
    ("R02", "Larguero entre caballetes 2 y 3 (lleva el embudo)", lambda: ARRIBA_Y, "Plano. Sin soportes."),
    ("C01", "Cartucho de 3 vasos (se unen 3 en fila)", lambda: ARRIBA_Y, "Plano. Sin soportes."),
    ("C02", "Rampa de rechazo (va en la punta del cartucho)", lambda: X_ARRIBA, "De lado. Sin soportes."),
    ("V01", "Vaso Ø34 x 60", lambda: ARRIBA_Y, "De pie. Sin soportes."),
]

NOMBRES_STL = {
    "L01": "pista", "B01": "porta_emisor", "H01": "base_tolva", "H02": "disco", "H03": "rascador",
    "K01": "soporte_tolva_pista", "K02": "soporte_pista", "F01": "embudo", "F02": "campana", "G01": "cuna_servo",
    "G02": "compuerta", "T01": "caballete", "S01": "patin_largo", "S02": "patin_corto", "R01": "larguero_corto",
    "R02": "larguero_largo", "C01": "cartucho", "C02": "rampa_rechazo", "V01": "vaso",
}


def a_cama(m: Manifold, filas) -> Manifold:
    R = np.array(filas, float)
    m = m.transform(np.column_stack([R, np.zeros(3)]))
    bb = m.bounding_box()
    return m.translate((-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2]))


def rascador_cama(gap):
    a = math.radians(RASC_ANG) - math.pi / 2
    tw = math.cos(a) * UD + math.sin(a) * WD
    rw = -math.sin(a) * UD + math.cos(a) * WD
    return a_cama(rascador(gap), [rw, ND, tw])


def verificar(m: Manifold, nombre: str):
    bb = m.bounding_box()
    dims = (bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2])
    ok = m.status().name == "NoError" and len(m.decompose()) == 1
    assert ok, f"{nombre}: malla con errores o en varios cuerpos"
    assert dims[0] <= CAMA and dims[1] <= CAMA and dims[2] <= 240, f"{nombre} no cabe en la cama: {dims}"
    return dims


CLAVIJAS = {"P01": (20.0, 17), "P02": (12.0, 8)}   # largo, cantidad (con 2 de repuesto cada una)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ensamble", action="store_true", help="exporta también el ensamble (STL y JSON del visor)")
    args = ap.parse_args()
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "stl").mkdir(exist_ok=True)
    piezas = ensamble()
    choques = revisar_choques(piezas)
    assert not choques, choques
    filas = []
    for cod, nombre, orient, notas in FICHAS:
        cant = len(piezas[cod]) if cod != "H03" else 1
        if cod == "H03":
            for gap, suf in zip(RASC_GAP, "abc"):
                m = rascador_cama(gap)
                dims = verificar(m, cod)
                escribir_stl(m, SALIDA / "stl" / f"{cod}{suf}_{NOMBRES_STL[cod]}_{str(gap).replace('.', 'mm')}.stl", f"{cod}{suf}")
            vol = m.volume()
        else:
            m = a_cama(piezas[cod][0], orient())
            dims = verificar(m, cod)
            escribir_stl(m, SALIDA / "stl" / f"{cod}_{NOMBRES_STL[cod]}.stl", cod)
            vol = m.volume()
        filas.append((cod, nombre, cant, dims, vol, notas))
        print(f"  {cod} x{cant:<2} {dims[0]:6.1f} x {dims[1]:6.1f} x {dims[2]:6.1f} mm  {vol / 1000:6.1f} cm3  {nombre}")
    for cod, (largo, cant) in CLAVIJAS.items():
        m = clavija(largo)
        verificar(m, cod)
        escribir_stl(m, SALIDA / "stl" / f"{cod}_clavija_{int(largo)}mm.stl", cod)
        filas.append((cod, f"Clavija Ø6 x {int(largo)}", cant, (6, 6, largo), m.volume(), "De pie. Imprime todas juntas."))
        print(f"  {cod} x{cant:<2} clavija Ø6 x {largo:.0f}")
    with open(SALIDA / "despiece.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["codigo", "pieza", "cantidad", "medidas_mm", "volumen_cm3", "gramos_aprox_total", "impresion"])
        for cod, nombre, cant, dims, vol, notas in filas:
            g = vol / 1000 * 1.24 * 0.55 * cant
            w.writerow([cod, nombre, cant, " x ".join(f"{d:.0f}" for d in dims), f"{vol / 1000:.1f}", f"{g:.0f}", notas])
    total = sum(v / 1000 * 1.24 * 0.55 * c for _, _, c, _, v, _ in filas)
    print(f"  filamento aprox. {total:.0f} g (PLA, 3 paredes, 20% relleno)")
    if args.ensamble:
        exportar_ensamble(piezas)


GRUPO = {"L01": "pista", "B01": "sensor", "H01": "tolva", "H02": "disco", "H03": "rascador", "K01": "armazon",
         "K02": "armazon", "F01": "embudo", "F02": "campana", "G01": "armazon", "G02": "compuerta", "T01": "armazon",
         "S01": "patin", "S02": "patin", "R01": "armazon", "R02": "armazon", "C01": "cartucho", "C02": "cartucho",
         "V01": "vaso"}


def exportar_ensamble(piezas):
    import base64
    todo = None
    datos = {"piezas": [], "cotas": {
        "Y_H": Y_H, "Y_G": Y_G, "Z_BIS": Z_BIS, "G_ABRE": G_ABRE, "FUN_RIM": FUN_RIM, "FUN_HOLE": FUN_HOLE,
        "FUN_A": FUN_A, "FUN_Y_RIM": FUN_Y_RIM, "ORIG": ORIG.tolist(), "SV": SV.tolist(), "TV": TV.tolist(),
        "NV": NV.tolist(), "DISCO_O": DISCO_O.tolist(), "UD": UD.tolist(), "WD": WD.tolist(), "ND": ND.tolist(),
        "R_PASO": R_PASO, "POCKET_D": POCKET_D, "S_END": S_END, "B1": B1, "SEP": SEP, "H_BAR": H_BAR,
        "S_COLOR": S_COLOR, "Y_BELT": Y_BELT, "SLED_E": SLED_E, "CUP_PASO": CUP_PASO, "CUP_H": CUP_H,
        "CUP_D": CUP_D, "X_RECHAZO": -1.5 * CART_L - CUP_PASO / 2, "Z_RECHAZO": Z_RECHAZO, "RAMPA": RAMPA,
        "S_SUELTA": S_SUELTA, "SUBE": SUBE, "LAB": LAB, "ALTO_TOTAL": 0.0}}
    for cod, ms in piezas.items():
        for i, m in enumerate(ms):
            todo = m if todo is None else todo + m
            mesh = m.to_mesh()
            v = np.asarray(mesh.vert_properties, np.float32)[:, :3]
            t = np.asarray(mesh.tri_verts, np.uint32)
            datos["piezas"].append({"cod": cod, "i": i, "grupo": GRUPO[cod],
                                    "v": base64.b64encode(np.round(v, 2).astype(np.float32).tobytes()).decode(),
                                    "t": base64.b64encode(t.astype(np.uint32).tobytes()).decode()})
    datos["cotas"]["ALTO_TOTAL"] = float(todo.bounding_box()[4])
    (SALIDA / "ensamble.json").write_text(json.dumps(datos), encoding="utf-8")
    escribir_stl(todo, SALIDA / "ensamble_referencia.stl", "ensamble")
    print(f"  ensamble: alto total {datos['cotas']['ALTO_TOTAL']:.0f} mm, {sum(len(p['t']) for p in datos['piezas']) // 1000} k de datos")


if __name__ == "__main__":
    main()
