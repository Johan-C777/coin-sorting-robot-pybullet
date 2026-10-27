"""Riel de monedas de canto (v3): placa inclinada con repisa y ventanas de altura creciente.

    pip install manifold3d numpy
    python scripts/generar_canto.py            # STL + verificación
    python scripts/generar_canto.py --probeta  # solo la probeta de ventanas y su cuña

Idea: la moneda va de pie (de canto) en la esquina entre una placa inclinada LEAN grados hacia
atrás y una repisa perpendicular a ella. Un empujador lento la lleva por una pista horizontal.
En cada ventana la placa tiene un recorte desde la repisa hasta la altura H = d + HOLGURA_H:
una moneda de diámetro menor que H se inclina hacia atrás y cae al receptor; una mayor queda
apoyada en la placa por encima de H y sigue. Las ventanas van de menor a mayor altura.

Marco de impresión de cada módulo (mm): X a lo largo de la pista, Y = t (sube por la placa; la
repisa está en Y = 0), Z = placa + n (Z = 0 es la cara trasera de la placa, que va sobre la
cama; n sale de la placa hacia las monedas). Sin soportes: la repisa sobre una ventana es un
puente de 3 mm de ancho.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generar_clasificador import SALIDA as _SALIDA_V2, caja, escribir_stl  # noqa: E402

SALIDA = _SALIDA_V2.parents[1] / "etapa1-v3-canto"

set_circular_segments(72)

# ---------------------------------------------------------------- parámetros
LEAN = 20.0            # inclinación de la placa respecto a la vertical (grados)
PLACA = 4.0            # espesor de la placa
BAJO = 6.0             # la placa baja 6 mm bajo la repisa (zócalo en las alas)
ALTO = 38.0            # altura total de la placa sobre la repisa (la moneda mayor mide 26,7)
REPISA_ESP = 3.0       # espesor de la repisa (Y de -3 a 0)
REPISA_ANCHO = 11.0    # ancho de la repisa (n de 0 a 11)
HOLGURA_H = 0.15       # H = d + HOLGURA_H + COMPENSACION_H (la simulación mejor con 0,15)
COMPENSACION_H = 0.0   # ajuste fino de la impresora (+ abre, - cierra)
LARGO_EXTRA = 8.0      # largo de ventana = d + 8
PASO = 42.0            # distancia entre inicios de ventana
BISEL_L, BISEL_P = 6.0, 2.5   # biselado de la entrada de cada alma: largo y profundidad

# (clave, nombre, diámetro) en el orden de las ventanas; $500 nueva y antigua comparten ventana
VENTANAS = [
    ("N50", "$50 nueva", 17.0),
    ("N100", "$100 nueva", 20.3),
    ("A50", "$50 antigua", 21.5),
    ("N200", "$200 nueva", 22.4),
    ("A100", "$100 antigua", 23.0),
    ("A500", "$500", 23.7),
    ("A200", "$200 antigua", 24.4),
    ("N1000", "$1000 nueva", 26.7),
]


def altura_h(d: float) -> float:
    return round(d + HOLGURA_H + COMPENSACION_H, 2)


def largo_v(d: float) -> float:
    return round(d + LARGO_EXTRA, 2)


def modulo(x1: float, ventanas: list[tuple[float, float, float]], h_previa: float | None,
           bisel_ini: bool = True) -> Manifold:
    """Módulo de riel de 0 a x1. ventanas: [(x_ini, x_fin, H)]. h_previa: H de la ventana anterior
    al módulo (para biselar la entrada del primer alma)."""
    top = ALTO
    m = caja(0, x1, -BAJO, top, 0, PLACA)
    # repisa: pared de 3 mm (Y -3..0) de 11 mm de alto sobre la placa
    m += caja(0, x1, -REPISA_ESP, 0, PLACA, PLACA + REPISA_ANCHO)
    # ventanas: recorte desde -BAJO hasta H en toda la placa
    for a, b, h in ventanas:
        m -= caja(a - 1e-3, b + 1e-3, -BAJO - 1, h, -1, PLACA + 1e-3)
    # biselado de la cara delantera tras cada ventana (solo por debajo de la H anterior)
    pos = [(a, b, h) for a, b, h in ventanas]
    previas = [h_previa] + [h for _, _, h in pos]
    inicios = [0.0] + [b for _, b, _ in pos]
    for hp, x0 in zip(previas, inicios):
        if hp is None or (x0 == 0.0 and not bisel_ini):
            continue
        tri = CrossSection([[(x0, PLACA), (x0, PLACA - BISEL_P), (x0 + BISEL_L, PLACA)]])
        # triángulo en (x, Z) extruido a lo largo de Y: se extruye en Z y se gira 90° sobre X
        prisma = Manifold.extrude(tri, hp + BAJO).rotate((90, 0, 0)).translate((0, hp, 0))
        m -= prisma
    return m


def verificar(m: Manifold, nombre: str) -> None:
    mesh = m.to_mesh()
    comp = m.decompose()
    bb = m.bounding_box()
    dims = (bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2])
    ok = m.status().name == "NoError" and len(comp) == 1
    print(f"  {nombre:28s} {dims[0]:6.1f} x {dims[1]:5.1f} x {dims[2]:5.1f} mm  vol {m.volume()/1000:6.1f} cm3  "
          f"{'OK' if ok else 'REVISAR'} ({len(comp)} cuerpo(s))")
    assert ok, nombre
    assert max(dims) <= 210.0 + 1e-6, f"{nombre} no cabe en la cama"


def cuña_prueba(largo: float = 40.0, fondo: float = 50.0, alto: float = 60.0) -> Manifold:
    """Soporte que inclina la placa LEAN grados hacia atrás. Perfil (u, h): u hacia atrás."""
    tg = math.tan(math.radians(LEAN))
    repisa_h = 2.0
    pts = [(-5, 0), (-5, repisa_h + 5 * tg), (0, repisa_h), ((alto - repisa_h) * tg, alto), (fondo, alto), (fondo, 0)]
    perfil = CrossSection([pts[::-1]])
    m = Manifold.extrude(perfil, largo)           # perfil en XY, extruido en Z
    return m.rotate((90, 0, 0)).rotate((0, 0, 90))


def probeta() -> Manifold:
    """Cuatro ventanas contiguas en el rango más difícil: $200 n, $100 a, $500, $200 a."""
    ks = [("N200", 22.4), ("A100", 23.0), ("A500", 23.7), ("A200", 24.4)]
    v = []
    x = 24.0
    for _, d in ks:
        v.append((x, x + largo_v(d), altura_h(d)))
        x += PASO
    x1 = v[-1][1] + 22.0
    return modulo(x1, v, h_previa=None)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probeta", action="store_true")
    args = ap.parse_args()
    SALIDA.mkdir(parents=True, exist_ok=True)
    print("Riel de canto")
    p = probeta()
    verificar(p, "R00_probeta_ventanas")
    escribir_stl(p, SALIDA / "R00_probeta_ventanas.stl", "R00 probeta ventanas")
    c = cuña_prueba()
    verificar(c, "R00b_cuna_prueba")
    escribir_stl(c, SALIDA / "R00b_cuna_prueba.stl", "R00b cuna prueba")


if __name__ == "__main__":
    main()
