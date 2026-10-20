"""Monedas antiguas y nuevas: selector de ocho estaciones (nueve ductos), vasos y lote."""
import re
from pathlib import Path

import pytest

from brazo.config import MASA_VASO_G, MONEDAS_POR_VASO, Puesto
from brazo.cups import Vaso, lote_demo, totales
from brazo.monedas import (AMBAS, ANTIGUA, CATALOGO, FUERA_DE_ALCANCE, POR_CLAVE, SELECTOR,
                           disenar_selector, estacion_de, margenes)
from brazo.planner import orden_objetivo
from brazo.protocol import parsear_vasos, trama_vasos

RAIZ = Path(__file__).resolve().parents[2]
CONFIG_CONTADOR = RAIZ / "firmware" / "esp32_contador" / "config.h"
GENERADOR = RAIZ / "scripts" / "generar_clasificador.py"
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
    """El riel físico (scripts/generar_clasificador.py) parte la estación de las
    $500 en dos ductos con el sensor de color: 9 ductos sobre las 8 estaciones."""
    texto = CONFIG_CONTADOR.read_text(encoding="utf-8")

    def arreglo(nombre, n):
        cuerpo = re.search(nombre + r"\[" + n + r"\]\s*=\s*\{([^}]*)\}", texto).group(1)
        return [x.strip().rstrip("f") for x in cuerpo.split(",")]

    ranura = [int(r) for r in arreglo("RANURA_DE_ESTACION", "N_ESTACIONES")]
    familia = [f.lower() for f in arreglo("FAMILIA", "N_ESTACIONES")]
    vaso = [int(v) for v in arreglo("VASO_DE_ESTACION", "N_ESTACIONES")]
    dens = [int(d) for d in arreglo("DENOMINACION_VASO", "N_VASOS")]
    diametro = [float(d) for d in arreglo("DIAMETRO_MM", "N_ESTACIONES")]
    luz = [float(r) for r in arreglo("RANURA_MM", "N_RANURAS")]

    # cada ducto sale de la estación del modelo con la misma denominación y familia
    esperadas = [(e.numero - 1, m.denominacion, m.familia)
                 for e in SELECTOR
                 for m in sorted(e.monedas, key=lambda m: m.familia != ANTIGUA)]
    assert list(zip(ranura, [dens[v] for v in vaso], familia)) == esperadas

    # cada moneda cabe en su ranura y no en la anterior (0 = extremo abierto)
    for r, d in zip(ranura, diametro):
        assert luz[r] == 0.0 or d < luz[r]
        assert r == 0 or d >= luz[r - 1] - 0.1   # apoyo de 0,1 mm a calibrar


def test_el_riel_impreso_usa_los_diametros_oficiales_y_cada_ranura_deja_pasar_su_moneda():
    """scripts/generar_clasificador.py (los STL) debe partir de las fichas del Banco de la República."""
    texto = GENERADOR.read_text(encoding="utf-8")
    bloque = texto[texto.index("RANURAS = ["):texto.index("RANURA_500")]
    ranuras = []
    for luz, monedas in re.findall(r"\(([\d.]+|None), \[(.*?)\]\),?\n", bloque):
        piezas = re.findall(r'\("(\w+)", "[^"]*", ([\d.]+)\)', monedas)
        ranuras.append((None if luz == "None" else float(luz),
                        [(c, float(d)) for c, d in piezas]))
    assert len(ranuras) == 8
    for luz, piezas in ranuras:
        for clave, d in piezas:
            assert d == POR_CLAVE[clave].diametro_mm, clave       # diámetro oficial
            assert luz is None or luz - d >= 0.4 - 1e-9, clave      # cae con 0,4 mm
    for i, (luz, _) in enumerate(ranuras[:-1]):
        siguiente = min(d for _, d in ranuras[i + 1][1])
        assert luz < siguiente, f"la ranura {i + 1} no retiene la moneda siguiente"


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
