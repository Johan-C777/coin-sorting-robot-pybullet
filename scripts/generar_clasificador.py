"""Clasificador físico de la etapa 1 (v2): tolva dosificadora, riel escalonado en dos
módulos, ductos verticales con barrera infrarroja y bifurcación de $500 con plato
basculante. Sin tornillos y sin soportes de impresión.

    pip install manifold3d numpy
    python scripts/generar_clasificador.py              # STL de impresión + verificación
    python scripts/generar_clasificador.py --ensamble   # + ensamble de referencia

Salida en hardware/stl/ (mm, orientación de impresión: Z = capas).
Impresora objetivo: Creality K1C, cama 220 x 220 x 250 mm.

Uniones (todas por encaje, sin tornillos)
  * clavijas Ø6 en agujeros ciegos del ala del riel (ductos y patas),
  * llaves de mariposa bajo la junta entre los dos módulos del riel,
  * puente del sensor a horcajadas sobre las paredes,
  * servo SG90 y TCS34725 a presión; motor 28BYJ-48 con bridas de nailon.

Marcos de referencia
  * riel (R): X a lo largo de la pista (bajando), Y a lo ancho (Y=0 cara de la pared
    guía), Z normal a la pista. En el ensamble se gira 22° sobre Y.
  * mundo (W): origen en el centro de la ranura, sobre el plano inferior del riel;
    Z hacia arriba. Los ductos se construyen y se imprimen en este marco.
"""
from __future__ import annotations

import argparse
import csv
import math
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

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
AJUSTE_PRESION = 0.0    # + afloja / - aprieta todos los encajes a presión (clavijas, llaves)
PEG_D = 6.0             # clavija
PEG_L = 2.9
HUECO_D = PEG_D + 0.10 + AJUSTE_PRESION
HUECO_PROF = 3.1        # agujero ciego en el ala (base de 4 mm)
IR_D = 5.2              # LED IR / fototransistor de 5 mm a presión
IR_VENTANA = 3.0        # abertura hacia el ducto: hace de tope del LED
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
ESP_BASE = 4.0
ALTO_PARED = 10.0
ESP_PARED = 2.4
ALA = 14.0              # ala a cada lado del canal
ENTRADA = 35.0          # zona donde cae la moneda de la tolva
ALMA = 12.0             # material entre ranuras
ALMA_EXTRA = {0: 4.6, 1: 2.6, 2: 1.6, 4: 17.7, 5: 17.2}   # alma extra tras la ranura i: separa las salidas >= 37 mm (collares de los tubos de 1")
# Base: lámina sobre 4 patas de tubo PVC de 3/4" con tees; dos bases impresas en ABS
PVC_D = 26.7             # tubo PVC presión de 3/4" (diámetro exterior)
BORE_R = PVC_D / 2 + 0.3 # alojamiento a presión
PARED_PVC = 3.0
PROF_PVC = 30.0          # penetración del tubo en la base
PLACA, PLACA_E = 44.0, 4.0
F_ACC = 11.0             # tee de 3/4": del centro al fondo de la copa (medir en el accesorio real)
LAMINA_E = 9.0           # lámina de MDF de 9 mm (6 mm se flecha entre las patas); su cara de arriba es el plano z = 0
Z_PISO = -200.0          # piso bajo la banda (cara de arriba de la banda en -130): 70 mm para motor y electrónica
SEP_BASE = 150.0         # separación entre patas delantera y trasera (hueco libre ≈ 123 mm para la banda)
Z_BOCA = -70.0          # altura (mundo) de la boca de los vasos; los ductos bajan hasta 6 mm sobre ella
EXTRA_LARGO = 4.0       # largo de ranura = ancho + 4 (la moneda cabe entera)
LARGO_FINAL = 32.0
PARED_FINAL = 4.0
INICIO_B = 24.0         # el módulo B arranca 24 mm antes de su primera ranura
MAX_PIEZA = 210.0
Y_PEG = 8.0             # clavija de ducto en el ala, a esta distancia de la pared
Y_PATA = 10.0           # clavija de pata en el ala
LLAVE_L, LLAVE_CUELLO, LLAVE_BOCA, LLAVE_ESP = 10.0, 6.5, 11.0, 2.4

# ductos
E_DUCTO = 2.0
PVC_DUCTO_D = 33.4      # tubo PVC presión de 1" RDE 21 (Ø ext 33,4; interior ≈ 30): pasa la $1000 (26,7)
BORE_DUCTO_R = (PVC_DUCTO_D + 0.3) / 2
R_COLLAR = BORE_DUCTO_R + 1.2
Z_RECT = 31.0           # el adaptador es rectangular (ranura) hasta aquí
D_EMBUDO = 9.0          # embudo de 36° de la ranura al tubo redondo
PROF_DUCTO = 20.0       # penetración del tubo de 1" en el collar
Z_TUBO = -(Z_RECT + D_EMBUDO)   # cara superior del tubo bajo el centro de la ranura
T_IR = 20.0             # barrera IR bajo el plano del riel
IR_PAD = 3.5            # espesor extra de pared donde asienta el LED

# bifurcación D6
T_PIV = 66.0            # pivote del plato bajo el plano del riel (≈115 ms de caída)
ANG_FLARE = 40.0        # ensanche del ducto, desde la vertical (se imprime sin soporte)
INCL_PLATO = 35.0       # inclinación del plato a cada lado
PLATO_L, PLATO_H = 31.0, 9.0
COL_INT0, COL_INT1 = 4.5, 32.3      # columnas de salida: borde interno y externo desde el centro
T_COL = 26.0            # de la punta del divisor al fondo
SG90 = dict(largo=22.8, ancho=12.2, orejas=27.8, eje_off=5.5, caja_sobre_oreja=4.3,
            buje=4.0, estriado=3.0, estriado_d=4.6, buje_d=12.4)
PAD_SERVO = 5.0

# puente del sensor de color
Z_PUENTE = ESP_BASE + ALTO_PARED
PUENTE_L, PUENTE_ESP, FALDON, FALDON_ALTO = 28.0, 2.6, 2.0, 7.0
SENSOR_PLACA, SENSOR_VENTANA = 20.5, 10.0

# tolva
TOLVA_SEMIANGULO = 40.0
DISCO_D, DISCO_ESP = 80.0, 3.0
CAVIDAD_D, CAVIDAD_R, N_CAVIDADES = 28.0, 24.0, 4
BOCA_SUP_D = 130.0
BASE_D, BASE_ESP = 100.0, 4.0
ANILLO_RE = 49.0
R_PATA_TOLVA = 58.0
BYJ = dict(eje_off=8.0, orejas=35.0, buje_d=9.6, eje_d=5.0, planos=3.0, cuerpo_d=28.0)

# altura del riel sobre la mesa en la pata más baja (centro del ala)
H_MIN_RIEL = 40.0
HOLGURA_TOLVA = 25.0    # caída de la moneda de la tolva al piso del riel

S22, C22 = math.sin(math.radians(INCLINACION)), math.cos(math.radians(INCLINACION))
T22 = S22 / C22
PERALTE_T = math.tan(math.radians(PERALTE))
ALTO_LABIO = ALTO_PARED - B * PERALTE_T


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
    """Sección en (x, z) extruida a lo largo de Y, de y0 a y1."""
    m = np.array([[1, 0, 0, 0], [0, 0, -1, y1], [0, 1, 0, 0]], float)
    return cs.extrude(y1 - y0).transform(m)


