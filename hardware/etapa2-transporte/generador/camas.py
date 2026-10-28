"""Exporta los STL de la banda (v2b, cadena de tablillas) en posicion de impresion y arma las camas.

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

# clave -> (archivo, descripción, filamento, relleno, rotación de impresión, cantidad, nota)
PETG = 'PETG Azul 4DLAB'
PLA_M = 'PLA+ Mármol 4DLAB'
PLA_A = 'PLA+ Azul 4DLAB'
PLA_N = 'PLA+ Negro 4DLAB'
R_VOLT, R_PY, R_MY, R_MX, R_PX, R_0 = (180, 0, 0), (-90, 0, 0), (90, 0, 0), (0, -90, 0), (0, 90, 0), (0, 0, 0)
ORI = {
    'BT01': ('modulo-1-motor', 'Módulo 1 (motor)', PETG, '15 %, 3 paredes', R_VOLT, 1, 'Piso contra la cama. Sin soportes.'),
    'BT02': ('modulo-2', 'Módulo 2', PLA_M, '15 %, 3 paredes', R_VOLT, 1, 'Piso contra la cama. Sin soportes.'),
    'BT03': ('modulo-3', 'Módulo 3 (bajo la torre)', PLA_M, '15 %, 3 paredes', R_VOLT, 1, 'Piso contra la cama. Sin soportes.'),
    'BT04': ('modulo-4', 'Módulo 4', PLA_M, '15 %, 3 paredes', R_VOLT, 1, 'Piso contra la cama. Sin soportes.'),
    'BT05': ('modulo-5', 'Módulo 5', PLA_M, '15 %, 3 paredes', R_VOLT, 1, 'Piso contra la cama. Sin soportes.'),
    'BT06': ('modulo-6-tensor', 'Módulo 6 (tensor)', PLA_M, '15 %, 3 paredes', R_VOLT, 1, 'Piso contra la cama. Sin soportes.'),
    'BT07': ('tapa-motor', 'Tapa lateral del motor (−Y)', PETG, '20 %, 3 paredes', R_PY, 1, 'Acostada sobre la cara interior.'),
    'BT08': ('tapa-tensor', 'Tapa lateral del tensor (−Y)', PLA_M, '20 %, 3 paredes', R_PY, 1, 'Acostada sobre la cara interior.'),
    'BT09G1': ('guia-menos-Y-tramo1', 'Guía −Y, tramo 1 (hueco del fototransistor)', PLA_N, '15 %, 3 paredes', R_VOLT, 1, 'Ala abajo, labio arriba.'),
    'BT09G2': ('guia-menos-Y', 'Guía −Y, tramos 2 a 5', PLA_N, '15 %, 3 paredes', R_VOLT, 4, 'Ala abajo, labio arriba.'),
    'BT10G1': ('guia-mas-Y-tramo1', 'Guía +Y, tramo 1 (hueco del LED)', PLA_N, '15 %, 3 paredes', R_VOLT, 1, 'Ala abajo, labio arriba.'),
    'BT10G2': ('guia-mas-Y', 'Guía +Y, tramos 2 a 5', PLA_N, '15 %, 3 paredes', R_VOLT, 4, 'Ala abajo, labio arriba.'),
    'BT11': ('eje-motriz', 'Eje motriz', PETG, '100 %', R_0, 1, 'Tumbado (las capas corren a lo largo del eje). Borde (brim) de 5 mm. Es lo único redondo apoyado en una línea: el arco de abajo es chico y sale limpio.'),
    'BT12': ('eje-libre', 'Eje libre', PETG, '100 %', R_0, 1, 'Tumbado, igual que el motriz.'),
    'BT13P': ('carro-tensor-mas-Y', 'Carro del tensor +Y', PETG, '40 %, 4 paredes', R_MX, 1, 'De pie sobre la cola roscada. Sin soportes.'),
    'BT13M': ('carro-tensor-menos-Y', 'Carro del tensor −Y', PETG, '40 %, 4 paredes', R_MX, 1, 'De pie sobre la cola roscada. Sin soportes.'),
    'BT14': ('tornillo-tensor', 'Tornillo del tensor', PETG, '100 %', R_PX, 2, 'De pie sobre el extremo de la rosca; la cabeza queda arriba.'),
    'BT15': ('soporte-nema17', 'Soporte del NEMA17', PETG, '30 %, 4 paredes', R_MY, 1, 'La base contra la cama; la jaula se cierra en cono. Sin soportes.'),
    'BT16': ('acople', 'Acople hexágono + D', PETG, '100 %', R_PY, 1, 'Sin soportes.'),
    'BT17': ('rueda-dentada', 'Rueda dentada de 8 dientes', PETG, '100 %', R_PY, 2, 'Plana. La motriz y la libre son iguales.'),
    'BT18': ('pata', 'Pata', PLA_M, '20 %, 3 paredes', R_0, 6, 'Acostada. Las clavijas en gota quedan horizontales y salen sin soportes.'),
    'BT19': ('seccion-cadena', 'Sección de cadena (14 eslabones articulados)', PLA_A, '100 %', R_VOLT, 12, 'Print-in-place: sale ya articulada. Tapa lisa contra la cama.'),
}
STOCK = {PETG: 429, PLA_M: 1000, PLA_A: 1000, PLA_N: 647}
TEMP = {PETG: '230–250 °C', PLA_M: '200–230 °C', PLA_A: '200–230 °C', PLA_N: '200–230 °C'}


def prueba():
    """Pieza de prueba: dos tramos de 3 eslabones articulados (uno con la presilla) + bloque con agujero de muñón, zócalo de clavija y clavija en gota."""
    def tramo(n, primero):
        return g.union([g.tablilla(i * g.PASO, 0, primero=primero and i == 0) for i in range(n)])
    t1 = tramo(3, False).rotate((180, 0, 0))
    t2 = tramo(3, True).rotate((180, 0, 0))
    def alza(m, y):
        x0, y0, z0, x1, y1, z1 = m.bounding_box()
        return m.translate((-x0, y - y0, -z0))
    t1, t2 = alza(t1, 0), alza(t2, 62)
    bq = g.caja(0, 40, 0, 40, 0, 14)
    bq = bq - g.hueco_y(10, 7, -1, 41, g.PIN_H) - g.hueco_y(30, 7, 3, 41, g.PEG_H)
    bq = bq.translate((60, 0, 0))
    cl = g.clavija_y(0, 0, 0, g.PEG_L, g.PEG_D).rotate((0, 0, 0))
    x0, y0, z0, x1, y1, z1 = cl.bounding_box()
    cl = cl.translate((60 - x0, 130 - y0, -z0))
    return t1 + t2 + bq + cl


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
    por = {}
    for pid, m, ex in g.piezas():
        tag = ex.get('tag', '')
        if pid in ('BT09', 'BT10'):
            if tag not in ('G1', 'G2'):
                continue
            por[pid + tag] = m
        elif pid == 'BT13':
            por['BT13' + ('P' if tag == '+Y' else 'M')] = m
        elif pid == 'BT14':
            por.setdefault('BT14', m)
        elif pid == 'BT17':
            por.setdefault('BT17', m)
        elif pid == 'BT18':
            por.setdefault('BT18', m)
        elif pid in ORI:
            por[pid] = m
    piezas = []
    for key, (arch, nom, mat, relleno, rot, cant, nota) in ORI.items():
        m, (w, d, h) = pose(por[key], rot)
        fn = f"{key}_{arch}.stl"
        (out / 'stl' / fn).write_bytes(stl_bytes([m]))
        piezas.append(dict(key=key, arch=arch, nom=nom, mat=mat, relleno=relleno, cant=cant, nota=nota, m=m, w=w, d=d, h=h, vol=m.volume() / 1000.0, fn=fn))
    pr, (w, d, h) = pose(prueba(), (0, 0, 0))
    (out / 'stl' / 'BT00_prueba-tolerancias.stl').write_bytes(stl_bytes([pr]))
    prueba_p = dict(key='BT00', arch='prueba-tolerancias', nom='Prueba de tolerancias', mat=PLA_A, relleno='100 %', cant=1,
                    nota='Dos tramos de 3 eslabones, uno con la presilla; un bloque con agujero de eje, zócalo de clavija y una clavija en gota.',
                    m=pr, w=w, d=d, h=h, vol=pr.volume() / 1000.0, fn='BT00_prueba-tolerancias.stl')
    for pz in piezas:
        assert pz['h'] <= 250 and max(pz['w'], pz['d']) <= 212, pz['key']
    camas = [('00', PLA_A, [dict(prueba_p, i=1, px=0, py=0, giro=0)])]
    n = 1
    for mat in (PETG, PLA_A, PLA_M, PLA_N):
        items = []
        for pz in piezas:
            if pz['mat'] == mat:
                items += [dict(pz, i=i + 1) for i in range(pz['cant'])]
        for cama in empacar(items):
            camas.append((f"{n:02d}", mat, [dict(p['it'], px=p['x'], py=p['y'], giro=p['giro']) for p in cama['puestos']]))
            n += 1
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
        sl = mat.replace('+', 'mas').replace('á', 'a').replace('ó', 'o').split()
        (out / 'camas' / f"cama-{num}_{sl[0]}-{sl[1].lower()}.stl").write_bytes(stl_bytes(meshes))
        filas.append((num, mat, its))
    escribir_md(out, filas, piezas, prueba_p)
    print(len(filas), 'camas', len(piezas) + 1, 'STL')


def gramos(pz):
    f = 1.0 if pz['relleno'].startswith('100') else 0.6
    dens = 1.27 if pz['mat'].startswith('PETG') else 1.24
    return pz['vol'] * dens * f


def escribir_md(out, filas, piezas, prueba_p):
    L = []
    L.append("# Banda transportadora (etapa 2): camas de impresión (versión print-and-place)\n")
    L.append("Para la torre de la etapa 1 v5. Impresora: Creality K1C, cama 220 × 220 × 250. Sin rodamientos, tornillos, tuercas ni correa. "
             "Son **46 piezas** en vez de unas 460: la cadena sale en 12 secciones ya articuladas, el bastidor en 6 módulos grandes con rompecabezas, "
             "las clavijas y los pasadores sueltos desaparecieron (van fundidos en la pieza) y no hay piezas de menos de 18 mm salvo las 2 ruedas, el acople y los tornillos.\n")
    L.append("Archivos: `stl/` tiene cada pieza en su posición de impresión; `camas/` tiene cada cama ya acomodada en un solo STL. Si prefieres acomodar tú, usa `stl/`.\n")
    L.append("## Ajustes\n")
    L.append("- Capa 0,2 mm, boquilla 0,4, **sin soportes en ninguna pieza**. Paredes y relleno por pieza en las tablas.")
    L.append("- Compensación de agujeros: ninguna. Las holguras ya están en el modelo (0,3 mm por lado en las articulaciones de la cadena).")
    L.append("- Desactiva el «elephant foot» compensation si tu perfil lo trae muy alto: en la cadena las primeras capas deben quedar libres de rebaba.")
    L.append("- Piezas largas (módulos de 192–204 mm): usa borde (brim) de 3 mm y limpia la cama; son las que más se curvan.\n")
    L.append("## Filamentos (inventario del 2026-10-28)\n")
    L.append("| Filamento | Para qué | Gramos necesarios | Hay | Sobra | Temp. |")
    L.append("|---|---|---|---|---|---|")
    uso = {PETG: 'Módulo del motor, tapa del motor, ejes, ruedas, acople, soporte NEMA, carros y tornillos del tensor',
           PLA_M: 'Módulos 2 a 6, tapa del tensor y patas',
           PLA_A: 'Las 12 secciones de cadena y la cama 00 de prueba',
           PLA_N: 'Guías laterales (10)'}
    need = {}
    for num, mat, its in filas:
        need[mat] = need.get(mat, 0) + sum(gramos(it) for it in its)
    for mat in (PETG, PLA_M, PLA_A, PLA_N):
        L.append(f"| {mat} | {uso[mat]} | {need.get(mat, 0):.0f} g | {STOCK[mat]} g | {STOCK[mat] - need.get(mat, 0):.0f} g | {TEMP[mat]} |")
    L.append("")
    L.append("- El PETG (429 g) sólo va a lo que gira o está junto al motor. La cadena va en PLA+ Azul porque necesita ≈ 640 g; el bastidor y las guías van en PLA+ porque no trabajan en caliente ni a flexión.")
    L.append("- Los gramos son una estimación por exceso (el relleno real de 15 % pesa menos).")
    L.append("- Si la presilla de la cadena se parte en la prueba (cama 00), reimprime sólo el primer eslabón de cada sección en PETG o baja la velocidad de las paredes a 60 mm/s y sube 5 °C.\n")
    L.append("## Orden de impresión\n")
    L.append("1. **Cama 00 (prueba, ≈ 25 min).** Dobla los dos tramos de eslabones: deben girar libres sin holgura exagerada. Encaja un tramo en el otro por la presilla del primer eslabón: tiene que entrar con un clic y no salirse al jalar. Mete la clavija en el zócalo y el eje en el agujero grande. **Si algo falla, dime la medida y lo corrijo antes de gastar filamento.**")
    L.append("2. Camas 02 a 05, la cadena (PLA+ Azul): 4 camas de 3 secciones. Es lo que más tarda (≈ 4 h por cama), pero ya no hay que armar nada suelto.")
    L.append("3. Cama 01, PETG Azul (ejes, ruedas, carros, tornillos, acople, soporte y módulo del motor).")
    L.append("4. Camas 06 a 08 (módulos, tapa y patas, PLA+ Mármol) y 09 (guías, PLA+ Negro).\n")
    L.append("## Armado\n")
    L.append("1. **Bastidor:** une los 6 módulos deslizándolos de arriba hacia abajo por los rompecabezas (cola de milano), con una gota de cianoacrilato en cada junta. Pega las 6 patas (clavijas integradas) en los zócalos de la pared +Y.")
    L.append("2. **Soporte del motor** al módulo 1; pega la tapa del motor y la del tensor con sus lengüetas.")
    L.append("3. **Cadena:** une las 12 secciones sobre la mesa encajando la presilla (primer eslabón) en el último pasador de la sección anterior; la 12 cierra con la 1 y queda un anillo de 168 eslabones. Con las tapas y las guías quitadas, mete el anillo por el costado −Y alrededor de las dos ruedas.")
    L.append("4. Ejes y ruedas en su sitio, carros del tensor en las ranuras y tornillos hasta que la cadena quede tensa pero giren libres a mano.")
    L.append("5. Pon las guías y las tapas. Antes de quitar una tapa, afloja el tensor por completo.\n")
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
        L.append("")
        for n_ in sorted({it['nota'] for it in its}):
            L.append(f"- {n_}")
        L.append(f"- Peso aproximado de la cama: {gt:.0f} g.\n")
    L.append(f"Total aproximado: **{tot:.0f} g** en {len(filas)} camas.\n")
    L.append("## Cantidades\n")
    L.append("| Pieza | Cant. | Filamento |")
    L.append("|---|---|---|")
    for pz in piezas:
        L.append(f"| `{pz['fn']}` | {pz['cant']} | {pz['mat']} |")
    L.append("\n## Qué se hizo contra los fallos\n")
    L.append("- **Voladizos:** ninguna cara pasa de 45°. Los agujeros horizontales son en gota o rombo, las clavijas en gota, el cubo del eje es octogonal y la ranura del tensor está abierta por abajo. Un análisis automático de las caras que miran hacia abajo, con cada pieza en su posición, deja sólo puentes cortos (≤ 8 mm, como los zócalos de clavija) y el arco de los primeros 0,8 mm de los nudillos de la cadena, que apoyan en la cama.")
    L.append("- **Cadena print-in-place:** juego de 0,3 mm por lado (agujero Ø3,6 sobre pasador Ø3); si en la cama 00 queda dura, se corrige con un número. El pasador es una gota para que no tenga voladizo al imprimirse acostado.")
    L.append("- **Pocas piezas pequeñas:** las clavijas Ø6 se integraron en guías y patas; los pasadores Ø3 son parte de cada eslabón; el rompecabezas de los módulos sustituye a todas las clavijas de unión del bastidor.")
    L.append("- **Riesgos que quedan:** (1) la tolerancia de la articulación (por eso la cama 00 primero); (2) la presilla de la sección, de PLA, puede ser frágil; (3) el juego de 168 articulaciones alarga la cadena, por eso el tensor tiene 24 mm de recorrido; (4) el torque de un NEMA17 de 48 mm con el radio de la rueda de ≈ 0,3 N·m es justo para la carga de monedas: si patina, baja la tensión.")
    (out / 'CAMAS.md').write_text("\n".join(L) + "\n")


if __name__ == '__main__':
    main()
