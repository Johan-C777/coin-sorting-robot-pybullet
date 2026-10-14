"""Clasificador físico de la etapa 1: tolva dosificadora, riel escalonado en dos
módulos con cola de milano, bifurcación activa de $500 y ductos de salida con
barrera infrarroja embebida. Todo con los alojamientos de la electrónica ya
modelados (28BYJ-48 o SG90, TCS34725/TCS3200, SG90 de la aguja, LED IR 5 mm).

    pip install manifold3d numpy
    python scripts/generar_clasificador.py              # STL de impresión
    python scripts/generar_clasificador.py --ensamble   # + ensamble de referencia

Salida en hardware/stl/ (mm, orientación de impresión: Z = capas).
Impresora objetivo: Creality K1C, cama 220 x 220 x 250 mm.

Marcos de referencia
  * riel: X a lo largo de la pista (bajando), Y a lo ancho (Y=0 cara de la pared
    guía), Z normal a la pista. El riel se monta girado 22° sobre Y.
  * ductos y bifurcación cuelgan en vertical "de mundo" bajo cada ranura.
"""
from __future__ import annotations

import argparse
import csv
import math
import struct
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from manifold3d import CrossSection, FillRule, JoinType, Manifold, OpType, set_circular_segments

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "hardware" / "stl"
CAMA = (220.0, 220.0, 250.0)
set_circular_segments(72)

# =====================================================================
# Tolerancias FDM
# =====================================================================
HOLGURA = 0.35          # encajes deslizantes, por lado
M3_ROSCA = 3.2          # agujero para roscar M3 directo en el plástico
M3_PASO = 3.4           # paso libre de M3
M3_CABEZA = 6.5         # alojamiento de cabeza (DIN 912 Ø5,5 + juego)
M3_CABEZA_H = 3.0
M2_ROSCA = 1.8          # orejas del SG90 (tornillo autorroscante M2)
IR_D = 5.2              # LED IR / fototransistor de 5 mm a presión
IR_VENTANA = 3.0        # abertura hacia el ducto: hace de tope del LED
IR_BOSS = 9.0
COMPENSACION_RANURA = 0.0   # ajuste fino de la impresora (+ abre, - cierra)

# =====================================================================
# Monedas y ranuras (mm). (ranura, [(clave, nombre, diámetro)]); None = extremo abierto
# =====================================================================
RANURAS = [
    (17.5, [("N50", "$50 nueva", 17.0)]),
    (20.8, [("N100", "$100 nueva", 20.3)]),
    (21.5, [("A50", "$50 antigua", 21.0)]),
    (22.9, [("N200", "$200 nueva", 22.4)]),
    (23.4, [("A100", "$100 antigua", 23.0)]),
    (24.1, [("A500", "$500 antigua", 23.5), ("N500", "$500 nueva", 23.7)]),
    (24.9, [("A200", "$200 antigua", 24.4)]),
    (None, [("N1000", "$1000 nueva", 26.7)]),
]
RANURA_500 = 5
HOLGURA_CAIDA = 0.4

# =====================================================================
# Riel
# =====================================================================
INCLINACION = 22.0      # pista respecto a la horizontal
PERALTE = 10.0          # inclinación lateral del piso hacia la pared guía
B = 30.0                # ancho útil del canal (moneda mayor 26,7)
ESP_BASE = 5.0
ALTO_PARED = 10.0
ESP_PARED = 2.4
ALTO_LABIO = 4.0
ALA = 20.0              # ala a cada lado del canal: tornillos de ductos y cuñas
ENTRADA = 35.0          # zona donde cae la moneda de la tolva
ALMA = 12.0             # material entre ranuras
EXTRA_LARGO = 4.0       # largo de ranura = ancho + 4 (la moneda cabe entera)
LARGO_FINAL = 32.0
PARED_FINAL = 4.0
INICIO_B = 24.0         # el módulo B arranca después de la cola
MAX_PIEZA = 210.0
COLA_LARGO, COLA_CUELLO, COLA_BOCA, COLA_ALTO = 14.0, 9.0, 13.0, 3.0
Y_TORN_COLA = 6.5
Y_TORN_DUCTO = 8.0
Y_TORN_CUNA = 14.0

# ductos estándar
T_GARGANTA = 24.0       # del riel a la garganta, sobre el eje vertical
T_IR = 14.0             # garganta -> barrera IR
LARGO_TUBO = 36.0
PARED_DUCTO = 2.2

# bifurcación de $500
G = 4.2                 # ranura donde la moneda rueda de canto ($500 ≤ 2,2 mm)
PARED_BIF = 3.0
PARED_SENSOR = 6.0
ALTO_BIF_PARED = 16.0   # altura de las paredes del canal; la moneda sobresale
RAMPA = 25.0            # pendiente de rodadura de canto
ZS = -26.0              # salida del embudo (boca de la ranura)
S_SENSOR = 50.0         # posición del sensor a lo largo del piso
S_AGUJA = 110.0         # pivote de la aguja (≈95 ms de margen para el SG90)
LARGO_AGUJA = 30.0
PIVOTE_BAJO = 4.5       # el pivote queda bajo el piso: el canto de la aguja enrasa
SENSORES_COLOR = {"tcs34725": (20.5, 7.0), "tcs3200": (28.5, 10.0)}  # placa, ventana

