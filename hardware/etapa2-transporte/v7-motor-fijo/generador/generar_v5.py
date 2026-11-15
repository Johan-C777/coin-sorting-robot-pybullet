"""Etapa 2 v5: todo impreso, sin compras. Un solo riel de cabeza ancha (por tramos con lengüeta), un carro que lo abraza y un hilo
de casa que da una vuelta al motor y a una polea. Sin soportes: todas las piezas se imprimen como están en el ensamble.

Marco: X a lo largo (embudo en X = 0), Y a lo ancho, Z arriba (mesa Z = 0). Cartucho: fondo en Z = 50, 52 mm de ancho.
    pip install manifold3d numpy
    python generar_v5.py
"""
from __future__ import annotations
import math, os, sys
import numpy as np
from manifold3d import CrossSection, Manifold, JoinType, set_circular_segments
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_banda as g
from generar_banda import caja, cil_x, cil_y, cil_z, union, hueco_y, hueco_x, octo_y, prisma_y

set_circular_segments(64)

# ------------------------------------------------------------------ datos de la torre (etapa 1) y del recorrido
Z_CART = 50.0
CART_X = (-209.0, 177.0)
CART_W = 52.0
U_MAX = 774.0
DESP0 = -152.0
X_CTR0 = (CART_X[0] + CART_X[1]) / 2 + DESP0           # centro del carro con u = 0: -168
C_MAX = X_CTR0 + U_MAX                                  # 606

# ------------------------------------------------------------------ riel (perfil en Y, Z)
FW, FT = 14.0, 2.4                  # pie plano que se pega a la mesa con cinta: semiancho y espesor
SW = 3.5                            # semiancho del cuello
HW = 8.5                            # semiancho máximo de la cabeza
ZS = 16.0                           # donde empieza la cabeza (debajo, a 45 grados)
ZH = ZS + (HW - SW)                 # ancho máximo
ZT = ZH + (HW - SW)                 # tapa plana (ZS + 10)
CL = 0.5                            # juego carro-riel
TL, TW0, TW1, CLJ = 12.0, 1.5, 2.4, 0.25   # lengüeta de unión: largo, semiancho en la raíz y en la punta, juego de la ranura

# ------------------------------------------------------------------ carro
LEN = 124.0                         # largo del carro
ZB = ZS - 3.0                           # borde inferior del carro
ZONA_X, ZONA_L = 45.0, 34.0         # zonas de apoyo (centro y largo): 2 zonas separadas 90 mm
PW = 29.0                           # semiancho de la placa; el cartucho (52) queda a 26
Z_HILO = 43.5                       # altura del hilo
Y_HILO = (18.5, 23.5)               # los dos cabos del hilo atraviesan el carro por estos planos
D_HILO = 2.6

# ------------------------------------------------------------------ motor, hilo y polea
ZC = 24.0                           # eje del motor y de la polea libre
R_T = 19.25                         # radio de fondo del tambor
R_B = 21.0                          # radio de la brida
R_EFF = Z_HILO - ZC                 # radio del hilo: 19.5
Y_HILO_C = 21.0                     # plano medio del hilo
XM = -267.0
Y_CARA = 33.0                       # cara del motor (el eje sale hacia -Y)
BASE_T = 2.85                       # espesor de la base (= ZC - 21.15: el motor se apoya en ella)
X_P = 703.0                         # eje de la polea libre (posición más tensa; se corre hasta 6 mm hacia -X)
SLOT = 6.0                          # recorrido del eje de la polea para tensar el hilo con cuñas
IR_X = -160.0                       # barrera infrarroja
Z_IR = 48.0
RIEL_X0 = -237.0
SEG = [(-212.0, -40.0), (-40.0, 132.0), (132.0, 304.0), (304.0, 476.0), (476.0, 648.0)]
RIEL_X1 = 675.0
NEMA = g.NEMA


def prisma_x(pts_yz, x0, x1):
    cs = CrossSection([[(-z, y) for (y, z) in pts_yz]])
    return cs.extrude(x1 - x0).rotate((0, 90, 0)).translate((x0, 0, 0))


def perfil_riel():
    return [(-FW, 0), (FW, 0), (FW, FT), (SW, FT), (SW, ZS), (HW, ZH), (SW, ZT), (-SW, ZT), (-HW, ZH), (-SW, ZS), (-SW, FT), (-FW, FT)]


def plano(xa, xb, ha, hb, z0, z1):
    """Trapecio en el plano XY (ancho ha en xa, hb en xb), extruido en Z."""
    return CrossSection([[(xa, -ha), (xb, -hb), (xb, hb), (xa, ha)]]).extrude(z1 - z0).translate((0, 0, z0))


