"""La cinemática debe coincidir con los números de la memoria de cálculo."""
import math
import random

import pytest

from brazo.config import (CABECEO_AGARRE, D1, HOME, L1, L2, L3, LIMITES,
                          YAW_ENTRADA, YAW_RACK, Z_AGARRE, Z_SEGURA)
from brazo.kinematics import (FueraDeAlcance, FueraDeLimite, det_jacobiano, fk,
                              ik, pose_puesto, t05)


def test_home_da_la_pose_documentada():
    x, y, z, phi = fk(HOME)
    assert (round(x, 6), round(y, 6), round(z, 6), round(phi, 6)) == (15.0, 0.0, 19.0, -90.0)


def test_dh_coincide_con_la_forma_cerrada():
    rng = random.Random(7)
    peor = 0.0
    for _ in range(500):
        q = [rng.uniform(lo, hi) for lo, hi in LIMITES]
        T = t05(q)
        x, y, z, _ = fk(q)
        peor = max(peor, math.dist([T[0][3], T[1][3], T[2][3]], [x, y, z]))
    assert peor < 1e-9


def test_ejemplo_resuelto_del_puesto_r1():
    q = ik(*pose_puesto(24.0, Z_AGARRE))
    esperado = [24.0, 49.02, -82.53, -56.50, 0.0]
    for obtenido, ref in zip(q, esperado):
        assert obtenido == pytest.approx(ref, abs=0.01)


def test_ida_y_vuelta_en_los_diez_puestos():
    for yaw in YAW_ENTRADA + YAW_RACK:
        for z in (Z_AGARRE, Z_SEGURA):
            objetivo = pose_puesto(yaw, z)
            q = ik(*objetivo)
            x, y, zz, phi = fk(q)
            assert math.dist([x, y, zz], objetivo) < 1e-9
            assert phi == pytest.approx(CABECEO_AGARRE, abs=1e-9)


def test_la_postura_es_la_misma_en_todos_los_puestos():
    """Todos los puestos están al mismo radio: solo cambia theta1."""
    poses = [ik(*pose_puesto(yaw, Z_AGARRE)) for yaw in YAW_ENTRADA + YAW_RACK]
    for q in poses[1:]:
        assert q[1:] == pytest.approx(poses[0][1:], abs=1e-9)


def test_respeta_los_limites_articulares():
    for q in [ik(*pose_puesto(yaw, z)) for yaw in YAW_ENTRADA + YAW_RACK
              for z in (Z_AGARRE, Z_SEGURA)]:
        for valor, (lo, hi) in zip(q, LIMITES):
            assert lo - 1e-9 <= valor <= hi + 1e-9


def test_fuera_de_alcance():
    with pytest.raises(FueraDeAlcance):
        ik(40.0, 30.0, Z_AGARRE)


def test_fuera_de_limite():
    with pytest.raises(FueraDeLimite):
        ik(2.0, 0.0, 2.0)          # demasiado cerca y bajo: el codo se pasa


def test_lejos_de_la_singularidad():
    q = ik(*pose_puesto(24.0, Z_AGARRE))
    assert abs(det_jacobiano(q)) > 200.0        # det = L1*L2*sen(theta3)
    assert abs(det_jacobiano([0, 0, 0, 0, 0])) < 1e-9   # brazo estirado
