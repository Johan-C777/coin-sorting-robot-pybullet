"""Cuña de calibración del riel: una ventana que se ensancha poco a poco junto a la pared guía.

Cada moneda se desliza pegada a la pared y cae por donde la ventana ya es lo bastante ancha. Se anota
entre qué marcas cae cada una y con eso se fijan los anchos de las ranuras del riel.

    python3 scripts/generar_cuna_prueba.py      # -> hardware/archivo/etapa1-v3-canto/P00_cuna_calibracion.stl
"""
import generar_clasificador as g
from generar_clasificador import B, ALA, ESP_BASE, ALTO_PARED, ESP_PARED, PERALTE_T, ALTO_LABIO, caja, prisma_yz, seccion, union

LARGO = 170.0
X0_V, X1_V = 25.0, 145.0       # tramo de la ventana
W0, W1 = 7.0, 15.0             # ancho de la ventana (desde la pared) al inicio y al final
PASO = 10.0                    # marcas cada 10 mm, largas cada 50


def ancho(x):
    return W0 + (W1 - W0) * (x - X0_V) / (X1_V - X0_V)


def cuna():
    m = union([caja(0, LARGO, -ALA, B + ALA, 0, ESP_BASE),
               prisma_yz(seccion([(0, ESP_BASE - 1), (B, ESP_BASE - 1), (B, ESP_BASE + B * PERALTE_T), (0, ESP_BASE)]), 0, LARGO),
               caja(0, LARGO, -ESP_PARED, 0, 0, ESP_BASE + ALTO_PARED),
               caja(0, LARGO, B, B + ESP_PARED, 0, ESP_BASE + B * PERALTE_T + ALTO_LABIO)])
    marcas = []
    for k in range(int(LARGO // PASO) + 1):
        x = k * PASO
        y0 = -ALA + 1.0
        y1 = -2.0 - ESP_PARED - (6.0 if k % 5 == 0 else 0.0)
        y1 = -ESP_PARED - 2.0
        largo_y = 9.0 if k % 5 == 0 else 5.0
        marcas.append(caja(max(x - 0.4, 0.0), x + 0.4, y0, y0 + largo_y, ESP_BASE - 0.01, ESP_BASE + 0.8))
    poli = [(X0_V, 0.0), (X1_V, 0.0), (X1_V, W1), (X0_V, W0)]
    ventana = seccion(poli).extrude(60).translate((0, 0, -1))
    return union([m, *marcas]) - ventana


if __name__ == "__main__":
    destino = g.RAIZ / "hardware" / "archivo" / "etapa1-v3-canto"
    destino.mkdir(parents=True, exist_ok=True)
    c = cuna()
    g.escribir_stl(c, destino / "P00_cuna_calibracion.stl", "cuna")
    print("estado:", c.status().name, "volumen %.1f cm3" % (c.volume() / 1000), "partes:", len(c.decompose()))
    print("ancho de ventana según la marca (mm):", ", ".join(f"{x:.0f}: {ancho(x):.2f}" for x in range(30, 150, 10)))
    for nombre, d in (("N50", 17.0), ("N100", 20.3), ("A50", 21.0), ("N200", 22.4), ("A100", 23.0), ("A500", 23.5),
                      ("N500", 23.7), ("A200", 24.4), ("N1000", 26.7)):
        x = X0_V + (d / 2 - W0) * (X1_V - X0_V) / (W1 - W0)
        print(f"  {nombre} {d}: ancho d/2 = {d/2:.2f} -> marca ≈ {x:.0f} mm")
