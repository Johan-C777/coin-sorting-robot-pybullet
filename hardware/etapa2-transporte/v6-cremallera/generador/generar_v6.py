"""Etapa 2 v6: cremallera impresa en el riel, motor con piñón sobre el carro. Todo impreso, sin soportes, sin hilo.
Marco: X a lo largo (embudo en X = 0), Y a lo ancho (la cremallera y el motor van del lado -Y), Z arriba (mesa Z = 0).
    pip install manifold3d numpy
    python generar_v6.py
"""
from __future__ import annotations
import math, os, sys
import numpy as np
from manifold3d import CrossSection, Manifold, JoinType, set_circular_segments
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v5 as b
from generar_v5 import (caja, cil_y, cil_z, union, hueco_y, hueco_x, prisma_y, prisma_x, perfil_riel, plano, riel,
                        FW, FT, SW, HW, ZS, ZH, ZT, CL, LEN, ZB, ZONA_X, ZONA_L, PW, X_CTR0, U_MAX, C_MAX, DESP0, CART_X, CART_W,
                        Z_CART, TL, TW0, TW1, CLJ, NEMA, poligono)
set_circular_segments(64)

# ------------------------------------------------------------------ cremallera y piñón (módulo 1,5; 20°)
M = 1.5
NZ = 18                              # dientes del piñón
RP = M * NZ / 2                      # radio primitivo 13,5
PASO = math.pi * M                   # 4,712 mm
ALFA = math.radians(20)
HA, HF = M, 1.25 * M                 # addendum y dedendum
BL = 0.15                            # juego de distancia entre centros (holgura de engrane)
ZC = 22.4                            # eje del motor y del piñón
Z_PRIM = ZC - RP - BL                # línea primitiva de la cremallera
Z_RAIZ, Z_PUNTA = Z_PRIM - HF, Z_PRIM + HA
Y_R = (-28.5, -20.0)                 # ancho de la cremallera (Y)
N_DIENTES = 172
X_V0 = -181.0 - 2 * PASO                        # centro de valle (donde puede cortarse el riel) del primer diente
X_R1 = X_V0 + N_DIENTES * PASO

# ------------------------------------------------------------------ motor y soporte en el carro
Y_PIN = (-26.9, -20.9)               # dientes del piñón
Y_HUB = (-29.4, -26.9)
Y_PLACA = (-32.7, -29.7)             # placa piloto: la cara del motor queda en Y = -32,7
Y_BRAZO = -62.0                      # fin de los brazos
ZP_TOP = 46.0                        # tope de brazos y placa (bajo la placa del carro)
HOLG_M = 0.35
XB = NEMA['lado'] / 2 + HOLG_M       # cara interior de los brazos: 21,5
TB = 3.0                             # espesor de brazos y placa

# ------------------------------------------------------------------ riel por tramos con cremallera
RIEL_X0, RIEL_X1 = -237.0, 675.0
N_TRAMO = (32, 69, 106, 143)         # número de diente donde cortan los tramos (centro de valle)
CORTES = [X_V0 + n * PASO for n in N_TRAMO]
SEG = list(zip([RIEL_X0] + CORTES, CORTES + [RIEL_X1]))
IR_X, Z_IR = -228.0, 48.0


def diente(xc, z0):
    hr = PASO / 4 + (HF) * math.tan(ALFA)       # semiancho en la raíz
    hp = PASO / 4 - HA * math.tan(ALFA)         # semiancho en la punta
    return [(xc + hr, z0), (xc + hp, Z_PUNTA), (xc - hp, Z_PUNTA), (xc - hr, z0)]


def cremallera(xa, xb):
    """Tira con dientes entre xa y xb (centros de valle), extruida a lo ancho. Perfil (x, z)."""
    xv0 = X_V0
    k0 = int(round((xa - xv0) / PASO)); k1 = int(round((xb - xv0) / PASO))
    pts = [(xa, 0.0), (xb, 0.0), (xb, Z_RAIZ)]
    for k in range(k1 - 1, k0 - 1, -1):
        xc = xv0 + (k + 0.5) * PASO
        pts += diente(xc, Z_RAIZ)
    pts.append((xa, Z_RAIZ))
    m = prisma_y(CrossSection([pts]), Y_R[0], Y_R[1])
    alma = caja(xa, xb, Y_R[1] - 0.01, -FW + 0.01, 0, FT)          # tira de unión al pie del riel
    return m + alma


def segmento(i):
    x0, x1 = SEG[i]
    m = riel(x0, x1, ranura=(i > 0) or True, lengueta=(i < len(SEG) - 1))
    xa, xb = max(x0, X_V0), min(x1, X_R1)
    if xb - xa > PASO:
        # tramos cortados en centros de valle: xa/xb ya lo son salvo en los extremos del riel
        ka = math.ceil((xa - X_V0) / PASO - 1e-6); kb = math.floor((xb - X_V0) / PASO + 1e-6)
        m = m + cremallera(X_V0 + ka * PASO, X_V0 + kb * PASO)
    if i == 0:
        m = m + caja(IR_X - 8, IR_X + 8, -41, 41, 0, FT)
        for sy in (-1, 1):
            ya, yb = sorted((sy * 33.0, sy * 41.0))
            m = m + caja(IR_X - 8, IR_X + 8, ya, yb, 0, 56.0)
        from generar_v5 import g
        m = m - hueco_y(IR_X, Z_IR, 36.5, 42, 5.3) - hueco_y(IR_X, Z_IR, -42, -36.5, 5.3)
        m = m - hueco_y(IR_X, Z_IR, 32, 42, g.IR_VENTANA) - hueco_y(IR_X, Z_IR, -42, -32, g.IR_VENTANA)
    return m


