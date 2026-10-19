"""Exporta el ensamble de la etapa 1 (tolva + selección) al visor 3D web, con simulación.

Uso:  python scripts/exportar_visor_3d.py
Genera hardware/visor/ensamble_etapa1.html (autocontenido, three.js por CDN).
Toda la geometría sale de generar_clasificador.py: el visor muestra lo que se imprime.
"""
import base64
import json
from pathlib import Path

import numpy as np
from manifold3d import Manifold

import generar_clasificador as g

RAIZ = g.RAIZ
SALIDA = RAIZ / "hardware" / "visor"
PLANTILLA = Path(__file__).with_name("visor_template.html")
C22, S22 = g.C22, g.S22
VASO_D, VASO_H = 34.0, 60.0
DENOM = {"N50": 50, "A50": 50, "N100": 100, "A100": 100, "N200": 200, "A200": 200,
         "A500": 500, "N500": 500, "N1000": 1000}
VASOS = [50, 100, 200, 500, 1000]
YS = 11.8                              # la moneda va pegada a la pared guía: centro a r = 11,8


def malla(m: Manifold):
    me = m.to_mesh()
    v = np.asarray(me.vert_properties, np.float32)[:, :3]
    t = np.asarray(me.tri_verts, np.uint32)
    return {"v": base64.b64encode(v.tobytes()).decode(), "t": base64.b64encode(t.tobytes()).decode()}


