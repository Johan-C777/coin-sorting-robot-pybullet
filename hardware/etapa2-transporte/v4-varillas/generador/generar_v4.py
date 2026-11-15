"""Etapa 2 v4: carro sobre 2 varillas + hilo con polea en el motor (sin cadena, sin retorno).

Marco: X a lo largo (embudo en X = 0), Y a lo ancho, Z arriba (mesa Z = 0). Cartucho: fondo en Z = 50, 52 mm de ancho,
386 mm de largo; el vaso 9 está bajo el embudo con el carro en u = 0 y el vaso 1 en el punto A (X = 470) con u = 774 mm.

    pip install manifold3d numpy
    python generar_v4.py            # imprime un resumen
"""
from __future__ import annotations
import os
import math, sys
import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_banda as g
from generar_banda import caja, cil_y, cil_x, cil_z, union, prisma_y, hueco_y, hueco_x, octo_y

set_circular_segments(64)

# --------------------------------------------------------------- datos de la torre v5 (de la etapa 1)
Z_CART = 50.0                       # fondo del cartucho
CART_X = (-209.0, 177.0)            # extremos del cartucho armado (marco del cartucho)
CART_W = 52.0
U_MAX = 774.0                       # carrera (vaso 9 bajo el embudo -> vaso 1 en A)
DESP0 = -152.0                      # marco del cartucho -> mundo con u = 0 (vaso 9 en X_VASO9 = +152 sube a 0)
X_CTR0 = (CART_X[0] + CART_X[1]) / 2 + DESP0     # centro del cartucho con u = 0: -168

# --------------------------------------------------------------- varillas y carro
D_ROD = 9.525                       # varilla lisa de 3/8" (se cambia por 10, 12 o 12,7 mm cambiando este número)
D_BORE = D_ROD + 0.475              # agujero del buje impreso (0,24 mm de juego por lado)
Y_ROD, Z_ROD = 30.0, 39.5
SL_LEN, SL_SP, SL_AP = 30.0, 130.0, 8.5   # largo del buje, distancia entre pares de bujes, apotema del octógono exterior
BLK_LEN, BLK_Y = 35.0, 38.5
PLACA = 4.0                         # espesor del carro (de Z=46 a 50)
Z_LINEA = 38.5                      # altura del hilo que sube al carro
TAB_X, TAB_Y = 11.0, 3.0
HILO_D = 2.4                        # agujero para el hilo en la oreja
C_MIN, C_MAX = X_CTR0, X_CTR0 + U_MAX
ext = SL_SP / 2 + BLK_LEN / 2       # semi-largo del carro: 82,5
X_TORRE_MIN = C_MIN - ext - 4.5     # cara de los bloques de las varillas: -255
X_TORRE_MAX = C_MAX + ext + 4.5     # +693
T_ESP = 25.0                        # espesor de las torres que sujetan las varillas
ROD_X0, ROD_X1 = X_TORRE_MIN - T_ESP, X_TORRE_MAX + T_ESP   # -280 .. 718: 998 mm

# --------------------------------------------------------------- polea y motor
NEMA = g.NEMA
ZC = 4.0 + 0.3 + NEMA['lado'] / 2   # eje del motor: 25,75
R_EFF = 80.0 / (2 * math.pi)        # radio efectivo del tambor: 12,732 mm = 80 mm de hilo por vuelta
R_TAMB, R_BRIDA = 12.7, 14.5
Z_TOP = ZC + R_EFF                  # hilo superior: 38,48
XM = -308.0
Y_CARA = 18.0                       # cara frontal del motor (el eje sale hacia -Y)
X_POL = 738.0                       # eje de la polea libre
IR_X = -228.0                       # barrera infrarroja (haz a lo largo de Y)
Z_IR = 48.0                         # el haz cruza el grosor de la placa del carro (Z 46 a 50)


