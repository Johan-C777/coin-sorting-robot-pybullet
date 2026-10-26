"""Exporta los STL de la banda (v2 sin herrajes) en posicion de impresion y arma las camas.

    python camas.py salida/        # salida/stl/*.stl, salida/camas/*.stl, salida/CAMAS.md
Cada cama es un solo STL con las piezas ya acomodadas en la cama de 220 x 220 de la K1C.
"""
import math
import sys
from pathlib import Path

import numpy as np
from manifold3d import Manifold

import generar_banda as g

CAMA = 220.0
MARGEN, SEP = 4.0, 5.0

# pid -> (nombre de archivo, descripcion, material, relleno, rotacion de impresion, cantidad, notas)
ORI = {
    'BT01': ('modulo-motor', 'Módulo del motor', 'PETG', '20 %', (180, 0, 0), 1, 'Cama de la banda abajo. El cubo del muñón sale de la pared: hay un voladizo corto bajo el cubo.'),
    'BT02': ('modulo-2', 'Módulo 2', 'PETG', '20 %', (180, 0, 0), 1, 'Cama abajo.'),
    'BT03': ('modulo-3', 'Módulo 3 (bajo la torre)', 'PETG', '20 %', (180, 0, 0), 1, 'Cama abajo.'),
    'BT04': ('modulo-4', 'Módulo 4', 'PETG', '20 %', (180, 0, 0), 1, 'Cama abajo.'),
    'BT05': ('modulo-5', 'Módulo 5', 'PETG', '20 %', (180, 0, 0), 1, 'Cama abajo.'),
    'BT06': ('modulo-6', 'Módulo 6', 'PETG', '20 %', (180, 0, 0), 1, 'Cama abajo.'),
    'BT07': ('modulo-tensor', 'Módulo del tensor', 'PETG', '20 %', (180, 0, 0), 1, 'Cama abajo. La oreja del tornillo queda hacia arriba.'),
    'BT08G1': ('guia-menos-Y-tramo1', 'Guía −Y, tramo 1 (con el hueco del fototransistor)', 'PLA', '20 %', (180, 0, 0), 1, 'Ala abajo, labio hacia arriba.'),
    'BT08G2': ('guia-menos-Y', 'Guía −Y, tramos 2 a 5', 'PLA', '20 %', (180, 0, 0), 4, 'Ala abajo, labio hacia arriba.'),
    'BT09G1': ('guia-mas-Y-tramo1', 'Guía +Y, tramo 1 (con el hueco del LED)', 'PLA', '20 %', (180, 0, 0), 1, 'Ala abajo, labio hacia arriba.'),
    'BT09G2': ('guia-mas-Y', 'Guía +Y, tramos 2 a 5', 'PLA', '20 %', (180, 0, 0), 4, 'Ala abajo, labio hacia arriba.'),
    'BT10': ('rodillo-motriz', 'Rodillo motriz', 'PETG', '40 %, 4 paredes', (90, 0, 0), 1, 'De pie sobre el muñón corto. Soportes de árbol sólo bajo el disco de la base. Las estrías de agarre quedan en la pared del cilindro.'),
    'BT11': ('rodillo-libre', 'Rodillo libre', 'PETG', '40 %, 4 paredes', (90, 0, 0), 1, 'De pie sobre el muñón corto. Soportes de árbol sólo bajo el disco de la base.'),
    'BT12P': ('carro-tensor-mas-Y', 'Carro del tensor +Y', 'PETG', '40 %, 4 paredes', (-90, 0, 0), 1, 'Plano, con el agujero del muñón hacia arriba.'),
    'BT12M': ('carro-tensor-menos-Y', 'Carro del tensor −Y', 'PETG', '40 %, 4 paredes', (90, 0, 0), 1, 'Plano, con el agujero del muñón hacia arriba.'),
    'BT13': ('tapa-motor', 'Tapa motor (−Y)', 'PETG', '20 %', (-90, 0, 0), 1, 'Cara interior abajo, cubo del muñón hacia arriba.'),
    'BT14': ('tapa-tensor', 'Tapa tensor (−Y)', 'PETG', '20 %', (-90, 0, 0), 1, 'Cara interior abajo, oreja hacia arriba.'),
    'BT15': ('soporte-nema17', 'Soporte del NEMA17', 'PETG', '30 %, 4 paredes', (-90, 0, 0), 1, 'Boca de la bolsa hacia la cama. Puente de 43 mm sobre la bolsa: soporte de árbol sólo bajo la placa.'),
    'BT16': ('pata', 'Pata', 'PETG', '20 %', (0, 0, 0), 7, 'Como está: el zócalo plano en la cama y la placa de pie.'),
    'BT17': ('clavija-6x12', 'Clavija Ø6 × 12 (P02)', 'PETG', '100 %', (0, -90, 0), 72, 'De pie. Imprime todas juntas; 64 + 8 de repuesto.'),
    'BT18': ('tornillo-tensor', 'Tornillo del tensor', 'PETG', '100 %', (0, 90, 0), 2, 'Cabeza abajo. La rosca no necesita soportes.'),
    'BT19': ('acople', 'Acople hexágono + D', 'PETG', '100 %', (90, 0, 0), 1, 'De pie sobre la boca hexagonal.'),
}


