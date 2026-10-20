"""Ruta de A a B: cuatro obstáculos con nivel de dificultad creciente."""
import math

import pytest

from brazo.kinematics import alcanzable, fk, ik
from brazo.obstaculos import (OBSTACULOS, R_ARCO, YAW_A, YAW_B, Z_TRANSITO,
                              fraccion_bloqueada, maniobra, puntos_vigilados, ruta)

POR_CODIGO = {o.codigo: o for o in OBSTACULOS}


def test_son_cuatro_y_estan_entre_el_punto_a_y_el_b():
    assert len(OBSTACULOS) == 4
    for o in OBSTACULOS:
        assert YAW_A < o.yaw < YAW_B[-1]


def test_el_nivel_sube_en_el_orden_en_que_se_encuentran():
    niveles = [t.obstaculo.nivel for t in ruta()]
    assert niveles == [1, 2, 3, 4]


def test_cada_obstaculo_fuerza_su_maniobra():
    assert maniobra(POR_CODIGO["O1"]).modo == "bajo"
    assert maniobra(POR_CODIGO["O2"]).modo == "rodeo"
    assert maniobra(POR_CODIGO["O3"]).modo == "espera"
    assert maniobra(POR_CODIGO["O4"]).modo == "bajo"


def test_cifras_de_las_maniobras():
    assert maniobra(POR_CODIGO["O1"]).z == pytest.approx(15.5, abs=0.05)
    assert maniobra(POR_CODIGO["O2"]).rho == pytest.approx(9.2, abs=0.05)
    assert maniobra(POR_CODIGO["O4"]).z == pytest.approx(16.1, abs=0.05)
    assert maniobra(POR_CODIGO["O4"]).holgura == pytest.approx(2.1, abs=0.05)


def test_sin_maniobra_cada_obstaculo_tapa_la_ruta():
    for t in ruta():
        assert t.bloqueo_directo > 0.25, t.obstaculo.codigo


def test_las_maniobras_geometricas_despejan_toda_la_vuelta():
    for t in ruta():
        if t.maniobra.modo in ("bajo", "rodeo"):
            assert t.bloqueo_con_maniobra == 0.0, t.obstaculo.codigo


def test_el_centinela_deja_ventana_entre_brazos():
    bloqueo = fraccion_bloqueada(POR_CODIGO["O3"])
    assert 0.0 < bloqueo < 1.0          # hay que esperar, pero la ventana existe


def test_los_extremos_de_la_ruta_estan_vigilados():
    assert "A" in puntos_vigilados(POR_CODIGO["O1"])
    assert len([p for p in puntos_vigilados(POR_CODIGO["O4"]) if p.startswith("R")]) >= 3


def test_las_poses_de_evasion_las_alcanza_el_brazo():
    for t in ruta():
        m = t.maniobra
        a = math.radians(t.obstaculo.yaw)
        x, y = m.rho * math.cos(a), m.rho * math.sin(a)
        assert alcanzable(x, y, m.z), t.obstaculo.codigo
        q = ik(x, y, m.z)
        assert fk(q)[3] == pytest.approx(-90.0, abs=1e-6)   # el vaso no se inclina


def test_transito_nominal_dentro_del_alcance():
    assert alcanzable(R_ARCO, 0.0, Z_TRANSITO)


def test_la_ruta_mezcla_las_maniobras_como_la_simulacion():
    from brazo.obstaculos import plan_en
    z, rho, modo, quien = plan_en(-52.0)        # saliendo de A: baja por O1 y se recoge por O2
    assert (modo, quien) == ("rodeo", "O2") and z == pytest.approx(15.5) and rho == pytest.approx(9.27, abs=0.01)
    z, rho, modo, quien = plan_en(0.0)          # entre O2 y O3: cruza por ventanas en el arco
    assert (modo, quien, rho) == ("espera", "O3", R_ARCO)
    z, rho, modo, quien = plan_en(76.0)         # sobre el rack: por debajo de O4
    assert (modo, quien) == ("bajo", "O4") and z == pytest.approx(16.2, abs=0.05)


def test_python_y_el_simulador_web_calculan_lo_mismo():
    """Corre el planificador JavaScript de la página en Node y lo compara."""
    import json
    import shutil
    import subprocess
    from pathlib import Path

    from brazo.obstaculos import (altura_bajo, holgura, plan_en, radio_interior,
                                  zona_angular)

    if shutil.which("node") is None:
        pytest.skip("Node no está instalado")
    raiz = Path(__file__).resolve().parents[2]
    salida = subprocess.run(
        ["node", str(raiz / "scripts" / "verificar_simulador.js"),
         str(raiz / "docs" / "simulacion_sistema_completo.html")],
        capture_output=True, text=True, check=True).stdout
    js = json.loads(salida)

    for ref, o in zip(js["obstaculos"], OBSTACULOS):
        assert ref["nombre"] == f"{o.codigo} {o.nombre}" and ref["nivel"] == o.nivel
        assert ref["zona"] == pytest.approx(zona_angular(o), abs=1e-9)
        assert ref["bajo"] == pytest.approx(altura_bajo(o), abs=1e-9)
        assert ref["interior"] == pytest.approx(radio_interior(o), abs=1e-9)
    for yaw, modo, z, rho, quien in js["plan"]:
        pz, prho, pmodo, pquien = plan_en(yaw)
        assert (pmodo, pquien) == (modo, quien), yaw
        assert (pz, prho) == pytest.approx((z, rho), abs=1e-9)
    for codigo, giro, yaw, h, r, ref in js["holguras"]:
        assert holgura(yaw, h, r, POR_CODIGO[codigo], giro) == pytest.approx(ref, abs=1e-9)