def prisma_x(pts_yz, x0, x1):
    cs = CrossSection([[(-z, y) for (y, z) in pts_yz]])
    return cs.extrude(x1 - x0).rotate((0, 90, 0)).translate((x0, 0, 0))


def octo_pts(yc, zc, ap):
    R = ap / math.cos(math.radians(22.5))
    return [(yc + R * math.cos(math.radians(22.5 + 45 * k)), zc + R * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]


def agujero_x(y, z, x0, x1, d, techo=None):
    """Agujero a lo largo de X: círculo + V a 45° arriba (sin techo plano)."""
    r = d / 2
    techo = min(r * math.sqrt(2) - 0.14, r * 1.45) if techo is None else techo
    a = r / math.sqrt(2)
    w = r * math.sqrt(2) - techo
    v = prisma_x([(y - a, z + a), (y + a, z + a), (y + w, z + techo), (y - w, z + techo)], x0, x1)
    return cil_x(y, z, x0, x1, d) + v


def tri_yz(p, x0, x1):
    return prisma_x(p, x0, x1)


# =====================================================================
# Piezas (cada una en su posición de ensamble; camas.py las pone en posición de impresión)
# =====================================================================
def carro(cx=0.0):
    """Carro en su posición de IMPRESIÓN (de cabeza: la cara donde se apoya el cartucho contra la cama); centrado en X = 0."""
    zrod = Z_CART - Z_ROD
    m = None
    parts = []
    for sx in (-SL_SP / 2, SL_SP / 2):
        parts.append(caja(sx - BLK_LEN / 2, sx + BLK_LEN / 2, -BLK_Y, BLK_Y, 0, PLACA))
    for sy in (-1, 1):
        y0, y1 = sorted((sy * 14.0, sy * 26.0))
        parts.append(caja(-SL_SP / 2, SL_SP / 2, y0, y1, 0, PLACA))
    parts.append(caja(-12, 12, -26, 26, 0, PLACA))
    m = union(parts)
    for sx in (-SL_SP / 2, SL_SP / 2):
        for sy in (-Y_ROD, Y_ROD):
            m = m + prisma_x(octo_pts(sy, zrod, SL_AP), sx - SL_LEN / 2, sx + SL_LEN / 2)
    m = m + caja(-TAB_X, TAB_X, -TAB_Y, TAB_Y, PLACA - 0.01, PLACA + 13.0)
    for sx in (-SL_SP / 2, SL_SP / 2):
        for sy in (-Y_ROD, Y_ROD):
            m = m - agujero_x(sy, zrod, sx - SL_LEN / 2 - 1, sx + SL_LEN / 2 + 1, D_BORE)
    for hx in (-7.0, 7.0):
        m = m - hueco_y(hx, Z_CART - Z_LINEA, -TAB_Y - 1, TAB_Y + 1, HILO_D)
    return m.translate((cx, 0, 0))


def carro_ensamble(cx):
    """El carro en el mundo (Z hacia arriba): se gira 180° sobre X y se sube a Z = 50."""
    m = carro(0).rotate((180, 0, 0)).translate((cx, 0, Z_CART))
    return m


def tope():
    """Tope en L que se pega al carro junto al borde del cartucho (4 iguales). Se imprime sobre la base del pie."""
    m = caja(-BLK_LEN / 2, BLK_LEN / 2, 0, 6.0, 0, 2.0)
    m = m + caja(-BLK_LEN / 2, BLK_LEN / 2, 0, 2.5, 0, 8.5)
    return m


def topes_ensamble(cx):
    out = []
    for sx in (-SL_SP / 2, SL_SP / 2):
        for sy in (-1, 1):
            t = tope()
            # el pie va sobre la placa (Z = 50), el borde del cartucho en |Y| = 26 + 0,5
            t = t.translate((0, 0, 0))
            if sy > 0:
                t = t.translate((cx + sx, 26.5, Z_CART))
            else:
                t = t.rotate((0, 0, 180)).translate((cx + sx, -26.5, Z_CART))
            out.append(t)
    return out


def torres_varillas(x0, x1, base_extra):
    """Dos torres con agujeros para las varillas, unidas por una base baja. base_extra = (xa, xb) de la base."""
    xa, xb = base_extra
    m = caja(xa, xb, -46, 46, 0, 4)
    if xb - xa > 60:                       # base aligerada: dos ventanas, queda una viga central |Y|<14
        for sy in (-1, 1):
            ya, yb = sorted((sy * 14, sy * 34))
            m = m - caja(xa + 12, xb - 12, ya, yb, -1, 5)
    for sy in (-1, 1):
        y0, y1 = sorted((sy * (Y_ROD - 12.5), sy * (Y_ROD + 12.5)))
        m = m + caja(x0, x1, y0, y1, 0, 47.5)
    for sy in (-1, 1):
        m = m - agujero_x(sy * Y_ROD, Z_ROD, x0 - 1, x1 + 1, D_BORE)
    return m


def bloque_motor():
    ancho = 60.0
    m = torres_varillas(X_TORRE_MIN - T_ESP, X_TORRE_MIN, (XM - 32, X_TORRE_MIN))
    # placa frontal del motor
    m = m + caja(XM - ancho / 2, XM + ancho / 2, Y_CARA - 5, Y_CARA, 0, 47.5)
    # refuerzos a 45 grados detrás de la placa, fuera del cuerpo del motor
    for sx in (-1, 1):
        xa, xb = sorted((XM + sx * 22.5, XM + sx * 27.5))
        m = m + prisma_x([(Y_CARA, 0), (Y_CARA + 30, 0), (Y_CARA, 30)], xa, xb)
    m = m - hueco_y(XM, ZC, Y_CARA - 6, Y_CARA + 1, NEMA['pilot'] + 0.8)
    for dx in (-15.52, 15.52):
        for dz in (-15.52, 15.52):
            m = m - hueco_y(XM + dx, ZC + dz, Y_CARA - 6, Y_CARA + 1, 3.4)
    return m


def bloque_extremo():
    m = torres_varillas(X_TORRE_MAX, X_TORRE_MAX + T_ESP, (X_TORRE_MAX, X_POL + 22))
    zc = ZC
    for sy in (-1, 1):
        ya, yb = sorted((sy * 3.9, sy * 10.1))
        m = m + caja(X_POL - 9, X_POL + 9, ya, yb, 4, zc + 11)
    for sy in (-1, 1):
        ya, yb = sorted((sy * 3.9, sy * 10.1))
        m = m - hueco_y(X_POL, zc, ya - sy * 0.0 - 1, yb + 1, 8.7)
    return m


def eje_libre():
    """Eje octogonal de la polea libre, tumbado (cara plana contra la cama)."""
    return octo_y(0, 0, -9.6, 9.6, 3.9)


def polea_libre():
    """Polea con garganta en V a 45°, radio de fondo R_TAMB; eje Z (se imprime plana)."""
    pts = [(0.0, 0.0), (R_BRIDA, 0.0), (R_BRIDA, 1.0), (R_TAMB, 1.0 + (R_BRIDA - R_TAMB) + 0.0),
           (R_TAMB, 7.0 - (R_BRIDA - R_TAMB) + 0.0), (R_BRIDA, 7.0), (R_BRIDA, 7.6), (0.0, 7.6)]
    # perfil: brida 1,0 mm, ladera a 45° hasta el fondo, fondo plano de 3,4 mm, ladera a 45° y brida
    pts = [(0.0, 0.0), (R_BRIDA, 0.0), (R_BRIDA, 1.2), (R_TAMB, 1.2 + (R_BRIDA - R_TAMB)),
           (R_TAMB, 7.6 - 1.2 - (R_BRIDA - R_TAMB)), (R_BRIDA, 7.6 - 1.2), (R_BRIDA, 7.6), (0.0, 7.6)]
    cs = CrossSection([pts])
    m = Manifold.revolve(cs, 96)
    m = m - cil_z(0, 0, -1, 9, 8.9)
    return m


def polea_motriz():
    """Tambor del motor: 13 mm de ancho, fondo Ø25,4, bridas cónicas a 45°. Agujero Ø5 con D (eje Ø5 del NEMA)."""
    pts = [(0.0, 0.0), (R_BRIDA, 0.0), (R_BRIDA, 1.2), (R_TAMB, 1.2 + (R_BRIDA - R_TAMB)),
           (R_TAMB, 13.0 - 1.2 - (R_BRIDA - R_TAMB)), (R_BRIDA, 13.0 - 1.2), (R_BRIDA, 13.0), (0.0, 13.0)]
    m = Manifold.revolve(CrossSection([pts]), 96)
    bore = cil_z(0, 0, -1, 14, 5.1) ^ caja(-5, 2.05, -5, 5, -1, 14)
    return m - bore


def puente_ir():
    """Puente de la barrera infrarroja: una base baja bajo el carro y dos postes fuera del ancho del carro."""
    m = caja(IR_X - 8, IR_X + 8, -54, 54, 0, 4)
    for sy in (-1, 1):
        ya, yb = sorted((sy * 44.0, sy * 52.0))
        m = m + caja(IR_X - 8, IR_X + 8, ya, yb, 0, Z_IR + 7)
    # alojamiento del LED (lado +Y) y del fototransistor (lado -Y) con ventana
    m = m - hueco_y(IR_X, Z_IR, 44 + 3, 52 + 1, 5.3)
    m = m - hueco_y(IR_X, Z_IR, -52 - 1, -44 - 3, 5.3)
    m = m - hueco_y(IR_X, Z_IR, 43, 53, g.IR_VENTANA)
    m = m - hueco_y(IR_X, Z_IR, -53, -43, g.IR_VENTANA)
    return m


def nema_ref():
    L = NEMA['lado']
    y0 = Y_CARA
    m = caja(XM - L / 2, XM + L / 2, y0, y0 + NEMA['largo'], ZC - L / 2, ZC + L / 2)
    m = m + cil_y(XM, ZC, y0 - 2, y0, NEMA['pilot'] - 0.5)
    m = m + cil_y(XM, ZC, y0 - NEMA['eje_l'], y0, NEMA['eje_d'])
    m = m + caja(XM - L / 2 - 5.5, XM - L / 2 + 1, y0 + NEMA['largo'] - 7, y0 + NEMA['largo'], ZC - 8, ZC + 8)
    return m


def cartucho_ref(u):
    x0 = CART_X[0] + DESP0 + u
    x1 = CART_X[1] + DESP0 + u
    return caja(x0, x1, -CART_W / 2, CART_W / 2, Z_CART, Z_CART + 16)


def piezas():
    return [('CA', carro_ensamble(X_CTR0)), ('BM', bloque_motor()), ('BR', bloque_extremo()), ('IR', puente_ir()),
            ('PM', polea_motriz().rotate((90, 0, 0)).translate((XM, 7.0, ZC))), ('K1', nema_ref())]


if __name__ == '__main__':
    print('rodillos X', ROD_X0, ROD_X1, 'largo', ROD_X1 - ROD_X0)
    for n, m in [('carro', carro()), ('tope', tope()), ('bloque_motor', bloque_motor()), ('bloque_extremo', bloque_extremo()),
                 ('eje_libre', eje_libre()), ('polea_libre', polea_libre()), ('polea_motriz', polea_motriz()), ('puente_ir', puente_ir())]:
        bb = m.bounding_box()
        print(f"{n:15s} vol {m.volume()/1000:7.1f} cm3  partes {len(m.decompose())}  caja {[round(bb[i+3]-bb[i],1) for i in range(3)]}")