def construir():
    d, piezas_g, ctx = g.construir_piezas()
    r_all = d.ranuras
    r500 = ctx["r500"]
    p_mundo = ctx["p_mundo"]
    zoff, base_z, centro = ctx["zoff"], ctx["base_z"], ctx["centro"]
    por_nombre = {p.nombre: p for p in piezas_g}
    out = []

    def add(pid, grupo, nombre, archivo, cant, kind, color, m, ex, desc, montaje, tag=None, pivote=None, eje=None):
        e = dict(pid=pid, grupo=grupo, nombre=nombre, archivo=archivo, cant=cant, kind=kind, color=color,
                 ex=ex, desc=desc, montaje=montaje, tag=tag, pivote=pivote, eje=eje)
        e.update(malla(m))
        out.append(e)

    def mundo(nombre):
        p = por_nombre[nombre]
        return p.pose(p.geom)

    # ---------------- riel ----------------
    add("R01", "Riel", "Módulo A del riel", "R01_riel_modulo_A.stl", 1, "print", "riel", mundo("R01_riel_modulo_A"), [-1, 0, 0],
        "Entrada de monedas y ranuras 1 a 4 ($50 nueva, $100 nueva, $50 antigua, $200 nueva). Piso con 10° de peralte hacia la pared guía.",
        "Se une al módulo B con 3 llaves de mariposa (R04) desde abajo y se apoya en 3 patas por lado.")
    add("R02", "Riel", "Módulo B del riel", "R02_riel_modulo_B.stl", 1, "print", "riel", mundo("R02_riel_modulo_B"), [1, 0, 0],
        "Ranuras 5 a 7 ($100 antigua, $500, $200 antigua) y el extremo abierto para la $1000, con su pared de tope.",
        "Baja sobre las llaves R04 y sobre las clavijas de sus patas, sin tornillos.")
    for nombre, m in g.partes_ensamble(piezas_g, ctx):
        if nombre.startswith("R04"):
            add("R04", "Riel", "Llave de mariposa", "R04_llave_union.stl", 3, "print", "llave", m, [0, 0, -1.2],
                "Pieza plana en forma de mariposa que traba los dos módulos del riel. Hay 3: una bajo cada ala y otra bajo el canal.",
                "Entra desde abajo en las dos mitades de su alojamiento, que tienen 0,2 mm de holgura.")
        elif nombre.startswith("R03"):
            add("R03", "Riel", "Pata del riel", "R03_pata{1,2,3}_{izq,der}.stl", 6, "print", "pata", m, [0, 0, -1],
                "Columna en cruz con la cabeza cortada a 22°. Hay 3 por lado, de alturas distintas: 139, 101 y 44 mm.",
                "La clavija Ø6 de la cabeza entra en un agujero ciego del ala. El pie se ata a la mesa con 2 bridas.")
        elif nombre == "T04_pata_tolva":
            add("T04", "Tolva", "Pata de la tolva", "T04_pata_tolva.stl", 4, "print", "pata", m, [0, 0, -1],
                f"Cuatro columnas de {base_z + 0:.0f} mm que levantan la base de la tolva sobre la entrada del riel.",
                "Su clavija Ø6 entra en la oreja de la base. El pie se ata a la mesa con 2 bridas.")

    # ---------------- ductos y bifurcación ----------------
    nombres = {0: "$50 nueva", 1: "$100 nueva", 2: "$50 antigua", 3: "$200 nueva", 4: "$100 antigua",
               6: "$200 antigua", 7: "$1000 nueva"}
    luces = {}
    for r in r_all:
        if r.i == g.RANURA_500:
            continue
        c0 = p_mundo(r.xc, r.yc, 0)
        hu, hy = g.medidas_tubo(r)
        nom = f"D{r.i + 1}_ducto_{r.clave}"
        add(f"D{r.i + 1}", "Ductos", f"Ducto {nombres[r.i]}", nom + ".stl", 1, "print", "ducto", mundo(nom), [0, 0, -1],
            f"Tubo vertical bajo la ranura {r.i + 1} ({r.ancho:.1f} mm). Dos cavidades Ø5,2 enfrentadas para la barrera infrarroja, {g.T_IR:.0f} mm bajo el riel.",
            "Dos clavijas Ø6 en sus orejas entran en el ala del riel. LED IR a un lado y fototransistor al otro, a presión.")
        luces[f"D{r.i + 1}"] = (c0, hy, -g.T_IR, 0.0)
    gd = g.geom_d6(r500, ctx["extra_d6"])
    c6 = p_mundo(r500.xc, r500.yc, 0)
    add("D6", "Bifurcación $500", "Bifurcador de $500", "D6_bifurcador_500.stl", 1, "print", "bif", mundo("D6_bifurcador_500"), [0, 0, -1.7],
        "Tubo vertical bajo la ranura 6 que se abre en dos columnas separadas por un divisor. En el cruce hay un plato basculante: inclinado a un lado, la moneda sale por una columna; al otro lado, por la otra. Las dos salidas quedan en la misma línea que los demás ductos.",
        "Dos clavijas en sus orejas al ala del riel. El servo SG90 entra a presión por la cara −Y y el plato se mete desde abajo. Se imprime en negro.")
    luces["D6a"] = (c6, gd["hy"], gd["up_ir"], -(g.COL_INT0 + g.COL_INT1) / 2)
    luces["D6b"] = (c6, gd["hy"], gd["up_ir"], (g.COL_INT0 + g.COL_INT1) / 2)
    piv = (c6[0], c6[1], c6[2] - g.T_PIV)
    add("B02", "Bifurcación $500", "Plato desviador", "B02_plato_desvio.stl", 1, "print", "plato", mundo("B02_plato_desvio"), [0, 0, -1.7],
        "Bloque basculante de 31 × 9 mm. El servo lo inclina 35° a cada lado: hacia −X la $500 antigua y hacia +X la $500 nueva.",
        "Su pasador Ø4 entra en la pared +Y y su estriado Ø4,6 se encaja a presión en el eje del SG90.",
        pivote=list(piv), eje="y")
    add("B03", "Bifurcación $500", "Puente del sensor", "B03_puente_sensor.stl", 1, "print", "puente", mundo("B03_puente_sensor"), [0, 0, 3.5],
        "Puente a horcajadas sobre las paredes del riel, antes de la ranura 5. Cuelga la placa del TCS34725 mirando la cara de la moneda, a 4 mm.",
        "Los faldones abrazan las paredes con un diente de agarre. La placa se desliza desde el lado −X bajo dos labios.")

    # ---------------- tolva ----------------
    for nom, pid, titulo, desc, mont, ex, col in (
            ("T03_base_tolva", "T03", "Base de la tolva",
             "Plato con el anillo del disco, la ventana de salida de la moneda, cuatro orejas con agujero y tres clavijas para el cono.",
             "El 28BYJ-48 queda bajo el plato, apretado con 2 bridas de nailon que pasan por las ranuras. Las orejas se apoyan en las patas T04.", [0, 0, 0.5], "tolva"),
            ("T02_disco_dosificador", "T02", "Disco dosificador",
             "Disco Ø80 con 4 cavidades. Cada giro de 90° suelta una moneda; a 1,5 s por moneda gira a 10 rpm.",
             "Entra a presión en el eje del 28BYJ-48, 0,35 mm sobre la base.", [0, 0, 1.4], "tolva2"),
            ("T01_tolva_cono_40", "T01", "Cono de la tolva",
             "Embudo con paredes a 40° y un rascador sobre la salida que deja pasar solo la moneda alojada en la cavidad.",
             "Tres agujeros ciegos en el flanje reciben las clavijas del anillo de la base.", [0, 0, 2.4], "tolva3")):
        add(pid, "Tolva", titulo, nom + ".stl", 1, "print", col, mundo(nom), ex, desc, mont,
            pivote=[centro[0], centro[1], base_z] if pid == "T02" else None, eje="z" if pid == "T02" else None)

    # ---------------- componentes ----------------
    byj = (g.cil_z(-g.BYJ["eje_off"], 0, -19.0, 0.0, 28.0)
           + g.caja(-g.BYJ["eje_off"] - 3.5, -g.BYJ["eje_off"] + 3.5, -g.BYJ["orejas"] / 2 - 3.5, g.BYJ["orejas"] / 2 + 3.5, -1.0, 0.0)
           + g.cil_z(0, 0, 0.0, 6.0, 5.0) + g.cil_z(-g.BYJ["eje_off"], 0, -19.0, -12.0, 9.0))
    add("C1", "Componentes", "Motor 28BYJ-48", None, 1, "comp", "motor", byj.translate((centro[0], centro[1], base_z)), [0, 0, -1.0],
        "Motor paso a paso que mueve el disco. El driver ULN2003 va aparte, en la caja de electrónica.",
        "GPIO 16, 17, 18 y 19. Queda bajo la base, apretado con 2 bridas de nailon.")
    y_o = -(gd["hy"] + g.E_DUCTO + g.PAD_SERVO)
    add("C2", "Componentes", "Micro-servo SG90", None, 1, "comp", "servo", g.servo_sg90(y_o, -g.T_PIV).translate(tuple(c6)), [0, -3, 0],
        "Inclina el plato: 55° lo manda hacia −X ($500 antigua) y 125° hacia +X ($500 nueva).",
        "Entra a presión en el bolsillo de la cara −Y de D6. Señal en GPIO 13.")
    pla = g.caja(-g.SENSOR_PLACA / 2, g.SENSOR_PLACA / 2, YS - g.SENSOR_PLACA / 2, YS + g.SENSOR_PLACA / 2, -1.6, 0)
    chip = g.caja(-3, 3, YS - 3, YS + 3, -2.6, -1.6)
    tcs = g.rot_y((pla + chip).translate((d.x_sensor, 0, g.Z_PUENTE)), g.INCLINACION).translate((0, 0, zoff))
    add("C3", "Componentes", "Sensor de color TCS34725", None, 1, "comp", "sensor", tcs, [0, 0, 6],
        "Lee la cara de la $500 mientras pasa: anillo, centro, anillo. Anillo plateado es antigua; dorado, nueva.",
        "Cuelga bajo el puente B03, con el sensor hacia la moneda. I2C en GPIO 21 (SDA) y 22 (SCL).")
    for k, (c0, hy, up, h) in luces.items():
        for s, pid, nombre, col, ex, desc, mont in (
                (1, "C4", "LED infrarrojo", "led", [0, -2, 0], "Emisor de cada barrera. Hay 9: 7 ductos y las 2 columnas de la bifurcación.",
                 "A presión en su cavidad Ø5,2, con su resistencia en serie."),
                (-1, "C5", "Fototransistor", "foto", [0, 2, 0], "Receptor de cada barrera. Cuando una moneda corta el haz, dispara la interrupción del ESP32.",
                 "Frente al LED. Pull-up externo de 10 kΩ. GPIO 34, 35, 36, 39, 32, 33, 25, 26 y 27.")):
            cil = g.cil_eje((h, s * (hy + 1.0), up), (0, float(s), 0), 7.6, 2.5).translate(tuple(c0))
            add(pid, "Componentes", nombre, None, 9, "comp", col, cil, ex, desc, mont, tag=k)

    # ---------------- datos de la simulación (se calculan antes de la base) ----------------
    monedas_tmp = {}
    for i, (w, ms) in enumerate(g.RANURAS):
        for key, nombre, diam in ms:
            monedas_tmp[key] = dict(d=diam, den=DENOM[key], nombre=nombre, slot=i)
    slots_tmp = []
    for r in r_all:
        c0 = p_mundo(r.xc, r.yc, 0)
        s = dict(i=r.i, x0=r.x0, largo=r.largo, ancho=r.ancho, xc=r.xc, yc=r.yc, c0=list(c0),
                 nombre=f"D{r.i + 1}" if r.i != g.RANURA_500 else "D6")
        if r.i == g.RANURA_500:
            col = (g.COL_INT0 + g.COL_INT1) / 2
            s["fondo"] = {"D6a": list(c0 + np.array([-col, 0, -gd["t_bot"]])), "D6b": list(c0 + np.array([col, 0, -gd["t_bot"]]))}
            s["ir"] = {"D6a": float(c0[2] + gd["up_ir"]), "D6b": float(c0[2] + gd["up_ir"])}
        else:
            s["fondo"] = {s["nombre"]: list(c0 + np.array([0, 0, -ctx["largos"][r.i]]))}
            s["ir"] = {s["nombre"]: float(c0[2] - g.T_IR)}
        slots_tmp.append(s)

    # ---------------- base (no se imprime, salvo los codos P01 y P02) ----------------
    b = ctx["base"]
    X0, X1, Y0, Y1 = b["lamina"]
    (sx0, sx1), (sy0, sy1) = b["x_ranura"], b["y_ranura"]
    lam = g.caja(X0, X1, Y0, Y1, -g.LAMINA_E, 0) - g.caja(sx0, sx1, sy0, sy1, -g.LAMINA_E - 1, 1)
    add("M1", "Base", "Lámina de la base", None, 1, "ref", "mesa", lam, [0, 0, 2],
        "Lámina de MDF o acrílico de 6 mm, %d × %d mm, con una ranura de 38 mm por donde bajan los ductos. Sostiene riel, tolva y bifurcador." % (X1 - X0, Y1 - Y0),
        "Se apoya en los 4 esquineros P02 y se ata con bridas por sus agujeros de las esquinas. Las patas del riel y de la tolva se atan a ella.")
    r_b = g.BORE_R + g.PARED_PVC
    pvc = []
    for x in (b["xl"], b["xr"]):
        for y in (b["yf"], b["yb"]):
            pvc.append(g.cil_z(x, y, g.Z_PISO + g.PLACA_E + 2.0, -g.LAMINA_E - g.PLACA_E - 2.0, g.PVC_D))
    for y in (b["yf"], b["yb"]):
        for z in (b["z_eje_alto"], b["z_eje_bajo"]):
            pvc.append(g.cil_eje((b["xl"] + r_b, y, z), (1, 0, 0), b["l_x"], g.PVC_D / 2))
    for x in (b["xl"], b["xr"]):
        pvc.append(g.cil_eje((x, b["yf"] + r_b, b["z_eje_alto"]), (0, 1, 0), b["l_y"], g.PVC_D / 2))
    add("M3", "Base", "Tubos PVC de 3/4\"", None, 10, "ref", "pvc", g.union(pvc), [0, 0, -3],
        "Cuatro patas de %d mm, dos largueros altos y dos bajos de %d mm, y dos travesaños de %d mm. Tubo PVC de presión de 3/4\" (26,7 mm)." % (b["l_pata"], b["l_x"], b["l_y"]),
        "Entran a presión en los codos impresos (30 mm de penetración). Se pueden pegar con cemento PVC si quedan flojos.")
    for nombre, m in g.partes_ensamble(piezas_g, ctx):
        if nombre.startswith("P01"):
            add("P01", "Base", "Pie de pata", "P01_pie_pvc.stl", 4, "print", "marco", m, [0, 0, -1],
                "Placa con un alojamiento vertical para la pata y otro horizontal para el larguero bajo.",
                "Apoya en el piso. Los tubos entran a presión.")
        elif nombre.startswith("P02"):
            add("P02", "Base", "Esquinero", "P02_esquinero_pvc.stl", 4, "print", "marco", m, [0, 0, 1],
                "Placa que sostiene la lámina, con un alojamiento vertical para la pata y dos horizontales para los largueros altos.",
                "Los tubos entran por abajo a presión. La lámina se ata a la placa con bridas por los agujeros de las esquinas.")
    xm_all = sorted(((nm, v) for sl in slots_tmp for nm, v in sl["fondo"].items()), key=lambda t: t[1][0])
    Z_BANDA_ = g.Z_BOCA - VASO_H
    xs_c = [v[0] for _, v in xm_all]
    add("M2", "Base", "Banda transportadora", None, 1, "ref", "banda",
        g.caja(min(xs_c) - 60, max(xs_c) + 60, 12.0 - 35, 12.0 + 35, Z_BANDA_ - 8, Z_BANDA_), [0, 0, -3],
        "Lleva los nueve vasos hasta el punto A del brazo.", "Es la etapa 2; aquí solo marca la altura de los vasos. Pasa entre las patas de la base.")
    SALIDA_COIN = {"D6a": "A500", "D6b": "N500"}
    for sl in slots_tmp:
        if sl["nombre"] != "D6":
            SALIDA_COIN[sl["nombre"]] = next(k for k, m in monedas_tmp.items() if m["slot"] == sl["i"])
    cups = []
    for nm, pos in xm_all:
        key = SALIDA_COIN[nm]
        mo = monedas_tmp[key]
        x, y = float(pos[0]), float(pos[1])
        cups.append(dict(den=mo["den"], fam="antigua" if key[0] == "A" else "nueva", salida=nm, key=key, x=x, y=y, ztop=g.Z_BOCA))
        vaso = (g.cil_z(x, y, Z_BANDA_, g.Z_BOCA, VASO_D) - g.cil_z(x, y, Z_BANDA_ + 2.0, g.Z_BOCA + 1, VASO_D - 3.0))
        add("V", "Base", "Vaso", None, 9, "ref", "vaso", vaso, [0, 0, -3.5],
            "Uno por cada tipo de moneda, nueva y antigua por separado. Ø%d × %d mm, justo bajo la salida de su ducto." % (VASO_D, VASO_H),
            "El ducto baja hasta 6 mm sobre su boca: la moneda cae directo, sin mangueras.", tag=f"V{nm}")

    sim = dict(c22=C22, s22=S22, zoff=zoff, esp_base=g.ESP_BASE, tan_peralte=g.PERALTE_T, entrada=g.ENTRADA / 2,
               tolva=dict(c=[float(centro[0]), float(centro[1]), float(base_z)], cav_r=g.CAVIDAD_R),
               x_sensor=d.x_sensor, y_moneda=YS,
               d6=dict(c0=[float(v) for v in c6], t_piv=g.T_PIV, t_bot=gd["t_bot"], col=(g.COL_INT0 + g.COL_INT1) / 2,
                       incl=g.INCL_PLATO, pl_h=g.PLATO_H, pl_l=g.PLATO_L, hu=gd["hu"]),
               monedas=monedas_tmp, slots=slots_tmp, vasos=cups, z_banda=g.Z_BOCA - VASO_H, vaso_d=VASO_D, z_mesa=0.0)
    return out, sim


def main():
    piezas, sim = construir()
    datos = json.dumps({"piezas": piezas, "sim": sim}, separators=(",", ":"))
    html = PLANTILLA.read_text(encoding="utf-8").replace("/*DATOS*/null", datos)
    SALIDA.mkdir(parents=True, exist_ok=True)
    ruta = SALIDA / "ensamble_etapa1.html"
    ruta.write_text(html, encoding="utf-8")
    print(f"{len(piezas)} mallas, {len(html) / 1e6:.2f} MB -> {ruta}")


if __name__ == "__main__":
    main()