# ------------------------------------------------------------------ piñón (evolvente)
def perfil_pinon():
    rb = RP * math.cos(ALFA); ra = RP + HA; rf = RP - HF
    inv = lambda a: math.tan(a) - a
    th_b = math.pi / (2 * NZ) + inv(ALFA)           # semiángulo del diente en la circunferencia base
    pts = []
    for k in range(NZ):
        a0 = 2 * math.pi * k / NZ
        t_max = math.sqrt((ra / rb) ** 2 - 1)
        ts = np.linspace(0, t_max, 9)
        der = [(a0 - th_b + (t - math.atan(t)) * 1.0, rb * math.sqrt(1 + t * t)) for t in ts]   # flanco izquierdo (ángulo crece hacia afuera)
        # flanco derecho (espejo)
        izq = [(a0 - (th_b - (t - math.atan(t))), rb * math.sqrt(1 + t * t)) for t in ts]
        der = [(a0 + (th_b - (t - math.atan(t))), rb * math.sqrt(1 + t * t)) for t in ts]
        # raíz: de rf al flanco (radial), flanco izquierdo hacia arriba, punta, flanco derecho hacia abajo
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


def pinon_colocado(cx=0.0, giro_deg=0.0):
    """Piñón montado en el eje del motor: eje a lo largo de Y, dientes entre Y_PIN, centro en (cx, ZC)."""
    p = pinon().rotate((0, 0, giro_deg)).rotate((90, 0, 0))       # (x, y, z) -> (x, -z, y)
    return p.translate((cx, Y_PIN[1], ZC))


# ------------------------------------------------------------------ carro
def carro(cx=0.0):
    h = LEN / 2
    exterior = [(-19, ZB), (19, ZB), (19, 36), (PW, 46), (PW, 50), (-PW, 50), (-PW, 46), (-19, 36)]
    carpa = [(-15, ZB - 1), (15, ZB - 1), (15, ZS + 1.5), (0, ZS + 16.5), (-15, ZS + 1.5)]
    carpa_z = [(-15, ZB), (15, ZB), (15, ZS + 1.5), (0, ZS + 16.5), (-15, ZS + 1.5)]
    cab = CrossSection([[(-SW, ZS - 6), (SW, ZS - 6), (SW, ZS), (HW, ZH), (SW, ZT), (0, ZT + SW), (-SW, ZT), (-HW, ZH), (-SW, ZS)]]).offset(CL, JoinType.Miter, 2)
    ajustada = poligono(cab)
    m = b.prisma_x(exterior, -h, h) - b.prisma_x(carpa, -h - 1, h + 1)
    for zc in (-ZONA_X, ZONA_X):
        m = m + (b.prisma_x(carpa_z, zc - ZONA_L / 2, zc + ZONA_L / 2) - b.prisma_x(ajustada, zc - ZONA_L, zc + ZONA_L))
    for sx in (-ZONA_X, ZONA_X):
        for sy in (-1, 1):
            ya, yb = sorted((sy * 26.3, sy * PW))
            m = m + caja(sx - 15, sx + 15, ya, yb, 49.99, 58.0)
    # soporte del motor: dos brazos y la placa piloto, en pie desde la cama (Z = 13) hasta bajo la placa del carro
    for sx in (-1, 1):
        xa, xb_ = sorted((sx * XB, sx * (XB + TB)))
        m = m + caja(xa, xb_, Y_BRAZO, -18.9, ZB, ZP_TOP)
    m = m + caja(-(XB + TB), XB + TB, Y_PLACA[0], Y_PLACA[1], ZB, ZP_TOP)
    m = m - hueco_y(0, ZC, Y_PLACA[0] - 1, Y_PLACA[1] + 1, NEMA['pilot'] + 0.8)
    m = m - hueco_y(0, ZC, -20.0, -6.0, 8.0)                 # la punta del eje entra en la cavidad del carro
    for sx in (-1, 1):                                          # ranura de la brida o la liga que sujeta el motor
        xa, xb_ = sorted((sx * (XB + TB - 1.2), sx * (XB + TB + 1)))
        m = m - caja(xa, xb_, -54.0, -50.0, ZB - 1, ZP_TOP + 1)
    return m.translate((cx, 0, 0))


def nema_ref(cx=0.0):
    L = NEMA['lado']
    yf = Y_PLACA[0]
    m = caja(cx - L / 2, cx + L / 2, yf - NEMA['largo'], yf, ZC - L / 2, ZC + L / 2)
    m = m + cil_y(cx, ZC, yf, yf + 2, NEMA['pilot'] - 0.5)
    eje = cil_y(cx, ZC, yf, yf + NEMA['eje_l'], NEMA['eje_d']) ^ caja(cx - 3, cx + 2.0, -100, 100, ZC - 3, ZC + 3)
    return m + eje