def rot_y(m, grados):
    c, s = math.cos(math.radians(grados)), math.sin(math.radians(grados))
    return m.transform(np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0]], float))


def rot_x(m, grados):
    c, s = math.cos(math.radians(grados)), math.sin(math.radians(grados))
    return m.transform(np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0]], float))


def a_cama(m):
    """Centra en XY y apoya en Z = 0."""
    x0, y0, z0, x1, y1, z1 = m.bounding_box()
    return m.translate((-(x0 + x1) / 2, -(y0 + y1) / 2, -z0))


def gota(r, extra=0.0):
    """Sección de un agujero horizontal sin puente: círculo con punta a 45° hacia arriba."""
    k = r / math.sqrt(2)
    return CrossSection.circle(r + extra) + seccion([(-k, k), (k, k), (0, r * math.sqrt(2))])


def agujero_y(h, z, r, y0, y1):
    """Agujero horizontal (eje Y) en gota, de y0 a y1, centrado en (h, z)."""
    return prisma_xz(gota(r).translate((h, z)), min(y0, y1), max(y0, y1))


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


def clavija(x, y, z0=0.0, direccion=(0, 0, 1)):
    """Clavija Ø6 con punta cónica; con z0 = 0 sale de la cara z = 0 hacia +Z (marco R)."""
    p = np.array([x, y, z0], float)
    a = _unit(direccion)
    return (cil_eje(p - a * 0.2, a, PEG_L - 0.6 + 0.2 + 0.1, PEG_D / 2)
            + cil_eje(p + a * (PEG_L - 0.6), a, 0.6, PEG_D / 2, PEG_D / 2 - 0.5))


def hueco_clavija(x, y):
    return cil_z(x, y, -1, HUECO_PROF, HUECO_D)


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
    def yc(self):
        return self.ancho / 2

    @property
    def dmax(self):
        return max(d for _, _, d in self.monedas)

    @property
    def clave(self):
        return "_".join(c for c, _, _ in self.monedas)


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


@dataclass
class Disposicion:
    ranuras: list
    la: float           # fin del módulo A / inicio del B
    fin_b: float
    x_sensor: float     # centro del puente del sensor
    patas: list         # x de las patas del riel


def disposicion() -> Disposicion:
    ranuras, x = [], ENTRADA
    la = None
    for i, (w, monedas) in enumerate(RANURAS):
        if i == 4:                       # cambia de módulo
            la = x
            x += INICIO_B
        ancho = B if w is None else w + COMPENSACION_RANURA
        largo = LARGO_FINAL if w is None else w + EXTRA_LARGO
        ranuras.append(Ranura(i, x, largo, ancho, monedas))
        x += largo + (0 if w is None else ALMA + ALMA_EXTRA.get(i, 0.0))
    fin_b = x + PARED_FINAL
    # primera pata entre las ranuras 2 y 3; luego una junto a la junta y otra al final
    x_pata_a = (ranuras[1].x0 + ranuras[1].largo + ranuras[2].x0) / 2
    return Disposicion(ranuras, la, fin_b, la + 6.0, [x_pata_a, la + 20.5, fin_b - 7.0])


def clavijas_ducto(r: Ranura):
    y2 = min(r.ancho + 6.5, B + 8.5)
    return [(r.xc, -Y_PEG), (r.xc, y2)]


# =====================================================================
# Riel escalonado modular (marco R, se imprime con la base en la cama)
# =====================================================================
def llave_perfil(holgura=0.0):
    h = holgura
    L, n, b = LLAVE_L + h, LLAVE_CUELLO / 2 + h, LLAVE_BOCA / 2 + h
    return [(-L, -b), (0, -n), (L, -b), (L, b), (0, n), (-L, b)]


Y_LLAVES = (-Y_PEG, B / 2, B + Y_PEG)


def riel_modulo(d: Disposicion, x0, x1, ranuras, final=False, llaves_en=None):
    piezas = [caja(x0, x1, -ALA, B + ALA, 0, ESP_BASE),
              prisma_yz(seccion([(0, ESP_BASE - 1), (B, ESP_BASE - 1), (B, ESP_BASE + B * PERALTE_T),
                                 (0, ESP_BASE)]), x0, x1),
              caja(x0, x1, -ESP_PARED, 0, 0, ESP_BASE + ALTO_PARED),
              caja(x0, x1, B, B + ESP_PARED, 0, ESP_BASE + B * PERALTE_T + ALTO_LABIO)]
    if final:
        piezas.append(caja(x1 - PARED_FINAL, x1, -ESP_PARED, B + ESP_PARED, 0, ESP_BASE + ALTO_PARED))
    m = union(piezas)

    huecos = []
    for r in ranuras:
        huecos.append(caja(r.x0, r.x0 + r.largo, 0, r.ancho, -1, 60))
        for px, py in clavijas_ducto(r):
            huecos.append(hueco_clavija(px, py))
    for xp in d.patas:
        if x0 <= xp <= x1:
            for py in (-Y_PATA, B + Y_PATA):
                huecos.append(hueco_clavija(xp, py))
    for yy in Y_LLAVES:                 # media llave a cada lado de la junta
        cs = seccion(llave_perfil(0.2)).translate((d.la, yy))
        huecos.append(cs.extrude(LLAVE_ESP + 0.6 + 1.0).translate((0, 0, -1.0)))
    return m - union(huecos)


def llave() -> Manifold:
    return seccion(llave_perfil(0.0)).extrude(LLAVE_ESP)


# =====================================================================
# Ductos de salida con barrera IR (marco W, origen en el centro de la ranura)
# =====================================================================
class Mundo:
    """Marco de mundo de una ranura: R -> W = girar 22° sobre Y alrededor del centro."""

    def __init__(self, xc, yc):
        self.xc, self.yc = xc, yc

    def r(self, m):
        return rot_y(m.translate((-self.xc, -self.yc, 0)), INCLINACION)

    def corte(self):
        """Todo lo que queda bajo el plano inferior del riel."""
        return self.r(caja(-1000, 1000, -1000, 1000, -1000, 0))


def medidas_tubo(r: Ranura):
    hu = r.largo * C22 / 2 + 0.8
    hy = r.ancho / 2 + 0.8
    return hu, hy


def orejas(r: Ranura, mw: Mundo, hy):
    """Orejas con clavija: cuña de 45° bajo cada una, en marco R y luego a W."""
    out = []
    for px, py in clavijas_ducto(r):
        if py < r.yc:
            y_in, y_far = r.yc - hy - E_DUCTO + 1.5, py - 4.5
        else:
            y_in, y_far = r.yc + hy + E_DUCTO - 1.5, py + 4.5
        run = abs(y_far - y_in)
        poli = [(y_in, 0.0), (y_far, 0.0), (y_far, -3.0), (y_in, -3.0 - 1.25 * run)]
        out.append(prisma_yz(seccion(poli), px - 5, px + 5))
        out.append(clavija(px, py))
    return mw.r(union(out))


