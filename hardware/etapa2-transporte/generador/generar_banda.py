"""Banda de la etapa 2 (v3, print-and-place): cadena de tablillas en 12 secciones que salen articuladas de una sola
impresión (pasador integrado), bastidor en 6 módulos que se encajan como rompecabezas (sin clavijas sueltas) y piezas
pensadas para imprimirse sin voladizos.

    pip install manifold3d numpy
    python generar_banda.py --datos banda.json     # mallas del ensamble para el visor

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
# cadena de tablillas impresas en secciones de 14 eslabones; 8 dientes; el pasador va fundido a la tablilla
DIENTES = 8
SECC_N, N_SECC = 14, 12
N_TAB = SECC_N * N_SECC                 # 168 eslabones
X_MOT, X_TEN = -330.0, 654.0            # ejes de la rueda motriz (-X) y de la libre (+X, con tensor); X_TEN = cadena sin holgura
PASO = 2 * (X_TEN - X_MOT) / (N_TAB - DIENTES)      # 12,3 mm: la cadena cierra justo con las ruedas en X_MOT y X_TEN
ANCHO_BANDA, ESP_BANDA = 56.0, 6.0      # ancho y espesor de la tablilla
SEG = 8.0                               # 7 segmentos de 8 mm: nudillos alternados y ranura central
KN_D = 6.0                              # nudillo (se aplana a la altura de la tablilla)
PIN_C, PIN_CH, PIN_CL = 3.0, 3.6, 57.0  # pasador, agujero del nudillo (0,3 mm de juego por lado: es el mínimo para que no se suelden al imprimir) y largo de corte
PIN_RANURA = 2.7                        # boca de los nudillos que encajan a presión entre secciones
RANURA, RUEDA_W = 8.4, 7.8              # ranura de la tablilla y grosor de la rueda dentada
RP = PASO / (2 * math.sin(math.pi / DIENTES))      # radio primitivo (centros de pasadores)
HEX_E = 10.0                            # hexagono del eje donde se calza la rueda
Z_PIN = Z_BANDA - ESP_BANDA / 2         # altura de los pasadores arriba
Z_CAMA = Z_BANDA - ESP_BANDA
Z_EJE = Z_PIN - RP
CARRERA_ATRAS, CARRERA_ADEL = 6.0, 24.0 # el eje libre se mueve entre X_TEN-6 (cadena suelta) y X_TEN+24 (tensa, con el juego de 168 articulaciones)
TAIL = 40.0                             # cola con rosca del carro del tensor
ESP_CAMA, ALTO_PARED, ESP_PARED = 3.2, 30.0, 9.0
Y_PARED = ANCHO_BANDA / 2 + 2.0         # cara interior de la pared +Y
YW = Y_PARED + ESP_PARED                # cara exterior de la pared +Y
Y_NERVIO = (-Y_PARED - 9.0, -Y_PARED)   # nervio -Y bajo la cama
PROF_NERVIO = 14.0
Y_TAPA = (-Y_PARED - 5.0, -Y_PARED)     # tapas -Y: cara interior a 2 mm del borde de la cadena
X_INI, X_FIN = -358.0, 722.0
JUNTAS = [-178.0, 2.0, 182.0, 362.0, 542.0]          # rompecabezas entre módulos
MODULOS = [X_INI] + JUNTAS + [X_FIN]
LAP = 12.0                              # los medios espesores de pared y nervio se traslapan 12 mm a cada lado de la junta
CAMA_X = (X_MOT + 17.0, X_TEN - 17.0)
PATAS_X = [-268.0, -88.0, 92.0, 272.0, 452.0, 596.0]
GUIAS = [-300.0, -127.0, 64.0, 255.0, 446.0, 637.0]

# clavijas Ø6 integradas (guías y patas), muñones Ø10 impresos
PEG_D, PEG_H, PEG_L = 6.0, 6.3, 5.5
PIN_D, PIN_H = 10.0, 10.4
CT = 12.0                               # espesor de los carros del tensor
TONG = 10.0                             # largo de la lengüeta de las tapas
Z_TONG = Z_CAMA - 7.0                   # centro de la lengüeta: z = 37
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
HEX_AC = 8.0                # espiga hexagonal del eje, de lado a lado
APOT_BUJE = Z_CAMA - Z_EJE  # el buje octogonal de la pared llega justo a la altura de la cama (sin voladizo)
X_REF = 300.0               # donde se muestra una sección de ejemplo sobre la cama


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


def rect2(x0, x1, y0, y1):
    return CrossSection.square((x1 - x0, y1 - y0)).translate((x0, y0))


def prisma_z(cs, z0, z1):
    return cs.extrude(z1 - z0).translate((0, 0, z0))


def prisma_y(cs, y0, y1):
    """Extruye un perfil (x, z) a lo largo de Y entre y0 e y1."""
    return cs.extrude(y1 - y0).rotate((90, 0, 0)).translate((0, y1, 0))


def octo_y(x, z, y0, y1, apot):
    """Prisma octogonal a lo largo de Y con caras planas arriba y abajo (apotema dado)."""
    R = apot / math.cos(math.radians(22.5))
    pts = [(R * math.cos(math.radians(22.5 + 45 * k)), R * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]
    return CrossSection([pts]).extrude(y1 - y0).rotate((-90, 0, 0)).translate((x, y0, z))


def losange_y(x, z, y0, y1, r):
    """Rombo con puntas arriba y abajo: cerrado el hueco horizontal a 45 grados (sin techo plano)."""
    return caja(-r, r, y0, y1, -r, r).rotate((0, 45, 0)).translate((x, 0, z))


def losange_x(y, z, x0, x1, r):
    return caja(x0, x1, -r, r, -r, r).rotate((45, 0, 0)).translate((0, y, z))


def hueco_y(x, z, y0, y1, d):
    """Agujero horizontal a lo largo de Y que se imprime sin soporte (círculo + rombo)."""
    return cil_y(x, z, y0, y1, d) + losange_y(x, z, y0, y1, d / 2)


def hueco_x(y, z, x0, x1, d):
    return cil_x(y, z, x0, x1, d) + losange_x(y, z, x0, x1, d / 2)


def hueco_px(x, z, y0, y1, d):
    """Agujero a lo largo de Y con la punta del rombo hacia +X: el carro del tensor se imprime parado sobre su cola (+X arriba)."""
    return hueco_y(0, 0, y0, y1, d).rotate((0, 90, 0)).translate((x, 0, z))


def clavija_y(x, z, y0, y1, d, arriba=True):
    """Clavija horizontal en gota (punta arriba): se imprime parada sin soporte."""
    r = d / 2
    k = r / math.sqrt(2)
    s = -1 if arriba else 1                       # en el perfil (px, py) py positivo = Z negativo tras rotar
    gota = CrossSection.circle(r, 48) + CrossSection([[(k, s * k), (-k, s * k), (0, s * r * math.sqrt(2))]])
    return gota.extrude(y1 - y0).rotate((-90, 0, 0)).translate((x, y0, z))


def pasador_gota(x, z, y0, y1, d=PIN_C, corte=1.55):
    """Pasador Ø3 con la parte de abajo (la que mira a la cama al imprimir) en punta recortada a 45 grados: no cuelga y gira en el agujero."""
    r = d / 2
    k = r / math.sqrt(2)
    gota = CrossSection.circle(r, 48) + CrossSection([[(k, -k), (-k, -k), (0, -r * math.sqrt(2))]])
    gota = gota ^ rect2(-5, 5, -corte, 5)
    return gota.extrude(y1 - y0).rotate((-90, 0, 0)).translate((x, y0, z))


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


NX0, NX1 = CAMA_X[0] + 20.0, CAMA_X[1] - 20.0        # el nervio -Y empieza y acaba lejos de las ruedas (ahí van las tapas)
PROHIBIDO = [(xj - LAP - 5.0, xj + LAP + 5.0) for xj in JUNTAS] + [(NX0 - 3.0, NX0 + TONG + 5.0), (NX1 - TONG - 5.0, NX1 + 3.0)]


def clavijas_guia(x0, x1):
    """Tres posiciones de clavija por guía, lejos de las juntas, las lengüetas de las tapas y el LED."""
    L, out = x1 - x0, []
    for f in (1 / 6, 0.5, 5 / 6):
        for dx in sorted(range(-45, 46, 2), key=abs):
            c = x0 + f * L + dx
            if x0 + 8 < c < x1 - 8 and not any(a < c < b for a, b in PROHIBIDO) and abs(c - X_IR) > 9:
                out.append(c)
                break
    return out


def cuerpo():
    """Bastidor continuo (se parte luego en módulos): cama bajo la cadena, pared +Y, nervio -Y, buje del motor, oreja del tensor."""
    cama = caja(CAMA_X[0], CAMA_X[1], Y_NERVIO[0], Y_PARED, Z_CAMA - ESP_CAMA, Z_CAMA)
    pared = caja(X_INI, X_FIN, Y_PARED, YW, Z_CAMA - ALTO_PARED, Z_CAMA)
    nervio = caja(NX0, NX1, Y_NERVIO[0], Y_NERVIO[1], Z_CAMA - PROF_NERVIO, Z_CAMA)
    partes = [cama, pared, nervio, octo_y(X_MOT, Z_EJE, Y_PARED, YW + 6, APOT_BUJE)]
    partes.append(caja(X_FIN - 6, X_FIN, YW, YW + 14, Z_EJE - 9, Z_CAMA))                     # oreja del tornillo del tensor
    for xp in PATAS_X:
        partes.append(caja(xp - 10, xp + 10, YW, YW + 3, Z_CAMA - ALTO_PARED, Z_CAMA))          # tope de la pata
    m = union(partes)
    ag = [hueco_y(X_MOT, Z_EJE, Y_PARED - 1, YW + 7, PIN_H)]                                   # muñón del eje motriz
    ag.append(caja(X_TEN - CARRERA_ATRAS - PIN_H / 2, X_TEN + CARRERA_ADEL + PIN_H / 2, Y_PARED - 1, YW + 1, Z_CAMA - ALTO_PARED - 1, Z_EJE + PIN_H / 2))   # muesca abierta abajo (sin techo)
    ag.append(hueco_x(YW + CT / 2, Z_EJE, X_FIN - 7, X_FIN + 1, 9.0))                           # paso del tornillo del tensor
    for xp in PATAS_X:                                                                         # agujeros de las clavijas de las patas
        for dx in (-5, 5):
            ag.append(cil_y(xp + dx, Z_CAMA - 12, YW + 3 - 8.4, YW + 3.01, PEG_H) + losange_y(xp + dx, Z_CAMA - 12, YW + 3 - 8.4, YW + 3.01, PEG_H / 2))
    for i in range(len(GUIAS) - 1):                                                            # agujeros de las clavijas de las guías
        for xg in clavijas_guia(GUIAS[i], GUIAS[i + 1]):
            ag.append(cil_z(xg, (Y_NERVIO[0] + Y_NERVIO[1]) / 2, Z_CAMA - PEG_L - 0.7, Z_CAMA + 1, PEG_H))
            ag.append(cil_z(xg, Y_PARED + ESP_PARED / 2, Z_CAMA - PEG_L - 0.7, Z_CAMA + 1, PEG_H))
    for nx, signo in ((NX0, 1), (NX1, -1)):                                                    # bolsillo de la lengüeta de cada tapa
        xa, xb = (nx - 0.01, nx + TONG + 0.4) if signo > 0 else (nx - TONG - 0.4, nx + 0.01)
        ag.append(caja(xa, xb, Y_NERVIO[0] - 1, Y_NERVIO[1] + 1, Z_TONG - 3.25, Z_TONG + 3.25))
    for a in ag:
        m = m - a
    return m


def _izq(xj):
    """Territorio del módulo de la izquierda en la junta xj: recto, con dos colas de milano en la cama y los medios espesores de pared y nervio."""
    z = rect2(-1000, xj, -100, 100)
    for yc in (-16.0, 12.0):
        z = z + CrossSection([[(xj - 1, yc - 4), (xj, yc - 4), (xj + 9, yc - 7), (xj + 9, yc + 7), (xj, yc + 4), (xj - 1, yc + 4)]])
    z = z + rect2(xj - 1, xj + LAP, Y_PARED + ESP_PARED / 2, 100) + rect2(xj - 1, xj + LAP, -100, -Y_PARED - ESP_PARED / 2)
    z = z - rect2(xj - LAP, xj + 1, Y_PARED, Y_PARED + ESP_PARED / 2) - rect2(xj - LAP, xj + 1, -Y_PARED - ESP_PARED / 2, -Y_PARED)
    return z


def territorios():
    big = rect2(-1000, 1000, -100, 100)
    out = []
    for k in range(len(MODULOS) - 1):
        t = big
        if k > 0:
            t = t ^ (big - _izq(JUNTAS[k - 1]))
        if k < len(JUNTAS):
            t = t ^ _izq(JUNTAS[k])
        out.append(t.offset(-0.1, JoinType.Miter, 2.0, 0))
    return out


def modulos():
    c = cuerpo()
    return [c ^ prisma_z(t, -5, 100) for t in territorios()]


def guia(x0, x1, lado):
    """Guia lateral en L: pie con tres clavijas integradas hacia abajo y labio de 6 mm a 1 mm sobre la cadena.
    Se imprime boca abajo (el ala en la cama): las clavijas quedan paradas arriba y no hay voladizos."""
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
            m = m - cil_y(X_IR, Z_IR, Y_LAB - 1, yb + 1, IR_VENTANA) - hueco_y(X_IR, Z_IR, Y_LAB + 3, YW + 1, IR_D)
        else:
            m = m - cil_y(X_IR, Z_IR, ya - 1, -Y_LAB + 1, IR_VENTANA) - hueco_y(X_IR, Z_IR, Y_NERVIO[0] - 1, -Y_LAB - 3, IR_D)
    for xg in clavijas_guia(x0, x1):
        m = m + cil_z(xg, ytor, Z_CAMA - PEG_L, Z_CAMA + 0.01, PEG_D)
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


def tablilla(x=0.0, z=0.0, primero=False):
    """Eslabón de 12,3 × 56 × 6 mm. Adelante: nudillos con el pasador Ø3 fundido. Atrás: nudillos con agujero Ø3,4 que abraza el
    pasador del eslabón anterior (print-in-place, 0,2 mm de juego). El primer eslabón de cada sección lleva los nudillos abiertos por
    abajo (ranura de 2,7 mm): se encajan a presión en el pasador del último eslabón de la sección anterior.
    Se imprime con la cara de arriba contra la cama; ningún voladizo pasa de 45 grados."""
    h = ESP_BANDA / 2
    kr = 3.2
    plate = caja(0, PASO, -ANCHO_BANDA / 2, ANCHO_BANDA / 2, -h, h)
    plate = plate - caja(-1, PASO + 1, -RANURA / 2, RANURA / 2, -h - 1, h + 1)
    seg = lambda j: (-ANCHO_BANDA / 2 + SEG * j, -ANCHO_BANDA / 2 + SEG * (j + 1))
    for j in (1, 5):                              # muescas traseras donde entran los nudillos del eslabón anterior
        ya, yb = seg(j)
        plate = plate - caja(-1, KN_D / 2 + 0.6, ya, yb, -h - 1, h + 1)
    for j in (0, 2, 4, 6):                        # muescas delanteras para los nudillos del siguiente
        ya, yb = seg(j)
        plate = plate - caja(PASO - KN_D / 2 - 0.6, PASO + 1, ya, yb, -h - 1, h + 1)
    def nud(xn, j):
        ya, yb = seg(j)
        return cil_y(xn, 0, ya + 0.2, yb - 0.2, 2 * kr) ^ caja(xn - 4, xn + 4, ya, yb, -h, h)
    m = plate + union([nud(0, j) for j in (0, 2, 4, 6)] + [nud(PASO, j) for j in (1, 5)])
    m = m - hueco_y(0, 0, -PIN_CL, PIN_CL, PIN_CH)
    if primero:
        m = m - caja(-PIN_RANURA / 2, PIN_RANURA / 2, -PIN_CL, PIN_CL, -h - 1, 0)
    m = m + pasador_gota(PASO, 0, -27.5, 27.5)
    return m.translate((x, 0, z))


def seccion(x=0.0, z=0.0):
    """Sección de 14 eslabones que se imprime ya articulada (print-in-place); la rueda toma los pasadores por la ranura central."""
    return union([tablilla(i * PASO, 0, primero=i == 0) for i in range(SECC_N)]).translate((x, 0, z))


def carro_tensor(lado):
    """Carro del eje libre: cuerpo con un hueco ciego para el muñón y una cola con la rosca del tensor."""
    y0, y1 = (YW, YW + CT) if lado > 0 else (Y_TAPA[0] - CT, Y_TAPA[0])
    ym = (y0 + y1) / 2
    m = caja(X_TEN - 10, X_TEN + 10, y0, y1, Z_EJE - 9, Z_EJE + 9)
    m = m + caja(X_TEN + 9.99, X_TEN + TAIL, y0, y1, Z_EJE - 7, Z_EJE + 7)
    if lado > 0:
        m = m - hueco_px(X_TEN, Z_EJE, y0 - 1, y1 - 1, PIN_H)
    else:
        m = m - hueco_px(X_TEN, Z_EJE, y0 + 1, y1 + 1, PIN_H)
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
    """Tapa lateral -Y desmontable: se quita para meter la cadena por el costado. La lengüeta de 10 mm entra por Y en el
    bolsillo del nervio y se pega con cianoacrilato. Se imprime acostada sobre la cara interior (sin voladizos)."""
    y0, y1 = Y_TAPA
    if motor:
        m = caja(X_INI, CAMA_X[0], y0, y1, Z_CAMA - ALTO_PARED, Z_CAMA)
        m = m + caja(CAMA_X[0], NX0, Y_NERVIO[0], y1, Z_CAMA - ALTO_PARED, Z_CAMA - ESP_CAMA)
        m = m + caja(NX0 - 0.01, NX0 + TONG, Y_NERVIO[0], Y_NERVIO[1], Z_TONG - 3.0, Z_TONG + 3.0)
        m = m + cil_y(X_MOT, Z_EJE, y0 - 6, y1, 34)
        m = m - hueco_y(X_MOT, Z_EJE, y0 - 7, y1 + 1, PIN_H)
    else:
        m = caja(CAMA_X[1], X_FIN, y0, y1, Z_CAMA - ALTO_PARED, Z_CAMA)
        m = m + caja(NX1, CAMA_X[1], Y_NERVIO[0], y1, Z_CAMA - ALTO_PARED, Z_CAMA - ESP_CAMA)
        m = m + caja(NX1 - TONG, NX1 + 0.01, Y_NERVIO[0], Y_NERVIO[1], Z_TONG - 3.0, Z_TONG + 3.0)
        m = m + caja(X_FIN - 6, X_FIN, y0 - 14, y0, Z_EJE - 9, Z_CAMA)
        m = m - caja(X_TEN - CARRERA_ATRAS - PIN_H / 2, X_TEN + CARRERA_ADEL + PIN_H / 2, y0 - 1, y1 + 1, Z_EJE - PIN_H / 2, Z_EJE + PIN_H / 2)
        m = m - hueco_x(0, 0, X_FIN - 7, X_FIN + 1, 9.0).rotate((90, 0, 0)).translate((0, y0 - CT / 2, Z_EJE))   # punta del rombo hacia -Y (arriba al imprimir)
    return m


def acople():
    """Acople impreso: socket hexagonal para la espiga del rodillo y bolsillo en D para el eje Ø5 del motor."""
    y0, y1 = Y_ACO
    m = cil_y(X_MOT, Z_EJE, y0, y1, 19.0)
    m = m - hex_y(X_MOT, Z_EJE, y0 - 1, 58.0, HEX_AC + 0.4)
    d = cil_y(X_MOT, Z_EJE, 58.0, y1 + 1, NEMA["eje_d"] + 0.2) ^ caja(X_MOT - 3, X_MOT + 2.1, 57, y1 + 2, Z_EJE - 3, Z_EJE + 3)
    return m - d


def soporte_motor():
    """Soporte del NEMA17 de una pieza: base que se pega a la pared +Y sobre el buje octogonal, jaula que se cierra en cono hacia la
    placa (sin puentes) y bolsa cuadrada donde el motor entra por atrás. Se imprime con la base en la cama y la boca de la bolsa arriba."""
    x0 = X_MOT
    z_top = Z_EJE + BOLSA / 2 + 3
    z_bot = Z_EJE - BOLSA / 2 - 3
    zb = Z_CAMA - ALTO_PARED
    y_ini = YW
    y_fin = Y_PLACA[1] + NEMA["largo"] + 0.6
    base = caja(x0 - 25, x0 + 25, y_ini, y_ini + 6, zb, z_top)
    placa = caja(x0 - BOLSA / 2 - 3, x0 + BOLSA / 2 + 3, Y_PLACA[0], Y_PLACA[1], z_bot, z_top)
    jaula = Manifold.batch_hull([base, placa])
    bolsa = caja(x0 - BOLSA / 2 - 3, x0 + BOLSA / 2 + 3, Y_PLACA[1], y_fin, z_bot, z_top)
    m = jaula + bolsa
    # interior de la jaula: caja de 34 que se cierra en cono hasta el hueco Ø23 de la placa
    caja_int = caja(x0 - 17, x0 + 17, y_ini + 6, Y_PLACA[0] - 14, Z_EJE - 17, Z_EJE + 17)
    cono = Manifold.batch_hull([caja_int, cil_y(x0, Z_EJE, Y_PLACA[0] - 0.2, Y_PLACA[0], 23.0)])
    m = m - cono
    m = m - octo_y(x0, Z_EJE, y_ini - 1, y_ini + 6.01, APOT_BUJE + 0.35)                     # calza sobre el buje de la pared
    m = m - cil_y(x0, Z_EJE, Y_PLACA[0] - 1, Y_PLACA[1] + 1, NEMA["pilot"] + 1.0)
    m = m - caja(x0 - BOLSA / 2, x0 + BOLSA / 2, Y_PLACA[1], y_fin + 1, Z_EJE - BOLSA / 2, Z_EJE + BOLSA / 2)
    return m


def pata(xp):
    """Placa contra la pared +Y con dos clavijas integradas en gota, zócalo bajo el retorno de la cadena y refuerzo. Se imprime de pie."""
    y0 = YW + 3
    y1 = y0 + 7
    m = caja(xp - 10, xp + 10, y0, y1, MESA, Z_CAMA)
    m = m + caja(xp - 10, xp + 10, Y_NERVIO[0] - 4, y1, MESA, MESA + 4)
    m = m + caja(xp - 2, xp + 2, 6.0, y0, MESA + 4, MESA + 11)
    m = m - caja(xp - 6, xp + 6, Y_NERVIO[0] + 4, 0.0, MESA - 1, MESA + 5)
    for dx in (-5, 5):
        m = m + clavija_y(xp + dx, Z_CAMA - 12, y0 - 8, y0 + 0.01, PEG_D)
    return m


# =====================================================================
# Comprados y referencias
# =====================================================================
def lazo_banda():
    """Largo de la cadena por la línea de pasadores: 168 eslabones de paso PASO."""
    return N_TAB * PASO


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
    """Piezas del ensamble: (id, malla, extras). Las que se imprimen en varias copias van una sola vez (cantidad en el visor)."""
    P = []
    for i, m in enumerate(modulos()):
        P.append((f"BT0{i + 1}", m, {}))
    P.append(("BT07", tapa(True), {}))
    P.append(("BT08", tapa(False), {}))
    for i in range(len(GUIAS) - 1):
        P.append(("BT09", guia(GUIAS[i], GUIAS[i + 1], -1), {"tag": f"G{i + 1}"}))
    for i in range(len(GUIAS) - 1):
        P.append(("BT10", guia(GUIAS[i], GUIAS[i + 1], 1), {"tag": f"G{i + 1}"}))
    P.append(("BT11", eje(True), {"pivote": [X_MOT, 0, Z_EJE], "eje": [0, 1, 0]}))
    P.append(("BT12", eje(False), {"pivote": [X_TEN, 0, Z_EJE], "eje": [0, 1, 0]}))
    P.append(("BT13", carro_tensor(1), {"tag": "+Y"}))
    P.append(("BT13", carro_tensor(-1), {"tag": "-Y"}))
    P.append(("BT14", tornillo_tensor(1), {"tag": "+Y"}))
    P.append(("BT14", tornillo_tensor(-1), {"tag": "-Y"}))
    P.append(("BT15", soporte_motor(), {}))
    P.append(("BT16", acople(), {"pivote": [X_MOT, 0, Z_EJE], "eje": [0, 1, 0]}))
    P.append(("BT17", rueda(X_MOT), {"tag": "motriz", "pivote": [X_MOT, 0, Z_EJE], "eje": [0, 1, 0]}))
    P.append(("BT17", rueda(X_TEN), {"tag": "libre", "pivote": [X_TEN, 0, Z_EJE], "eje": [0, 1, 0]}))
    for xp in PATAS_X:
        P.append(("BT18", pata(xp), {}))
    P.append(("BT19", seccion(X_REF, Z_PIN), {"origen": [X_REF, 0, Z_PIN]}))
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
    aux = tablilla(X_REF, Z_PIN)
    for pid, m, ex in piezas():
        v, t = malla(m)
        bb = m.bounding_box()
        out.append(dict(pid=pid, v=b64(v), t=b64(t), vol=round(m.volume() / 1000.0, 2), bb=[round(x, 1) for x in bb], **ex))
    v, t = malla(aux)
    out.append(dict(pid="AUX", v=b64(v), t=b64(t), vol=0, bb=[0] * 6, aux=True, origen=[X_REF, 0, Z_PIN]))
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
