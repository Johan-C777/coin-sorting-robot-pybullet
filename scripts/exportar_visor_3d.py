"""Exporta el ensamble de la etapa 1 (tolva + selección) al visor 3D web.

Uso:  python scripts/exportar_visor_3d.py
Genera hardware/visor/ensamble_etapa1.html (autocontenido, three.js por CDN).
"""
import base64
import json
import math
from pathlib import Path

import numpy as np
from manifold3d import Manifold

import generar_clasificador as g

RAIZ = g.RAIZ
SALIDA = RAIZ / "hardware" / "visor"
PLANTILLA = Path(__file__).with_name("visor_template.html")
C22, S22, T22 = g.C22, g.S22, math.tan(math.radians(g.INCLINACION))


def malla(m: Manifold):
    me = m.to_mesh()
    v = np.asarray(me.vert_properties, np.float32)[:, :3]
    t = np.asarray(me.tri_verts, np.uint32)
    return {"v": base64.b64encode(v.tobytes()).decode(), "t": base64.b64encode(t.tobytes()).decode()}


def mundo(m):                      # marco del riel -> marco de mundo
    return g.rot_y(m, g.INCLINACION)


def p_mundo(x, y, z):
    return (x * C22 + z * S22, y, -x * S22 + z * C22)


def cil_x(x0, x1, y, z, d):
    return g.cil_eje((x0, y, z), np.array([1.0, 0, 0]), x1 - x0, d / 2)


