"""Genera las piezas imprimibles de la celda del Sistema de Logística de Monedas.

    python scripts/generar_stl.py

El brazo no se genera aquí: está modelado en SolidWorks (cad/PLANOS_BRACITO) y
sus STL salen de ahí. Este script cubre riel, tolva, embudos, banda, portavasos,
puestos del rack y bandeja de electrónica, con los criterios de impresión FDM:

  * riel continuo extruido, canal central liso, sin bloques apilados;
  * embudos cónicos que entregan directo al vaso, sin tubos de bajada;
  * marco de banda de perfil único por tramo, con dos rodillos.

Todo en milímetros y en la orientación de impresión (Z = capas).
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from geometria_stl import (Malla, anillo_variable, caja, cilindro,
                           escribir_stl, placa_agujereada, prisma, tubo)

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "hardware" / "Modelos3D" / "stl"

# =====================================================================
# Parámetros maestros (mm). Son los mismos de la simulación HTML.
# =====================================================================
MONEDAS = [(50, 17.0, 2.00), (100, 20.3, 3.34), (200, 22.4, 4.61),
           (500, 23.7, 7.14), (1000, 26.7, 9.95)]
LUZ_EXTRA = 0.6
LUCES = [round(d + LUZ_EXTRA, 1) for _, d, _ in MONEDAS]      # 17,6 ... 27,3
LUZ_ENTRADA = 16.0
PASO = 65.0
ENTRADA = 40.0
LARGO_RIEL = ENTRADA + PASO * 5              # 365
CORTE = 180.0
SOLAPA = 20.0
ANCHO_RIEL = 30.0
ESP_RIEL = 10.0
INCLINACION = 25.0
LARGO_CANAL = 185.0

# celda del brazo
R_ARCO = 230.0
DIAM_VASO = 52.0
ANCHO_BANDA = 70.0
TRAMO_BANDA = 145.0

# alturas de caída de cada estación, medidas en la simulación
ALTURA_EMBUDO = [199.7, 169.4, 139.1, 108.8, 78.5]

PIEZAS = []


def registrar(archivo, nombre, cantidad, malla, material, ajustes, nota):
    lo, hi = malla.caja_envolvente()
    PIEZAS.append({
        "archivo": archivo, "pieza": nombre, "cantidad": cantidad,
        "medidas_mm": f"{hi[0]-lo[0]:.1f} x {hi[1]-lo[1]:.1f} x {hi[2]-lo[2]:.1f}",
        "triangulos": len(malla.t), "material": material,
        "impresion": ajustes, "nota": nota})


# =====================================================================
# ETAPA 1: selección, conteo y transporte
# =====================================================================
def medio_hueco(x: float) -> float:
    if x < ENTRADA:
        return LUZ_ENTRADA / 2
    i = min(int((x - ENTRADA) // PASO), len(LUCES) - 1)
    return LUCES[i] / 2


def perfil_riel(x_ini: float, x_fin: float):
    """Contorno continuo del riel: borde exterior recto, interior escalonado."""
    puntos = [(x_ini, medio_hueco(x_ini))]
    for i in range(len(LUCES)):
        xc = ENTRADA + PASO * i
        if x_ini < xc < x_fin:
            puntos.append((xc, medio_hueco(xc - 0.01)))
            puntos.append((xc, medio_hueco(xc + 0.01)))
    puntos.append((x_fin, medio_hueco(x_fin - 0.01)))
    puntos.append((x_fin, ANCHO_RIEL))
    puntos.append((x_ini, ANCHO_RIEL))
    return puntos


def riel_tramo_a() -> Malla:
    cuerpo = prisma(perfil_riel(0.0, CORTE), 0.0, ESP_RIEL)
    lengueta = caja(CORTE - 0.2, medio_hueco(CORTE + 1), 0.0,
                    CORTE + SOLAPA, ANCHO_RIEL, ESP_RIEL / 2)
    return cuerpo.mas(lengueta)


def riel_tramo_b() -> Malla:
    cuerpo = prisma(perfil_riel(CORTE + SOLAPA, LARGO_RIEL), 0.0, ESP_RIEL)
    labio = caja(CORTE, medio_hueco(CORTE + 1), ESP_RIEL / 2,
                 CORTE + SOLAPA + 0.2, ANCHO_RIEL, ESP_RIEL)
    return cuerpo.mas(labio).mover(-CORTE, 0, 0)


def canal_costado() -> Malla:
    base = placa_agujereada(0, 0, LARGO_CANAL, 22, 0, 6,
                            [(25, 11, 1.7), (LARGO_CANAL / 2, 11, 1.7),
                             (LARGO_CANAL - 25, 11, 1.7)])
    pared = caja(0, 19, 5.8, LARGO_CANAL, 22, 20)
    tope = caja(0, 0, 5.8, 4, 22, 14)
    return base.mas(pared, tope)


def abrazadera() -> Malla:
    r, seg = 2.7, 24
    perfil = [(0, 0), (12.0 - r, 0)]
    for i in range(1, seg):
        ang = math.pi * i / seg
        perfil.append((12.0 - r * math.cos(ang), r * math.sin(ang)))
    perfil += [(12.0 + r, 0), (24, 0), (24, 20), (0, 20)]
    cuerpo = prisma(perfil, 0.0, 14.0)
    ala = placa_agujereada(-14, 14, 0.2, 20, 0, 6, [(-7, 17, 1.7)])
    return cuerpo.mas(ala)


def tolva() -> Malla:
    seg = 48
    arriba = [(55 * math.cos(2 * math.pi * i / seg), 55 * math.sin(2 * math.pi * i / seg))
              for i in range(seg)]
    abajo = [(16 * math.cos(2 * math.pi * i / seg), 16 * math.sin(2 * math.pi * i / seg))
             for i in range(seg)]
    cuerpo = anillo_variable(abajo, 0.0, arriba, 75.0, 2.4)
    boca = tubo(0, 0, -18.0, 0.5, 16.0, 13.6, seg)
    orejas = caja(-62, -6, 60, -50, 6, 66).mas(caja(50, -6, 60, 62, 6, 66))
    return cuerpo.mas(boca, orejas)


def paleta_dosificadora() -> Malla:
    cubo = tubo(0, 0, 0, 9.0, 8.0, 2.6, 32)
    brazo = caja(-4.0, 6.0, 0, 4.0, 48.0, 6.0)
    diente = caja(-9.0, 44.0, 0, 9.0, 52.0, 6.0)
    asiento = caja(-6.0, -6.0, 6.0, 6.0, 6.0, 9.0)
    return cubo.mas(brazo, diente, asiento)


def embudo(alto: float) -> Malla:
    """Cono truncado que baja de la ranura hasta la boca del vaso."""
    seg = 48
    arriba = [(29.0 * math.cos(2 * math.pi * i / seg), 29.0 * math.sin(2 * math.pi * i / seg))
              for i in range(seg)]
    abajo = [(15.0 * math.cos(2 * math.pi * i / seg), 15.0 * math.sin(2 * math.pi * i / seg))
             for i in range(seg)]
    cuerpo = anillo_variable(abajo, 0.0, arriba, alto, 2.4)
    brida = placa_agujereada(-36, -36, 36, 36, alto - 3.0, alto,
                             [(-30, -30, 2.2), (30, -30, 2.2), (-30, 30, 2.2), (30, 30, 2.2)])
    collar = tubo(0, 0, alto - 3.2, alto + 6.0, 31.4, 29.0, seg)
    return cuerpo.mas(brida, collar)


def soporte_sensor() -> Malla:
    base = placa_agujereada(0, 0, 34, 16, 0, 3, [(6, 8, 1.7), (28, 8, 1.7)])
    pared = caja(6, 12.8, 2.8, 28, 16, 27)
    cuna = caja(11, 9.0, 2.8, 23, 12.9, 13)
    return base.mas(pared, cuna)


def rodillo() -> Malla:
    cuerpo = tubo(0, 0, 0, ANCHO_BANDA, 15.0, 2.6, 64)
    p1 = tubo(0, 0, 0, 3.0, 17.5, 2.6, 64)
    p2 = tubo(0, 0, ANCHO_BANDA - 3.0, ANCHO_BANDA, 17.5, 2.6, 64)
    return cuerpo.mas(p1, p2)


def marco_banda() -> Malla:
    """Tramo del marco: alma, pared lateral y pie, todo en una pieza."""
    largo = TRAMO_BANDA
    alma = placa_agujereada(0, 0, largo, 44, 0, 6,
                            [(24, 30, 2.7), (largo / 2, 12, 1.7), (largo - 24, 30, 2.7)])
    pared = caja(0, 38, 5.8, largo, 44, 18)
    solapa = caja(largo - 0.2, 6, 6, largo + 24, 38, 9)
    rebaje = caja(-24, 6, 3, 0.2, 38, 6)
    pie = caja(largo / 2 - 26, -20, 0, largo / 2 + 26, 0.2, 6)
    return alma.mas(pared, solapa, rebaje, pie)


def portavaso() -> Malla:
    base = placa_agujereada(-29, -29, 29, 29, 0, 3,
                            [(-22, -22, 1.7), (22, -22, 1.7), (-22, 22, 1.7), (22, 22, 1.7)])
    anillo = tubo(0, 0, 2.8, 15.0, DIAM_VASO / 2 + 2.2, DIAM_VASO / 2 + 0.4, 64)
    return base.mas(anillo)


def acople_motor() -> Malla:
    lado_motor = tubo(0, 0, 0, 12.0, 9.0, 3.1, 48)
    lado_rodillo = tubo(0, 0, 12.0, 24.0, 9.0, 2.6, 48)
    return lado_motor.mas(lado_rodillo)


def pie_nivelador() -> Malla:
    disco = cilindro(0, 0, 0, 6.0, 11.0, 48)
    espiga = cilindro(0, 0, 5.8, 14.0, 4.0, 32)
    return disco.mas(espiga)


# =====================================================================
# ETAPA 2: brazo de 5 GDL, pinza y rack
# =====================================================================
def puesto_rack() -> Malla:
    """Un puesto del rack curvo: se atornilla a la placa base del rack."""
    base = placa_agujereada(-32, -32, 32, 32, 0, 4,
                            [(-25, -25, 2.2), (25, -25, 2.2), (-25, 25, 2.2), (25, 25, 2.2)])
    anillo = tubo(0, 0, 3.8, 18.0, DIAM_VASO / 2 + 2.4, DIAM_VASO / 2 + 0.6, 64)
    rampa = tubo(0, 0, 16.0, 18.0, DIAM_VASO / 2 + 2.4, DIAM_VASO / 2 + 2.0, 64)
    return base.mas(anillo, rampa)


def bandeja_electronica() -> Malla:
    """Bandeja para el ESP32 y el PCA9685, con separadores integrados."""
    placa = placa_agujereada(0, 0, 120, 78, 0, 4,
                             [(8, 8, 2.2), (112, 8, 2.2), (8, 70, 2.2), (112, 70, 2.2)])
    postes = Malla()
    for x, y in [(18, 20), (18, 58), (66, 20), (66, 58)]:
        postes = postes.mas(tubo(x, y, 3.8, 11.0, 4.0, 1.3, 24))
    bordes = caja(0, 0, 3.8, 120, 3, 10).mas(caja(0, 75, 3.8, 120, 78, 10))
    return placa.mas(postes, bordes)


# =====================================================================
# Escritura de los archivos
# =====================================================================
def main() -> int:
    SALIDA.mkdir(parents=True, exist_ok=True)
    piezas = [
        # ---------------- etapa 1 ----------------
        ("E01_riel_tramo_a.stl", "Riel selector, tramo de entrada", 2, riel_tramo_a(),
         "PETG", "0,2 mm · 4 perímetros · 40 %",
         "Cuerpo continuo extruido con el canal central liso. El riel derecho es la misma pieza volteada sobre su eje largo."),
        ("E02_riel_tramo_b.stl", "Riel selector, tramo de salida", 2, riel_tramo_b(),
         "PETG", "0,2 mm · 4 perímetros · 40 %",
         "Se une al tramo A a media madera, 20 mm de solapa y dos M3."),
        ("E03_canal_costado.stl", "Canal del costado", 4, canal_costado(),
         "PETG", "0,2 mm · 3 perímetros · 30 %",
         "Dos tramos por lado; el riel se apoya dentro del canal."),
        ("E04_abrazadera_varilla.stl", "Abrazadera de varilla M5", 4, abrazadera(),
         "PETG", "0,2 mm · 4 perímetros · 40 %",
         "Fija la altura y los 25 grados de inclinación sobre varilla roscada."),
        ("E05_tolva.stl", "Tolva de alimentación", 1, tolva(),
         "PLA o PETG", "0,25 mm · 3 perímetros · 15 %",
         "Se imprime boca abajo, sin soportes. Capacidad aproximada de 300 monedas."),
        ("E06_paleta_dosificadora.stl", "Paleta dosificadora", 1, paleta_dosificadora(),
         "PETG", "0,2 mm · 4 perímetros · 60 %",
         "Va en el servo SG90: deja pasar una moneda por ciclo."),
        ("E07_embudo_estacion1.stl", "Embudo de la estación 1 ($50)", 1, embudo(ALTURA_EMBUDO[0]),
         "PLA", "0,25 mm · 3 perímetros · 12 %",
         "Cono truncado que entrega directo al vaso; se imprime de pie, sin soportes."),
        ("E07_embudo_estacion2.stl", "Embudo de la estación 2 ($100)", 1, embudo(ALTURA_EMBUDO[1]),
         "PLA", "0,25 mm · 3 perímetros · 12 %", "Misma pieza, más corta por la caída del riel."),
        ("E07_embudo_estacion3.stl", "Embudo de la estación 3 ($200)", 1, embudo(ALTURA_EMBUDO[2]),
         "PLA", "0,25 mm · 3 perímetros · 12 %", "Misma pieza, más corta por la caída del riel."),
        ("E07_embudo_estacion4.stl", "Embudo de la estación 4 ($500)", 1, embudo(ALTURA_EMBUDO[3]),
         "PLA", "0,25 mm · 3 perímetros · 12 %", "Misma pieza, más corta por la caída del riel."),
        ("E07_embudo_estacion5.stl", "Embudo de la estación 5 ($1.000)", 1, embudo(ALTURA_EMBUDO[4]),
         "PLA", "0,25 mm · 3 perímetros · 12 %", "La más corta, junto a la salida del riel."),
        ("E08_soporte_sensor.stl", "Soporte de sensor infrarrojo", 5, soporte_sensor(),
         "PETG", "0,2 mm · 3 perímetros · 30 %",
         "Deja la barrera apuntando al centro de la ranura."),
        ("E09_rodillo_banda.stl", "Rodillo de la banda", 2, rodillo(),
         "PETG", "0,2 mm · 4 perímetros · 30 %",
         "Eje de 5 mm; el motriz se acopla con E12."),
        ("E10_marco_banda.stl", "Marco de la banda, tramo", 6, marco_banda(),
         "PETG", "0,2 mm · 3 perímetros · 25 %",
         "Alma, pared lateral y pie en una sola pieza; tres tramos por lado."),
        ("E11_portavaso.stl", "Portavaso de la banda", 5, portavaso(),
         "PETG", "0,2 mm · 3 perímetros · 20 %", "Sujeta el vaso de 52 mm sobre la cinta."),
        ("E12_acople_motor.stl", "Acople motor a rodillo", 1, acople_motor(),
         "PETG", "0,2 mm · 5 perímetros · 60 %", "De eje de 6 mm del motorreductor a 5 mm del rodillo."),
        ("E13_pie_nivelador.stl", "Pie nivelador", 8, pie_nivelador(),
         "TPU o PETG", "0,2 mm · 3 perímetros · 30 %", "Cuatro para el selector y cuatro para la banda."),
        # ---------------- celda del brazo ----------------
        ("B11_puesto_rack.stl", "Puesto del rack", 5, puesto_rack(),
         "PETG", "0,2 mm · 3 perímetros · 20 %", "Los cinco puestos del arco de 230 mm de radio."),
        ("B12_bandeja_electronica.stl", "Bandeja del ESP32 y el PCA9685", 1, bandeja_electronica(),
         "PLA o PETG", "0,2 mm · 3 perímetros · 15 %", "Separadores integrados, sin tornillería extra."),
    ]

    total_tri = 0
    total_piezas = 0
    for archivo, nombre, cantidad, malla, material, ajustes, nota in piezas:
        n = escribir_stl(str(SALIDA / archivo), malla, archivo[:-4])
        registrar(archivo, nombre, cantidad, malla, material, ajustes, nota)
        total_tri += n
        total_piezas += cantidad
        lo, hi = malla.caja_envolvente()
        print(f"{archivo:30s} x{cantidad:<2d} {n:6d} tri   "
              f"{hi[0]-lo[0]:6.1f} x {hi[1]-lo[1]:6.1f} x {hi[2]-lo[2]:6.1f} mm")

    with open(SALIDA / "piezas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(PIEZAS[0].keys()))
        w.writeheader()
        w.writerows(PIEZAS)

    grandes = [p for p in PIEZAS
               if max(float(v) for v in p["medidas_mm"].split(" x ")) > 220]
    print(f"\n{len(piezas)} archivos, {total_piezas} piezas a imprimir, {total_tri} triángulos")
    print("luces del riel:", LUCES, "mm sobre monedas de",
          [d for _, d, _ in MONEDAS], "mm")
    print("piezas que superan 220 mm en alguna dirección:",
          [p["archivo"] for p in grandes] or "ninguna")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
