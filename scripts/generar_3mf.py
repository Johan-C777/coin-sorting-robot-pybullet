"""Empaqueta todos los STL en un único proyecto .3mf con varias bandejas.

    python scripts/generar_3mf.py

Qué hace:
  * lee los STL de stl/, une vértices repetidos y deja cada malla apoyada en z = 0;
  * reparte las 52 piezas en bandejas de 220 x 220 mm por material y por familia,
    con un acomodo por estanterías y 6 mm de separación;
  * escribe un 3MF con el modelo (norma 3MF) más los metadatos de bandejas y de
    ajustes de impresión que leen OrcaSlicer y Bambu Studio;
  * pone ajustes por pieza donde hacen falta (perímetros y relleno).

Si el laminador no entiende las bandejas, igual abre el proyecto con todas las
piezas ya separadas por grupos y basta con usar «organizar todo».
"""
from __future__ import annotations

import csv
import json
import math
import struct
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple

RAIZ = Path(__file__).resolve().parents[1]
STL = RAIZ / "hardware" / "Modelos3D" / "stl"
SALIDA = RAIZ / "hardware" / "Modelos3D" / "sistema_monedas_completo.3mf"

# ----------------------------------------------------------------------
# Cama y acomodo
# ----------------------------------------------------------------------
CAMA_X, CAMA_Y = 220.0, 220.0
MARGEN = 8.0
SEPARACION = 6.0
PASO_BANDEJA = CAMA_X + 30.0          # separación entre bandejas en la escena

# ----------------------------------------------------------------------
# Material y ajustes por pieza. El primer valor agrupa las bandejas.
# ----------------------------------------------------------------------
GRUPOS = [
    ("PETG · etapa 1", [
        ("E01_riel_tramo_a.stl", 2, {"wall_loops": "4", "sparse_infill_density": "40%"}),
        ("E02_riel_tramo_b.stl", 2, {"wall_loops": "4", "sparse_infill_density": "40%"}),
        ("E03_canal_costado.stl", 4, {"wall_loops": "3", "sparse_infill_density": "30%"}),
        ("E04_abrazadera_varilla.stl", 4, {"wall_loops": "4", "sparse_infill_density": "40%"}),
        ("E06_paleta_dosificadora.stl", 1, {"wall_loops": "4", "sparse_infill_density": "60%"}),
        ("E08_soporte_sensor.stl", 5, {"wall_loops": "3", "sparse_infill_density": "30%"}),
        ("E09_rodillo_banda.stl", 2, {"wall_loops": "4", "sparse_infill_density": "30%"}),
        ("E10_marco_banda.stl", 6, {"wall_loops": "3", "sparse_infill_density": "25%"}),
        ("E11_portavaso.stl", 5, {"wall_loops": "3", "sparse_infill_density": "20%"}),
        ("E12_acople_motor.stl", 1, {"wall_loops": "5", "sparse_infill_density": "60%"}),
    ]),
    ("PLA · tolva y embudos", [
        ("E05_tolva.stl", 1, {"wall_loops": "3", "sparse_infill_density": "15%"}),
        ("E07_embudo_estacion1.stl", 1, {"wall_loops": "3", "sparse_infill_density": "12%"}),
        ("E07_embudo_estacion2.stl", 1, {"wall_loops": "3", "sparse_infill_density": "12%"}),
        ("E07_embudo_estacion3.stl", 1, {"wall_loops": "3", "sparse_infill_density": "12%"}),
        ("E07_embudo_estacion4.stl", 1, {"wall_loops": "3", "sparse_infill_density": "12%"}),
        ("E07_embudo_estacion5.stl", 1, {"wall_loops": "3", "sparse_infill_density": "12%"}),
        ("B12_bandeja_electronica.stl", 1, {"wall_loops": "3", "sparse_infill_density": "15%"}),
    ]),
    ("PETG · celda del brazo", [
        ("B11_puesto_rack.stl", 5, {"wall_loops": "3", "sparse_infill_density": "20%"}),
    ]),
    ("TPU o PETG · pies", [
        ("E13_pie_nivelador.stl", 8, {"wall_loops": "3", "sparse_infill_density": "30%"}),
    ]),
]

