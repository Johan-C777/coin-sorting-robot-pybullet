"""El planificador debe dejar el rack ordenado con los movimientos mínimos."""
from brazo.config import Puesto
from brazo.cups import Vaso, lote_demo
from brazo.planner import aplicar, orden_objetivo, planificar


def rack_ordenado(vasos, clave, sentido="asc"):
    en_rack = sorted((v for v in vasos if v.puesto.zona == "rack"),
                     key=lambda v: v.puesto.indice)
    valores = [clave(v) for v in en_rack]
    return valores == sorted(valores, reverse=(sentido == "desc"))


def test_desde_la_entrada_son_cinco_movimientos():
    vasos = lote_demo()
    movs = planificar(vasos, "valor", "asc")
    assert len(movs) == 5
    aplicar(vasos, movs)
    assert rack_ordenado(vasos, lambda v: v.valor)


def test_valor_y_peso_dan_ordenes_distintos():
    vasos = lote_demo()
    assert orden_objetivo(vasos, "valor") != orden_objetivo(vasos, "peso")


def test_reordenar_un_rack_lleno_usa_huecos_de_entrada():
    vasos = lote_demo()
    aplicar(vasos, planificar(vasos, "valor", "asc"))
    movs = planificar(vasos, "valor", "desc")
    aplicar(vasos, movs)
    assert rack_ordenado(vasos, lambda v: v.valor, "desc")
    assert any(m.motivo == "liberar" for m in movs)
    assert len(movs) <= 10


def test_no_mueve_lo_que_ya_esta_ordenado():
    vasos = lote_demo()
    aplicar(vasos, planificar(vasos, "peso", "asc"))
    assert planificar(vasos, "peso", "asc") == []


def test_un_solo_vaso_fuera_de_sitio():
    vasos = [Vaso(50, 10, Puesto("rack", 0)), Vaso(100, 10, Puesto("rack", 1)),
             Vaso(200, 10, Puesto("rack", 2)), Vaso(500, 10, Puesto("rack", 3)),
             Vaso(1000, 10, Puesto("entrada", 0))]
    movs = planificar(vasos, "valor", "asc")
    assert len(movs) == 1
    assert movs[0].origen == Puesto("entrada", 0)
    assert movs[0].destino == Puesto("rack", 4)
