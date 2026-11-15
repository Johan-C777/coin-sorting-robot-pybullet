"""Etapa 2 v7: motor fijo. Una barra dentada (cremallera de 810 mm, en 4 tramos) se mueve con el cartucho; el piñón del motor, fijo
entre los patines de la torre, la empuja. Todo impreso, sin soportes, sin hilo, sin compras.
Marco: X a lo largo (embudo en X = 0), Y a lo ancho (la barra y el motor van del lado -Y), Z arriba (mesa Z = 0). Con u = 0 el carro está en X_CTR0.
    pip install manifold3d numpy
    python generar_v7.py
"""
from __future__ import annotations
import math, os, sys
import numpy as np
from manifold3d import CrossSection, Manifold, JoinType, set_circular_segments
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v5 as b
from generar_v5 import (caja, cil_y, cil_z, hueco_y, prisma_y, prisma_x, riel, FW, FT, SW, HW, ZS, ZH, ZT, CL, LEN, ZB, ZONA_X, ZONA_L,
                        PW, X_CTR0, U_MAX, DESP0, CART_X, CART_W, Z_CART, NEMA, poligono)
set_circular_segments(64)

# ------------------------------------------------------------------ engrane (módulo 1,5; 20°)
M = 1.5
NZ = 16                              # dientes del piñón
RP = M * NZ / 2                      # radio primitivo 12
PASO = math.pi * M                   # 4,712 mm
ALFA = math.radians(20)
HA, HF = M, 1.25 * M                 # addendum y dedendum
BL = 0.35                            # juego de distancia entre centros (cubre hasta ~0,10 mm de hinchazón por lado)
TD = 0.10                            # los dientes de la barra se hacen más delgados 0,10 mm por lado (la impresión los engorda)

# ------------------------------------------------------------------ soporte del motor (fijo)
XP = -14.5                           # eje del piñón: centro del hueco entre los patines S01 y S02 (x = -49 a 20)
BASE_T = 2.0                         # espesor de la base del soporte (el motor y la barra se apoyan sobre ella)
ZC = BASE_T + NEMA['lado'] / 2       # eje del motor y del piñón: 23,15
Y_PLACA = (-49.0, -46.0)             # placa piloto: la cara del motor queda en Y = -49
Y_HUB = (-45.5, -43.0)
Y_PIN = (-43.0, -37.0)               # dientes del piñón
Y_MOT = Y_PLACA[0] - NEMA['largo']   # fondo del motor: -97
XS = 27.5                            # semiancho de la placa y de la base (queda 5,5 mm de cada lado en el hueco entre patines)
XB = NEMA['lado'] / 2 + 0.35         # cara interior de los brazos
TB = 3.0

# ------------------------------------------------------------------ barra dentada (en su propio marco: fondo en Z = 0; se apoya en la base del soporte)
Z_PRIM = ZC - BASE_T - RP - BL       # 8,8
Z_RAIZ, Z_PUNTA = Z_PRIM - HF, Z_PRIM + HA
Y_BAR = (-45.5, -34.5)               # ancho 11
N_DIENTES = 172
X_T1 = XP + 18.0                     # centro de valle más adelantado (con u = 0)
X_T0 = X_T1 - N_DIENTES * PASO       # centro de valle más atrasado
N_TRAMO = 43                         # dientes por tramo (4 tramos de 202,6 mm)
XPEG = XP + 40.0                     # clavija de la barra (con u = 0)
Y_PEG = -37.0
D_PEG = 8.0
H_TAB = 8.5                          # alto de la lengüeta de la clavija
Z_PEG = 30.0                         # tope de la clavija
TAB = (Y_BAR[0], -28.5)              # ancho de la lengüeta (Y)

# unión de los tramos: lengüeta con techo en cresta (sin techos planos)
K45 = 0.8                            # avance horizontal por cada mm de altura en techos y flancos: 39° respecto a la vertical
Z_CU, Z_CA = 3.0, 5.6                # alto del cuello y de la cresta
X_PICO = (Z_CA - Z_CU) * K45
X_FIN = X_PICO + 2.5
Z_FIN = Z_CA - 2.5 / K45

# ------------------------------------------------------------------ brazo (une el carro con la clavija de la barra)
XSL = 40.0                           # ranura en la pared -Y del carro (x local)
Y_PL = (-22.4, -19.4)                # placa del brazo (pegada a la pared del carro, que está en Y = -19)
CAP_Z = (47.8, 49.8)                 # tapa (asiento) en la placa del carro
Z_BZ = (ZB, 36.0)
BLK_Y = (-46.5, -19.4)

