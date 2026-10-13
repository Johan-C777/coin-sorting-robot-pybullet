"""Monedas colombianas de las dos familias y diseño del riel selector.

La tolva recibe monedas mezcladas de la familia nueva (2012) y de la familia
anterior (1989-1996). El riel las separa solo por diámetro: dos rieles
paralelos dejan una ranura que se abre por escalones y cada moneda cae en la
primera estación cuya luz supera su diámetro. Como cada estación recibe una
sola combinación de denominación y familia, la barrera infrarroja de esa
estación cuenta a la vez cuántas monedas hay y de qué familia son.

Datos tomados de las fichas técnicas del Banco de la República
(banrep.gov.co/es/billetes-monedas). Diámetros en mm y masas en g; los
espesores son de referencia y no intervienen en el selector.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

NUEVA = "nueva"
ANTIGUA = "antigua"
AMBAS = "ambas"


@dataclass(frozen=True)
class Moneda:
    clave: str             # N50, A100, ... (N = nueva, A = antigua)
    denominacion: int
    familia: str           # NUEVA o ANTIGUA
    desde: int             # año de entrada en circulación
    diametro_mm: float
    masa_g: float
    espesor_mm: float
    material: str

    @property
    def nombre(self) -> str:
        return f"${self.denominacion:,} {self.familia}".replace(",", ".")


CATALOGO: List[Moneda] = [
    # familia nueva, en circulación desde el segundo semestre de 2012
    Moneda("N50", 50, NUEVA, 2012, 17.00, 2.00, 1.30, "acero niquelado"),
    Moneda("N100", 100, NUEVA, 2012, 20.30, 3.34, 1.50, "acero recubierto de latón"),
    Moneda("N200", 200, NUEVA, 2012, 22.40, 4.61, 1.70, "acero niquelado"),
    Moneda("N500", 500, NUEVA, 2012, 23.70, 7.14, 2.20, "bimetálica: alpaca y CuAlNi"),
    Moneda("N1000", 1000, NUEVA, 2012, 26.70, 9.95, 2.30, "bimetálica"),
    # familia anterior
    Moneda("A50", 50, ANTIGUA, 1989, 21.50, 4.50, 1.40, "alpaca (CuZnNi)"),
    Moneda("A100", 100, ANTIGUA, 1992, 23.00, 5.31, 1.55, "CuAlNi, dorada"),
    Moneda("A200", 200, ANTIGUA, 1994, 24.40, 7.08, 1.70, "alpaca (CuZnNi)"),
    Moneda("A500", 500, ANTIGUA, 1993, 23.70, 7.14, 2.05, "bimetálica: CuAlNi y alpaca"),
    Moneda("A1000", 1000, ANTIGUA, 1996, 21.67, 7.30, 2.76, "CuAlNi"),
]

# Monedas que el riel no admite, con la razón. La $1.000 de 1996 mide 21,67 mm,
# a 0,17 mm de la $50 antigua: ninguna ranura impresa separa esa diferencia.
# Es además una moneda escasa en circulación. Se propone para la siguiente
# etapa un sensor de color en la estación 3 (la $50 es plateada y la $1.000
# de 1996 dorada).
FUERA_DE_ALCANCE: Dict[str, str] = {
    "A1000": "0,17 mm de diferencia con la $50 antigua; se separaría por color",
}

POR_CLAVE: Dict[str, Moneda] = {m.clave: m for m in CATALOGO}

# Separación mínima entre diámetros de denominaciones distintas para que una
# ranura impresa en FDM (tolerancia ±0,15 mm) pueda distinguirlas.
SEPARACION_MINIMA_MM = 0.5
# Holgura máxima que se le da a cada moneda sobre su diámetro.
HOLGURA_MAX_MM = 0.6


@dataclass(frozen=True)
class Estacion:
    """Una ranura del riel selector."""
    numero: int                    # 1 a N, en el orden en que la moneda las recorre
    monedas: Tuple[Moneda, ...]    # varias solo si son idénticas en diámetro y valor
    luz_mm: float                  # ancho de la ranura

    @property
    def denominacion(self) -> int:
        return self.monedas[0].denominacion

    @property
    def diametro_mm(self) -> float:
        return self.monedas[0].diametro_mm

    @property
    def familia(self) -> str:
        familias = {m.familia for m in self.monedas}
        return familias.pop() if len(familias) == 1 else AMBAS

    @property
    def masa_g(self) -> float:
        return self.monedas[0].masa_g

    @property
    def etiqueta(self) -> str:
        return "+".join(m.clave for m in self.monedas)


def _redondear(x: float, paso: float = 0.05) -> float:
    return round(round(x / paso) * paso, 2)


def disenar_selector(monedas: Optional[Sequence[Moneda]] = None,
                     holgura_max: float = HOLGURA_MAX_MM,
                     separacion_min: float = SEPARACION_MINIMA_MM) -> List[Estacion]:
    """Ordena por diámetro, agrupa las idénticas y calcula la luz de cada ranura.

    La luz de la estación i queda entre su diámetro y el de la siguiente:
        luz_i = d_i + min(holgura_max, (d_(i+1) - d_i) / 2)
    redondeada a 0,05 mm, que es lo que se puede ajustar en el CAD.

    Lanza ValueError si dos denominaciones distintas quedan más cerca que
    `separacion_min`: el riel no podría distinguirlas.
    """
    if monedas is None:
        monedas = [m for m in CATALOGO if m.clave not in FUERA_DE_ALCANCE]
    orden = sorted(monedas, key=lambda m: (m.diametro_mm, m.denominacion))

    grupos: List[List[Moneda]] = []
    for m in orden:
        if grupos and abs(grupos[-1][0].diametro_mm - m.diametro_mm) < 0.05:
            if grupos[-1][0].denominacion != m.denominacion:
                raise ValueError(f"{grupos[-1][0].clave} y {m.clave} miden lo mismo "
                                 "y valen distinto")
            grupos[-1].append(m)
        else:
            grupos.append([m])

    for a, b in zip(grupos, grupos[1:]):
        sep = b[0].diametro_mm - a[0].diametro_mm
        if sep < separacion_min:
            raise ValueError(f"{a[0].clave} y {b[0].clave} quedan a {sep:.2f} mm: "
                             "el riel no los distingue")

    estaciones = []
    for i, g in enumerate(grupos):
        d = g[0].diametro_mm
        if i + 1 < len(grupos):
            hueco = grupos[i + 1][0].diametro_mm - d
            luz = d + min(holgura_max, hueco / 2.0)
        else:
            luz = d + holgura_max
        estaciones.append(Estacion(i + 1, tuple(g), _redondear(luz)))
    return estaciones


def estacion_de(diametro_mm: float, estaciones: Sequence[Estacion]) -> Optional[Estacion]:
    """Primera estación por la que cae una moneda de ese diámetro."""
    for e in estaciones:
        if diametro_mm < e.luz_mm:
            return e
    return None


def margenes(estaciones: Sequence[Estacion]) -> List[Tuple[float, float]]:
    """(holgura para caer, margen contra la siguiente moneda) de cada estación, en mm."""
    res = []
    for i, e in enumerate(estaciones):
        pasa = e.luz_mm - e.diametro_mm
        retiene = (estaciones[i + 1].diametro_mm - e.luz_mm
                   if i + 1 < len(estaciones) else float("inf"))
        res.append((round(pasa, 2), round(retiene, 2)))
    return res


SELECTOR: List[Estacion] = disenar_selector()


def masa_moneda_g(denominacion: int, antigua: bool = False) -> float:
    for m in CATALOGO:
        if m.denominacion == denominacion and (m.familia == ANTIGUA) == antigua:
            return m.masa_g
    raise KeyError((denominacion, antigua))


def tabla_selector() -> str:
    """Tabla de texto con el diseño del riel, para la consola y la documentación."""
    filas = ["est  moneda(s)      diámetro  luz     cae con  margen  vaso"]
    for e, (pasa, ret) in zip(SELECTOR, margenes(SELECTOR)):
        r = "   -  " if ret == float("inf") else f"{ret:5.2f} "
        filas.append(f"{e.numero:>3}  {e.etiqueta:<12} {e.diametro_mm:6.2f}   "
                     f"{e.luz_mm:6.2f}  {pasa:5.2f}    {r}  ${e.denominacion}")
    return "\n".join(filas)


if __name__ == "__main__":
    print(tabla_selector())