def construir():
    r_a, r_b, la, fin_b = g.disposicion()
    r500 = (r_a + r_b)[g.RANURA_500]
    piezas = []        # cada una: dict de metadatos + malla

    def add(pid, grupo, nombre, archivo, cant, kind, color, m, ex, desc, montaje, idx=None):
        d = dict(pid=pid, grupo=grupo, nombre=nombre, archivo=archivo, cant=cant, kind=kind,
                 color=color, ex=ex, desc=desc, montaje=montaje, idx=idx)
        d.update(malla(m))
        piezas.append(d)

    # ---------------- riel ----------------
    riel_a = g.riel_modulo(0, la, r_a, macho=True)
    riel_b = g.riel_modulo(la, fin_b, r_b, hembra=True, final=True)
    add("R01", "Riel", "Módulo A del riel", "R01_riel_modulo_A.stl", 1, "print", "riel", mundo(riel_a), [-1, 0, 0],
        "Entrada de monedas y ranuras 1 a 4 ($50 nueva, $100 nueva, $50 antigua, $200 nueva). Lleva la cola de milano macho.",
        "Se une al módulo B con 2 tornillos M3 × 6 desde arriba. Se apoya en 4 cuñas de 22°.")
    add("R02", "Riel", "Módulo B del riel", "R02_riel_modulo_B.stl", 1, "print", "riel", mundo(riel_b), [1, 0, 0],
        "Ranuras 5 a 7 ($100 antigua, $500, $200 antigua) y el extremo abierto para la $1000. Cola de milano hembra.",
        "Encastra sobre la cola de A con 0,35 mm de holgura. Se apoya en 4 cuñas de 22°.")

    # ---------------- cuñas ----------------
    h0, L = 4.0, 22.0
    n = 0
    for x0, x1 in ((0.0, la), (la, fin_b)):
        for xs in (x0 + 12, x1 - 12):
            X0 = xs * C22 - L / 2
            dz = -(T22 * X0 + h0 + L * T22)
            for lado, esp, y0 in (("izq", False, -14.0), ("der", True, 44.0)):
                n += 1
                add("R03", "Riel", "Cuña de 22°", f"R03_cuna_22_{lado}.stl", 8, "print", "cuna",
                    g.cuna(esp).translate((X0, y0, dz)), [0, 0, -1],
                    "Soporte que inclina el riel a 22° sobre el bastidor. Hay 4 izquierdas (lado pared guía) y 4 derechas.",
                    "Un M3 × 10 inclinado la une al ala del riel y un M3 vertical la fija al bastidor.", idx=n)

    # ---------------- ductos ----------------
    nombres = {0: "$50 nueva", 1: "$100 nueva", 2: "$50 antigua", 3: "$200 nueva", 4: "$100 antigua",
               6: "$200 antigua", 7: "$1000 nueva"}
    ir_parejas = []
    for r in r_a + r_b:
        if r.i == g.RANURA_500:
            continue
        d = g.ducto(r)
        add(f"D{r.i + 1}", "Ductos", f"Ducto {nombres[r.i]}", f"D{r.i + 1}_ducto_{g._clave(r)}.stl", 1, "print", "ducto",
            mundo(d), [0, 0, -1],
            f"Tubo de salida bajo la ranura {r.i + 1} ({r.ancho:.1f} mm). Lleva dos cavidades Ø5,2 opuestas para la barrera infrarroja.",
            "2 M3 × 10 desde abajo por la brida. LED IR en un lado y fototransistor en el otro.")
        c0 = np.array([r.xc, r.ancho / 2, 0.0])
        hy = r.ancho / 2 + 0.8
        p_ir = c0 + g.ABAJO * g.T_IR
        ir_parejas.append((r.i, p_ir, hy))

    # ---------------- bifurcación ----------------
    bif_pos = p_mundo(r500.xc, r500.ancho / 2, 0)
    bif = g.bifurcacion(r500).translate(bif_pos)
    add("B01", "Bifurcación $500", "Bifurcación de $500", "B01_bifurcacion_500_tcs34725.stl", 1, "print", "bif", bif,
        [0, 0, -1.7],
        "Ranura 6. Un embudo pone la moneda de canto y la hace rodar por una ranura de 4,2 mm a 25°. Lleva el alojamiento del sensor de color, el del servo y dos barreras IR. Se imprime en negro.",
        "2 M3 × 10 a la ranura 6 del riel. El sensor entra por la cara +X y el servo por la cara −X.")
    gb = g.geometria_bif(r500)
    piv_y, piv_z = gb["piv"]
    # aguja en 0°, con su pivote para animarla
    ag = g.aguja()
    cr, sr = g.CR, g.SR
    mat = np.array([[0, 0, 1, -1.4], [cr, sr, 0, piv_y], [-sr, cr, 0, piv_z]], float)
    ag = ag.transform(mat).translate(bif_pos)
    add("B02", "Bifurcación $500", "Aguja desviadora", "B02_aguja_desvio.stl", 1, "print", "aguja", ag, [0, 0, -1.7],
        "Aguja de ferrocarril. A 0° queda a ras del piso y la moneda pasa a $500 antigua. A 45° baja y la moneda cae a $500 nueva.",
        "Su estriado Ø4,6 encaja a presión en el eje del SG90.")
    piezas[-1]["pivote"] = [bif_pos[0], piv_y + bif_pos[1], piv_z + bif_pos[2]]

    placa, _ = g.SENSORES_COLOR["tcs34725"]
    x_pos = g.G / 2 + g.PARED_SENSOR
    hs = gb["h_sensor"]
    ps = g.pt(g.S_SENSOR, hs)
    tapa = g.tapa_sensor("tcs34725")
    # la tapa cubre la placa por fuera de la cara +X, inclinada como la rampa
    tapa = g.rot_x(g.rot_y(tapa, 90.0), -g.RAMPA).translate((x_pos + 1.6, *ps)).translate(bif_pos)
    add("B03", "Bifurcación $500", "Tapa del sensor", "B03_tapa_sensor_tcs34725.stl", 1, "print", "bif", tapa, [3, 0, -1.7],
        "Tapa que sujeta la placa del TCS34725 en su alojamiento. Queda abierta hacia el lado del conector.",
        "2 M3 × 6 a los pilotos de la bifurcación.")

    # ---------------- tolva ----------------
    ex_, ey_, ez_ = p_mundo(g.ENTRADA / 2, 12.0, g.ESP_BASE)
    tpos = (ex_ - g.CAVIDAD_R, ey_, ez_ + 25)
    add("T03", "Tolva", "Base de la tolva", "T03_base_tolva_28byj.stl", 1, "print", "tolva", g.tolva_base().translate(tpos),
        [0, 0, 0.5],
        "Plato con el alojamiento del motor, la ventana de salida de la moneda y las 4 orejas de fijación.",
        "Se fija al bastidor con 4 M3 embutidos. El 28BYJ-48 va por debajo con 2 M3 × 6.")
    add("T02", "Tolva", "Disco dosificador", "T02_disco_dosificador_28byj.stl", 1, "print", "tolva2",
        g.tolva_disco().translate((0, 0, g.Z_DISCO)).translate(tpos), [0, 0, 1.4],
        "Disco Ø80 con 4 cavidades. Cada vuelta de 90° suelta una moneda; a 1,5 s por moneda gira a 10 rpm.",
        "Entra a presión en el eje del 28BYJ-48, 0,35 mm sobre la base.")
    add("T01", "Tolva", "Cono de la tolva", "T01_tolva_cono_40.stl", 1, "print", "tolva3",
        g.tolva_cono().translate((0, 0, g.Z_ANILLO)).translate(tpos), [0, 0, 2.4],
        "Embudo con paredes a 40° y un rascador sobre la salida que deja pasar solo la moneda alojada en la cavidad.",
        "3 M3 × 12 desde abajo de la base.")

    # ---------------- componentes (no se imprimen) ----------------
    tp = np.array(tpos)
    byj = g.cil_z(-g.BYJ["eje_off"], 0, -19.0, 0.0, 28.0) + g.caja(-g.BYJ["eje_off"] - 3.5, -g.BYJ["eje_off"] + 3.5,
                                                                 -g.BYJ["orejas"] / 2 - 3.5, g.BYJ["orejas"] / 2 + 3.5, -1.0, 0.0)
    byj = byj + g.cil_z(0, 0, 0.0, 6.0, 5.0) + g.cil_z(-g.BYJ["eje_off"], 0, -19.0, -12.0, 9.0)
    add("C1", "Componentes", "Motor 28BYJ-48 con ULN2003", None, 1, "comp", "motor", byj.translate(tpos), [0, 0, -1.0],
        "Motor paso a paso que mueve el disco dosificador. El driver ULN2003 va aparte, en la caja de electrónica.",
        "GPIO 16, 17, 18 y 19 del ESP32. 2 M3 × 6 a la base.")

    sg = g.SG90
    x_oreja = g.G / 2 - 0.5 - (sg["caja_sobre_oreja"] + sg["buje"] + sg["estriado"])
    z_c = piv_z - sg["eje_off"]
    prof = 22.5
    cuerpo = g.caja(x_oreja - (prof - sg["caja_sobre_oreja"]), x_oreja + sg["caja_sobre_oreja"],
                    piv_y - sg["ancho"] / 2, piv_y + sg["ancho"] / 2,
                    z_c - sg["largo"] / 2, z_c + sg["largo"] / 2)
    orejas = g.caja(x_oreja, x_oreja + 2.0, piv_y - sg["ancho"] / 2, piv_y + sg["ancho"] / 2,
                    z_c - sg["orejas"] / 2, z_c + sg["orejas"] / 2)
    eje = g.cil_eje((x_oreja + sg["caja_sobre_oreja"], piv_y, piv_z), np.array([1.0, 0, 0]),
                    sg["buje"] + sg["estriado"] + 1.0, 2.3)
    add("C2", "Componentes", "Micro-servo SG90 (aguja)", None, 1, "comp", "servo",
        (cuerpo + orejas + eje).translate(bif_pos), [-3, 0, -1.7],
        "Mueve la aguja entre 0° ($500 antigua) y 45° ($500 nueva).",
        "Entra por la cara −X de la bifurcación, con 2 tornillos M2 en las orejas. Señal en GPIO 13.")

    pl = g.caja(x_pos, x_pos + 1.6, -placa / 2, placa / 2, -placa / 2, placa / 2)
    chip = g.caja(x_pos + 1.6, x_pos + 2.8, -3, 3, -3, 3)
    tcs = g.rot_x(pl + chip, -g.RAMPA).translate((0, *ps)).translate(bif_pos)
    add("C3", "Componentes", "Sensor de color TCS34725", None, 1, "comp", "sensor", tcs, [2, 0, -1.7],
        "Lee el anillo de la moneda de $500: plateado es antigua, dorado es nueva. Mira a través de una ventana de 7 mm.",
        "En su alojamiento de la cara +X, sujeto por la tapa. I2C en GPIO 21 (SDA) y 22 (SCL).")

    # barreras IR: LED a un lado, fototransistor al otro
    ir_led, ir_fto = [], []
    for i, p_ir, hy in ir_parejas:
        for s, lst in ((1, ir_led), (-1, ir_fto)):
            y0 = p_ir[1] + s * (hy + 2.0)
            m = g.cil_eje((p_ir[0], y0, p_ir[2]), np.array([0, float(s), 0]), 8.6, 2.5)
            lst.append(mundo(m))
    for yy, zz in [((gb["yn"][0] + gb["yn"][1]) / 2, gb["z_ir"]), ((gb["ya"][0] + gb["ya"][1]) / 2, gb["z_ir"])]:
        ir_led.append(cil_x(g.G / 2 + 3.0, g.G / 2 + 3.0 + 8.6, yy, zz, 5.0).translate(bif_pos))
        ir_fto.append(cil_x(-g.G / 2 - 3.0 - 8.6, -g.G / 2 - 3.0, yy, zz, 5.0).translate(bif_pos))
    add("C4", "Componentes", "LED infrarrojo (9)", None, 9, "comp", "led", g.union(ir_led), [0, -2, 0],
        "Emisor de cada barrera. Hay 9, uno por salida: 7 ductos y las 2 salidas de la bifurcación.",
        "Va a presión en su cavidad Ø5,2, con su resistencia en serie.")
    add("C5", "Componentes", "Fototransistor (9)", None, 9, "comp", "foto", g.union(ir_fto), [0, 2, 0],
        "Receptor de cada barrera. Cuando una moneda corta el haz, dispara la interrupción del ESP32.",
        "Frente al LED. Pull-up externo de 10 kΩ. GPIO 34, 35, 36, 39, 32, 33, 25, 26 y 27.")

    return piezas


def main():
    piezas = construir()
    datos = json.dumps({"piezas": piezas}, separators=(",", ":"))
    html = PLANTILLA.read_text(encoding="utf-8").replace("/*DATOS*/null", datos)
    SALIDA.mkdir(parents=True, exist_ok=True)
    ruta = SALIDA / "ensamble_etapa1.html"
    ruta.write_text(html, encoding="utf-8")
    print(f"{len(piezas)} mallas, {len(html) / 1e6:.2f} MB -> {ruta}")


if __name__ == "__main__":
    main()
