"""Cruza el firmware del clasificador (etapa 1) con el modelo en Python y con el CAD.

Si alguien cambia un diámetro, una masa, la altura del haz o un pin en un solo lugar,
esta prueba lo detecta antes de que llegue a la placa.
"""
import re
from pathlib import Path

from brazo.monedas import ANTIGUA, POR_CLAVE

RAIZ = Path(__file__).resolve().parents[2]
FW = RAIZ / "firmware" / "etapa1_clasificador"
MONEDAS_H = (FW / "lib" / "Clasificacion" / "Monedas.h").read_text(encoding="utf-8")
CAL_H = (FW / "include" / "calibracion.h").read_text(encoding="utf-8")
PINES_H = (FW / "include" / "pines.h").read_text(encoding="utf-8")
GENERADOR = (RAIZ / "scripts" / "generar_v5.py").read_text(encoding="utf-8")
PRUEBA_MOTOR = (RAIZ / "firmware" / "etapa1_prueba_motor" / "src" / "config.h").read_text(encoding="utf-8")


def tipos_firmware():
    patron = r'\{"(\w+)", "[^"]*", (\d+), Familia::(\w+), ([\d.]+)f, ([\d.]+)f, ([\d.]+)f\}'
    return [(c, int(v), fam, float(d), float(e), float(m)) for c, v, fam, d, e, m in re.findall(patron, MONEDAS_H)]


def test_el_firmware_clasifica_las_nueve_monedas_del_catalogo():
    tipos = tipos_firmware()
    assert [t[0] for t in tipos] == ["N50", "N100", "A50", "N200", "A100", "A500", "N500", "A200", "N1000"]
    for clave, valor, familia, diametro, espesor, masa in tipos:
        m = POR_CLAVE[clave]
        assert valor == m.denominacion
        assert (familia == "Antigua") == (m.familia == ANTIGUA)
        assert diametro == m.diametro_mm
        assert espesor == m.espesor_mm
        assert masa == m.masa_g


def test_la_1000_antigua_del_firmware_es_la_del_catalogo():
    d = float(re.search(r"DIAMETRO_A1000_MM = ([\d.]+)f", MONEDAS_H).group(1))
    assert d == POR_CLAVE["A1000"].diametro_mm


def test_la_calibracion_de_fabrica_es_la_geometria_de_la_pista_impresa():
    b1, sep, h_bar, _ = (float(x) for x in re.search(
        r"^B1, SEP, H_BAR, S_COLOR = ([\d.]+), ([\d.]+), ([\d.]+), ([\d.]+)", GENERADOR, re.M).groups())
    valores = [float(x) for x in re.findall(r"\*/ (-?[\d.]+)f", CAL_H)]
    assert valores[0] == sep          # sep_barreras_mm
    assert valores[1] == h_bar        # h_haz_mm


def test_los_pines_son_los_del_firmware_de_prueba():
    def mapa(texto):
        return {k: v for k, v in re.findall(r"constexpr uint8_t (PIN_\w+)\s*=\s*(\d+);", texto)}

    nuevo, previo = mapa(PINES_H), mapa(PRUEBA_MOTOR)
    for pin, gpio in previo.items():
        assert nuevo[pin] == gpio, pin
    tolva = re.search(r"PIN_TOLVA\[4\]\s*=\s*\{([^}]*)\}", PINES_H).group(1)
    assert tolva.replace(" ", "") == "4,5,6,7"
    usados = [int(g) for g in nuevo.values()] + [4, 5, 6, 7]
    assert len(usados) == len(set(usados)), "pin repetido"
    prohibidos = {0, 3, 45, 46, 19, 20, *range(26, 38), 43, 44}
    assert not prohibidos & set(usados)
