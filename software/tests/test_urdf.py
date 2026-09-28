"""El URDF de PyBullet debe describir exactamente la misma cadena cinemática."""
import math
import random
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from brazo.config import LIMITES
from brazo.kinematics import fk

URDF = Path(__file__).resolve().parents[2] / "sim" / "pybullet" / "brazo_clasificador.urdf"
CADENA = [("j1_base", 0), ("j2_hombro", 1), ("j3_codo", 2),
          ("j4_cabeceo", 3), ("j5_giro", 4), ("tcp_fijo", None)]


def _rot(eje, ang):
    x, y, z = eje
    c, s = math.cos(ang), math.sin(ang)
    k = 1 - c
    return [[c + x * x * k, x * y * k - z * s, x * z * k + y * s],
            [y * x * k + z * s, c + y * y * k, y * z * k - x * s],
            [z * x * k - y * s, z * y * k + x * s, c + z * z * k]]


def _aplicar(R, p, v):
    return [sum(R[i][j] * v[j] for j in range(3)) + p[i] for i in range(3)]


def _componer(R1, p1, R2, p2):
    R = [[sum(R1[i][k] * R2[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return R, _aplicar(R1, p1, p2)


def urdf_fk(juntas, q_grados):
    """Posición del TCP recorriendo el árbol del URDF, en centímetros."""
    R = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    p = [0.0, 0.0, 0.0]
    for nombre, idx in CADENA:
        j = juntas[nombre]
        xyz = [float(v) for v in j.find("origin").get("xyz").split()]
        Rj = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        if j.get("type") == "revolute":
            eje = [float(v) for v in j.find("axis").get("xyz").split()]
            Rj = _rot(eje, math.radians(q_grados[idx]))
        R, p = _componer(R, p, Rj, xyz)
    return [v * 100 for v in p]


@pytest.fixture(scope="module")
def juntas():
    raiz = ET.parse(URDF).getroot()
    return {j.get("name"): j for j in raiz.findall("joint")}


def test_el_urdf_existe_y_tiene_las_seis_juntas_moviles(juntas):
    moviles = [n for n, j in juntas.items() if j.get("type") in ("revolute", "prismatic")]
    assert len(moviles) == 7          # 5 articulaciones + 2 dedos


def test_limites_iguales_a_los_del_controlador(juntas):
    for nombre, idx in CADENA[:5]:
        lim = juntas[nombre].find("limit")
        lo, hi = math.degrees(float(lim.get("lower"))), math.degrees(float(lim.get("upper")))
        assert lo == pytest.approx(LIMITES[idx][0], abs=0.01)
        assert hi == pytest.approx(LIMITES[idx][1], abs=0.01)


def test_la_cadena_del_urdf_reproduce_la_cinematica(juntas):
    rng = random.Random(11)
    peor = 0.0
    for _ in range(200):
        q = [rng.uniform(lo, hi) for lo, hi in LIMITES]
        peor = max(peor, math.dist(urdf_fk(juntas, q), fk(q)[:3]))
    assert peor < 1e-9