# ------------------------------------------------------------------ riel por tramos (el de la v6, sin dientes)
X_V0 = -181.0 - 2 * PASO
N_RIEL = (32, 69, 106, 143)
RIEL_X0, RIEL_X1 = -237.0, 675.0
CORTES = [X_V0 + n * PASO for n in N_RIEL]
SEG = list(zip([RIEL_X0] + CORTES, CORTES + [RIEL_X1]))
IR_X, Z_IR = -228.0, 48.0
Y_IR_N = (-55.5, -47.5)              # poste -Y fuera del carril de la barra


def diente(xc, z0):
    hr = PASO / 4 + HF * math.tan(ALFA) - TD
    hp = PASO / 4 - HA * math.tan(ALFA) - TD
    return [(xc + hr, z0), (xc + hp, Z_PUNTA), (xc - hp, Z_PUNTA), (xc - hr, z0)]


def valle(k):
    return X_T0 + k * PASO


# ------------------------------------------------------------------ barra
def cola_milano(z_min=0.0):
    """Perfil (x, z) de la lengüeta: fondo plano en la cama, techo que sube desde la cara de corte hasta una cresta y vuelve a bajar."""
    return [(-1.0, z_min), (X_FIN, z_min), (X_FIN, Z_FIN), (X_PICO, Z_CA), (0.0, Z_CU), (-1.0, Z_CU)]


def tramo_barra(j, juego=0.25):
    """Tramo j = 0 (más atrasado) a 3 (más adelantado, con la lengüeta ancha y la clavija). Dientes entre valles k0..k1."""
    k0, k1 = j * N_TRAMO, (j + 1) * N_TRAMO
    xa, xb = valle(k0), valle(k1)
    pts = [(xa, 0.0), (xb, 0.0), (xb, Z_RAIZ)]
    for k in range(k1 - 1, k0 - 1, -1):
        pts += diente(valle(k) + PASO / 2, Z_RAIZ)
    pts.append((xa, Z_RAIZ))
    m = prisma_y(CrossSection([pts]), Y_BAR[0], Y_BAR[1])
    if j < 3:                                                   # lengüeta hacia adelante; los tramos se juntan deslizándolos de lado
        m = m + prisma_y(CrossSection([[(xb + x, z) for x, z in cola_milano()]]), Y_BAR[0], Y_BAR[1])
    if j > 0:                                                   # ranura para la lengüeta del tramo de adelante (abierta a los dos lados y abajo)
        ran = CrossSection([[(xa + x, z) for x, z in cola_milano(z_min=-1.0)]]).offset(juego, JoinType.Miter, 2)
        m = m - prisma_y(ran, Y_BAR[0] - 1, Y_BAR[1] + 1)
    if j == 3:
        m = m + caja(xb - 0.01, XPEG + 9.0, TAB[0], TAB[1], 0, H_TAB)
        m = m + cil_z(XPEG, Y_PEG, H_TAB - 0.01, Z_PEG, D_PEG)
    return m


# ------------------------------------------------------------------ piñón (evolvente)
def perfil_pinon():
    rb = RP * math.cos(ALFA); ra = RP + HA; rf = RP - HF
    th_b = math.pi / (2 * NZ) + (math.tan(ALFA) - ALFA)
    pts = []
    for k in range(NZ):
        a0 = 2 * math.pi * k / NZ
        t_max = math.sqrt((ra / rb) ** 2 - 1)
        ts = np.linspace(0, t_max, 9)
        izq = [(a0 - (th_b - (t - math.atan(t))), rb * math.sqrt(1 + t * t)) for t in ts]
        der = [(a0 + (th_b - (t - math.atan(t))), rb * math.sqrt(1 + t * t)) for t in ts]
        seq = [(izq[0][0], rf)] + izq + der[::-1] + [(der[0][0], rf)]
        pts += [(r * math.cos(a), r * math.sin(a)) for a, r in seq]
    return pts


def pinon():
    cs = CrossSection([perfil_pinon()])
    z_pin = Y_PIN[1] - Y_PIN[0]; z_hub = Y_HUB[1] - Y_HUB[0]
    m = cs.extrude(z_pin)
    hub = Manifold.cylinder(z_hub, 5.0).translate((0, 0, z_pin - 0.01))
    m = m + hub
    bore = Manifold.cylinder(z_pin + z_hub + 2, NEMA['eje_d'] / 2 + 0.05).translate((0, 0, -1))
    bore = bore ^ caja(-5, 2.05, -5, 5, -1, z_pin + z_hub + 1)
    return m - bore


def pinon_colocado(giro_deg=0.0):
    """Piñón en el eje del motor: eje a lo largo de Y, dientes entre Y_PIN, cubo del lado de la placa, centro en (XP, ZC)."""
    p = pinon().rotate((0, 0, giro_deg)).rotate((90, 0, 0))       # (x, y, z) -> (x, -z, y)
    return p.translate((XP, Y_PIN[1], ZC))