def prueba():
    """Pieza de prueba de tolerancias: bloque con agujero de muñón, de clavija y de rosca, mas un muñón."""
    b = g.caja(0, 40, 0, 40, 0, 14)
    b = b - g.cil_z(10, 10, -1, 15, g.PIN_H) - g.cil_z(10, 30, -1, 15, g.PEG_H)
    r = g.hilo(-1, 15, 0, 0, g.HILO_JUEGO).rotate((0, -90, 0))      # eje X -> Z
    r = r.translate((30, 20, 0))
    b = b - r
    muñon = g.cil_z(55, 10, 0, 20, g.PIN_D)
    rosca = g.hilo(0, 24, 0, 0).rotate((0, -90, 0)).translate((55, 30, 0))
    return b + muñon + rosca


def pose(m, rot):
    m = m.rotate(rot) if any(rot) else m
    x0, y0, z0, x1, y1, z1 = m.bounding_box()
    return m.translate((-x0, -y0, -z0)), (x1 - x0, y1 - y0, z1 - z0)


def stl_bytes(meshes):
    tris = []
    for m in meshes:
        mm = m.to_mesh()
        v = np.asarray(mm.vert_properties, dtype=np.float64)[:, :3]
        t = np.asarray(mm.tri_verts, dtype=np.int64)
        tris.append(v[t])
    t = np.concatenate(tris)
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    out = np.zeros(len(t), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    out['n'], out['v'] = n, t
    return b'\0' * 80 + np.uint32(len(t)).tobytes() + out.tobytes()


def empacar(items):
    """Estantes de izquierda a derecha; prueba cada pieza girada 90 grados. Devuelve camas [[(item, x, y, giro)]]."""
    util = CAMA - 2 * MARGEN
    camas = []
    for it in sorted(items, key=lambda i: -max(i['w'], i['d'])):
        puesto = False
        for cama in camas:
            for giro in (0, 1):
                w, d = (it['w'], it['d']) if not giro else (it['d'], it['w'])
                for x, y in cama['candidatos']:
                    if x + w <= util and y + d <= util and not any(
                            x < o['x'] + o['w'] + SEP and o['x'] < x + w + SEP and y < o['y'] + o['d'] + SEP and o['y'] < y + d + SEP
                            for o in cama['puestos']):
                        cama['puestos'].append(dict(it=it, x=x, y=y, w=w, d=d, giro=giro))
                        cama['candidatos'] += [(x + w + SEP, y), (x, y + d + SEP)]
                        puesto = True
                        break
                if puesto:
                    break
            if puesto:
                break
        if not puesto:
            w, d = it['w'], it['d']
            camas.append(dict(puestos=[dict(it=it, x=0, y=0, w=w, d=d, giro=0)], candidatos=[(0, 0), (w + SEP, 0), (0, d + SEP)]))
    return camas


def main():
    out = Path(sys.argv[1])
    (out / 'stl').mkdir(parents=True, exist_ok=True)
    (out / 'camas').mkdir(exist_ok=True)
    P = g.piezas()
    por = {}
    for pid, m, ex in P:
        tag = ex.get('tag', '')
        key = pid + (tag if pid in ('BT08', 'BT09') else ('P' if tag == '+Y' and pid == 'BT12' else ('M' if tag == '-Y' and pid == 'BT12' else '')))
        if pid in ('BT08', 'BT09') and tag not in ('G1', 'G2'):
            continue
        if pid == 'BT18' and tag == '-Y':
            continue
        if pid == 'BT16' and key in por:
            continue
        por[key] = m
    piezas = []
    for key, (arch, nom, mat, relleno, rot, cant, nota) in ORI.items():
        m, (w, d, h) = pose(por[key], rot)
        fn = f"{key}_{arch}.stl"
        (out / 'stl' / fn).write_bytes(stl_bytes([m]))
        piezas.append(dict(key=key, arch=arch, nom=nom, mat=mat, relleno=relleno, cant=cant, nota=nota, m=m, w=w, d=d, h=h, vol=m.volume() / 1000.0, fn=fn))
    pr, (w, d, h) = pose(prueba(), (0, 0, 0))
    (out / 'stl' / 'BT00_prueba-tolerancias.stl').write_bytes(stl_bytes([pr]))
    prueba_p = dict(key='BT00', arch='prueba-tolerancias', nom='Prueba de tolerancias', mat='PETG', relleno='100 %', cant=1,
                    nota='Muñón en agujero de 10,4, clavija en 6,2 y rosca con 0,35 mm de juego. Imprímela primero.',
                    m=pr, w=w, d=d, h=h, vol=pr.volume() / 1000.0, fn='BT00_prueba-tolerancias.stl')
    for pz in piezas:
        assert pz['h'] <= 250, pz['key']
    # camas por material, la prueba va sola
    camas = [('00', 'PETG', [dict(prueba_p, i=1)])]
    n = 1
    for mat in ('PETG', 'PLA'):
        items = []
        for pz in piezas:
            if pz['mat'] != mat:
                continue
            for i in range(pz['cant']):
                items.append(dict(pz, i=i + 1))
        # las clavijas y los tornillos van juntos en una cama aparte al 100 %
        pequenas = [i for i in items if i['key'] in ('BT17', 'BT18', 'BT19')]
        grandes = [i for i in items if i['key'] not in ('BT17', 'BT18', 'BT19')]
        for grupo in (grandes, pequenas):
            if not grupo:
                continue
            for cama in empacar(grupo):
                camas.append((f"{n:02d}", mat, [dict(p['it'], px=p['x'], py=p['y'], giro=p['giro']) for p in cama['puestos']]))
                n += 1
    # cama 00 con coordenadas
    camas[0] = ('00', 'PETG', [dict(prueba_p, i=1, px=0, py=0, giro=0)])
    filas = []
    for num, mat, its in camas:
        meshes = []
        for it in its:
            m = it['m']
            if it.get('giro'):
                m = m.rotate((0, 0, 90))
                x0, y0, z0, x1, y1, z1 = m.bounding_box()
                m = m.translate((-x0, -y0, -z0))
            meshes.append(m.translate((it['px'] + MARGEN, it['py'] + MARGEN, 0)))
        (out / 'camas' / f"cama-{num}_{mat}.stl").write_bytes(stl_bytes(meshes))
        filas.append((num, mat, its))
    escribir_md(out, filas, piezas, prueba_p)
    print(len(filas), 'camas', len(piezas) + 1, 'STL')


def gramos(pz):
    f = 1.0 if pz['relleno'].startswith('100') else 0.6
    dens = 1.27 if pz['mat'] == 'PETG' else 1.24
    return pz['vol'] * dens * f


def escribir_md(out, filas, piezas, prueba_p):
    L = []
    L.append("# Banda transportadora (etapa 2): camas de impresión\n")
    L.append("Para la torre de la etapa 1 v5. Impresora: Creality K1C, cama 220 × 220 × 250. Sin tornillos, tuercas ni rodamientos: todo se une con clavijas Ø6 × 12, muñones y un tornillo impreso.\n")
    L.append("Archivos: `stl/` tiene cada pieza en su posición de impresión; `camas/` tiene cada cama ya acomodada en un solo STL. Si prefieres acomodar tú, usa `stl/`.\n")
    L.append("## Ajustes\n")
    L.append("- Boquilla 0,4, capa 0,2 mm, 3 paredes y 20 % de relleno salvo que la tabla diga otra cosa (lo que carga o gira lleva 4 paredes y más relleno).")
    L.append("- PETG para lo estructural y lo que gira, PLA para las guías. Sin soportes salvo donde se indica.")
    L.append("- Compensación de agujeros: ninguna. Las holguras ya están en el modelo (muñón 10 en 10,4; clavija 6 en 6,2; rosca con 0,35 mm).")
    L.append("- Las estimaciones de peso son aproximadas (relleno y paredes cambian el resultado).\n")
    L.append("## Orden\n")
    L.append("1. **Cama 00, prueba de tolerancias.** Mete el muñón en el agujero de 10,4, una clavija en el de 6,2 y atornilla la rosca en el bloque. Si algo queda flojo o no entra, dime la medida y lo corrijo antes de imprimir lo demás.")
    L.append("2. Camas de PETG en el orden de abajo (primero las clavijas, que se necesitan para armar).")
    L.append("3. Cama de guías en PLA al final.\n")
    L.append("## Camas\n")
    tot = 0.0
    for num, mat, its in filas:
        L.append(f"### Cama {num} · {mat}\n")
        L.append("| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |")
        L.append("|---|---|---|---|---|---|")
        cuenta = {}
        for it in its:
            cuenta.setdefault(it['key'], [it, 0])[1] += 1
        gt = 0
        for key, (it, c) in cuenta.items():
            w, d, h = (it['d'], it['w'], it['h']) if it.get('giro') else (it['w'], it['d'], it['h'])
            gg = gramos(it) * c
            gt += gg
            L.append(f"| `{it['fn']}` | {it['nom']} | {c} | {it['relleno']} | {w:.0f} × {d:.0f} × {h:.0f} | {gg:.0f} |")
        tot += gt
        notas = sorted({it['nota'] for it in its})
        L.append("")
        for n_ in notas:
            L.append(f"- {n_}")
        L.append(f"- Peso aproximado de la cama: {gt:.0f} g.\n")
    L.append(f"Total aproximado: **{tot:.0f} g** en {len(filas)} camas.\n")
    L.append("## Cantidades que hay que imprimir\n")
    L.append("| Pieza | Cant. | Material |")
    L.append("|---|---|---|")
    for pz in piezas:
        L.append(f"| `{pz['fn']}` | {pz['cant']} | {pz['mat']} |")
    L.append("\n## Cosas a vigilar al imprimir\n")
    L.append("- **Rodillos:** quedan con el eje vertical para que giren redondos, pero así las capas cruzan el muñón. Imprímelos con 4 paredes y mira que el muñón no tenga huecos. Si uno se parte, avísame y lo paso a otra orientación.")
    L.append("- **Muñones:** una gota de grasa de silicona en los agujeros al armar. Si aparece juego, se reimprime el rodillo.")
    L.append("- **Clavijas de módulos, patas y soporte del motor:** se pegan con cianoacrilato. Las de guías y tapas no, porque se sacan para meter la cinta.")
    L.append("- **Bolsa del motor:** el NEMA17 entra por atrás con un poco de fuerza. Si queda flojo, una gota de cianoacrilato en las esquinas.")
    (out / 'CAMAS.md').write_text("\n".join(L) + "\n")


if __name__ == '__main__':
    main()
