"""Perfil quíntico, duración de tramos y ciclo de recoger y colocar."""
import math

import pytest

from brazo.config import HOME, PINZA_ABIERTA_MM, Puesto, Z_AGARRE, Z_SEGURA
from brazo.kinematics import fk, ik, pose_puesto
from brazo.trajectory import (ciclo_pick_place, duracion_total, muestrear,
                              perfil, picos, quintico)


def test_extremos_del_perfil():
    assert quintico(0) == 0
    assert quintico(1) == pytest.approx(1)
    for t in (0.0, 1.0):
        _, vel, acc = perfil(100.0, 2.0, t * 2.0)
        assert vel == pytest.approx(0, abs=1e-9)
        assert acc == pytest.approx(0, abs=1e-9)


def test_picos_teoricos():
    vmax, amax = picos(172.0, 2.2933333)
    assert vmax == pytest.approx(140.6, abs=0.1)
    assert amax == pytest.approx(188.8, abs=0.2)


def test_el_perfil_es_monotono():
    prev = -1.0
    for k in range(101):
        s = quintico(k / 100)
        assert s >= prev - 1e-12
        prev = s


def test_ciclo_completo_tiene_ocho_tramos():
    tramos = ciclo_pick_place(Puesto("entrada", 0), Puesto("rack", 4), HOME)
    assert len(tramos) == 8
    assert 4.0 < duracion_total(tramos) < 12.0


def test_las_poses_muestreadas_son_alcanzables():
    tramos = ciclo_pick_place(Puesto("entrada", 2), Puesto("rack", 1), HOME)
    alturas = []
    for _, q, pinza in muestrear(tramos[1:], 0.05):     # sin el tramo de entrada
        x, y, z, phi = fk(q)
        alturas.append(z)
        assert 0 <= pinza <= 70
        assert phi == pytest.approx(-90.0, abs=1e-6)
    assert min(alturas) == pytest.approx(Z_AGARRE, abs=0.3)
    assert max(alturas) == pytest.approx(Z_SEGURA, abs=0.1)


def test_el_traslado_pasa_por_encima_de_los_vasos():
    """Con el vaso sujeto, su base viaja a 10,8 cm: 1,9 cm sobre los demás."""
    tramos = ciclo_pick_place(Puesto("entrada", 0), Puesto("rack", 0), HOME)
    traslado = tramos[4]
    _, _, z, _ = fk(traslado.evaluar(traslado.duracion / 2)[0])
    assert z - 6.2 > 8.9
