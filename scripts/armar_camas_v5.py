"""Arma camas .3mf (K1C, 220x220) desde los STL v5, ya orientados.

Uso: python scripts/armar_camas_v5.py hardware/etapa1-clasificador/stl hardware/etapa1-clasificador/impresion
Regenera las camas 2, 3 y 7 (ver impresion/CAMAS.md); las demás son de una sola pieza repetida."""
import struct, sys, zipfile, os
import numpy as np

BED, MARGEN, GAP = 220.0, 5.0, 5.0
CAMAS = {
 "cama2_PLA+negro_disco_soportes_clavijas": [("H02_disco",1),("K01_soporte_tolva_pista",1),("K02_soporte_pista",1),("P01_clavija_20mm",19)],
 "cama3_PLA+negro_embudo_cartucho_prueba": [("F01_embudo",1),("C01_cartucho",1),("C02_rampa_rechazo",1),("V01_vaso",2),("P02_clavija_12mm",6)],
 "cama7_PLA_verde_vasos_cartuchos_compuerta": [("V01_vaso",7),("C01_cartucho",2),("G01_cuna_servo",1),("G02_compuerta",1)],
}
BRIM = {"G02_compuerta": 4.0}   # margen extra por pieza

def stl(path):
    b = open(path, "rb").read()
    n = struct.unpack("<I", b[80:84])[0]
    d = np.frombuffer(b[84:84+n*50], dtype=np.dtype([("n","<3f4"),("v","<9f4"),("a","<u2")]))
    return d["v"].reshape(-1,3,3).astype(float)

def pack(items):
    # estantes: piezas altas primero
    items = sorted(items, key=lambda t: -(t[2][1]+2*BRIM.get(t[0],0)))
    x = y = MARGEN; fila = 0; out = []
    for name, tri, (w, h) in items:
        m = BRIM.get(name, 0); w2, h2 = w+2*m, h+2*m
        if x + w2 > BED-MARGEN: x = MARGEN; y += fila + GAP; fila = 0
        if y + h2 > BED-MARGEN: raise SystemExit(f"no cabe {name}")
        out.append((name, tri, x+m, y+m)); x += w2 + GAP; fila = max(fila, h2)
    return out

def escribe(path, placed):
    objs, items = [], []
    cnt = {}
    for i, (name, tri, ox, oy) in enumerate(placed, 1):
        mn = tri.reshape(-1,3).min(0)
        t = tri - mn + np.array([ox, oy, 0.0])
        verts, idx = {}, []
        for tt in t.reshape(-1,3):
            k = tuple(np.round(tt, 4)); verts.setdefault(k, len(verts)); idx.append(verts[k])
        vs = "".join(f'<vertex x="{a}" y="{b}" z="{c}"/>' for a,b,c in verts)
        ts = "".join(f'<triangle v1="{idx[j]}" v2="{idx[j+1]}" v3="{idx[j+2]}"/>' for j in range(0,len(idx),3))
        cnt[name] = cnt.get(name,0)+1
        nm = f"{name}_{cnt[name]}"
        objs.append(f'<object id="{i}" name="{nm}" type="model"><mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>')
        items.append(f'<item objectid="{i}" partnumber="{nm}"/>')
    model = ('<?xml version="1.0" encoding="utf-8"?><model xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" unit="millimeter">'
             f'<resources>{"".join(objs)}</resources><build>{"".join(items)}</build></model>')
    ct = '<?xml version="1.0" encoding="utf-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels = '<?xml version="1.0" encoding="utf-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" Target="/3D/3dmodel.model" Id="rel0"/></Relationships>'
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct); z.writestr("_rels/.rels", rels); z.writestr("3D/3dmodel.model", model)

if __name__ == "__main__":
    src, dst = sys.argv[1:3]
    os.makedirs(dst, exist_ok=True)
    for cama, piezas in CAMAS.items():
        items = []
        for name, q in piezas:
            tri = stl(os.path.join(src, name + ".stl")); mn, mx = tri.reshape(-1,3).min(0), tri.reshape(-1,3).max(0)
            items += [(name, tri, (mx[0]-mn[0], mx[1]-mn[1]))]*q
        placed = pack(items); escribe(os.path.join(dst, cama + ".3mf"), placed)
        print(cama, len(placed), "piezas")