# ------------------------------------------------------------------ cola de milano del brazo y su tapa
def ranura_pts(holgura):
    xs = XSL
    return [(xs - 4.0 - holgura, -30.0), (xs + 4.0 + holgura, -30.0), (xs + 4.0 + holgura, -17.5), (xs + 7.0 + holgura, -14.5),
            (xs + 7.0 + holgura, -12.5), (xs - 7.0 - holgura, -12.5), (xs - 7.0 - holgura, -14.5), (xs - 4.0 - holgura, -17.5)]


def perfil_cola(h):
    """Planta de la cola del brazo, recortada en Y >= -19,4 (lo que queda dentro de la pared del carro)."""
    return CrossSection([ranura_pts(h)]) ^ CrossSection([[(-1000, -19.4), (1000, -19.4), (1000, 0), (-1000, 0)]])


def tronco(h):
    """Tapa del brazo / su asiento en la placa del carro: la planta de la cola crece unos 35° con la altura, por escalones de 0,25 mm."""
    z0, z1 = CAP_Z
    n = int(round((z1 - z0) / 0.25))
    base = perfil_cola(h)
    partes = []
    for i in range(n + (1 if h else 0)):
        z = z0 + i * 0.25
        off = 0.7 * (i + 1) * 0.25
        partes.append(base.offset(off, JoinType.Miter, 2).extrude(0.25 + (0.2 if (h and i == n) else 0.0) + 0.001).translate((0, 0, z - 0.001)))
    out = partes[0]
    for q in partes[1:]: out = out + q
    return out


# ------------------------------------------------------------------ carro (el de la v5 sin hilo) con la ranura del brazo
def carro(cx=0.0, juego=0.2):
    hh = LEN / 2
    exterior = [(-19, ZB), (19, ZB), (19, 36), (PW, 46), (PW, 50), (-PW, 50), (-PW, 46), (-19, 36)]
    carpa = [(-15, ZB - 1), (15, ZB - 1), (15, ZS + 1.5), (0, ZS + 16.5), (-15, ZS + 1.5)]
    carpa_z = [(-15, ZB), (15, ZB), (15, ZS + 1.5), (0, ZS + 16.5), (-15, ZS + 1.5)]
    cab = CrossSection([[(-SW, ZS - 6), (SW, ZS - 6), (SW, ZS), (HW, ZH), (SW, ZT), (0, ZT + SW), (-SW, ZT), (-HW, ZH), (-SW, ZS)]]).offset(CL, JoinType.Miter, 2)
    ajustada = poligono(cab)
    m = prisma_x(exterior, -hh, hh) - prisma_x(carpa, -hh - 1, hh + 1)
    for zc in (-ZONA_X, ZONA_X):
        m = m + (prisma_x(carpa_z, zc - ZONA_L / 2, zc + ZONA_L / 2) - prisma_x(ajustada, zc - ZONA_L, zc + ZONA_L))
    for sx in (-ZONA_X, ZONA_X):
        for sy in (-1, 1):
            ya, yb = sorted((sy * 26.3, sy * PW))
            m = m + caja(sx - 15, sx + 15, ya, yb, 49.99, 58.0)
    # ranura de cola de milano para el brazo: de arriba abajo (la tapa del cartucho la cierra), con asiento cónico en la placa
    m = m - CrossSection([ranura_pts(juego)]).extrude(60).translate((0, 0, ZB - 5))
    m = m - tronco(juego)
    return m.translate((cx, 0, 0))


# ------------------------------------------------------------------ brazo: del carro a la clavija de la barra
def brazo(cx=0.0):
    xpl = XPEG - X_CTR0                                     # x local de la clavija
    m = caja(XSL - 4.0, xpl + 7.0, Y_PL[0], Y_PL[1], Z_BZ[0], Z_BZ[1])                 # placa pegada a la pared del carro, de pie
    m = m + caja(xpl - 7.0, xpl + 7.0, BLK_Y[0], Y_PL[1], Z_BZ[0], Z_BZ[1])           # bloque con el ojal alargado en Y para la clavija
    ojal = Manifold.batch_hull([cil_z(xpl, Y_PEG - 6.5, Z_BZ[0] - 1, Z_BZ[1] + 1, D_PEG + 0.6), cil_z(xpl, Y_PEG + 6.5, Z_BZ[0] - 1, Z_BZ[1] + 1, D_PEG + 0.6)])
    m = m - ojal
    cola = CrossSection([ranura_pts(0.0)]).extrude(CAP_Z[0] - Z_BZ[0] + 0.001).translate((0, 0, Z_BZ[0]))
    cola = cola ^ caja(XSL - 8, XSL + 8, -19.4, -12.0, Z_BZ[0] - 1, CAP_Z[0] + 1)
    m = m + cola
    m = m + caja(XSL - 4.0, XSL + 4.0, Y_PL[0], -19.3, Z_BZ[0], CAP_Z[0])
    m = m + tronco(0.0)
    return m.translate((cx, 0, 0))


