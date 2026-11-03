"""Piezas corregidas tras la primera ronda de pruebas físicas (2026-11-03). No toca los STL de generar_v5.py.

  H02c  Disco de 6 bolsillos Ø33 (antes 8 de Ø29), con entrada achaflanada, 6 radios de apoyo
        de 0,4 mm en la cara trasera y un bolsillo en la posición de salida (90°). Mismo eje,
        mismo grosor total (2,4) y misma distancia al plato: sirve con H01 y con H03a/b/c.
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


def disco_c():
    E, R, RP = g.DISCO_E, 50.0, g.R_PASO       # radio 50 (H02 era 51): holgura con el aro de H01
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