# SG90 (medir con calibrador y ajustar si su servo difiere)
SG90 = dict(largo=22.8, ancho=12.2, orejas=27.8, eje_off=5.5,
            caja_sobre_oreja=4.3, buje=4.0, estriado=3.0, estriado_d=4.6, buje_d=12.4)

# tolva
TOLVA_SEMIANGULO = 40.0     # pared a 40° de la vertical (criterio de tolvas)
DISCO_D, DISCO_ESP = 80.0, 3.0
CAVIDAD_D, CAVIDAD_R, N_CAVIDADES = 28.0, 24.0, 4
BOCA_SUP_D = 130.0
BASE_D, BASE_ESP = 100.0, 4.0
ANILLO_RE = 49.0
R_TORN_CONO = 44.7
R_TORN_BASE = 55.0
BYJ = dict(eje_off=8.0, orejas=35.0, buje_d=9.6, eje_d=5.0, planos=3.0)


# =====================================================================
# Geometría básica
# =====================================================================
def caja(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def cil_z(x, y, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2).translate((x, y, z0))


def _unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def cil_eje(p, a, largo, r, r2=None):
    """Cilindro (o cono) desde p a lo largo del vector a."""
    a = _unit(a)
    aux = np.array([1.0, 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1.0, 0])
    u = _unit(np.cross(a, aux))
    v = np.cross(a, u)
    m = np.column_stack([u, v, a, np.asarray(p, float)])
    return Manifold.cylinder(largo, r, -1.0 if r2 is None else r2).transform(m)


def disco(p, a, r, h=0.4):
    a = _unit(a)
    return cil_eje(np.asarray(p) - a * h / 2, a, h, r)


def hull(*ms):
    return Manifold.batch_hull(list(ms))


def union(ms):
    ms = [m for m in ms if m is not None]
    return Manifold.batch_boolean(ms, OpType.Add) if len(ms) > 1 else ms[0]


def ccw(poly):
    s = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
            for i in range(len(poly)))
    return list(poly) if s > 0 else list(reversed(poly))


def seccion(*polys):
    return CrossSection([ccw(p) for p in polys], FillRule.NonZero)


M_YZ = np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]], float)


def prisma_yz(cs, x0, x1):
    """Sección en (y, z) extruida a lo largo de X."""
    return cs.extrude(x1 - x0).transform(M_YZ).translate((x0, 0, 0))


def prisma_xz(cs, y0, y1):
    m = np.array([[1, 0, 0, 0], [0, 0, -1, y1], [0, 1, 0, 0]], float)
    return cs.extrude(y1 - y0).transform(m)


def rot_y(m, grados):
    c, s = math.cos(math.radians(grados)), math.sin(math.radians(grados))
    return m.transform(np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0]], float))


def rot_z(m, grados):
    c, s = math.cos(math.radians(grados)), math.sin(math.radians(grados))
    return m.transform(np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0]], float))


def a_cama(m):
    """Centra en XY y apoya en Z = 0."""
    x0, y0, z0, x1, y1, z1 = m.bounding_box()
    return m.translate((-(x0 + x1) / 2, -(y0 + y1) / 2, -z0))


def escribir_stl(m: Manifold, ruta: Path, nombre: str):
    malla = m.to_mesh()
    v = np.asarray(malla.vert_properties, np.float32)[:, :3]
    t = np.asarray(malla.tri_verts, np.int64)
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    n = np.cross(b - a, c - a)
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    datos = np.zeros(len(t), dtype=[("n", "<f4", 3), ("a", "<f4", 3), ("b", "<f4", 3),
                                    ("c", "<f4", 3), ("attr", "<u2")])
    datos["n"], datos["a"], datos["b"], datos["c"] = n, a, b, c
    with open(ruta, "wb") as f:
        f.write(nombre.encode()[:80].ljust(80, b" "))
        f.write(struct.pack("<I", len(t)))
        f.write(datos.tobytes())


# =====================================================================
# Ranuras: validación y disposición
# =====================================================================
@dataclass
class Ranura:
    i: int
    x0: float
    largo: float
    ancho: float
    monedas: list

    @property
    def xc(self):
        return self.x0 + self.largo / 2

    @property
    def dmax(self):
        return max(d for _, _, d in self.monedas)


def validar_ranuras() -> list[str]:
    avisos = []
    for i, (w, monedas) in enumerate(RANURAS):
        if w is None:
            continue
        for _, nombre, d in monedas:
            if w - d < HOLGURA_CAIDA - 1e-9:
                raise ValueError(f"ranura {i + 1}: {nombre} ({d}) no tiene {HOLGURA_CAIDA} mm de holgura")
        siguiente = min(d for _, ms in RANURAS[i + 1:] for _, _, d in ms)
        margen = siguiente - w
        if margen <= 0:
            raise ValueError(f"ranura {i + 1} ({w}): la moneda de {siguiente} mm se cuela")
        if margen < 0.25:
            avisos.append(f"ranura {i + 1} ({w} mm): la moneda siguiente ({siguiente} mm) pasa "
                          f"con solo {margen:.2f} mm de apoyo; calibrar COMPENSACION_RANURA")
    return avisos