# ----------------------------------------------------------------------
# Ajustes generales del proyecto (claves de OrcaSlicer y Bambu Studio)
# ----------------------------------------------------------------------
AJUSTES = {
    "from": "project",
    "name": "Sistema de Logistica de Monedas Inteligentes",
    "version": "1.9.0.0",
    "layer_height": "0.2",
    "initial_layer_print_height": "0.25",
    "line_width": "0.42",
    "initial_layer_line_width": "0.5",
    "wall_loops": "4",
    "top_shell_layers": "5",
    "bottom_shell_layers": "4",
    "top_surface_pattern": "monotonic",
    "sparse_infill_density": "30%",
    "sparse_infill_pattern": "gyroid",
    "infill_direction": "45",
    "enable_support": "0",
    "support_type": "normal(auto)",
    "support_threshold_angle": "40",
    "brim_type": "outer_only",
    "brim_width": "4",
    "brim_object_gap": "0.1",
    "elefant_foot_compensation": "0.15",
    "seam_position": "aligned",
    "outer_wall_speed": "45",
    "inner_wall_speed": "80",
    "sparse_infill_speed": "120",
    "initial_layer_speed": "25",
    "travel_speed": "180",
    "reduce_crossing_wall": "1",
    "ironing_type": "no ironing",
    "detect_thin_wall": "1",
    "xy_hole_compensation": "0.05",
    "xy_contour_compensation": "0",
}


# ----------------------------------------------------------------------
# Lectura de STL binario
# ----------------------------------------------------------------------
def leer_stl(ruta: Path):
    """Devuelve (vertices, triangulos) con los vértices unificados."""
    with open(ruta, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        crudos = []
        for _ in range(n):
            d = struct.unpack("<12fH", f.read(50))
            crudos.append((d[3:6], d[6:9], d[9:12]))
    indice: Dict[Tuple[int, int, int], int] = {}
    vertices: List[Tuple[float, float, float]] = []
    triangulos: List[Tuple[int, int, int]] = []

    def idx(p):
        clave = (round(p[0] * 1e4), round(p[1] * 1e4), round(p[2] * 1e4))
        if clave not in indice:
            indice[clave] = len(vertices)
            vertices.append((p[0], p[1], p[2]))
        return indice[clave]

    for a, b, c in crudos:
        ia, ib, ic = idx(a), idx(b), idx(c)
        if ia != ib and ib != ic and ia != ic:
            triangulos.append((ia, ib, ic))
    return vertices, triangulos


def apoyar(vertices):
    """Lleva la pieza a x >= 0, y >= 0, z = 0 y devuelve su huella."""
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    dx, dy, dz = -min(xs), -min(ys), -min(zs)
    movidos = [(v[0] + dx, v[1] + dy, v[2] + dz) for v in vertices]
    return movidos, (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))


# ----------------------------------------------------------------------
# Acomodo por estanterías dentro de cada bandeja
# ----------------------------------------------------------------------
def acomodar(instancias):
    """Reparte las instancias en bandejas con un acomodo por estanterías.

    Para cada fila se toma primero la pieza más profunda que quepa y luego se
    rellena el hueco que queda con las piezas que entren, así no se desperdicia
    media bandeja cuando hay una pieza grande.
    """
    pendientes = sorted(instancias, key=lambda i: (-i["huella"][1], -i["huella"][0]))
    ancho_util = CAMA_X - 2 * MARGEN
    bandejas = []
    while pendientes:
        colocadas, y = [], MARGEN
        while True:
            fila = [i for i in pendientes
                    if y + i["huella"][1] <= CAMA_Y - MARGEN and i["huella"][0] <= ancho_util]
            if not fila:
                break
            primera = fila[0]
            pendientes.remove(primera)
            x = MARGEN
            primera["pos"] = (x, y)
            colocadas.append(primera)
            x += primera["huella"][0] + SEPARACION
            alto_fila = primera["huella"][1]
            while True:                                  # se rellena la fila
                caben = [i for i in pendientes
                         if i["huella"][0] <= CAMA_X - MARGEN - x and i["huella"][1] <= alto_fila]
                if not caben:
                    break
                it = caben[0]
                pendientes.remove(it)
                it["pos"] = (x, y)
                colocadas.append(it)
                x += it["huella"][0] + SEPARACION
            y += alto_fila + SEPARACION
        if not colocadas:
            raise SystemExit("hay una pieza que no cabe en la cama")
        bandejas.append(colocadas)
    return bandejas