def pad_ir(mw_hu, hy, up, lado):
    """Plataforma del LED a un lado del tubo, con cartela de 45° por debajo."""
    s = lado
    y0, y1 = hy, hy + E_DUCTO + IR_PAD
    arriba = caja(-7, 7, min(s * y0, s * y1), max(s * y0, s * y1), up - 7, up + 7)
    base = caja(-7, 7, min(s * y0, s * (y0 + E_DUCTO)), max(s * y0, s * (y0 + E_DUCTO)),
                up - 7 - IR_PAD, up + 7)
    return hull(arriba, base)


def agujeros_ir(hy, up, h=0.0):
    out = []
    for s in (1, -1):
        y_out = s * (hy + E_DUCTO + IR_PAD + 1.0)
        y_stop = s * (hy + 2.0)
        out.append(agujero_y(h, up, IR_D / 2, y_out, y_stop))
        out.append(agujero_y(h, up, IR_VENTANA / 2, s * (hy + 2.5), s * (hy - 0.5)))
    return out


def adaptador(r: Ranura) -> Manifold:
    """Adaptador de la ranura a un tubo PVC de 1": caja de la ranura con barrera IR y orejas con clavija,
    embudo de 36° y collar redondo en el que entra el tubo (PROF_DUCTO mm)."""
    mw = Mundo(r.xc, r.yc)
    hu, hy = medidas_tubo(r)
    top = (hu + E_DUCTO) * T22 + 4.0
    eo, yo = hu + E_DUCTO, hy + E_DUCTO
    z_e = -Z_RECT
    z_c = -Z_RECT - D_EMBUDO
    z_f = z_c - PROF_DUCTO
    ext = caja(-eo, eo, -yo, yo, z_e, top) ^ mw.corte()
    pads = [pad_ir(hu, hy, -T_IR, s) for s in (1, -1)]
    embudo = hull(caja(-eo, eo, -yo, yo, z_e - 0.01, z_e), cil_z(0, 0, z_c, z_c + 0.01, 2 * R_COLLAR))
    collar = cil_z(0, 0, z_f, z_c + 0.01, 2 * R_COLLAR)
    m = union([ext, *pads, orejas(r, mw, hy), embudo, collar])
    dentro = hull(caja(-hu, hu, -hy, hy, z_e - 0.01, z_e), cil_z(0, 0, z_c, z_c + 0.01, 2 * BORE_DUCTO_R))
    huecos = [caja(-hu, hu, -hy, hy, z_e, top + 2), dentro, cil_z(0, 0, z_f - 1.0, z_c, 2 * BORE_DUCTO_R),
              *agujeros_ir(hy, -T_IR)]
    return m - union(huecos)


# =====================================================================
# Bifurcación D6: tubo vertical, plato basculante y dos columnas de salida
# =====================================================================
def geom_d6(r: Ranura, extra: float = 0.0):
    hu, hy = medidas_tubo(r)
    t_fl = T_PIV - 16.0
    t = math.tan(math.radians(ANG_FLARE))
    d_fl = (COL_INT1 - hu) / t
    t_div = T_PIV + 26.0
    t_bot = t_div + T_COL + extra
    return dict(hu=hu, hy=hy, t_fl=t_fl, d_fl=d_fl, t_div=t_div, t_bot=t_bot,
                y_servo=-(hy + E_DUCTO), up_ir=-(t_div + T_COL - 14.0))


def d6(r: Ranura, extra: float = 0.0) -> Manifold:
    g = geom_d6(r, extra)
    mw = Mundo(r.xc, r.yc)
    hu, hy, t_fl, d_fl, t_div, t_bot = (g[k] for k in ("hu", "hy", "t_fl", "d_fl", "t_div", "t_bot"))
    sg = SG90
    hw = COL_INT1 + E_DUCTO
    top = (hu + E_DUCTO) * T22 + 4.0
    eo, yo = hu + E_DUCTO, hy + E_DUCTO
    desfase = (E_DUCTO / math.cos(math.radians(ANG_FLARE)) - E_DUCTO) / math.tan(math.radians(ANG_FLARE))
    # exterior
    tubo = caja(-eo, eo, -yo, yo, -t_fl, top) ^ mw.corte()
    ensanche = hull(caja(-eo, eo, -yo, yo, -t_fl + desfase - 0.01, -t_fl + desfase),
                    caja(-hw, hw, -yo, yo, -t_fl - d_fl - 0.01, -t_fl - d_fl))
    ancho = caja(-hw, hw, -yo, yo, -t_bot, -t_fl - d_fl)
    # pastilla del servo en la cara -Y: tope de las orejas y bolsillo del cuerpo
    z_p = -T_PIV
    eje_u = z_p - sg["eje_off"]                      # el cuerpo del servo sube desde el eje
    z_top_cuerpo = z_p + (sg["largo"] - sg["eje_off"])
    z_c = z_p + sg["largo"] / 2 - sg["eje_off"]
    z_orejas_a, z_orejas_b = z_c + 16.1, z_c - 16.1       # orejas de 32,2 mm, centradas en el cuerpo
    pad_y0, pad_y1 = -(yo + PAD_SERVO), -yo + 0.5
    pad = hull(caja(-9.5, 9.5, pad_y0, pad_y1, z_orejas_b, z_orejas_a),
               caja(-9.5, 9.5, -yo, pad_y1, z_orejas_b - PAD_SERVO, z_orejas_a))
    # pivote de pasador en la cara +Y
    m = union([tubo, ensanche, ancho, pad])

    # interior
    interior = [caja(-hu, hu, -hy, hy, -t_fl - 0.01, top + 2),
                hull(caja(-hu, hu, -hy, hy, -t_fl - 0.01, -t_fl),
                     caja(-COL_INT1, COL_INT1, -hy, hy, -t_fl - d_fl - 0.01, -t_fl - d_fl)),
                caja(-COL_INT1, COL_INT1, -hy, hy, -t_div - 0.01, -t_fl - d_fl)]
    for s in (1, -1):
        interior.append(caja(min(s * COL_INT0, s * COL_INT1), max(s * COL_INT0, s * COL_INT1), -hy, hy,
                             -t_bot - 1, -t_div))
    # punta del divisor: cuña de 45° (sus caras miran hacia arriba)
    punta = prisma_xz(seccion([(-COL_INT0, -t_div), (COL_INT0, -t_div), (0, -t_div + COL_INT0)]),
                      -hy - 1, hy + 1)
    huecos = interior
    # pasador +Y y buje -Y del plato
    huecos.append(cil_eje((0, hy - 1.0, z_p), (0, 1, 0), E_DUCTO + 2.0, 2.2))
    # bolsillo del servo (gable arriba, sin puente) y paso del buje
    pw, ph = sg["ancho"] / 2 + 0.25, sg["largo"]
    pocket = seccion([(-pw, z_p - sg["eje_off"] - 0.3), (pw, z_p - sg["eje_off"] - 0.3),
                      (pw, z_top_cuerpo + 0.3), (0, z_top_cuerpo + 0.3 + pw), (-pw, z_top_cuerpo + 0.3)])
    huecos.append(prisma_xz(pocket, pad_y0 - 1, pad_y0 + sg["caja_sobre_oreja"] + 0.3))
    huecos.append(agujero_y(0, z_p, sg["buje_d"] / 2 + 0.4, pad_y0 + sg["caja_sobre_oreja"] + 0.2, -hy + 0.5))
    # barreras IR de las dos columnas
    for s in (1, -1):
        huecos += [h for h in agujeros_ir_col(s, g, hy)]
    cuerpo = union([m, *[pad_ir_col(s, g, hy) for s in (1, -1)]]) + punta
    return cuerpo - union(huecos)