def disposicion():
    """Devuelve (ranuras_A, ranuras_B, largo_A, fin_B) en coordenadas del riel."""
    ranuras, x = [], ENTRADA
    for i, (w, monedas) in enumerate(RANURAS):
        if i == 4:                       # cambia de módulo
            largo_a = x
            x += INICIO_B
        ancho = B if w is None else w + COMPENSACION_RANURA
        largo = LARGO_FINAL if w is None else w + EXTRA_LARGO
        ranuras.append(Ranura(i, x, largo, ancho, monedas))
        x += largo + (0 if w is None else ALMA)
    return ranuras[:4], ranuras[4:], largo_a, x + PARED_FINAL


# =====================================================================
# Riel escalonado modular
# =====================================================================
def cola(x, holgura=0.0, z1=COLA_ALTO):
    """Cola de milano en la mitad inferior de la base; la hembra lleva HOLGURA por lado."""
    h = holgura
    poly = [(x - 1.0, -COLA_CUELLO - h), (x + COLA_LARGO + h, -COLA_BOCA - h),
            (x + COLA_LARGO + h, B + COLA_BOCA + h), (x - 1.0, B + COLA_CUELLO + h)]
    z0 = -1.0 if h else 0.0
    return seccion(poly).extrude(z1 - z0).translate((0, 0, z0))


def riel_modulo(x0, x1, ranuras, macho=False, hembra=False, final=False):
    t = math.tan(math.radians(PERALTE))
    piezas = [caja(x0, x1, -ALA, B + ALA, 0, ESP_BASE),
              prisma_yz(seccion([(0, ESP_BASE - 1), (B, ESP_BASE - 1), (B, ESP_BASE + B * t),
                                 (0, ESP_BASE)]), x0, x1),
              caja(x0, x1, -ESP_PARED, 0, 0, ESP_BASE + ALTO_PARED),
              caja(x0, x1, B, B + ESP_PARED, 0, ESP_BASE + B * t + ALTO_LABIO)]
    if final:
        piezas.append(caja(x1 - PARED_FINAL, x1, -ESP_PARED, B + ESP_PARED, 0, ESP_BASE + ALTO_PARED))
    if macho:
        piezas.append(cola(x1))
    m = union(piezas)

    huecos = []
    for r in ranuras:
        huecos.append(caja(r.x0, r.x0 + r.largo, 0, r.ancho, -1, 60))
        for yy in (-Y_TORN_DUCTO, B + Y_TORN_DUCTO):
            huecos.append(cil_z(r.xc, yy, -1, ESP_BASE + 1, M3_ROSCA))
    for xx in (x0 + 12, x1 - 12):
        for yy in (-Y_TORN_CUNA, B + Y_TORN_CUNA):
            huecos.append(cil_z(xx, yy, -1, ESP_BASE + 1, M3_ROSCA))
    if hembra:
        huecos.append(cola(x0, HOLGURA, COLA_ALTO + HOLGURA))
        for yy in (-Y_TORN_COLA, B + Y_TORN_COLA):
            huecos.append(cil_z(x0 + 8, yy, -1, 60, M3_PASO))
    if macho:
        for yy in (-Y_TORN_COLA, B + Y_TORN_COLA):
            huecos.append(cil_z(x1 + 8, yy, -1, COLA_ALTO + 1, M3_ROSCA))
    return m - union(huecos)


# =====================================================================
# Ductos de salida con barrera IR
# =====================================================================
S22, C22 = math.sin(math.radians(INCLINACION)), math.cos(math.radians(INCLINACION))
ABAJO = np.array([S22, 0.0, -C22])          # vertical de mundo vista desde el riel
Y_EJE = np.array([0.0, 1.0, 0.0])


E_DUCTO = 2.0
L_DUCTO = 32.0          # largo del tubo siguiendo la caída
T_IR = 20.0             # barrera IR, medida desde el plano de la ranura
IR_PAD = 3.5            # espesor extra de pared donde asienta el LED


def caja_eje(p, a, hy, hu, largo):
    """Prisma recto desde p siguiendo a: medio ancho hy en Y y hu en el plano XZ."""
    a = _unit(a)
    u = np.array([-a[2], 0.0, a[0]])
    m = np.column_stack([[0.0, 1.0, 0.0], u, a, np.asarray(p, float)])
    return Manifold.cube((2 * hy, 2 * hu, largo)).translate((-hy, -hu, 0)).transform(m)


def brida(r: Ranura, z0=-3.5, z1=0.0):
    """Placa mínima: alrededor del tubo y dos orejas para los M3."""
    ex = (r.largo + 6) / 2
    return union([caja(r.xc - ex, r.xc + ex, -1, B + 1, z0, z1),
                  caja(r.xc - 5.5, r.xc + 5.5, -(Y_TORN_DUCTO + 5.5), 0, z0, z1),
                  caja(r.xc - 5.5, r.xc + 5.5, B, B + Y_TORN_DUCTO + 5.5, z0, z1)])


