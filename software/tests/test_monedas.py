"""Monedas antiguas y nuevas: selector de ocho estaciones, vasos y lote."""
import re
from pathlib import Path

import pytest

from brazo.config import MASA_VASO_G, MONEDAS_POR_VASO, Puesto
from brazo.cups import Vaso, lote_demo, totales
from brazo.monedas import (AMBAS, CATALOGO, FUERA_DE_ALCANCE, POR_CLAVE, SELECTOR,
                           disenar_selector, estacion_de, margenes)
from brazo.planner import orden_objetivo
from brazo.protocol import parsear_vasos, trama_vasos

CONFIG_CONTADOR = (Path(__file__).resolve().parents[2]
                   / "firmware" / "esp32_contador" / "config.h")
ADMITIDAS = [m for m in CATALOGO if m.clave not in FUERA_DE_ALCANCE]


def test_el_riel_tiene_ocho_estaciones_en_orden_de_diametro():
    assert len(SELECTOR) == 8
    diametros = [e.diametro_mm for e in SELECTOR]
    assert diametros == sorted(diametros)
    assert [e.etiqueta for e in SELECTOR] == [
        "N50", "N100", "A50", "N200", "A100", "N500+A500", "A200", "N1000"]


def test_cada_moneda_admitida_cae_en_su_estacion():
    for m in ADMITIDAS:
        e = estacion_de(m.diametro_mm, SELECTOR)
        assert e is not None and m in e.monedas, m.clave
        assert e.denominacion == m.denominacion


def test_cada_luz_deja_pasar_su_moneda_y_retiene_la_siguiente():
    for pasa, retiene in margenes(SELECTOR):
        assert pasa >= 0.25          # cae con holgura
        assert retiene >= 0.25       # la siguiente moneda no se cuela


def test_las_dos_500_comparten_estacion_porque_son_identicas():
    a, n = POR_CLAVE["A500"], POR_CLAVE["N500"]
    assert a.diametro_mm == n.diametro_mm and a.masa_g == n.masa_g
    e = estacion_de(a.diametro_mm, SELECTOR)
    assert e.familia == AMBAS


def test_la_1000_de_1996_no_se_puede_separar_por_diametro():
    with pytest.raises(ValueError, match="A1000"):
        disenar_selector(CATALOGO)


def test_el_firmware_del_contador_usa_el_mismo_riel():
    texto = CONFIG_CONTADOR.read_text(encoding="utf-8")

    def arreglo(nombre):
        cuerpo = re.search(nombre + r"\[N_ESTACIONES\]\s*=\s*\{([^}]*)\}", texto).group(1)
        return [float(x.strip().rstrip("f")) for x in cuerpo.split(",")]

    assert arreglo("DIAMETRO_MM") == pytest.approx([e.diametro_mm for e in SELECTOR], abs=1e-6)
    assert arreglo("LUZ_MM") == pytest.approx([e.luz_mm for e in SELECTOR], abs=1e-6)
    assert arreglo("MASA_MONEDA_G") == pytest.approx([e.masa_g for e in SELECTOR], abs=1e-6)
    vasos = [int(v) for v in arreglo("VASO_DE_ESTACION")]
    dens = [50, 100, 200, 500, 1000]
    assert [dens[v] for v in vasos] == [e.denominacion for e in SELECTOR]


def test_el_peso_del_vaso_cuenta_las_antiguas():
    v = Vaso(100, 30, antiguas=10)
    assert v.nuevas == 20
    assert v.peso_g == pytest.approx(MASA_VASO_G + 20 * 3.34 + 10 * 5.31)
    assert v.valor == 3000          # la familia no cambia el valor


def test_vasos_imposibles_se_rechazan():
    with pytest.raises(ValueError):
        Vaso(100, 5, antiguas=6)
    with pytest.raises(ValueError):
        Vaso(1000, 10, antiguas=1)    # la $1.000 antigua no entra al riel


def test_las_antiguas_cambian_el_orden_por_peso():
    con = lote_demo()
    sin = [Vaso(v.denominacion, v.monedas, v.puesto) for v in con]
    assert orden_objetivo(con, "peso", "asc") != orden_objetivo(sin, "peso", "asc")
    assert [con[i].denominacion for i in orden_objetivo(con, "peso", "asc")] == \
        [50, 1000, 500, 200, 100]


def test_la_carga_de_diseno_sigue_siendo_el_vaso_de_1000_nuevas():
    peor = max(MASA_VASO_G + MONEDAS_POR_VASO * m.masa_g for m in ADMITIDAS)
    assert peor == pytest.approx(416.0)


def test_lote_ida_y_vuelta_por_la_trama():
    vasos = lote_demo()
    linea = trama_vasos(vasos)
    assert linea == "VASOS:500x12,100x30a10,1000x8,50x25a9,200x17a6"
    leidos = parsear_vasos(linea)
    assert [(v.denominacion, v.monedas, v.antiguas) for v in leidos] == \
        [(v.denominacion, v.monedas, v.antiguas) for v in vasos]
    assert leidos[2].puesto == Puesto("entrada", 2)
    assert totales(leidos)["antiguas"] == 25


def test_trama_mal_escrita_se_rechaza():
    with pytest.raises(ValueError):
        parsear_vasos("VASOS:500x12a20")
    with pytest.raises(ValueError):
        parsear_vasos("S:1,2,3")