def pad_ir_col(s, g, hy):
    """Plataformas del LED a ambos lados de la columna s (centro h = s·15,4)."""
    h = s * (COL_INT0 + COL_INT1) / 2
    up = g["up_ir"]
    out = []
    for lado in (1, -1):
        y0, y1 = hy, hy + E_DUCTO + IR_PAD
        arriba = caja(h - 7, h + 7, min(lado * y0, lado * y1), max(lado * y0, lado * y1), up - 7, up + 7)
        base = caja(h - 7, h + 7, min(lado * y0, lado * (y0 + E_DUCTO)), max(lado * y0, lado * (y0 + E_DUCTO)),
                    up - 7 - IR_PAD, up + 7)
        out.append(hull(arriba, base))
    return union(out)


def agujeros_ir_col(s, g, hy):
    return agujeros_ir(hy, g["up_ir"], h=s * (COL_INT0 + COL_INT1) / 2)


def plato(r: Ranura) -> Manifold:
    """Plato basculante: bloque de 31 x 9 con buje de estriado (-Y) y pasador (+Y). Eje Y por el centro."""
    g = geom_d6(r)
    hy = g["hy"]
    sg = SG90
    c = 3.0
    perfil = seccion([(-PLATO_L / 2 + c, -PLATO_H / 2), (PLATO_L / 2 - c, -PLATO_H / 2),
                      (PLATO_L / 2, -PLATO_H / 2 + c), (PLATO_L / 2, PLATO_H / 2 - c),
                      (PLATO_L / 2 - c, PLATO_H / 2), (-PLATO_L / 2 + c, PLATO_H / 2),
                      (-PLATO_L / 2, PLATO_H / 2 - c), (-PLATO_L / 2, -PLATO_H / 2 + c)])
    y_min = -hy + sg["buje"] * 0 + 1.9           # cara -Y: tras el buje (sobresale 1,6) + 0,3 de aire
    y_max = hy - 0.5
    cuerpo = prisma_xz(perfil, y_min, y_max)
    pasador = cil_eje((0, y_max - 0.2, 0), (0, 1, 0), 1.8, 2.0)
    estriado = cil_eje((0, y_min - 1.0, 0), (0, 1, 0), 1.0 + 4.6, sg["estriado_d"] / 2 + 0.05)
    return cuerpo + pasador - estriado


# =====================================================================
# Puente del sensor de color (marco R, se imprime con la cara de arriba en la cama)
# =====================================================================
def puente() -> Manifold:
    """Puente a horcajadas sobre las dos paredes. Su cara de abajo (z = 0) apoya en la parte alta de
    las paredes; el TCS34725 cuelga debajo en una guía abierta hacia -X, con la cara del sensor mirando
    la moneda. Se imprime boca abajo (faldones y guía hacia arriba)."""
    x0, x1 = -PUENTE_L / 2, PUENTE_L / 2
    y_in0, y_in1 = -ESP_PARED - 0.05, B + ESP_PARED + 0.05
    placa = caja(x0, x1, y_in0 - FALDON, y_in1 + FALDON, 0, PUENTE_ESP)
    piezas = [placa]
    for (ya, yb, lado) in ((y_in0 - FALDON, y_in0, 1), (y_in1, y_in1 + FALDON, -1)):
        for xa, xb in ((x0, x0 + 8), (x1 - 8, x1)):
            piezas.append(caja(xa, xb, ya, yb, -FALDON_ALTO, 0.01))
            # diente de agarre con entrada a 45°
            y_pared = yb if lado == 1 else ya
            piezas.append(prisma_yz(seccion([(y_pared, -FALDON_ALTO + 0.4),
                                             (y_pared + lado * -0.4, -FALDON_ALTO + 0.8),
                                             (y_pared, -FALDON_ALTO + 1.2)]), xa, xb))
    ys, p, ep, prof = 11.8, SENSOR_PLACA + 0.5, 1.2, 2.2
    # guía del sensor: dos paredes con labio que lo sujetan por abajo; abierta hacia -X, tope en +X
    for lado in (1, -1):
        y_i = ys + lado * p / 2
        y_o = y_i + lado * ep
        poli = [(y_o, 0.01), (y_i, 0.01), (y_i, -prof + 0.9), (y_i - lado * 0.6, -prof + 0.4),
                (y_i - lado * 0.6, -prof), (y_o, -prof)]
        piezas.append(prisma_yz(seccion(poli), x0 + 1, p / 2 + ep))
    piezas.append(caja(p / 2 - 0.3, p / 2 + ep, ys - p / 2 - ep + 0.05, ys + p / 2 + ep - 0.05, -prof + 0.05, 0.01))
    return union(piezas)


# =====================================================================
# Patas del riel y de la tolva (cruz hueca, pie con ranuras para bridas)
# =====================================================================
def _pie_y_cartelas(altura, ancho_pie, largo_pie, sentido, y_c):
    """Pie plano con cartelas de 45° hacia afuera. sentido = -1 hacia -Y, +1 hacia +Y, 0 simétrico."""
    piezas = []
    esp = 3.0
    if sentido == 0:
        piezas.append(caja(-ancho_pie / 2, ancho_pie / 2, -ancho_pie / 2, ancho_pie / 2, 0, esp))
        run = ancho_pie / 2 - 0.4 - 6.0
        for s in (1, -1):
            piezas.append(prisma_xz(seccion([(s * 5.5, esp - 0.1), (s * (ancho_pie / 2 - 0.4), esp - 0.1),
                                             (s * 5.5, esp + min(run * 1.0, altura - esp))]).translate((0, 0)), -1.5, 1.5))
            piezas.append(prisma_yz(seccion([(s * 5.5, esp - 0.1), (s * (ancho_pie / 2 - 0.4), esp - 0.1),
                                             (s * 5.5, esp + min(run * 1.0, altura - esp))]), -1.5, 1.5))
    else:
        s = sentido
        y0, y1 = (y_c - 6, y_c + 6)
        out = largo_pie
        ya, yb = (min(s * out, 2), max(s * out, 2)) if s < 0 else (-2, out)
        piezas.append(caja(-ancho_pie / 2, ancho_pie / 2, ya, yb, 0, esp))
        run = out - 0.4 - 6.0
        poli = [(s * 5.5, esp - 0.1), (s * (out - 0.4), esp - 0.1), (s * 5.5, esp + min(run * 1.0, altura - esp))]
        piezas.append(prisma_yz(seccion(poli), -1.5, 1.5))
        for sx in (1, -1):
            piezas.append(prisma_xz(seccion([(sx * 5.5, esp - 0.1), (sx * (ancho_pie / 2 - 0.4), esp - 0.1),
                                             (sx * 5.5, esp + min((ancho_pie / 2 - 0.4 - 6) * 1.0, altura - esp))]), -1.5, 1.5))
    return piezas