def ducto(r: Ranura) -> Manifold:
    """Tubo recto bajo la ranura, siguiendo la vertical de mundo, con la barrera IR."""
    c0 = np.array([r.xc, r.ancho / 2, 0.0])
    hy = r.ancho / 2 + 0.8
    hu = r.largo * C22 / 2 + 0.8
    arriba = c0 - ABAJO * (hu + 2.0)            # arranca sobre el plano del riel y se recorta
    corte = caja(-1000, 1000, -1000, 1000, -1000, 0)
    cuerpo = caja_eje(arriba, ABAJO, hy + E_DUCTO, hu + E_DUCTO, L_DUCTO + hu + 2.0) ^ corte
    p_ir = c0 + ABAJO * T_IR
    pads = caja_eje(p_ir - ABAJO * 5.5, ABAJO, hy + E_DUCTO + IR_PAD, 5.5, 11.0)
    m = union([cuerpo, pads, brida(r)])
    huecos = [caja_eje(arriba - ABAJO * 1.0, ABAJO, hy, hu, L_DUCTO + hu + 4.0)]
    for s in (1, -1):
        y_ext = hy + E_DUCTO + IR_PAD
        huecos.append(cil_eje(p_ir + s * Y_EJE * (y_ext + 1.0), -s * Y_EJE, E_DUCTO + IR_PAD, IR_D / 2))
        huecos.append(cil_eje(p_ir + s * Y_EJE * (hy + 2.0), -s * Y_EJE, 4.0, IR_VENTANA / 2))
    for yy in (-Y_TORN_DUCTO, B + Y_TORN_DUCTO):
        huecos.append(cil_z(r.xc, yy, -6, 1, M3_PASO))
    return m - union(huecos)


def imprimir_boca_abajo(m):
    return a_cama(m.rotate((180.0, 0.0, 0.0)))


# =====================================================================
# Módulo de bifurcación activa ($500 antigua / nueva)
# Marco de mundo con origen en el centro de la ranura 6 (cara inferior del
# riel). La moneda cae de plano, el embudo en V la pone de canto y rueda por
# una ranura de G mm a 25°; el TCS34725 lee el anillo y el SG90 baja la aguja.
# =====================================================================
SR, CR = math.sin(math.radians(RAMPA)), math.cos(math.radians(RAMPA))
Y0 = -15.0
ZF0 = ZS - 27.0


def pt(s, h):
    """Punto (y, z) a s mm por el piso y h mm perpendicular a él."""
    return (Y0 + s * CR + h * SR, ZF0 - s * SR + h * CR)


def zf(y):
    return ZF0 - (y - Y0) * SR / CR


def rot_x(m, grados):
    c, s = math.cos(math.radians(grados)), math.sin(math.radians(grados))
    return m.transform(np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0]], float))


def geometria_bif(r: Ranura):
    d500 = r.dmax
    alto = d500 + 3.3
    s_fin = S_AGUJA + 32.0 + 10.0
    piv = pt(S_AGUJA, -PIVOTE_BAJO)
    yn0, yn1 = pt(S_AGUJA, 0)[0], pt(S_AGUJA + 32.0, 0)[0]
    ya0 = pt(s_fin, 0)[0]
    ya1 = ya0 + d500 + 4.5
    z_bot = pt(s_fin, 0)[1] - 26.0
    return dict(alto=alto, s_fin=s_fin, piv=piv, yn=(yn0, yn1), ya=(ya0, ya1), z_bot=z_bot,
                z_ir=z_bot + 12.0, h_sensor=d500 - 1.9)