def main() -> int:
    mallas = {}          # archivo -> (vertices, triangulos, huella)
    instancias_por_grupo = []
    for grupo, piezas in GRUPOS:
        lista = []
        for archivo, cantidad, ajustes in piezas:
            ruta = STL / archivo
            if not ruta.exists():
                raise SystemExit(f"falta {ruta}")
            if archivo not in mallas:
                v, t = leer_stl(ruta)
                v, huella = apoyar(v)
                mallas[archivo] = (v, t, huella)
            v, t, huella = mallas[archivo]
            for k in range(cantidad):
                lista.append({"archivo": archivo, "grupo": grupo, "ajustes": ajustes,
                              "huella": huella, "copia": k + 1, "total": cantidad})
        # las piezas grandes primero: el acomodo por estanterías aprovecha mejor
        lista.sort(key=lambda i: (-i["huella"][1], -i["huella"][0], i["archivo"]))
        instancias_por_grupo.append((grupo, acomodar(lista)))

    # ---------------- objetos del modelo ----------------
    objetos = {}         # archivo -> id
    for i, archivo in enumerate(sorted(mallas), start=1):
        objetos[archivo] = i

    bandejas = []
    for grupo, grupos_bandejas in instancias_por_grupo:
        for lista in grupos_bandejas:
            bandejas.append({"grupo": grupo, "instancias": lista})

    # ---------------- 3D/3dmodel.model ----------------
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<model unit="millimeter" xml:lang="en-US" '
           'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
           'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
           'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" '
           'requiredextensions="p">',
           ' <metadata name="Application">Sistema de Logistica de Monedas</metadata>',
           ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
           ' <metadata name="Copyright"></metadata>',
           ' <metadata name="Title">Piezas imprimibles del sistema</metadata>',
           ' <resources>']
    for archivo, oid in sorted(objetos.items(), key=lambda kv: kv[1]):
        v, t, _ = mallas[archivo]
        out.append(f'  <object id="{oid}" p:UUID="{oid:08d}-81cb-4c03-9d28-80fed5dfa1dc" '
                   f'type="model">')
        out.append('   <mesh>')
        out.append('    <vertices>')
        for x, y, z in v:
            out.append(f'     <vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>')
        out.append('    </vertices>')
        out.append('    <triangles>')
        for a, b, c in t:
            out.append(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>')
        out.append('    </triangles>')
        out.append('   </mesh>')
        out.append('  </object>')
    out.append(' </resources>')
    out.append(' <build>')

    identificador = 100
    for nb, bandeja in enumerate(bandejas):
        offset = nb * PASO_BANDEJA
        for inst in bandeja["instancias"]:
            oid = objetos[inst["archivo"]]
            x, y = inst["pos"]
            inst["identify_id"] = identificador
            identificador += 1
            out.append(f'  <item objectid="{oid}" '
                       f'p:UUID="{inst["identify_id"]:08d}-b206-40ff-9872-83e8017abed1" '
                       f'transform="1 0 0 0 1 0 0 0 1 {x + offset:.3f} {y:.3f} 0" printable="1"/>')
    out.append(' </build>')
    out.append('</model>')
    modelo = "\n".join(out)

    # ---------------- Metadata/model_settings.config ----------------
    cfg = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>']
    for archivo, oid in sorted(objetos.items(), key=lambda kv: kv[1]):
        ajustes = {}
        for _, piezas in GRUPOS:
            for a, _c, aj in piezas:
                if a == archivo:
                    ajustes = aj
        cfg.append(f'  <object id="{oid}">')
        cfg.append(f'    <metadata key="name" value="{archivo[:-4]}"/>')
        cfg.append('    <metadata key="extruder" value="1"/>')
        for k, val in ajustes.items():
            cfg.append(f'    <metadata key="{k}" value="{val}"/>')
        cfg.append(f'    <part id="{oid}" subtype="normal_part">')
        cfg.append(f'      <metadata key="name" value="{archivo[:-4]}"/>')
        cfg.append('      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>')
        cfg.append('    </part>')
        cfg.append('  </object>')

    for nb, bandeja in enumerate(bandejas, start=1):
        resumen = sorted({i["archivo"][:3] for i in bandeja["instancias"]})
        nombre = f'Bandeja {nb} - {bandeja["grupo"]} ({len(bandeja["instancias"])} piezas)'
        cfg.append('  <plate>')
        cfg.append(f'    <metadata key="plater_id" value="{nb}"/>')
        cfg.append(f'    <metadata key="plater_name" value="{nombre}"/>')
        cfg.append('    <metadata key="locked" value="false"/>')
        cfg.append('    <metadata key="filament_map_mode" value="Auto For Flush"/>')
        for inst in bandeja["instancias"]:
            cfg.append('    <model_instance>')
            cfg.append(f'      <metadata key="object_id" value="{objetos[inst["archivo"]]}"/>')
            cfg.append('      <metadata key="instance_id" value="0"/>')
            cfg.append(f'      <metadata key="identify_id" value="{inst["identify_id"]}"/>')
            cfg.append('    </model_instance>')
        cfg.append('  </plate>')
        bandeja["nombre"] = nombre
        bandeja["resumen"] = resumen
    cfg.append('</config>')
    model_settings = "\n".join(cfg)

    # ---------------- Metadata/project_settings.config ----------------
    proyecto = dict(AJUSTES)
    proyecto["print_settings_id"] = "Sistema monedas 0.2 mm"
    ajustes_json = json.dumps(proyecto, indent=1, ensure_ascii=False)

    # ---------------- archivos auxiliares ----------------
    content_types = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
                     ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
                     ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
                     ' <Default Extension="png" ContentType="image/png"/>\n'
                     ' <Default Extension="config" ContentType="text/xml"/>\n'
                     '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            ' <Relationship Id="rel-1" Target="/3D/3dmodel.model" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
            '</Relationships>')

    resumen_txt = ["Sistema de Logistica de Monedas Inteligentes",
                   f"{len(objetos)} piezas distintas, "
                   f"{sum(len(b['instancias']) for b in bandejas)} copias, "
                   f"{len(bandejas)} bandejas de {CAMA_X:.0f} x {CAMA_Y:.0f} mm", ""]
    for nb, b in enumerate(bandejas, start=1):
        detalle = {}
        for i in b["instancias"]:
            detalle[i["archivo"][:-4]] = detalle.get(i["archivo"][:-4], 0) + 1
        resumen_txt.append(f"{b['nombre']}")
        for k in sorted(detalle):
            resumen_txt.append(f"   {k} x{detalle[k]}")
        resumen_txt.append("")

    with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", modelo)
        z.writestr("Metadata/model_settings.config", model_settings)
        z.writestr("Metadata/project_settings.config", ajustes_json)
        z.writestr("Metadata/bandejas.txt", "\n".join(resumen_txt))

    print(f"{SALIDA.name}: {len(objetos)} objetos, "
          f"{sum(len(b['instancias']) for b in bandejas)} piezas, "
          f"{len(bandejas)} bandejas, {SALIDA.stat().st_size/1024:.0f} kB")
    for nb, b in enumerate(bandejas, start=1):
        alto = max(mallas[i["archivo"]][2][2] for i in b["instancias"])
        print(f"  {nb}. {b['nombre']:58s} alto máx {alto:6.1f} mm")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
