"""Ajustes de la tolva tras las primeras pruebas (2026-11-03). No toca los STL de generar_v5.py.

  H02b  Disco v2: bolsillos Ø30 con entrada achaflanada (antes Ø29). Mismo grosor (2,4) y mismo
        eje: sirve con H01 y con los rascadores H03a/b/c.
  H04   Cuña de apoyo: rellena el hueco entre la espalda de H01 y la pista L01 (entre la zona que
        apoya en K01 y las almohadillas) para que H01 no se incline. Se pega con cianoacrilato a la
        espalda de H01 y descansa en L01 con 0,3 mm de holgura.
Salida: hardware/etapa1-clasificador/stl/ajustes/
"""
import math, sys
import numpy as np
from manifold3d import Manifold
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import generar_v5 as g

SAL = g.SALIDA / "stl" / "ajustes"
POCKET_V2, CHAFLAN = 30.0, 0.5
W0, W1, PROF = -6.0, 34.0, 14.0      # ventana de la cuña (marco del disco): w y profundidad tras la espalda


def disco_v2():
    E, R = g.DISCO_E, g.DISCO_R
    m = Manifold.cylinder(E, R)
    for i in range(g.N_BOLS):
        a = 2 * math.pi * i / g.N_BOLS
        c = (g.R_PASO * math.cos(a), g.R_PASO * math.sin(a))
        r = POCKET_V2 / 2
        bolsa = Manifold.cylinder(E + 2, r).translate((c[0], c[1], -1))
        cono = Manifold.cylinder(CHAFLAN + 0.01, r, r + CHAFLAN + 0.01).translate((c[0], c[1], E - CHAFLAN))
        canal = g.caja(g.R_PASO, R + 5, -r, r, -1, E + 1)
        canal = canal.transform(np.array([[math.cos(a), -math.sin(a), 0, 0], [math.sin(a), math.cos(a), 0, 0], [0, 0, 1, 0]]))
        m -= bolsa + cono + canal
    m += Manifold.cylinder(6.0, 7.0).translate((0, 0, E))
    m += Manifold.cylinder(E, 12.0)
    h = g.HOLGURA
    eje = g.caja(-2.5 - h / 2, 2.5 + h / 2, -1.5 - h / 2, 1.5 + h / 2, -1, E + 5)
    eje = eje ^ Manifold.cylinder(E + 7, 2.5 + h / 2).translate((0, 0, -1))
    return g.marco_disco((m - eje).translate((0, 0, 0.05)))


def cuna():
    L = g.pista()
    d = 0.3
    ocupado = L
    for v in (g.SV, g.TV, g.NV):
        ocupado = ocupado + L.translate(tuple(d * v)) + L.translate(tuple(-d * v))
    K = g.soporte(g.X_CAB[0], -20, 50, 330, g.zona_tolva(), pines_z=(-10.0, 10.0, 38.0))
    bloque = g.marco_disco(g.caja(-g.ARO_R0, g.ARO_R0, W0, W1, -g.BASE_E - PROF, -g.BASE_E))
    motor = g.caja(-g.OREJAS / 2 - 1, g.OREJAS / 2 + 1, -g.MOTOR_OFF - 8, -g.MOTOR_OFF + 8, -g.BASE_E - 8, 1)
    motor += Manifold.cylinder(g.MOTOR_L + 5, g.MOTOR_D / 2 + 1.0).translate((0, -g.MOTOR_OFF, -g.BASE_E - g.MOTOR_L - 5))
    m = bloque - ocupado - K - g.marco_disco(motor)
    partes = [p for p in m.decompose() if p.volume() > 50]
    return partes


if __name__ == "__main__":
    SAL.mkdir(parents=True, exist_ok=True)
    m = g.a_cama(disco_v2(), [g.UD, g.WD, g.ND])
    print("H02b", g.verificar(m, "H02b"), round(m.volume() / 1000, 1), "cm3")
    g.escribir_stl(m, SAL / "H02b_disco_v2_bolsillo30.stl", "H02b")
    partes = cuna()
    print("cuna: partes", [round(p.volume() / 1000, 2) for p in partes])
    for i, p in enumerate(partes):
        R = np.array([g.UD, -g.WD, -g.ND])
        assert np.linalg.det(R) > 0
        q = g.a_cama(p, R)
        print("H04", i, [round(b - a, 1) for a, b in zip(q.bounding_box()[:3], q.bounding_box()[3:])], round(q.volume() / 1000, 2), "cm3", q.status().name)
        g.escribir_stl(q, SAL / f"H04_cuna_apoyo_{i + 1}.stl", "H04")