def bifurcacion(r: Ranura, sensor="tcs34725") -> Manifold:
    g = geometria_bif(r)
    placa, ventana = SENSORES_COLOR[sensor]
    yc = r.ancho / 2
    piv, z_bot, alto = g["piv"], g["z_bot"], g["alto"]
    (yn0, yn1), (ya0, ya1) = g["yn"], g["ya"]
    ztope = pt(g["s_fin"], alto)[1]

    def cavidad(a):
        zt = pt(g["s_fin"], a)[1]
        return (seccion([(-15, zf(-15)), (15, zf(15)), (15, ZS + 2), (-15, ZS + 2)])
                + seccion([pt(0, 0), pt(g["s_fin"], 0), pt(g["s_fin"], a), pt(0, a)])
                + seccion([(yn0, z_bot - 1), (yn1, z_bot - 1), (yn1, zf(yn1) + 0.5), (yn0, zf(yn0) + 0.5)])
                + seccion([(ya0, z_bot - 1), (ya1, z_bot - 1), (ya1, zt), (ya0, zt)])
                + CrossSection.circle(5.5).translate(piv))

    cav = cavidad(alto)
    cav_pared = cavidad(ALTO_BIF_PARED)
    hs = g["h_sensor"]
    zona_sensor = seccion([pt(S_SENSOR + s, hs + h) for s, h in
                           ((-placa / 2 - 9, -placa / 2 - 4), (placa / 2 + 9, -placa / 2 - 4),
                            (placa / 2 + 9, placa / 2 + 4), (-placa / 2 - 9, placa / 2 + 4))])
    zc = piv[1] - SG90["eje_off"]
    zona_servo = seccion([(piv[0] - 8, zc - 17), (piv[0] + 8, zc - 17),
                          (piv[0] + 8, zc + 17), (piv[0] - 8, zc + 17)])
    perfil = cav_pared.offset(PARED_BIF, JoinType.Round) + zona_sensor + zona_servo
    sg = SG90
    x_oreja = G / 2 - 0.5 - (sg["caja_sobre_oreja"] + sg["buje"] + sg["estriado"])
    x_neg, x_pos = x_oreja, G / 2 + PARED_SENSOR   # cara -X plana: las orejas del servo apoyan en ella
    cuerpo = prisma_yz(perfil, x_neg, x_pos) ^ caja(-50, 50, -50, 250, z_bot, 50)

    def riel(m):  # del marco del riel (relativo a la ranura) al de mundo
        return rot_y(m.translate((-r.xc, -yc, 0)), INCLINACION)

    brida_m = riel(brida(r))
    embudo_ext = union([hull(riel(caja(r.x0 - 2.5, r.x0 + r.largo + 2.5, -2.5, r.ancho + 2.5, -3.5, 0)),
                             caja(x_neg, x_pos, -17, 17, ZS - 2, ZS)),
                        brida_m])
    embudo_int = hull(riel(caja(r.x0, r.x0 + r.largo, 0, r.ancho, -5, 1)),
                      caja(-G / 2, G / 2, -15, 15, ZS - 1, ZS + 0.5))

    # SG90 de la aguja en la cara -X; el estriado entra a la ranura
    z_c = piv[1] - sg["eje_off"]
    orejas = [z_c + sg["orejas"] / 2, z_c - sg["orejas"] / 2]

    salidas = [((yn0 + yn1) / 2, g["z_ir"]), ((ya0 + ya1) / 2, g["z_ir"])]
    X = np.array([1.0, 0, 0])

    m = union([cuerpo, embudo_ext, brida_m])

    bolsillo = caja(x_oreja - 1, x_oreja + sg["caja_sobre_oreja"] + 0.3,
                    piv[0] - sg["ancho"] / 2 - 0.35, piv[0] + sg["ancho"] / 2 + 0.35,
                    z_c - sg["largo"] / 2 - 0.35, z_c + sg["largo"] / 2 + 0.35)
    huecos = [prisma_yz(cav, -G / 2, G / 2), embudo_int, bolsillo]
    for yy in (-Y_TORN_DUCTO, B + Y_TORN_DUCTO):
        huecos.append(riel(cil_z(r.xc, yy, -6, 1, M3_PASO)))
        huecos.append(riel(cil_z(r.xc, yy, -34, -4, 7.0)))
    # sensor de color: ventana, alojamiento de la placa y dos pilotos M3 para la tapa
    ps = pt(S_SENSOR, hs)
    huecos.append(cil_eje((G / 2 - 0.5, *ps), X, PARED_SENSOR + 2, ventana / 2))
    alo = caja(x_pos - 2.0, x_pos + 1, -placa / 2 - HOLGURA, placa / 2 + HOLGURA,
               -placa / 2 - HOLGURA, placa / 2 + HOLGURA)
    huecos.append(rot_x(alo, -RAMPA).translate((0, *ps)))
    for s in (-1, 1):
        py, pz = pt(S_SENSOR + s * (placa / 2 + 4.5), hs)
        huecos.append(cil_eje((G / 2 + 1, py, pz), X, PARED_SENSOR + 1, M3_ROSCA / 2))
    # servo: paso del buje y pilotos de las orejas
    huecos.append(cil_eje((x_oreja - 1, *piv), X, (-G / 2 + 0.01) - (x_oreja - 1), sg["buje_d"] / 2))
    for ez in orejas:
        huecos.append(cil_eje((x_oreja - 1, piv[0], ez), X, (x_neg + 6.0) - (x_oreja - 1), M2_ROSCA / 2))
    # barreras IR en las dos salidas (haz a lo largo de X, a través de la ranura)
    for yy, zz in salidas:
        for s in (1, -1):
            huecos.append(cil_eje((s * (G / 2 + 1.0), yy, zz), s * X, 30, IR_D / 2))
        huecos.append(cil_eje((-G / 2 - 1.5, yy, zz), X, G + 3, IR_VENTANA / 2))
    return m - union(huecos)


def aguja() -> Manifold:
    """Lengüeta del desvío: canto superior a ras del piso en 0°, baja 45° hacia $500 nueva."""
    perfil = (CrossSection.circle(4.4)
              + seccion([(0, 0.5), (LARGO_AGUJA - 3, 0.5), (LARGO_AGUJA, 3.0),
                         (LARGO_AGUJA, PIVOTE_BAJO), (0, PIVOTE_BAJO)]))
    m = perfil.extrude(G - 1.4)
    return m - cil_z(0, 0, -1, 10, SG90["estriado_d"])


