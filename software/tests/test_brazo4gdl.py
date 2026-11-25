"""Pruebas de la cinemática del brazo construido (4 GDL, doble paralelogramo)."""
import math
import random

import pytest

from brazo import brazo4gdl as b


def test_pasos_por_grado():
    assert b.PASOS_POR_GRADO == pytest.approx(142.222, abs=1e-3)


def test_pose_cero_es_la_del_cad():
    # brazo vertical, antebrazo y garra horizontales: la punta queda a L2 + L_PITCH + L3 al frente
    p = b.directa(b.Juntas(0, 90, 0, 0))
    assert p.x == pytest.approx(b.L2 + b.L_PITCH + b.L3)
    assert p.z == pytest.approx(b.Z_HOMBRO + b.L1)


def test_ida_y_vuelta():
    rnd = random.Random(7)
    probadas = 0
    while probadas < 300:
        q = b.Juntas(rnd.uniform(*b.LIM_J1), rnd.uniform(*b.LIM_J2),
                     rnd.uniform(*b.LIM_J3), rnd.uniform(*b.LIM_CABECEO))
        if b.fuera_de_limites(q):
            continue
        q2 = b.inversa(b.directa(q))
        for a, c in zip((q.j1, q.j2, q.j3, q.cabeceo), (q2.j1, q2.j2, q2.j3, q2.cabeceo)):
            assert a == pytest.approx(c, abs=1e-6)
        probadas += 1


def test_agarre_desde_arriba_en_el_anillo():
    lo, hi = b.alcance_horizontal(100, -90)
    assert lo < 200 and hi > 280


def test_fuera_de_alcance():
    with pytest.raises(ValueError):
        b.inversa(b.Pose(600, 0, 100, 0))


def test_gcode():
    lineas = b.gcode_secuencia([b.Pose(250, 0, 100, -90)])
    assert lineas[0] == "G90" and lineas[-1] == "M400"
    assert lineas[1].startswith("G1 Y0.00 Z") and " A" in lineas[1]