def pata(altura, sentido, inclinada=True) -> Manifold:
    """Pata de cruz de 12 mm. Parte superior inclinada 22° (cara del riel), clavija normal a ella.
    La cara superior pasa por (0, 0, altura); `sentido` dice hacia dónde sale el pie."""
    n = 12.0
    cruz = [caja(-n / 2, n / 2, -1.2, 1.2, 0, altura + 8), caja(-1.2, 1.2, -n / 2, n / 2, 0, altura + 8)]
    cabeza = caja(-n / 2, n / 2, -n / 2, n / 2, altura - 7, altura + 8)
    cuerpo = union([*cruz, cabeza])
    if inclinada:
        plano = rot_y(caja(-100, 100, -100, 100, -1000, 0), INCLINACION).translate((0, 0, altura))
        cuerpo = cuerpo ^ plano
    pie = _pie_y_cartelas(altura, 32.0 + altura * 0.05, 24.0, sentido, 0.0)
    m = union([cuerpo, *pie])
    huecos = []
    ysl = 17.0 * sentido if sentido else 0.0
    for sx in (1, -1):
        huecos.append(caja(sx * 13 - 2.1, sx * 13 + 2.1, ysl - 0.8, ysl + 0.8, -1, 4))
    pegs = union([clavija(0, 0, altura, direccion=(S22, 0, C22) if inclinada else (0, 0, 1))])
    return (m - union(huecos)) + pegs


def pata_tolva(altura) -> Manifold:
    n = 13.0
    cruz = [caja(-n / 2, n / 2, -1.2, 1.2, 0, altura), caja(-1.2, 1.2, -n / 2, n / 2, 0, altura)]
    cabeza = caja(-n / 2, n / 2, -n / 2, n / 2, altura - 6, altura)
    pie = _pie_y_cartelas(altura, 36.0, 0, 0, 0.0)
    m = union([*cruz, cabeza, *pie])
    huecos = [caja(sx * 15 - 2.1, sx * 15 + 2.1, -0.8, 0.8, -1, 4) for sx in (1, -1)]
    return (m - union(huecos)) + clavija(0, 0, altura)


# =====================================================================
# Tolva dosificadora: cono 40°, disco de 4 cavidades y base con motor
# =====================================================================
Z_DISCO = BASE_ESP + HOLGURA
Z_ANILLO = Z_DISCO + DISCO_ESP + HOLGURA


def _polar(r, grados):
    return r * math.cos(math.radians(grados)), r * math.sin(math.radians(grados))


R_PEG_CONO = 44.7       # clavijas del anillo que centran el cono (a 90, 210 y 330 grados)


def tolva_cono() -> Manifold:
    """Se imprime con el flanje abajo; tres agujeros ciegos reciben las clavijas del anillo de la base."""
    t = math.tan(math.radians(TOLVA_SEMIANGULO))
    ri, dr = DISCO_D / 2, (BOCA_SUP_D - DISCO_D) / 2
    h = dr / t
    e = 1.6 / math.cos(math.radians(TOLVA_SEMIANGULO))
    z0 = 4.0
    ext = union([cil_z(0, 0, 0, z0, 2 * ANILLO_RE),
                 Manifold.cylinder(h, ri + e, ri + dr + e).translate((0, 0, z0)),
                 cil_z(0, 0, z0 + h, 10 + z0 + h, 2 * (ri + dr + e))])
    inte = union([cil_z(0, 0, -1, z0 + 0.01, 2 * ri),
                  Manifold.cylinder(h, ri, ri + dr).translate((0, 0, z0)),
                  cil_z(0, 0, z0 + h - 0.01, 12 + z0 + h, 2 * (ri + dr))])
    # rascador sobre la salida: solo pasa la moneda que va dentro de la cavidad
    arco = [_polar(9, a) for a in range(-55, 19, 3)] + [_polar(ri + 1, a) for a in range(18, -56, -3)]
    rascador = seccion(arco).extrude(8.0)
    m = (ext - inte) + (rascador ^ cil_z(0, 0, -1, 10, 2 * ri + 2))
    for a in (90, 210, 330):
        m -= hueco_clavija(*_polar(R_PEG_CONO, a))
    return m


def tolva_disco() -> Manifold:
    m = union([cil_z(0, 0, 0, DISCO_ESP, DISCO_D),
               cil_z(0, 0, DISCO_ESP - 0.1, DISCO_ESP + 6, 16),
               Manifold.cylinder(7, 8, 1.5).translate((0, 0, DISCO_ESP + 6))])
    for k in range(N_CAVIDADES):
        m -= cil_z(*_polar(CAVIDAD_R, 45 + 360 / N_CAVIDADES * k), -1, DISCO_ESP + 1, CAVIDAD_D)
    a = BYJ["planos"] / 2 + 0.15
    m -= cil_z(0, 0, -1, 30, BYJ["eje_d"] + 0.3) ^ caja(-a, a, -5, 5, -1, 30)
    return m


def tolva_base() -> Manifold:
    ears = [hull(cil_z(*_polar(R_PATA_TOLVA, a), 0, BASE_ESP, 13.0),
                 cil_z(*_polar(R_PATA_TOLVA - 8.0, a), 0, BASE_ESP, 13.0)) for a in (45, 135, 225, 315)]
    piezas = ears + [cil_z(0, 0, 0, BASE_ESP, BASE_D),
                     cil_z(0, 0, BASE_ESP - 0.5, Z_ANILLO, 2 * ANILLO_RE)
                     - cil_z(0, 0, 0, 20, DISCO_D + 2 * HOLGURA)]
    huecos = [cil_z(CAVIDAD_R, 0, -11, BASE_ESP + 1, CAVIDAD_D + 1)]
    for a in (45, 135, 225, 315):                 # clavija de la pata de la tolva
        huecos.append(hueco_clavija(*_polar(R_PATA_TOLVA, a)))
    huecos.append(cil_z(0, 0, -1, BASE_ESP + 1, BYJ["buje_d"] + 0.4))
    piezas += [clavija(*_polar(R_PEG_CONO, a), z0=Z_ANILLO) for a in (90, 210, 330)]
    # bridas de nailon que abrazan el motor (ranuras de 4,2 x 1,6)
    for sx in (-BYJ["eje_off"] - 7.5, -BYJ["eje_off"] + 7.5):
        for sy in (1, -1):
            huecos.append(caja(sx - 2.1, sx + 2.1, sy * 16.5 - 0.8, sy * 16.5 + 0.8, -1, BASE_ESP + 1))
    return union(piezas) - union(huecos)


# =====================================================================
# Piezas y colocación en el ensamble
# =====================================================================
@dataclass
class Pieza:
    nombre: str
    geom: Manifold
    cant: int
    nota: str
    pose: Callable[[Manifold], Manifold]       # del marco de la pieza al ensamble
    giros: list = field(default_factory=lambda: [(0, 0)])
    grupo: str = ""


GIROS_EJES = [(rx, ry) for rx in (0, 90, 180, 270) for ry in (0, 90, 180, 270)]