def tapa_sensor(sensor="tcs34725") -> Manifold:
    placa, _ = SENSORES_COLOR[sensor]
    ls, lh = placa / 2 + 9.5, placa / 2 + 3
    m = caja(-ls, ls, -lh, lh, 0, 2.5)
    m -= caja(-placa / 2 + 1.5, placa / 2 - 1.5, -placa / 2 + 1.5, lh + 1, -1, 4)   # abierta hacia el conector
    for s in (-1, 1):
        m -= cil_z(s * (placa / 2 + 4.5), 0, -1, 4, M3_PASO)
    return m


# =====================================================================
# Tolva dosificadora: cono 40°, disco de 4 cavidades y base con motor
# Orden de apilado (Z): base 0-5 | disco 5,35-8,35 | anillo hasta 8,7 | cono
# =====================================================================
Z_DISCO = BASE_ESP + HOLGURA
Z_ANILLO = Z_DISCO + DISCO_ESP + HOLGURA


def _polar(r, grados):
    return r * math.cos(math.radians(grados)), r * math.sin(math.radians(grados))


def tolva_cono() -> Manifold:
    t = math.tan(math.radians(TOLVA_SEMIANGULO))
    ri, dr = DISCO_D / 2, (BOCA_SUP_D - DISCO_D) / 2
    h = dr / t
    e = 1.6 / math.cos(math.radians(TOLVA_SEMIANGULO))
    ext = union([cil_z(0, 0, 0, 4, 2 * ANILLO_RE),
                 Manifold.cylinder(h, ri + e, ri + dr + e).translate((0, 0, 4)),
                 cil_z(0, 0, 4 + h, 10 + h, 2 * (ri + dr + e))])
    inte = union([cil_z(0, 0, -1, 4.01, 2 * ri),
                  Manifold.cylinder(h, ri, ri + dr).translate((0, 0, 4)),
                  cil_z(0, 0, 4 + h - 0.01, 12 + h, 2 * (ri + dr))])
    # rascador sobre la salida: solo pasa la moneda que va dentro de la cavidad
    arco = [_polar(9, a) for a in range(-55, 19, 3)] + [_polar(ri + 1, a) for a in range(18, -56, -3)]
    rascador = seccion(arco).extrude(8.0)
    m = (ext - inte) + (rascador ^ cil_z(0, 0, -1, 10, 2 * ri + 2))
    for a in (90, 210, 330):
        m -= cil_z(*_polar(R_TORN_CONO, a), -1, 7, M3_ROSCA)
    return m


def tolva_disco(motor="28byj") -> Manifold:
    m = union([cil_z(0, 0, 0, DISCO_ESP, DISCO_D),
               cil_z(0, 0, DISCO_ESP - 0.1, DISCO_ESP + 6, 16),
               Manifold.cylinder(7, 8, 1.5 if motor == "28byj" else 3.5).translate((0, 0, DISCO_ESP + 6))])
    for k in range(N_CAVIDADES):
        m -= cil_z(*_polar(CAVIDAD_R, 45 + 360 / N_CAVIDADES * k), -1, DISCO_ESP + 1, CAVIDAD_D)
    if motor == "28byj":       # eje Ø5 con dos planos a 3 mm
        a = BYJ["planos"] / 2 + 0.15
        m -= cil_z(0, 0, -1, 30, BYJ["eje_d"] + 0.3) ^ caja(-a, a, -5, 5, -1, 30)
    else:                      # estriado del SG90 a presión + tornillo M2 del horn
        m -= cil_z(0, 0, -1, SG90["estriado"], SG90["estriado_d"])
        m -= cil_z(0, 0, -1, 30, 2.2)
        m -= cil_z(0, 0, DISCO_ESP + 3, 30, 4.4)
    return m


