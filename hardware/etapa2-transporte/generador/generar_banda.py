"""Banda de la etapa 2 (v2), ajustada a la torre v5 de la etapa 1 y sin herrajes:
muñones impresos en lugar de rodamientos, clavijas Ø6 en lugar de tornillos y tornillo de tensor impreso.

La torre v5 se para sobre la mesa y pasa por encima de la banda. La banda lleva el
cartucho de 9 vasos (C01 x3 + C02 + V01 x9) y pone el vaso pedido bajo el hueco del
embudo; para el rechazo pone la rampa C02 y el vaso de rechazo va a mano en la mesa.

    pip install manifold3d numpy
    python generar_banda.py --datos banda.json     # mallas del ensamble para el visor
    python generar_banda.py --stl salida/          # STL de impresion (tras el visto bueno)

Marco de referencia (el del ensamble v5 con Y y Z intercambiadas para que Z sea la altura):
  X a lo largo de la banda, con el hueco del embudo en X = 0;
  Y a lo ancho (Y = 0 es el eje del embudo; en la v5 es Z);
  Z hacia arriba, Z = 0 en la mesa (en la v5 es Y).
Impresora objetivo: Creality K1C, cama 220 x 220 x 250 mm.
"""
from __future__ import annotations

import argparse
import base64
import json
import math
from pathlib import Path

import numpy as np
from manifold3d import CrossSection, JoinType, Manifold, set_circular_segments

set_circular_segments(64)

# =====================================================================
# Tolerancias FDM (las mismas de la etapa 1)
# =====================================================================
HOLGURA = 0.35
M3_ROSCA, M3_PASO, M3_CABEZA = 3.2, 3.4, 6.5
M4_PASO, M4_TUERCA = 4.4, 7.4
M8_PASO, M8_TUERCA, M8_TUERCA_H = 8.4, 13.4, 6.8
R608_D, R608_H = 22.1, 7.0
IR_D, IR_VENTANA = 5.2, 3.0

# =====================================================================
# Lo que viene de la torre v5 (leido de su ensamble, no de memoria)
# =====================================================================
MESA = 0.0
Z_BANDA = 50.0              # fondo del cartucho
HUECO_X = 0.0               # eje del hueco del embudo
PASO_VASO = 38.0
X_VASO1, X_VASO9 = -152.0, 152.0
X_RAMPA = -190.0            # centro de la rampa C02 respecto al cartucho
X_CART = (-209.0, 177.0)    # extremos del cartucho armado (C02 + 3 C01)
ANCHO_CART = 52.0
A_X = 470.0                 # punto A del brazo
REC = dict(x=0.0, y=60.0, d=34.0, h=60.0)   # vaso de rechazo, a mano, en la mesa
PATIN_Y = 83.0              # cara interior de los patines de la torre (|Y| >= 83)
ARCO_Z = 124.0              # bajo el arco de los caballetes
BOCA_VASO = 113.0

# =====================================================================
# Banda
# =====================================================================
Y_C = 0.0
# cadena de tablillas impresas: paso 12 mm, 8 dientes, pasador a media altura de la tablilla
PASO, DIENTES = 12.0, 8
ANCHO_BANDA, ESP_BANDA = 56.0, 6.0      # ancho y espesor de la tablilla
SEG = 8.0                               # 7 segmentos de 8 mm: nudillos alternados y ranura central
KN_D, PIN_C, PIN_CH, PIN_CL = 6.0, 3.0, 3.4, 57.0
RANURA, RUEDA_W = 8.4, 7.8              # ranura de la tablilla y grosor de la rueda dentada
RP = PASO / (2 * math.sin(math.pi / DIENTES))      # radio primitivo (centros de pasadores)
HEX_E = 10.0                            # hexagono del eje donde se calza la rueda
Z_PIN = Z_BANDA - ESP_BANDA / 2         # altura de los pasadores arriba
Z_CAMA = Z_BANDA - ESP_BANDA
Z_EJE = Z_PIN - RP
N_TAB = 176                             # se imprimen 176; se sacan las que sobren al tensar
X_MOT, X_TEN = -330.0, 660.0            # ejes del rodillo motriz (-X) y del libre con tensor (+X)
CARRERA = 12.0
TAIL = 40.0                             # cola con rosca del carro del tensor
ESP_CAMA, ALTO_PARED, ESP_PARED = 3.2, 30.0, 9.0
Y_PARED = ANCHO_BANDA / 2 + 2.0         # cara interior de la pared +Y
YW = Y_PARED + ESP_PARED                # cara exterior de la pared +Y
Y_NERVIO = (-Y_PARED - 9.0, -Y_PARED)   # nervio -Y bajo la cama
PROF_NERVIO = 12.0
Y_TAPA = (-Y_PARED - 5.0, -Y_PARED)     # tapas -Y: cara interior a 2 mm del borde de la cinta
MODULOS = [-358.0, -200.0, -45.0, 120.0, 285.0, 450.0, 570.0, 722.0]
X_INI, X_FIN = MODULOS[0], MODULOS[-1]
CAMA_X = (X_MOT + 17.0, X_TEN - 17.0)
PATAS_X = [-270.0, -120.0, 60.0, 235.0, 410.0, 603.0, 625.0]
GUIAS = [-300.0, -127.0, 64.0, 255.0, 446.0, 637.0]