def construir_piezas():
    d = disposicion()
    r_all = d.ranuras
    r500 = r_all[RANURA_500]
    zoff = H_MIN_RIEL + d.patas[-1] * S22      # altura del plano inferior del riel en x = 0

    def p_mundo(x, y, z):
        return np.array([x * C22 + z * S22, y, -x * S22 + z * C22 + zoff])

    def pose_riel(m):
        return rot_y(m, INCLINACION).translate((0, 0, zoff))

    def pose_ducto(r):
        c = p_mundo(r.xc, r.yc, 0)
        return lambda m: m.translate(tuple(c))

    largos = {}
    for r in r_all:
        cz = p_mundo(r.xc, r.yc, 0)[2]
        largos[r.i] = cz - (Z_BOCA + 6.0)
    extra_d6 = largos[RANURA_500] - (T_PIV + 26.0 + T_COL)
    tubos = {i: largos[i] + Z_TUBO for i in largos}      # corte del tubo PVC de 1": del collar a 6 mm sobre el vaso
    piezas: list[Pieza] = []
    riel_a = riel_modulo(d, 0, d.la, r_all[:4])
    riel_b = riel_modulo(d, d.la, d.fin_b, r_all[4:], final=True)
    piezas.append(Pieza("R01_riel_modulo_A", riel_a, 1, "entrada + ranuras 1-4", pose_riel, grupo="riel"))
    piezas.append(Pieza("R02_riel_modulo_B", riel_b, 1, "ranuras 5-7 + extremo abierto", pose_riel, grupo="riel"))
    piezas.append(Pieza("R04_llave_union", llave(), 3, "mariposa bajo la junta A-B, entra desde abajo",
                        lambda m: pose_riel(m.translate((d.la, 0, 0))), giros=[(0, 0), (180, 0)], grupo="riel"))
    for k, xp in enumerate(d.patas):
        h = zoff - xp * S22
        for lado, nom in ((-1, "izq"), (1, "der")):
            y = -Y_PATA if lado < 0 else B + Y_PATA
            piezas.append(Pieza(f"R03_pata{k + 1}_{nom}", pata(h, lado), 1,
                                f"altura {h:.0f} mm; pie atado con brida",
                                (lambda m, xp=xp, y=y: m.translate((xp * C22, y, 0))), grupo="pata"))
    for r in r_all:
        if r.i == RANURA_500:
            continue
        piezas.append(Pieza(f"D{r.i + 1}_adaptador_{r.clave}", adaptador(r), 1,
                            f"ranura {r.ancho:.1f} mm, IR 5 mm; tubo PVC 1\" de {tubos[r.i]:.0f} mm",
                            pose_ducto(r), grupo="ducto"))
    piezas.append(Pieza("D6_bifurcador_500", d6(r500, extra_d6), 1, "plato basculante; servo y IR a presión; PLA negro",
                        pose_ducto(r500), grupo="d6"))
    # plato: se arma con el eje del servo a lo largo de Y, en (0, y, -T_PIV) de D6
    piezas.append(Pieza("B02_plato_desvio", plato(r500), 1, "buje de estriado SG90 a presión",
                        lambda m: pose_ducto(r500)(m.translate((0, 0, -T_PIV))), giros=GIROS_EJES, grupo="d6"))
    piezas.append(Pieza("B03_puente_sensor", puente(), 1, "TCS34725 a presión, a horcajadas sobre las paredes",
                        lambda m: pose_riel(m.translate((d.x_sensor, 0, Z_PUENTE))), giros=GIROS_EJES, grupo="d6"))
    piezas.append(Pieza("T01_tolva_cono_40", tolva_cono(), 1, "semiángulo 40°, boca Ø130; se imprime boca abajo",
                        None, giros=GIROS_EJES, grupo="tolva"))
    piezas.append(Pieza("T02_disco_dosificador", tolva_disco(), 1, "28BYJ-48, eje a presión", None, grupo="tolva"))
    piezas.append(Pieza("T03_base_tolva", tolva_base(), 1, "motor con 2 bridas de nailon", None, grupo="tolva"))
    # tolva y patas de la tolva: posición en el ensamble
    ex, ey, ez, _ = np.append(p_mundo(ENTRADA / 2, 12.0, ESP_BASE), 1)
    base_z = ez + HOLGURA_TOLVA
    centro = np.array([ex - CAVIDAD_R, ey, 0.0])
    z_rel = {"T01_tolva_cono_40": Z_ANILLO, "T02_disco_dosificador": Z_DISCO, "T03_base_tolva": 0.0}
    for p in piezas:
        if p.grupo == "tolva":
            p.pose = (lambda m, dz=z_rel[p.nombre]: m.translate((centro[0], centro[1], base_z + dz)))
    h_pata_t = base_z
    piezas.append(Pieza("T04_pata_tolva", pata_tolva(h_pata_t), 4, f"altura {h_pata_t:.0f} mm",
                        None, grupo="pata_tolva"))
    base = base_pvc(d, p_mundo, largos)
    piezas.append(Pieza("P01_base_extremo", base_extremo(base["sep"]), 2,
                        f"base ABS de un extremo: 2 patas PVC 3/4 separadas {base['sep']:.0f} mm", None, grupo="base"))
    return d, piezas, dict(base=base, zoff=zoff, base_z=base_z, centro=centro, r500=r500, p_mundo=p_mundo, largos=largos, tubos=tubos, extra_d6=extra_d6)


# =====================================================================
# Base: dos bases impresas (ABS) bajo las patas; el resto es tubo y tees de PVC de 3/4"
# =====================================================================
def zocalo_pvc():
    """Placa cuadrada con un alojamiento vertical (el tubo entra PROF_PVC mm). Se imprime con la placa en la cama."""
    r_b = BORE_R + PARED_PVC
    boss = cil_z(0, 0, 0, PLACA_E + 34.0, 2 * r_b)
    placa = caja(-PLACA / 2, PLACA / 2, -PLACA / 2, PLACA / 2, 0, PLACA_E)
    hueco = cil_z(0, 0, PLACA_E + 2.0, PLACA_E + 36.0, 2 * BORE_R)
    return union([placa, boss]), hueco


def base_extremo(sep):
    """Una base de extremo: dos zócalos unidos por una viga plana; ata las dos patas de ese lado."""
    placa, hueco = zocalo_pvc()
    piezas = [placa, placa.translate((0, sep, 0)),
              caja(-12.0, 12.0, 0, sep, 0, PLACA_E + 2.0)]
    huecos = [hueco, hueco.translate((0, sep, 0))]
    for yy in (0, sep):
        for sx in (1, -1):
            for sy in (1, -1):
                huecos.append(caja(sx * 17 - 2, sx * 17 + 2, yy + sy * 17 - 2, yy + sy * 17 + 2, -1, PLACA_E + 1))
    return union(piezas) - union(huecos)