def tolva_base(motor="28byj") -> Manifold:
    tabs = [hull(cil_z(*_polar(R_TORN_BASE, a), 0, BASE_ESP, 11.0),
                 cil_z(*_polar(R_TORN_BASE - 12.0, a), 0, BASE_ESP, 11.0)) for a in (45, 135, 225, 315)]
    piezas = tabs + [cil_z(0, 0, 0, BASE_ESP, BASE_D),
              cil_z(0, 0, BASE_ESP - 0.5, Z_ANILLO, 2 * ANILLO_RE) - cil_z(0, 0, 0, 20, DISCO_D + 2 * HOLGURA),
              ]
    huecos = [cil_z(CAVIDAD_R, 0, -11, BASE_ESP + 1, CAVIDAD_D + 1)]
    for a in (45, 135, 225, 315):           # fijación al bastidor, cabeza embutida
        x, y = _polar(R_TORN_BASE, a)
        huecos += [cil_z(x, y, -1, 10, M3_PASO), cil_z(x, y, BASE_ESP - M3_CABEZA_H, 10, M3_CABEZA)]
    for a in (90, 210, 330):                # cono, desde abajo
        x, y = _polar(R_TORN_CONO, a)
        huecos += [cil_z(x, y, -1, Z_ANILLO + 1, M3_PASO), cil_z(x, y, -1, M3_CABEZA_H, M3_CABEZA)]
    if motor == "28byj":
        huecos.append(cil_z(0, 0, -1, BASE_ESP + 1, BYJ["buje_d"] + 0.4))
        for s in (1, -1):
            huecos.append(cil_z(-BYJ["eje_off"], s * BYJ["orejas"] / 2, -1, BASE_ESP - 0.5, M3_ROSCA))
    else:
        sg, h = SG90, HOLGURA
        pad = sg["caja_sobre_oreja"] + sg["buje"] + sg["estriado"] - (Z_DISCO + DISCO_ESP - 0.35)
        huecos.append(cil_z(0, 0, -1, BASE_ESP + 1, sg["buje_d"]))
        huecos.append(caja(-sg["ancho"] / 2 - h, sg["ancho"] / 2 + h, -sg["eje_off"] - sg["largo"] / 2 - h,
                           -sg["eje_off"] + sg["largo"] / 2 + h, -1, sg["caja_sobre_oreja"] - pad + 0.3))
        for s in (1, -1):
            ey = -sg["eje_off"] + s * sg["orejas"] / 2
            piezas.append(caja(-3.5, 3.5, ey - 2.4, ey + 2.4, -pad, 0.1))
            huecos.append(cil_z(0, ey, -pad - 1, 2.5, M2_ROSCA))
    return union(piezas) - union(huecos)


# =====================================================================
# Cuña de 22° para montar el riel (una por esquina, izquierda y derecha)
# =====================================================================
def cuna(espejo=False) -> Manifold:
    t = math.tan(math.radians(INCLINACION))
    largo, ancho, h0 = 22.0, 28.0, 4.0
    m = prisma_xz(seccion([(0, 0), (largo, 0), (largo, h0), (0, h0 + largo * t)]), 0, ancho)
    n = _unit((t, 0, 1))
    y_ala = Y_TORN_CUNA - 6.0               # la cuña arranca 6 mm dentro del ala
    tope = np.array([largo / 2, y_ala, h0 + largo / 2 * t])
    m -= cil_eje(tope + n, -n, 40, M3_PASO / 2)
    m -= cil_eje(tope - 4 * n, -n, 40, M3_CABEZA / 2)
    y_v = ancho - 7.0                       # tornillo al bastidor, fuera del ala
    m -= cil_z(largo / 2, y_v, -1, 40, M3_PASO) + cil_z(largo / 2, y_v, 3, 40, M3_CABEZA)
    return m.mirror((0, 1, 0)) if espejo else m


# =====================================================================
# Salida
# =====================================================================
ORIENTACIONES = [(rx, 0) for rx in range(0, 360, 5)] + [(0, 90), (0, 270)]


def voladizo(m, ang=45.0):
    """Área (mm2) que mira hacia abajo más allá de `ang` desde la vertical, sin contar la cama."""
    me = m.to_mesh()
    v = np.asarray(me.vert_properties, float)[:, :3]
    tr = v[np.asarray(me.tri_verts, int)]
    n = np.cross(tr[:, 1] - tr[:, 0], tr[:, 2] - tr[:, 0])
    area = np.linalg.norm(n, axis=1) / 2
    nz = n[:, 2] / np.maximum(2 * area, 1e-12)
    cama = tr[:, :, 2].max(1) < tr[:, :, 2].min() + 0.05
    malo = (nz < -math.sin(math.radians(ang))) & ~cama
    return float(area[malo].sum()), float(area[cama].sum())


def orientar(m):
    """Prueba giros sobre X cada 5 grados y sobre Y a +-90 y deja la de menos voladizo (a igualdad, más apoyo en la cama)."""
    mejor = None
    for rx, ry in ORIENTACIONES:
        c = a_cama(m.rotate((rx, ry, 0)))
        x0, y0, z0, x1, y1, z1 = c.bounding_box()
        if max(x1 - x0, y1 - y0) > CAMA[0] - 2 or z1 > CAMA[2]:
            continue
        mal, apoyo = voladizo(c)
        clave = mal - 0.1 * apoyo
        if mejor is None or clave < mejor[0]:
            mejor = (clave, c, (rx, ry), mal)
    return mejor[1], mejor[2], mejor[3]


def _clave(r: Ranura):
    return "_".join(c for c, _, _ in r.monedas)


