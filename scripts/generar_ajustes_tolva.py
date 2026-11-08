"""Piezas corregidas tras la primera ronda de pruebas físicas (2026-11-03). No toca los STL de generar_v5.py.

  H02c  Disco de 6 bolsillos Ø33 (antes 8 de Ø29), con entrada achaflanada, 6 radios de apoyo
        de 0,4 mm en la cara trasera y un bolsillo en la posición de salida (90°). Mismo eje,
        mismo grosor total (2,4) y misma distancia al plato: sirve con H01 y con H03a/b/c.
  H02d Disco de 4 bolsillos Ø36 (misma geometría que H02c; bolsillo a 90°, radio de paso 42).
  H04  Tope trasero: bloque que rellena la cuña abierta entre la pista L01 y el aro de H01 por encima del
        hueco de salida (t = 44…58 mm sobre la repisa), por donde la moneda rebota y cae detrás de L01.
        Se pega con cianoacrilato sobre la cara de la placa de L01 (cara plana contra la placa).
  H03d  Rascador de 3,0 mm: más holgura para la $1.000 (2,7 mm de grosor) que el de 2,8.
Salida: hardware/etapa1-clasificador/stl/ajustes/
"""
import math, sys
import numpy as np
from manifold3d import Manifold
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import generar_v5 as g

SAL = g.SALIDA / "stl" / "ajustes"
N, POCKET, CHAFLAN = 6, 33.0, 0.6
RELIEVE, RADIO_W, CUBO_R = 0.4, 4.0, 13.0       # altura de los radios, semiancho, radio del apoyo central


def rot(a):
    return np.array([[math.cos(a), -math.sin(a), 0, 0], [math.sin(a), math.cos(a), 0, 0], [0, 0, 1, 0]])


def disco_c(N=N, POCKET=POCKET, R=50.0):
    E, RP = g.DISCO_E, g.R_PASO                # radio 50 (H02 era 51): holgura con el aro de H01
    r = POCKET / 2
    m = Manifold.cylinder(E - RELIEVE, R).translate((0, 0, RELIEVE))           # cuerpo, 0,4 sobre el plato
    m += Manifold.cylinder(RELIEVE + 0.01, CUBO_R)                              # apoyo central
    for i in range(N):                                                           # radios de apoyo en las paredes entre bolsillos
        a = 2 * math.pi * i / N
        m += g.caja(0, R - 1, -RADIO_W, RADIO_W, 0, RELIEVE + 0.01).transform(rot(a))
    for i in range(N):
        a = math.pi / 2 + 2 * math.pi * i / N                                    # un bolsillo en 90° (salida)
        c = (RP * math.cos(a), RP * math.sin(a))
        bolsa = Manifold.cylinder(E + 2, r).translate((c[0], c[1], -1))
        cono = Manifold.cylinder(CHAFLAN + 0.01, r, r + CHAFLAN + 0.01).translate((c[0], c[1], E - CHAFLAN))
        canal = g.caja(RP, R + 5, -r, r, -1, E + 1).transform(rot(a))
        m -= bolsa + cono + canal
    m += Manifold.cylinder(6.0, 7.0).translate((0, 0, E))                        # cubo hacia el frente
    m += Manifold.cylinder(E, 12.0)
    h = g.HOLGURA
    eje = g.caja(-2.5 - h / 2, 2.5 + h / 2, -1.5 - h / 2, 1.5 + h / 2, -1, E + 5)
    eje = eje ^ Manifold.cylinder(E + 7, 2.5 + h / 2).translate((0, 0, -1))
    return g.marco_disco((m - eje).translate((0, 0, 0.05)))


def inflar(m, d=0.3):
    r = m
    for v in (g.SV, g.TV, g.NV):
        r = r + m.translate(tuple(d * v)) + m.translate(tuple(-d * v))
    return r


S0, S1, T0, T1, NMAX = 2.0, 42.0, 44.0, 58.0, 14.0


def tope():
    caja = g.marco_pista(g.caja(S0, S1, T0, T1, 0.0, NMAX))
    m = caja - inflar(g.base_tolva()) - inflar(g.disco())
    return max(m.decompose(), key=lambda c: c.volume())


if __name__ == "__main__":
    SAL.mkdir(parents=True, exist_ok=True)
    d = disco_c()
    partes = d.decompose()
    H = g.base_tolva()
    print("cuerpos", len(partes), "| choque H01", round((d ^ H).volume(), 3),
          "| choque H03a/b/c", [round((d ^ g.rascador(x)).volume(), 3) for x in g.RASC_GAP])
    m = g.a_cama(d, [g.UD, g.WD, g.ND])
    print("H02c", [round(b - a, 1) for a, b in zip(m.bounding_box()[:3], m.bounding_box()[3:])], round(m.volume() / 1000, 1), "cm3", m.status().name)
    g.escribir_stl(m, SAL / "H02c_disco_6_bolsillos.stl", "H02c")
    d4 = disco_c(4, 36.0, 45.5)                         # H02d: 4 bolsillos Ø36 (la $1.000 no entraba en los de Ø33)
    print("H02d cuerpos", len(d4.decompose()), "| choque H01", round((d4 ^ H).volume(), 3),
          "| H03a/b/c/d", [round((d4 ^ g.rascador(x)).volume(), 3) for x in (*g.RASC_GAP, 3.0)])
    m4 = g.a_cama(d4, [g.UD, g.WD, g.ND])
    print("H02d", [round(b - a, 1) for a, b in zip(m4.bounding_box()[:3], m4.bounding_box()[3:])], round(m4.volume() / 1000, 1), "cm3", m4.status().name)
    g.escribir_stl(m4, SAL / "H02d_disco_4_bolsillos.stl", "H02d")
    t = tope()
    print("H04 tope: choques H01", round((t ^ g.base_tolva()).volume(), 3), "L01", round((t ^ g.pista()).volume(), 3),
          "H02", round((t ^ g.disco()).volume(), 3), "vol", round(t.volume() / 1000, 2), "cm3")
    R = np.array([g.SV, g.TV, g.NV])            # cara contra la placa (n = 0) sobre la cama: z = n
    q = g.a_cama(t, R)
    print("H04", [round(b - a, 1) for a, b in zip(q.bounding_box()[:3], q.bounding_box()[3:])], q.status().name, len(q.decompose()))
    g.escribir_stl(q, SAL / "H04_tope_trasero.stl", "H04")
    r = g.rascador_cama(3.0)
    g.verificar(r, "H03d")
    g.escribir_stl(r, SAL / "H03d_rascador_3mm0.stl", "H03d")
    print("H03d choque con H02c", round((g.rascador(3.0) ^ d).volume(), 3))