def base_pvc(d, p_mundo, largos):
    """Posiciones y cortes de la base. Devuelve un diccionario."""
    sal_x = [p_mundo(r.xc, r.yc, 0)[0] for r in d.ranuras]
    x_ini, x_fin = min(sal_x) - R_COLLAR - 3.0, max(sal_x) + R_COLLAR + 3.0   # tramo donde bajan los ductos
    xl, xr = -68.0, x_fin + PLACA / 2 + 3.0 + 40.0                   # 40 mm extra a la derecha para el motor de la banda
    yf = -60.0
    yb = yf + SEP_BASE
    r_b = BORE_R + PARED_PVC
    z_tee = -LAMINA_E - 40.0
    z_pie = Z_PISO + PLACA_E + 2.0                                   # fondo del alojamiento: ahí asienta el tubo
    return dict(xl=xl, xr=xr, yf=yf, yb=yb, sep=SEP_BASE, x_ranura=(x_ini, x_fin), y_ranura=(-12.0, 36.0),
                lamina=(xl - 24.0, xr + 24.0, yf - 24.0, yb + 24.0),
                z_tee=z_tee, z_pie=z_pie,
                l_pata=(z_tee - F_ACC) - z_pie,                      # tubo largo, del zócalo a la tee
                l_tope=-LAMINA_E - (z_tee + F_ACC),                  # tubo corto sobre la tee: sostiene la lámina
                l_x=(xr - xl) - 2 * F_ACC)                           # larguero entre las dos tees (delantero y trasero)


# =====================================================================
# Orientación de impresión y verificación de voladizos
# =====================================================================
def voladizo(m, ang=45.0):
    """Área (mm2) de caras que miran hacia abajo más allá de `ang` desde la vertical, sin la cama."""
    me = m.to_mesh()
    v = np.asarray(me.vert_properties, float)[:, :3]
    tr = v[np.asarray(me.tri_verts, int)]
    n = np.cross(tr[:, 1] - tr[:, 0], tr[:, 2] - tr[:, 0])
    area = np.linalg.norm(n, axis=1) / 2
    nz = n[:, 2] / np.maximum(2 * area, 1e-12)
    cama = tr[:, :, 2].max(1) < tr[:, :, 2].min() + 0.05
    malo = (nz < -math.sin(math.radians(ang))) & ~cama
    return float(area[malo].sum()), float(area[cama].sum())


def voladizo_capas(m, paso=0.5, ang=45.0, puente=10.0):
    """Analiza por capas. Devuelve (mm2 de voladizo, mm2 que no se puede puentear, z del primero).
    Una zona en voladizo se puentea si su ancho es menor que `puente` mm."""
    _, _, _, _, _, zmax = m.bounding_box()
    avance = paso * math.tan(math.radians(ang))
    previa = None
    total = dura = 0.0
    z_malo = None
    for z in np.arange(paso * 0.5, zmax, paso):
        cs = m.slice(float(z))
        if previa is not None and not cs.is_empty():
            soporte = previa.offset(avance, JoinType.Round, 2.0, 24) if not previa.is_empty() else previa
            falta = cs - soporte if not previa.is_empty() else cs
            a = falta.area()
            if a > 0.2:
                total += a
                nucleo = falta.offset(-puente / 2, JoinType.Round, 2.0, 24).area()
                if nucleo > 0.0 and z > 0.9:
                    dura += a
                    z_malo = z if z_malo is None else z_malo
        previa = cs
    return total, dura, z_malo


def orientar(m, giros):
    """Prueba los giros dados y deja el de menos voladizo (a igualdad, más apoyo en la cama)."""
    mejor = None
    for rx, ry in giros:
        c = a_cama(m.rotate((rx, ry, 0)))
        x0, y0, z0, x1, y1, z1 = c.bounding_box()
        if max(x1 - x0, y1 - y0) > CAMA[0] - 2 or z1 > CAMA[2]:
            continue
        mal, apoyo = voladizo(c)
        clave = mal - 0.1 * apoyo
        if mejor is None or clave < mejor[0]:
            mejor = (clave, c, (rx, ry), mal)
    return mejor[1], mejor[2], mejor[3]


# =====================================================================
# Ensamble y comprobaciones
# =====================================================================
def partes_ensamble(piezas, ctx):
    """Lista (nombre, malla en el ensamble). Las piezas con cantidad se repiten donde corresponde."""
    d = ctx["d"] if "d" in ctx else None
    out = []
    for p in piezas:
        if p.nombre.startswith("R04"):
            for yy in Y_LLAVES:
                out.append((p.nombre, p.pose(p.geom.translate((0, yy, 0)))))
        elif p.nombre.startswith("R03"):
            out.append((p.nombre, p.pose(p.geom)))
        elif p.nombre.startswith("P01"):
            b = ctx["base"]
            for x in (b["xl"], b["xr"]):
                out.append((p.nombre, p.geom.translate((x, b["yf"], Z_PISO))))
        elif p.nombre == "T04_pata_tolva":
            for a in (45, 135, 225, 315):
                x, y = _polar(R_PATA_TOLVA, a)
                out.append((p.nombre, p.geom.translate((ctx["centro"][0] + x, ctx["centro"][1] + y, 0))))
        else:
            out.append((p.nombre, p.pose(p.geom)))
    return out


ENCAJES = {("B03_puente_sensor", "R01_riel_modulo_A"), ("B03_puente_sensor", "R02_riel_modulo_B")}


def interferencias(partes, tol=0.5):
    malas = []
    for i in range(len(partes)):
        bi = partes[i][1].bounding_box()
        for j in range(i + 1, len(partes)):
            bj = partes[j][1].bounding_box()
            if any(bi[k] > bj[k + 3] or bj[k] > bi[k + 3] for k in range(3)):
                continue
            v = (partes[i][1] ^ partes[j][1]).volume()
            if v > (6.0 if tuple(sorted((partes[i][0], partes[j][0]))) in ENCAJES else tol):
                malas.append((partes[i][0], partes[j][0], v))
    return malas


def servo_sg90(y_orejas, z_eje):
    """Modelo del SG90 en D6: eje a lo largo de +Y, plano de las orejas en y = y_orejas, cuerpo hacia arriba."""
    sg = SG90
    zb, zt = z_eje - sg["eje_off"], z_eje - sg["eje_off"] + sg["largo"]
    cuerpo = union([caja(-sg["ancho"] / 2, sg["ancho"] / 2, y_orejas - 16.2, y_orejas + sg["caja_sobre_oreja"], zb, zt),
                    caja(-sg["ancho"] / 2, sg["ancho"] / 2, y_orejas - 2.5, y_orejas, zb - 4.7, zt + 4.7)])
    eje = union([cil_eje((0, y_orejas + sg["caja_sobre_oreja"] - 0.01, z_eje), (0, 1, 0), sg["buje"], 5.8),
                 cil_eje((0, y_orejas + sg["caja_sobre_oreja"] + sg["buje"] - 0.01, z_eje), (0, 1, 0),
                         sg["estriado"], sg["estriado_d"] / 2 - 0.1)])
    return cuerpo + eje


def moneda(d, esp, centro, normal):
    return cil_eje(np.asarray(centro, float) - _unit(normal) * esp / 2, normal, esp, d / 2)