# ------------------------------------------------------------------ soporte del motor
def soporte():
    x0, x1 = XP - XS, XP + XS
    trap = CrossSection([[(x0 - BASE_T, 0), (x1 + BASE_T, 0), (x1, BASE_T), (x0, BASE_T)]])
    m = prisma_y(trap, Y_MOT - 3.0, Y_BAR[1] + 3.4)                        # base con rampas de 45° en los bordes: la barra sube y baja sin atascarse
    ztop = ZC + NEMA['lado'] / 2 + 3.0
    m = m + caja(x0, x1, Y_PLACA[0], Y_PLACA[1], BASE_T - 0.01, ztop)      # placa piloto
    m = m - hueco_y(XP, ZC, Y_PLACA[0] - 1, Y_PLACA[1] + 1, NEMA['pilot'] + 0.8)
    m = m + caja(XP + XB, XP + XB + TB, Y_MOT - 3.0, Y_PLACA[0], BASE_T - 0.01, 30.0)       # brazos
    m = m + caja(XP - XB - TB, XP - XB, Y_PLACA[0] - 24.0, Y_PLACA[0], BASE_T - 0.01, 30.0)   # el lado -X termina antes: sale el conector del motor
    for sx in (-1, 1):                                                     # ranuras para la brida o la liga que sujeta el motor (fuera de los brazos)
        xa, xb_ = sorted((XP + sx * (XB + TB + 1.2), XP + sx * (XB + TB + 4.8)))
        m = m - caja(xa, xb_, Y_PLACA[0] - 30.0, Y_PLACA[0] - 22.0, -1, BASE_T + 1)
    # pared guía del lado del riel: la barra pasa entre ella y la placa (juego 0,4 mm)
    m = m + caja(XP - 22.0, XP + 14.0, Y_BAR[1] + 0.4, Y_BAR[1] + 3.4, BASE_T - 0.01, BASE_T + Z_PUNTA + 1.5)
    return m


def nema_ref():
    L = NEMA['lado']
    yf = Y_PLACA[0]
    m = caja(XP - L / 2, XP + L / 2, yf - NEMA['largo'], yf, ZC - L / 2, ZC + L / 2)
    m = m + cil_y(XP, ZC, yf, yf + 2, NEMA['pilot'] - 0.5)
    eje = cil_y(XP, ZC, yf, yf + NEMA['eje_l'], NEMA['eje_d']) ^ caja(XP - 3, XP + 2.0, -100, 100, ZC - 3, ZC + 3)
    return m + eje


# ------------------------------------------------------------------ riel con la barrera infrarroja
def segmento(i):
    x0, x1 = SEG[i]
    m = riel(x0, x1, ranura=True, lengueta=(i < len(SEG) - 1))
    if i == 0:
        from generar_v5 import g
        trap = CrossSection([[(IR_X - 8 - BASE_T, 0), (IR_X + 8 + BASE_T, 0), (IR_X + 8, BASE_T), (IR_X - 8, BASE_T)]])
        m = m + prisma_y(trap, Y_IR_N[0], 41)
        for (ya, yb) in ((33.0, 41.0), Y_IR_N):
            m = m + caja(IR_X - 8, IR_X + 8, ya, yb, 0, 56.0)
        m = m - hueco_y(IR_X, Z_IR, 36.5, 42, 5.3) - hueco_y(IR_X, Z_IR, Y_IR_N[0] - 1, Y_IR_N[0] + 4.5, 5.3)
        m = m - hueco_y(IR_X, Z_IR, 32, 42, g.IR_VENTANA) - hueco_y(IR_X, Z_IR, Y_IR_N[0] - 1, Y_IR_N[1] + 1, g.IR_VENTANA)
    return m


def barra_ensamblada(u=0.0, dz=BASE_T):
    """Los 4 tramos en su sitio con el carro en u (la barra se apoya en la base del soporte: dz = BASE_T)."""
    return [tramo_barra(j).translate((u, 0, dz)) for j in range(4)]


if __name__ == '__main__':
    for n, m in [('carro', carro()), ('brazo', brazo()), ('soporte', soporte()), ('pinon', pinon())] + [(f'barra{j+1}', tramo_barra(j)) for j in range(4)] + [(f'riel{i+1}', segmento(i)) for i in range(len(SEG))]:
        bb = m.bounding_box()
        print(f"{n:10s} vol {m.volume()/1000:6.1f} cm3  partes {len(m.decompose())}  caja {[round(bb[i+3]-bb[i],1) for i in range(3)]}")