def riel(x0, x1, ranura=False, lengueta=False):
    m = prisma_x(perfil_riel(), x0, x1)
    if ranura:
        m = m - plano(x0 - 0.01, x0 + TL + 0.3, TW0 + CLJ, TW1 + CLJ, -1, ZT + 1)
    if lengueta:
        m = m + (plano(x1 - 0.01, x1 + TL, TW0, TW1, 0, ZT) ^ prisma_x(perfil_riel(), x1 - 0.01, x1 + TL))
    return m


def segmento(i):
    x0, x1 = SEG[i]
    m = riel(x0, x1, ranura=True, lengueta=(i < len(SEG) - 1))
    if i == 0:                                              # la barrera infrarroja va en el primer tramo
        m = m + caja(IR_X - 8, IR_X + 8, -41, 41, 0, FT)
        for sy in (-1, 1):
            ya, yb = sorted((sy * 33.0, sy * 41.0))
            m = m + caja(IR_X - 8, IR_X + 8, ya, yb, 0, 56.0)
        m = m - hueco_y(IR_X, Z_IR, 36.5, 42, 5.3)
        m = m - hueco_y(IR_X, Z_IR, -42, -36.5, 5.3)
        m = m - hueco_y(IR_X, Z_IR, 32, 42, g.IR_VENTANA)
        m = m - hueco_y(IR_X, Z_IR, -42, -32, g.IR_VENTANA)
    return m


def poligono(cs):
    return [tuple(p) for p in cs.to_polygons()[0]]


def carro(cx=0.0):
    """Carro: placa de 4 mm con dos zonas de apoyo que abrazan la cabeza del riel (juego CL), cuatro topes y dos agujeros de hilo."""
    h = LEN / 2
    exterior = [(-19, ZB), (19, ZB), (19, 36), (PW, 46), (PW, 50), (-PW, 50), (-PW, 46), (-19, 36)]
    # carpa: cavidad ancha entre las zonas, con techo en punta a 45° (sin puente). La cavidad ajustada de las zonas también.
    carpa = [(-15, ZB - 1), (15, ZB - 1), (15, ZS + 1.5), (0, ZS + 16.5), (-15, ZS + 1.5)]
    carpa_z = [(-15, ZB), (15, ZB), (15, ZS + 1.5), (0, ZS + 16.5), (-15, ZS + 1.5)]
    cab = CrossSection([[(-SW, ZS - 6), (SW, ZS - 6), (SW, ZS), (HW, ZH), (SW, ZT), (0, ZT + SW), (-SW, ZT), (-HW, ZH), (-SW, ZS)]]).offset(CL, JoinType.Miter, 2)
    ajustada = poligono(cab)
    m = prisma_x(exterior, -h, h) - prisma_x(carpa, -h - 1, h + 1)
    for zc in (-ZONA_X, ZONA_X):
        m = m + (prisma_x(carpa_z, zc - ZONA_L / 2, zc + ZONA_L / 2) - prisma_x(ajustada, zc - ZONA_L, zc + ZONA_L))
    for sx in (-ZONA_X, ZONA_X):
        for sy in (-1, 1):
            ya, yb = sorted((sy * 26.3, sy * PW))
            m = m + caja(sx - 15, sx + 15, ya, yb, 49.99, 58.0)
    for y in Y_HILO:
        m = m - hueco_x(y, Z_HILO, -h - 1, h + 1, D_HILO)
    return m.translate((cx, 0, 0))


def rueda(ancho, bore_d, plano_d=None, hub_r=7.5):
    """Tambor o polea: fondo R_T, bridas cónicas a 45°, disco central y aro con la cara de arriba abierta. Eje Z, se imprime plana."""
    c = R_B - R_T
    ext = [(0, 0), (R_B, 0), (R_B, 1.2), (R_T, 1.2 + c), (R_T, ancho - 1.2 - c), (R_B, ancho - 1.2), (R_B, ancho), (0, ancho)]
    m = Manifold.revolve(CrossSection([ext]), 96)
    cav = [(hub_r, 3.0), (17.0, 3.0), (17.0, ancho + 1), (hub_r, ancho + 1)]
    m = m - Manifold.revolve(CrossSection([cav]), 96)
    bore = cil_z(0, 0, -1, ancho + 1, bore_d)
    if plano_d is not None:
        bore = bore ^ caja(-bore_d, plano_d, -bore_d, bore_d, -1, ancho + 1)
    return m - bore


def polea_motriz():
    return rueda(13.0, 5.1, plano_d=2.05)


def polea_libre():
    return rueda(9.0, 8.9)


def eje_libre():
    return octo_y(0, 0, -10.2, 10.2, 3.9)