# clavijas Ø6 x 12 (la P02 de la etapa 1), muñones Ø10 impresos
PEG_D, PEG_H, PEG_L = 6.0, 6.2, 12.0
PIN_D, PIN_H = 10.0, 10.4
CT = 12.0                               # espesor de los carros del tensor
TRASLAPE = 16.0                         # largo del encastre entre tapa y nervio
# tornillo del tensor: sección elíptica retorcida (paso de 10 mm por vuelta)
HILO_A, HILO_B, HILO_PASO, HILO_JUEGO = 4.1, 2.8, 10.0, 0.35

# guias del cartucho: labio interior a 27 mm del eje, alto 6 mm (la rampa C02 sobresale arriba)
LUZ = ANCHO_CART + 2.0
Y_LAB = LUZ / 2
ALTO_LAB = 6.0
X_IR = -290.0               # la barrera ve el borde -X del cartucho
Z_IR = Z_BANDA + 3.0

# motor NEMA17 (cabe en una bolsa impresa, sin tornillos)
NEMA = dict(lado=42.3, largo=48.0, pilot=22.0, eje_d=5.0, eje_l=24.0)
Y_PLACA = (78.0, 82.0)      # placa frontal del soporte (cara del motor en Y=82)
BOLSA = 42.9                # hueco para el motor (0,3 mm de holgura por lado)
Y_ACO = (46.0, 72.0)        # acople impreso
HEX_AC = 8.0                # espiga hexagonal del rodillo, de lado a lado
GUIA_TORN = [g + 30 + 60 * k for g in GUIAS[:-1] for k in range(3)]
X_REF = 300.0                # donde se muestra una tablilla de ejemplo sobre la cama