def verificar_d6(ctx):
    """Plato en sus dos extremos, encaje del servo y trayecto de la moneda por D6."""
    r = ctx["r500"]
    g = geom_d6(r, ctx["extra_d6"])
    cuerpo = d6(r, ctx["extra_d6"])
    pl = plato(r)
    z_p = -T_PIV
    avisos = []
    y_o = -(g["hy"] + E_DUCTO + PAD_SERVO)
    srv = servo_sg90(y_o, z_p)
    v = (cuerpo ^ srv).volume()
    if v > 2.0:
        avisos.append(f"el servo interfiere con D6: {v:.1f} mm3")
    if (pl.translate((0, 0, z_p)) ^ srv).volume() > 0.5:
        avisos.append("el servo choca con el plato")
    dm, em = r.dmax, 2.2
    for signo in (1, -1):
        a = signo * INCL_PLATO                      # rot_y(+a) baja el lado +x
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        plato_i = rot_y(pl, a).translate((0, 0, z_p))
        v = (cuerpo ^ plato_i).volume()
        if v > 0.5:
            avisos.append(f"el plato inclinado hacia {'+x' if signo > 0 else '-x'} choca con D6: {v:.1f} mm3")
        n = np.array([sa, 0.0, ca])                 # normal de la cara superior
        t = signo * np.array([ca, 0.0, -sa])        # hacia abajo del plato
        base = np.array([0.0, 0.0, z_p])
        choque = 0.0
        for z in np.linspace(-6.0, z_p + PLATO_H / 2 + em + 1, 12):          # caída por el tubo
            choque += (cuerpo ^ moneda(dm, em, (0, 0, z), (0, 0, 1))).volume()
        sale = None
        for s_ in np.linspace(0, PLATO_L / 2 + 1.0, 9):                       # resbalando por el plato
            c = base + n * (PLATO_H / 2 + em / 2 + 0.05) + t * s_
            choque += (cuerpo ^ moneda(dm, em, c, n)).volume()
            sale = c
        xc_col = signo * (COL_INT0 + COL_INT1) / 2
        for k, z in enumerate(np.linspace(sale[2], -g["t_bot"] - 2, 10)):     # cae a la columna
            x = sale[0] + (xc_col - sale[0]) * min(1.0, k / 4)
            choque += (cuerpo ^ moneda(dm, em, (x, 0, z), (0, 0, 1))).volume()
        if choque > 1.0:
            avisos.append(f"la moneda choca con D6 yendo hacia {'+x' if signo > 0 else '-x'}: {choque:.1f} mm3")
    return avisos


def verificar_pasos_ductos(piezas, largos):
    avisos = []
    for p in piezas:
        if p.grupo != "ducto":
            continue
        cuerpo = p.geom
        r = next(rr for rr in disposicion().ranuras if f"D{rr.i + 1}_" in p.nombre)
        choque = 0.0
        for z in np.linspace(-1.0, -largos[r.i] + 1.0, 30):
            choque += (cuerpo ^ moneda(r.dmax, 2.2, (0, 0, z), (0, 0, 1))).volume()
        if choque > 0.5:
            avisos.append(f"{p.nombre}: la moneda de {r.dmax} choca con el tubo ({choque:.1f} mm3)")
    return avisos


def tabla_alineacion(d, ctx):
    """Salidas inferiores de los ductos en el mundo (X, Y): deben caer sobre la línea de vasos."""
    p_mundo = ctx["p_mundo"]
    filas = []
    for r in d.ranuras:
        c = p_mundo(r.xc, r.yc, 0)
        if r.i == RANURA_500:
            g = geom_d6(r, ctx["extra_d6"])
            for s in (-1, 1):
                filas.append((f"D6{'b' if s > 0 else 'a'}", c[0] + s * (COL_INT0 + COL_INT1) / 2, c[1],
                              c[2] - g["t_bot"]))
        else:
            filas.append((f"D{r.i + 1}", c[0], c[1], c[2] - ctx["largos"][r.i]))
    return filas


def construir(ensamble=False, rapido=False):
    for a in validar_ranuras():
        print("AVISO:", a)
    d, piezas, ctx = construir_piezas()
    ctx["d"] = d
    SALIDA.mkdir(parents=True, exist_ok=True)
    for viejo in SALIDA.glob("*.stl"):
        viejo.unlink()
    filas, fallos = [], []
    total_cm3 = 0.0
    for p in piezas:
        m, giro, mal = orientar(p.geom, p.giros)
        if m.is_empty() or m.status().name != "NoError":
            raise RuntimeError(f"{p.nombre}: malla inválida ({m.status()})")
        if len(m.decompose()) > 1:
            raise RuntimeError(f"{p.nombre}: la pieza queda en {len(m.decompose())} trozos sueltos")
        x0, y0, z0, x1, y1, z1 = m.bounding_box()
        dims = (x1 - x0, y1 - y0, z1 - z0)
        if max(dims[:2]) > CAMA[0] or z1 > CAMA[2]:
            raise ValueError(f"{p.nombre} {dims} no cabe en la cama {CAMA}")
        capas = voladizo_capas(m) if not rapido else (0, 0, None)
        escribir_stl(m, SALIDA / f"{p.nombre}.stl", p.nombre)
        vol = m.volume() / 1000
        total_cm3 += vol * p.cant
        filas.append([p.nombre, p.cant, *(f"{v:.1f}" for v in dims), f"{vol:.1f}", f"{capas[0]:.0f}",
                      f"{capas[1]:.0f}", p.nota])
        marca = "" if capas[1] < 1 else f"  <-- NO PUENTEABLE desde z={capas[2]:.1f}"
        if marca:
            fallos.append(p.nombre)
        print(f"{p.nombre:28s} x{p.cant}  {dims[0]:6.1f} x {dims[1]:6.1f} x {dims[2]:6.1f} mm  "
              f"{vol:6.1f} cm3  voladizo {capas[0]:6.0f} (duro {capas[1]:5.0f}) mm2  giro {giro}{marca}")
    print(f"TOTAL macizo: {total_cm3:.0f} cm3 (con relleno 15 %: unos {total_cm3 * 0.45 * 1.24:.0f} g de PLA)")
    with open(SALIDA / "piezas_clasificador.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pieza", "cantidad", "x_mm", "y_mm", "z_mm", "volumen_cm3", "voladizo_mm2", "no_puenteable_mm2", "nota"])
        w.writerows(filas)
    if fallos:
        print("PIEZAS CON VOLADIZO NO PUENTEABLE:", ", ".join(fallos))
    for a in verificar_pasos_ductos(piezas, ctx["largos"]) + verificar_d6(ctx):
        print("AVISO D6/ductos:", a)
    print("salidas (X, Y, Z mundo):", ", ".join(f"{n} {x:.1f}/{y:.1f}/{z:.0f}" for n, x, y, z in tabla_alineacion(d, ctx)))
    if ensamble:
        partes = partes_ensamble(piezas, ctx)
        malas = interferencias(partes)
        for a, b, v in malas:
            print(f"INTERFERENCIA {a} x {b}: {v:.1f} mm3")
        print("sin interferencias" if not malas else "HAY interferencias")
        carpeta = SALIDA / "ensamble"
        carpeta.mkdir(exist_ok=True)
        escribir_stl(union([m for _, m in partes]), carpeta / "ensamble_referencia.stl", "ensamble")
    return d, piezas, ctx


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ensamble", action="store_true", help="comprueba interferencias y exporta el ensamble")
    ap.add_argument("--rapido", action="store_true", help="omite el análisis capa por capa")
    a = ap.parse_args()
    construir(a.ensamble, a.rapido)