def bloque_motor():
    x0, x1 = XM - 31.5, XM + 31.5
    m = caja(x0, x1, -FW, 80, 0, BASE_T)
    m = m + riel(RIEL_X0, SEG[0][0], lengueta=True)
    m = m + caja(XM - 30, XM + 30, Y_CARA - 5, Y_CARA, 0, 47.5)
    m = m + caja(XM + 21.6, XM + 24.6, Y_CARA, 81, 0, 30)
    m = m + caja(XM - 24.6, XM - 21.6, Y_CARA, 72, 0, 30)      # la pared -X termina antes: sale el conector del motor
    m = m - hueco_y(XM, ZC, Y_CARA - 6, Y_CARA + 1, NEMA['pilot'] + 0.8)
    for sx in (-1, 1):
        xa, xb = sorted((XM + sx * 25.8, XM + sx * 29.4))
        m = m - caja(xa, xb, 45, 60, -1, BASE_T + 1)           # ranuras para la brida o la liga que sujeta el motor
    return m


def bloque_extremo():
    xa = SEG[-1][1]
    m = caja(xa, X_P + 18, -FW, 36, 0, BASE_T)
    m = m + riel(xa, RIEL_X1, ranura=True)
    for ya, yb in ((Y_HILO_C - 10.0, Y_HILO_C - 5.0), (Y_HILO_C + 5.0, Y_HILO_C + 10.0)):
        m = m + caja(X_P - 9, X_P + 9, ya, yb, 0, ZC + 11)
        m = m + prisma_y(CrossSection([[(X_P - 9, BASE_T - 0.5), (X_P - 9, BASE_T + 12), (X_P - 21, BASE_T - 0.5)]]), ya, yb)
    ranura = Manifold.batch_hull([hueco_y(X_P, ZC, Y_HILO_C - 11, Y_HILO_C + 11, 8.7), hueco_y(X_P - SLOT, ZC, Y_HILO_C - 11, Y_HILO_C + 11, 8.7)])
    m = m - ranura
    return m


def cuna(t):
    """Cuña plana de t mm: se mete entre el eje de la polea y el extremo -X de la ranura de una mejilla (una por mejilla)."""
    return caja(0, t, 0, 4.6, 0, 8.2)


def nema_ref():
    L = NEMA['lado']
    m = caja(XM - L / 2, XM + L / 2, Y_CARA, Y_CARA + NEMA['largo'], ZC - L / 2, ZC + L / 2)
    m = m + cil_y(XM, ZC, Y_CARA - 2, Y_CARA, NEMA['pilot'] - 0.5)
    m = m + (cil_y(XM, ZC, Y_CARA - NEMA['eje_l'], Y_CARA, NEMA['eje_d']) ^ caja(XM - 3, XM + 2.0, -100, 100, ZC - 3, ZC + 3))
    m = m + caja(XM - L / 2 - 5.5, XM - L / 2 + 1, Y_CARA + NEMA['largo'] - 7, Y_CARA + NEMA['largo'], ZC - 8, ZC + 8)
    return m


def cartucho_ref(u):
    return caja(CART_X[0] + DESP0 + u, CART_X[1] + DESP0 + u, -CART_W / 2, CART_W / 2, Z_CART, Z_CART + 16)


def poleas_ensamble():
    pm = polea_motriz().rotate((90, 0, 0)).translate((XM, Y_HILO_C + 6.5, ZC))     # y de 14,5 a 27,5
    pl = polea_libre().rotate((90, 0, 0)).translate((X_P, Y_HILO_C + 4.5, ZC))
    ej = eje_libre().translate((X_P, Y_HILO_C, ZC))
    return pm, pl, ej


def piezas():
    pm, pl, ej = poleas_ensamble()
    P = [('CA', carro(X_CTR0)), ('BM', bloque_motor()), ('BR', bloque_extremo()), ('PM', pm), ('PL', pl), ('EJ', ej), ('K1', nema_ref())]
    P += [(f'S{i+1}', segmento(i)) for i in range(len(SEG))]
    return P


if __name__ == '__main__':
    print('riel de', RIEL_X0, 'a', RIEL_X1, '=', RIEL_X1 - RIEL_X0, 'mm; carro de', X_CTR0 - LEN / 2, 'a', C_MAX + LEN / 2)
    for n, m in [('carro', carro()), ('bloque_motor', bloque_motor()), ('bloque_extremo', bloque_extremo()), ('polea_motriz', polea_motriz()),
                 ('polea_libre', polea_libre()), ('eje_libre', eje_libre())] + [(f'seg{i+1}', segmento(i)) for i in range(len(SEG))]:
        bb = m.bounding_box()
        print(f"{n:15s} vol {m.volume()/1000:6.1f} cm3  partes {len(m.decompose())}  caja {[round(bb[i+3]-bb[i],1) for i in range(3)]}")