def construir(ensamble=False):
    for a in validar_ranuras():
        print("AVISO:", a)
    r_a, r_b, la, fin_b = disposicion()
    if la + COLA_LARGO > MAX_PIEZA or fin_b - la > MAX_PIEZA:
        raise ValueError(f"módulos de {la + COLA_LARGO:.1f} y {fin_b - la:.1f} mm superan {MAX_PIEZA}")
    r500 = (r_a + r_b)[RANURA_500]

    riel_a = riel_modulo(0, la, r_a, macho=True)
    riel_b = riel_modulo(la, fin_b, r_b, hembra=True, final=True)
    piezas = [("R01_riel_modulo_A", a_cama(riel_a), 1, "entrada + ranuras 1-4, cola macho"),
              ("R02_riel_modulo_B", a_cama(riel_b), 1, "ranuras 5-7 + extremo abierto, cola hembra"),
              ("R03_cuna_22_izq", a_cama(cuna()), 4, "lado pared guía"),
              ("R03_cuna_22_der", a_cama(cuna(True)), 4, "lado labio")]
    ductos = {}
    for r in r_a + r_b:
        if r.i == RANURA_500:
            continue
        ductos[r.i] = ducto(r)
        nombre = f"D{r.i + 1}_ducto_{_clave(r)}"
        piezas.append((nombre, imprimir_boca_abajo(ductos[r.i]), 1, f"ranura {r.ancho:.1f} mm, IR 5 mm"))
    for sensor in SENSORES_COLOR:
        piezas.append((f"B01_bifurcacion_500_{sensor}", a_cama(bifurcacion(r500, sensor)), 1,
                       "imprimir SOLO la del sensor elegido, en PLA negro"))
        piezas.append((f"B03_tapa_sensor_{sensor}", a_cama(tapa_sensor(sensor)), 1, "con la bifurcación"))
    piezas.append(("B02_aguja_desvio", a_cama(aguja()), 1, "estriado del SG90 a presión"))
    piezas.append(("T01_tolva_cono_40", a_cama(tolva_cono()), 1, "semiángulo 40°, boca Ø160"))
    for motor in ("28byj", "sg90"):
        piezas.append((f"T02_disco_dosificador_{motor}", a_cama(tolva_disco(motor)), 1, "elegir uno"))
        piezas.append((f"T03_base_tolva_{motor}", a_cama(tolva_base(motor)), 1, "elegir uno"))

    SALIDA.mkdir(parents=True, exist_ok=True)
    filas = []
    for nombre, m, n, nota in piezas:
        m, giro, mal = orientar(m)
        if m.is_empty() or m.status().name != "NoError":
            raise RuntimeError(f"{nombre}: malla inválida ({m.status()})")
        x0, y0, z0, x1, y1, z1 = m.bounding_box()
        dims = (x1 - x0, y1 - y0, z1 - z0)
        cabe = all(d <= c for d, c in zip(sorted(dims[:2]) + [dims[2]], sorted(CAMA[:2]) + [CAMA[2]]))
        if not cabe:
            raise ValueError(f"{nombre} ({dims}) no cabe en la cama {CAMA}")
        escribir_stl(m, SALIDA / f"{nombre}.stl", nombre)
        filas.append([nombre, n, *(f"{d:.1f}" for d in dims), f"{m.volume() / 1000:.1f}", f"{mal:.0f}", nota])
        print(f"{nombre:38s} x{n}  {dims[0]:6.1f} x {dims[1]:6.1f} x {dims[2]:6.1f} mm  "
              f"{m.volume() / 1000:6.1f} cm3  voladizo {mal:6.0f} mm2  giro {giro}")
    print(f"TOTAL macizo: {sum(float(f[5]) * f[1] for f in filas):.0f} cm3 "
          f"(con relleno 15 %: unos {sum(float(f[5]) * f[1] for f in filas) * 0.45 * 1.24:.0f} g de PLA)")
    with open(SALIDA / "piezas_clasificador.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pieza", "cantidad", "x_mm", "y_mm", "z_mm", "volumen_cm3", "voladizo_mm2", "nota"])
        w.writerows(filas)

    if ensamble:
        _ensamble(riel_a, riel_b, ductos, r500)


def _ensamble(riel_a, riel_b, ductos, r500):
    def mundo(m):
        return rot_y(m, INCLINACION)

    def p_mundo(x, y, z):
        return (x * C22 + z * S22, y, -x * S22 + z * C22)

    partes = [mundo(riel_a), mundo(riel_b)] + [mundo(d) for d in ductos.values()]
    partes.append(bifurcacion(r500).translate(p_mundo(r500.xc, r500.ancho / 2, 0)))
    nombres = ["rielA", "rielB"] + [f"D{i + 1}" for i in ductos] + ["bif"]
    libres = True
    for i in range(len(partes)):
        for j in range(i + 1, len(partes)):
            v = (partes[i] ^ partes[j]).volume()
            if v > 0.5:
                libres = False
                print(f"INTERFERENCIA {nombres[i]} x {nombres[j]}: {v:.1f} mm3")
    print("sin interferencias" if libres else "HAY interferencias")
    ex, ey, ez = p_mundo(ENTRADA / 2, 12.0, ESP_BASE)
    tolva = union([tolva_base(), tolva_disco().translate((0, 0, Z_DISCO)),
                   tolva_cono().translate((0, 0, Z_ANILLO))])
    partes.append(tolva.translate((ex - CAVIDAD_R, ey, ez + 25)))
    carpeta = SALIDA / "ensamble"
    carpeta.mkdir(exist_ok=True)
    escribir_stl(union(partes), carpeta / "ensamble_referencia.stl", "ensamble")
    print("ensamble de referencia:", carpeta / "ensamble_referencia.stl")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ensamble", action="store_true", help="exporta también el ensamble de referencia")
    construir(ap.parse_args().ensamble)
