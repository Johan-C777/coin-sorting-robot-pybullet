"""Las tramas tienen que ser idénticas a las de la simulación y el firmware."""
import pytest

from brazo.config import HOME, PINZA_ABIERTA_MM, Z_AGARRE
from brazo.cups import lote_demo
from brazo.kinematics import ik, pose_puesto
from brazo.protocol import (angulos_servo, estado_json, parsear_trama, pwm_us,
                            trama)


def test_trama_de_reposo():
    assert trama(HOME, PINZA_ABIERTA_MM) == "S:90,90,90,30,90,85"


def test_trama_del_ejemplo_r1():
    q = ik(*pose_puesto(24.0, Z_AGARRE))
    assert trama(q, PINZA_ABIERTA_MM) == "S:114,49,83,64,90,85"


def test_anchos_de_pulso():
    assert pwm_us(0) == 500
    assert pwm_us(90) == 1500
    assert pwm_us(180) == 2500
    assert pwm_us(114) == 1767


def test_ida_y_vuelta_de_la_trama():
    q = ik(*pose_puesto(-55.0, Z_AGARRE))
    assert parsear_trama(trama(q, 66)) == angulos_servo(q, 66)


def test_trama_invalida():
    with pytest.raises(ValueError):
        parsear_trama("X:1,2,3")
    with pytest.raises(ValueError):
        parsear_trama("S:1,2,3")


def test_estado_para_el_dashboard():
    est = estado_json(HOME, PINZA_ABIERTA_MM, lote_demo())
    assert est["estado"] == "listo"
    assert len(est["entrada"]) == 5
    assert est["totales"]["valor"] == 21650
    assert est["servos"] == [90, 90, 90, 30, 90, 85]