def caja(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def cil_z(x, y, z0, z1, d, d2=None):
    return Manifold.cylinder(z1 - z0, d / 2, (d if d2 is None else d2) / 2).translate((x, y, z0))


def cil_y(x, z, y0, y1, d, d2=None):
    m = Manifold.cylinder(y1 - y0, d / 2, (d if d2 is None else d2) / 2)
    return m.rotate((-90, 0, 0)).translate((x, y0, z))


def cil_x(y, z, x0, x1, d):
    return Manifold.cylinder(x1 - x0, d / 2).rotate((0, 90, 0)).translate((x0, y, z))


def hex_y(x, z, y0, y1, ac):
    r = ac / math.sqrt(3)
    pts = [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    return CrossSection([pts]).extrude(y1 - y0).rotate((-90, 0, 0)).translate((x, y0, z))


def union(ms):
    out = ms[0]
    for m in ms[1:]:
        out = out + m
    return out


def hilo(x0, x1, y, z, extra=0.0):
    """Rosca gruesa de dos filos: elipse que gira a lo largo del eje X. El hueco es la misma forma con juego."""
    a, b = HILO_A + extra, HILO_B + extra
    pts = [(a * math.cos(t), b * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
    L = x1 - x0
    fase = math.radians(360.0 * (x0 - X_TEN) / HILO_PASO)       # misma fase global: tornillo y hueco encajan
    pts = [(px * math.cos(fase) - py * math.sin(fase), px * math.sin(fase) + py * math.cos(fase)) for px, py in pts]
    m = CrossSection([pts]).extrude(L, n_divisions=int(L * 3), twist_degrees=360.0 * L / HILO_PASO)
    return m.rotate((0, 90, 0)).translate((x0, y, z))


# =====================================================================
# Posiciones del cartucho (p = 0 con el vaso 5 bajo el hueco)
# =====================================================================
def desp_vaso(k):
    """Desplazamiento del cartucho (mm) con el vaso k (1..9) bajo el hueco."""
    return -(X_VASO1 + (k - 1) * PASO_VASO)


S_MIN = desp_vaso(9)                    # -152
S_RECHAZO = -X_RAMPA                    # +190
S_A = lambda k: A_X - (X_VASO1 + (k - 1) * PASO_VASO)   # vaso k en el punto A


def nervio_x(x0, x1):
    cx0, cx1 = max(x0, CAMA_X[0]), min(x1, CAMA_X[1])
    nx0 = cx0 + 20 if x0 == X_INI else cx0
    nx1 = cx1 - 20 if x1 == X_FIN else cx1
    return cx0, cx1, nx0, nx1


# =====================================================================
# Piezas
# =====================================================================
def modulo(x0, x1):
    extremo_mot = x0 == X_INI
    extremo_ten = x1 == X_FIN
    cx0, cx1, nx0, nx1 = nervio_x(x0, x1)
    cama = caja(cx0, cx1, Y_NERVIO[0], Y_PARED, Z_CAMA - ESP_CAMA, Z_CAMA)
    pared = caja(x0, x1, Y_PARED, YW, Z_CAMA - ALTO_PARED, Z_CAMA)
    nervio = caja(nx0, nx1, Y_NERVIO[0], Y_NERVIO[1], Z_CAMA - PROF_NERVIO, Z_CAMA)
    partes = [cama, pared, nervio]
    ymn = (Y_NERVIO[0] + Y_NERVIO[1]) / 2
    ag = []
    # bridas de union entre modulos: una clavija Ø6 en la pared y otra en el nervio
    for xj, lado in ((x0, -1), (x1, 1)):
        if (extremo_mot and lado < 0) or (extremo_ten and lado > 0):
            continue
        xa, xb = (xj, xj + 6) if lado < 0 else (xj - 6, xj)
        partes.append(caja(xa, xb, YW, YW + 8, Z_CAMA - ALTO_PARED, Z_CAMA))
        hx = (xj - 0.5, xj + 6) if lado < 0 else (xj - 6, xj + 0.5)
        ag.append(cil_x(YW + 4, Z_CAMA - ALTO_PARED / 2, hx[0], hx[1], PEG_H))
        if nx0 <= xa and xb <= nx1:
            partes.append(caja(xa, xb, Y_NERVIO[0] - 8, Y_NERVIO[0], Z_CAMA - PROF_NERVIO, Z_CAMA))
            ag.append(cil_x(Y_NERVIO[0] - 4, Z_CAMA - PROF_NERVIO / 2, hx[0], hx[1], PEG_H))
    for xp in PATAS_X:
        if x0 + 12 < xp < x1 - 12:
            partes.append(caja(xp - 10, xp + 10, YW, YW + 3, Z_CAMA - ALTO_PARED, Z_CAMA))
            for dx in (-5, 5):
                ag.append(cil_y(xp + dx, Z_CAMA - 12, YW - 3, YW + 3.01, PEG_H))
    if extremo_ten:
        partes.append(caja(x1 - 6, x1, YW, YW + 14, Z_EJE - 9, Z_EJE + 9))
    if extremo_mot:
        partes.append(cil_y(X_MOT, Z_EJE, Y_PARED, YW + 6, 34))
    m = union(partes)
    # ventanas de aligeramiento de la pared (no sobre las patas ni los extremos)
    for xa in np.arange(x0 + 16, x1 - 16 - 22, 34.0):
        if extremo_mot and xa < X_MOT + 40:
            continue
        if extremo_ten and xa > X_TEN - 50:
            continue
        if any(xa - 14 < xp < xa + 22 + 14 for xp in PATAS_X):
            continue
        m = m - caja(xa, xa + 22, Y_PARED - 1, YW + 1, Z_CAMA - ALTO_PARED + 8, Z_CAMA - 8)
    # clavijas verticales de las guias
    for xg in GUIA_TORN:
        if nx0 + 4 < xg < nx1 - 4:
            ag.append(cil_z(xg, ymn, Z_CAMA - 4.5, Z_CAMA + 1, PEG_H))
        if x0 + 4 < xg < x1 - 4 and CAMA_X[0] - 2 < xg < CAMA_X[1] + 2:
            ag.append(cil_z(xg, Y_PARED + ESP_PARED / 2, Z_CAMA - 4.5, Z_CAMA + 1, PEG_H))
    # encaste con la tapa -Y: el nervio pierde la mitad de abajo en TRASLAPE y lleva dos clavijas verticales
    if extremo_mot:
        ag.append(caja(nx0 - 1, nx0 + TRASLAPE + 0.4, Y_NERVIO[0] - 0.1, Y_NERVIO[1], Z_CAMA - PROF_NERVIO - 1, Z_CAMA - PROF_NERVIO / 2))
        for dx in (4, 12):
            ag.append(cil_z(nx0 + dx, ymn, Z_CAMA - PROF_NERVIO - 1, Z_CAMA + 1, PEG_H))
    if extremo_ten:
        ag.append(caja(nx1 - TRASLAPE - 0.4, nx1 + 1, Y_NERVIO[0] - 0.1, Y_NERVIO[1], Z_CAMA - PROF_NERVIO - 1, Z_CAMA - PROF_NERVIO / 2))
        for dx in (4, 12):
            ag.append(cil_z(nx1 - dx, ymn, Z_CAMA - PROF_NERVIO - 1, Z_CAMA + 1, PEG_H))
        # ranura del muñon del rodillo libre y agujero del tornillo del tensor en la oreja
        ag.append(caja(X_TEN - CARRERA - PIN_H / 2, X_TEN + CARRERA + PIN_H / 2, Y_PARED - 1, YW + 1, Z_EJE - PIN_H / 2, Z_EJE + PIN_H / 2))
        ag.append(cil_x(YW + CT / 2, Z_EJE, x1 - 7, x1 + 1, 9.0))
    if extremo_mot:
        ag.append(cil_y(X_MOT, Z_EJE, Y_PARED - 1, YW + 7, PIN_H))
        # clavijas que sujetan el soporte del motor
        for dx in (-19, 19):
            for zz in (Z_CAMA - ALTO_PARED + 8, Z_CAMA - 5):
                ag.append(cil_y(X_MOT + dx, zz, YW - 6, YW + 0.01, PEG_H))
    for a in ag:
        m = m - a
    return m


def guia(x0, x1, lado):
    """Guia lateral en L: pie sobre la pared o el nervio (con clavijas) y labio de 6 mm a 1 mm sobre la cinta."""
    zt = Z_BANDA + ALTO_LAB
    if lado < 0:
        pie = caja(x0, x1, Y_NERVIO[0], Y_NERVIO[1], Z_CAMA, zt)
        lab = caja(x0, x1, -Y_LAB - 3, -Y_LAB, Z_BANDA + 1.0, zt)
        ala = caja(x0, x1, Y_NERVIO[0], -Y_LAB, zt - 3, zt)
        ytor = (Y_NERVIO[0] + Y_NERVIO[1]) / 2
    else:
        pie = caja(x0, x1, Y_PARED, YW, Z_CAMA, zt)
        lab = caja(x0, x1, Y_LAB, Y_LAB + 3, Z_BANDA + 1.0, zt)
        ala = caja(x0, x1, Y_LAB, YW, zt - 3, zt)
        ytor = Y_PARED + ESP_PARED / 2
    m = pie + lab + ala
    if x0 <= X_IR <= x1:
        # boss del LED / fototransistor de la barrera de referencia del cartucho
        if lado > 0:
            ya, yb = Y_LAB, Y_LAB + 3 + 5.0
        else:
            ya, yb = -Y_LAB - 3 - 5.0, -Y_LAB
        m = m + caja(X_IR - 6, X_IR + 6, ya, yb, Z_BANDA + 1.0, zt)
        if lado > 0:
            m = m - cil_y(X_IR, Z_IR, Y_LAB - 1, yb + 1, IR_VENTANA) - cil_y(X_IR, Z_IR, Y_LAB + 3, YW + 1, IR_D)
        else:
            m = m - cil_y(X_IR, Z_IR, ya - 1, -Y_LAB + 1, IR_VENTANA) - cil_y(X_IR, Z_IR, Y_NERVIO[0] - 1, -Y_LAB - 3, IR_D)
    for xg in GUIA_TORN:
        if x0 + 4 < xg < x1 - 4:
            m = m - cil_z(xg, ytor, Z_CAMA - 1, zt + 1, PEG_H)
    return m


def eje(motriz):
    """Eje de una pieza con muñones Ø10 (giran en la pared y la tapa) y un hexágono central donde se calza la rueda.
    El motriz termina en una espiga hexagonal de 8 mm para el acople."""
    if motriz:
        m = cil_y(0, 0, -41 + 1, 45.0, PIN_D) + hex_y(0, 0, 44.99, 57.0, HEX_AC)
    else:
        m = cil_y(0, 0, Y_TAPA[0] - CT + 1.5, YW + CT - 1.5, PIN_D)
    m = m + hex_y(0, 0, -RUEDA_W / 2 - 0.1, RUEDA_W / 2 + 0.1, HEX_E)
    return m.translate((X_MOT if motriz else X_TEN, 0, Z_EJE))


def rueda(x):
    """Rueda dentada de 8 dientes que toma los pasadores de la cadena por la ranura central de las tablillas."""
    n = DIENTES
    disco = cil_y(0, 0, -RUEDA_W / 2, RUEDA_W / 2, 2 * (RP + 1.2))
    for k in range(n):
        a = 2 * math.pi * k / n
        px, pz = RP * math.cos(a), RP * math.sin(a)
        disco = disco - cil_y(px, pz, -RUEDA_W, RUEDA_W, PIN_C + 0.6)
        # boca abierta hacia afuera para que entre el pasador
        boca = caja(0, 12, -RUEDA_W, RUEDA_W, -(PIN_C + 0.4) / 2, (PIN_C + 0.4) / 2)
        boca = boca.rotate((0, -math.degrees(a), 0)).translate((px, 0, pz))
        disco = disco - boca
    disco = disco - hex_y(0, 0, -RUEDA_W, RUEDA_W, HEX_E + 0.4)
    return disco.translate((x, 0, Z_EJE))


def tablilla(x=0.0, z=0.0):
    """Tablilla de 12 × 56 × 6 mm con el pasador trasero en (x, z): nudillos alternados, ranura central para la rueda.
    Se imprime con la cara de arriba sobre la cama."""
    h = ESP_BANDA / 2
    plate = caja(0, PASO, -ANCHO_BANDA / 2, ANCHO_BANDA / 2, -h, h)
    plate = plate - caja(-1, PASO + 1, -RANURA / 2, RANURA / 2, -h - 1, h + 1)
    seg = lambda j: (-ANCHO_BANDA / 2 + SEG * j, -ANCHO_BANDA / 2 + SEG * (j + 1))
    for j in (1, 5):                              # muescas traseras donde entran los nudillos de la tablilla anterior
        ya, yb = seg(j)
        plate = plate - caja(-1, KN_D / 2 + 0.6, ya, yb, -h - 1, h + 1)
    for j in (0, 2, 4, 6):                        # muescas delanteras para los nudillos de la siguiente
        ya, yb = seg(j)
        plate = plate - caja(PASO - KN_D / 2 - 0.6, PASO + 1, ya, yb, -h - 1, h + 1)
    nud = []
    for j in (0, 2, 4, 6):
        ya, yb = seg(j)
        nud.append(cil_y(0, 0, ya + 0.2, yb - 0.2, KN_D))
    for j in (1, 5):
        ya, yb = seg(j)
        nud.append(cil_y(PASO, 0, ya + 0.2, yb - 0.2, KN_D))
    m = plate + union(nud)
    m = m - cil_y(0, 0, -PIN_CL, PIN_CL, PIN_CH) - cil_y(PASO, 0, -PIN_CL, PIN_CL, PIN_CH)
    return m.translate((x, 0, z))


def pasador(x=0.0, z=0.0):
    return cil_y(x, z, -PIN_CL / 2, PIN_CL / 2, PIN_C)


def carro_tensor(lado):
    """Carro del eje libre: cuerpo con un hueco ciego para el muñón y una cola con la rosca del tensor."""
    y0, y1 = (YW, YW + CT) if lado > 0 else (Y_TAPA[0] - CT, Y_TAPA[0])
    ym = (y0 + y1) / 2
    m = caja(X_TEN - 10, X_TEN + 10, y0, y1, Z_EJE - 9, Z_EJE + 9)
    m = m + caja(X_TEN + 9.99, X_TEN + TAIL, y0, y1, Z_EJE - 7, Z_EJE + 7)
    if lado > 0:
        m = m - cil_y(X_TEN, Z_EJE, y0 - 1, y1 - 1, PIN_H)
    else:
        m = m - cil_y(X_TEN, Z_EJE, y0 + 1, y1 + 1, PIN_H)
    m = m - hilo(X_TEN + 8, X_TEN + TAIL + 0.5, ym, Z_EJE, HILO_JUEGO)
    return m


def tornillo_tensor(lado):
    """Tornillo impreso: cabeza ranurada afuera de la oreja, rosca gruesa que tira del carro."""
    ym = YW + CT / 2 if lado > 0 else Y_TAPA[0] - CT / 2
    m = hilo(X_TEN + 18, X_FIN + 0.01, ym, Z_EJE)
    cab = cil_x(ym, Z_EJE, X_FIN, X_FIN + 8, 22.0)
    for k in range(8):
        a = 2 * math.pi * k / 8
        cab = cab - cil_x(ym + 11 * math.cos(a), Z_EJE + 11 * math.sin(a), X_FIN - 1, X_FIN + 9, 3.0)
    return m + cab


def tapa(motor):
    """Tapa lateral -Y desmontable: se quita para meter la cinta cerrada por el costado.
    Se encaja en el nervio con una lengueta y dos clavijas verticales."""
    y0, y1 = Y_TAPA
    ymn = (Y_NERVIO[0] + Y_NERVIO[1]) / 2
    if motor:
        nx = CAMA_X[0] + 20
        m = caja(X_INI, CAMA_X[0], y0, y1, Z_CAMA - ALTO_PARED, Z_CAMA)
        m = m + caja(CAMA_X[0], nx, Y_NERVIO[0], y1, Z_CAMA - PROF_NERVIO, Z_CAMA - ESP_CAMA)
        m = m + caja(CAMA_X[0], nx, Y_NERVIO[0], y1, Z_CAMA - ALTO_PARED, Z_CAMA - PROF_NERVIO)
        lx0, lx1 = nx, nx + TRASLAPE
        hx = [nx + 4, nx + 12]
        m = m + cil_y(X_MOT, Z_EJE, y0 - 6, y1, 34)
        m = m - cil_y(X_MOT, Z_EJE, y0 - 7, y1 + 1, PIN_H)
    else:
        nx = CAMA_X[1] - 20
        m = caja(CAMA_X[1], X_FIN, y0, y1, Z_CAMA - ALTO_PARED, Z_CAMA)
        m = m + caja(nx, CAMA_X[1], Y_NERVIO[0], y1, Z_CAMA - PROF_NERVIO, Z_CAMA - ESP_CAMA)
        lx0, lx1 = nx - TRASLAPE, nx
        hx = [nx - 4, nx - 12]
        m = m + caja(X_FIN - 6, X_FIN, y0 - 14, y0, Z_EJE - 9, Z_EJE + 9)
        m = m - caja(X_TEN - CARRERA - PIN_H / 2, X_TEN + CARRERA + PIN_H / 2, y0 - 1, y1 + 1, Z_EJE - PIN_H / 2, Z_EJE + PIN_H / 2)
        m = m - cil_x(y0 - CT / 2, Z_EJE, X_FIN - 7, X_FIN + 1, 9.0)
    m = m + caja(lx0, lx1, Y_NERVIO[0], Y_NERVIO[1], Z_CAMA - PROF_NERVIO, Z_CAMA - PROF_NERVIO / 2 - 0.35)
    for x in hx:
        m = m - cil_z(x, ymn, Z_CAMA - PROF_NERVIO - 1, Z_CAMA - PROF_NERVIO / 2, PEG_H)
    return m


def acople():
    """Acople impreso: socket hexagonal para la espiga del rodillo y bolsillo en D para el eje Ø5 del motor."""
    y0, y1 = Y_ACO
    m = cil_y(X_MOT, Z_EJE, y0, y1, 19.0)
    m = m - hex_y(X_MOT, Z_EJE, y0 - 1, 58.0, HEX_AC + 0.4)
    d = cil_y(X_MOT, Z_EJE, 58.0, y1 + 1, NEMA["eje_d"] + 0.2) ^ caja(X_MOT - 3, X_MOT + 2.1, 57, y1 + 2, Z_EJE - 3, Z_EJE + 3)
    return m - d


def soporte_motor():
    """Base clavijada a la pared +Y y bolsa cuadrada donde el NEMA17 entra por atras. Sin tornillos."""
    x0 = X_MOT
    z_top = Z_EJE + BOLSA / 2 + 3
    z_bot = Z_EJE - BOLSA / 2 - 3
    base = caja(x0 - 25, x0 + 25, YW, YW + 6, Z_CAMA - ALTO_PARED, z_top)
    base = base - cil_y(x0, Z_EJE, YW - 1, YW + 7, 35.0)
    bolsa = caja(x0 - BOLSA / 2 - 3, x0 + BOLSA / 2 + 3, Y_PLACA[0], Y_PLACA[1] + NEMA["largo"] + 0.6, z_bot, z_top)
    bolsa = bolsa - caja(x0 - BOLSA / 2, x0 + BOLSA / 2, Y_PLACA[1], Y_PLACA[1] + NEMA["largo"] + 1.0, Z_EJE - BOLSA / 2, Z_EJE + BOLSA / 2)
    bolsa = bolsa - cil_y(x0, Z_EJE, Y_PLACA[0] - 1, Y_PLACA[1] + 1, NEMA["pilot"] + 1.0)
    m = base + bolsa
    for xs in (x0 - BOLSA / 2 - 3, x0 + BOLSA / 2 - 0.0):
        m = m + caja(xs, xs + 3, YW + 6 - 0.01, Y_PLACA[0] + 0.01, z_bot, z_top)
    # clavijas: 4 agujeros Ø6,2 a través de la base, ciegos en la pared
    for dx in (-19, 19):
        for zz in (Z_CAMA - ALTO_PARED + 8, Z_CAMA - 5):
            m = m - cil_y(x0 + dx, zz, YW - 0.01, YW + 6.01, PEG_H)
    return m


def pata(xp):
    """Placa contra la pared +Y (fuera del lazo, con dos clavijas) y zocalo bajo el retorno de la cinta."""
    y0 = YW + 3
    y1 = y0 + 7
    m = caja(xp - 10, xp + 10, y0, y1, MESA, Z_CAMA)
    m = m + caja(xp - 10, xp + 10, Y_NERVIO[0] - 4, y1, MESA, MESA + 4)
    m = m + caja(xp - 2, xp + 2, 6.0, y0, MESA + 4, MESA + 12)
    m = m - caja(xp - 6, xp + 6, Y_NERVIO[0] + 4, 0.0, MESA - 1, MESA + 5)
    for dx in (-5, 5):
        m = m - cil_y(xp + dx, Z_CAMA - 12, y0 - 0.01, y0 + 6.0, PEG_H)
    return m


def clavija():
    """Clavija Ø6 x 12 (la P02 de la etapa 1), puesta en el agujero de la pared del primer empalme."""
    return cil_x(YW + 4, Z_CAMA - ALTO_PARED / 2, -200.0 - 6.0, -200.0 + 6.0, PEG_D)


# =====================================================================
# Comprados y referencias
# =====================================================================
def lazo_banda():
    """Largo de la cadena por la línea de pasadores con las ruedas de radio primitivo RP."""
    return 2 * (X_TEN - X_MOT) + 2 * math.pi * RP


def nema():
    y0 = Y_PLACA[1]
    m = caja(X_MOT - NEMA["lado"] / 2, X_MOT + NEMA["lado"] / 2, y0, y0 + NEMA["largo"], Z_EJE - NEMA["lado"] / 2, Z_EJE + NEMA["lado"] / 2)
    m = m + cil_y(X_MOT, Z_EJE, y0 - 2, y0, NEMA["pilot"] - 0.5)
    eje = cil_y(X_MOT, Z_EJE, y0 - NEMA["eje_l"], y0, NEMA["eje_d"]) ^ caja(X_MOT - 3, X_MOT + 2.0, y0 - 25, y0 + 1, Z_EJE - 3, Z_EJE + 3)
    return m + eje


def leds_ref():
    yb = Y_LAB + 3
    led = cil_y(X_IR, Z_IR, yb, yb + 8, 5)
    foto = cil_y(X_IR, Z_IR, -yb - 8, -yb, 5)
    return led, foto


def vaso_rechazo():
    return cil_z(REC["x"], REC["y"], MESA, MESA + REC["h"], REC["d"]) - cil_z(REC["x"], REC["y"], MESA + 2, MESA + REC["h"] + 1, REC["d"] - 2.4)


# =====================================================================
# Exportacion
# =====================================================================
def malla(m: Manifold):
    mm = m.to_mesh()
    return (np.asarray(mm.vert_properties, dtype=np.float32)[:, :3], np.asarray(mm.tri_verts, dtype=np.uint32))


def b64(a):
    return base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()


def piezas():
    P = []
    for i in range(len(MODULOS) - 1):
        P.append((f"BT0{i + 1}", modulo(MODULOS[i], MODULOS[i + 1]), {}))
    for i in range(len(GUIAS) - 1):
        P.append(("BT08", guia(GUIAS[i], GUIAS[i + 1], -1), {"tag": f"G{i + 1}"}))
    for i in range(len(GUIAS) - 1):
        P.append(("BT09", guia(GUIAS[i], GUIAS[i + 1], 1), {"tag": f"G{i + 1}"}))
    P.append(("BT10", eje(True), {"pivote": [X_MOT, 0, Z_EJE], "eje": [0, 1, 0]}))
    P.append(("BT11", eje(False), {"pivote": [X_TEN, 0, Z_EJE], "eje": [0, 1, 0]}))
    P.append(("BT12", carro_tensor(1), {"tag": "+Y"}))
    P.append(("BT12", carro_tensor(-1), {"tag": "-Y"}))
    P.append(("BT13", tapa(True), {}))
    P.append(("BT14", tapa(False), {}))
    P.append(("BT15", soporte_motor(), {}))
    for xp in PATAS_X:
        P.append(("BT16", pata(xp), {}))
    P.append(("BT17", clavija(), {}))
    P.append(("BT18", tornillo_tensor(1), {"tag": "+Y"}))
    P.append(("BT18", tornillo_tensor(-1), {"tag": "-Y"}))
    P.append(("BT19", acople(), {"pivote": [X_MOT, 0, Z_EJE], "eje": [0, 1, 0]}))
    P.append(("BT20", rueda(X_MOT), {"tag": "motriz", "pivote": [X_MOT, 0, Z_EJE], "eje": [0, 1, 0]}))
    P.append(("BT20", rueda(X_TEN), {"tag": "libre", "pivote": [X_TEN, 0, Z_EJE], "eje": [0, 1, 0]}))
    P.append(("BT21", tablilla(X_REF, Z_PIN), {"origen": [X_REF, 0, Z_PIN]}))
    P.append(("BT22", pasador(X_REF, Z_PIN), {}))
    P.append(("K1", nema(), {}))
    led, foto = leds_ref()
    P.append(("K2", led, {}))
    P.append(("K3", foto, {}))
    P.append(("K4", vaso_rechazo(), {}))
    return P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", type=Path)
    a = ap.parse_args()
    out = []
    for pid, m, ex in piezas():
        v, t = malla(m)
        bb = m.bounding_box()
        out.append(dict(pid=pid, v=b64(v), t=b64(t), vol=round(m.volume() / 1000.0, 2), bb=[round(x, 1) for x in bb], **ex))
    sim = dict(z_banda=Z_BANDA, x_mot=X_MOT, x_ten=X_TEN, z_eje=Z_EJE, rp=RP, paso_cad=PASO, dientes=DIENTES, n_cad=N_TAB, z_pin=Z_PIN, esp=ESP_BANDA, ancho=ANCHO_BANDA,
               lazo=lazo_banda(), a_x=A_X, s_min=S_MIN, s_rechazo=S_RECHAZO, paso=PASO_VASO,
               x_vaso1=X_VASO1, x_rampa=X_RAMPA, cart=list(X_CART), x_ir=X_IR, z_ir=Z_IR, rec=REC,
               y_lab=Y_LAB, s_a=[S_A(k) for k in range(1, 10)])
    if a.datos:
        a.datos.write_text(json.dumps(dict(piezas=out, sim=sim)))
    for o in out:
        print(o["pid"], o.get("tag", ""), o["vol"], o["bb"])
    print("lazo", round(lazo_banda(), 1))


if __name__ == "__main__":
    main()
