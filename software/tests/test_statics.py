"""Los pares tienen que coincidir con la tabla de la memoria de cálculo."""
import math

import pytest

from brazo.config import HOME, Z_AGARRE, Z_SEGURA
from brazo.kinematics import ik, pose_puesto
from brazo.statics import (SERVOS, carga_vaso_kg, factores_seguridad,
                           momento_de_vuelco, pares)

AGARRE = ik(*pose_puesto(24.0, Z_AGARRE))
TRASLADO = ik(*pose_puesto(24.0, Z_SEGURA))
EXTENDIDO = [0.0, 0.0, 0.0, 0.0, 0.0]


def test_carga_de_diseno():
    assert carga_vaso_kg() == pytest.approx(0.416, abs=1e-6)


def test_pares_en_las_poses_documentadas():
    assert pares(AGARRE).hombro == pytest.approx(13.60, abs=0.05)
    assert pares(AGARRE).codo == pytest.approx(6.82, abs=0.05)
    assert pares(TRASLADO).hombro == pytest.approx(13.35, abs=0.05)
    assert pares(EXTENDIDO).hombro == pytest.approx(22.07, abs=0.05)
    assert pares(EXTENDIDO).codo == pytest.approx(11.74, abs=0.05)


def test_la_muneca_no_carga_con_la_pinza_vertical():
    assert pares(AGARRE).muneca == pytest.approx(0.0, abs=1e-6)
    assert pares(EXTENDIDO).muneca == pytest.approx(3.56, abs=0.05)


def test_factores_de_seguridad_en_operacion():
    fs = factores_seguridad(AGARRE)
    assert fs["J2"] > 2.0          # DS3235MG
    assert fs["J3"] > 2.0          # DS3218MG
    assert fs["pinza"] > 1.5       # MG90S con almohadillas de TPU


def test_el_caso_extendido_es_el_critico():
    assert factores_seguridad(EXTENDIDO)["J2"] < factores_seguridad(AGARRE)["J2"]
    assert factores_seguridad(EXTENDIDO)["J2"] > 1.4


def test_momento_de_vuelco_para_el_anclaje():
    assert momento_de_vuelco(AGARRE) == pytest.approx(1.33, abs=0.02)
    assert momento_de_vuelco(EXTENDIDO) == pytest.approx(2.16, abs=0.03)


def test_los_servos_declarados_cubren_todas_las_juntas():
    assert set(SERVOS) == {"J1", "J2", "J3", "J4", "J5", "pinza"}
