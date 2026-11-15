"""Escribe stl/ (cada pieza en posición de impresión), camas/ (acomodadas en la cama de 220 x 220) y las piezas de prueba de la v7.
    python exportar_v7.py <carpeta_salida>
"""
import os, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v7 as v, analisis as an
import camas as cm
from generar_banda import caja


def main(out):
    out = Path(out)
    for d in ('stl', 'camas', 'prueba-engrane-y-union', 'prueba-brazo'): (out / d).mkdir(parents=True, exist_ok=True)
    P = {'V7-CA_carro': v.carro(), 'V7-BZ_brazo': v.brazo(), 'V7-SP_soporte-motor': v.soporte(), 'V7-PI_pinon': v.pinon()}
    for j in range(4): P[f'V7-B{j+1}_barra-{j+1}'] = v.tramo_barra(j)
    for i in range(len(v.SEG)): P[f'V7-R{i+1}_riel-{i+1}'] = v.segmento(i)
    pz = {}
    for n, m in P.items():
        if n.startswith('V7-B4'):
            m = m.rotate((0, 0, 45))                      # 233,6 mm de largo: va en diagonal en la cama de 220
        p, box = an.pose(m, (0, 0, 0)); pz[n] = p
        (out / 'stl' / f'{n}.stl').write_bytes(cm.stl_bytes([p]))
        print(f'{n:22s} {box[0]:6.1f} x {box[1]:6.1f} x {box[2]:5.1f}')
    poner = lambda n, x, y: pz[n].translate((x, y, 0))
    cama1 = [poner('V7-CA_carro', 5, 5), poner('V7-SP_soporte-motor', 135, 5), poner('V7-BZ_brazo', 5, 80), poner('V7-PI_pinon', 180, 80)]
    cama2 = [poner(f'V7-B{j}_barra-{j}', 3, 3 + 14 * (j - 1)) for j in (1, 2, 3)] + [poner('V7-R1_riel-1', 3, 50)]
    cama3 = [poner('V7-B4_barra-4', 5, 5)]
    cama4 = [poner(f'V7-R{i}_riel-{i}', 5, 5 + 34 * (i - 2)) for i in (2, 3, 4, 5)]
    camas = (('cama-1_PETG_carro-brazo-soporte-y-pinon', cama1), ('cama-2_PLA_barras-1-2-3-y-riel-1', cama2),
             ('cama-3_PLA_barra-4-en-diagonal', cama3), ('cama-4_PLA_rieles-2-3-4-5', cama4))
    for nom, ms in camas:
        bb = [m.bounding_box() for m in ms]
        xs = max(b[3] for b in bb); ys = max(b[4] for b in bb)
        assert xs <= 216 and ys <= 216, (nom, xs, ys)
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                a, b = bb[i], bb[j]
                sep = max(b[0] - a[3], a[0] - b[3], b[1] - a[4], a[1] - b[4])
                assert sep > 2.5 or nom.startswith('cama-3'), (nom, i, j, sep)
        (out / 'camas' / f'{nom}.stl').write_bytes(cm.stl_bytes(ms))
        print(nom, 'ocupa', round(xs, 1), 'x', round(ys, 1))
    # --- prueba 1: unión de la barra con 3 juegos de ranura (0,15 / 0,25 / 0,35 mm) + engrane con el piñón
    xb = v.valle(v.N_TRAMO)
    a = v.tramo_barra(0) ^ caja(xb - 16 * v.PASO, xb + v.X_FIN + 2, -100, 100, -1, 60)
    pa, _ = an.pose(a, (0, 0, 0)); piezas1 = [pa.translate((5, 5, 0))]
    vol = a.volume()
    for k, (jg, nd) in enumerate(((0.15, 8), (0.25, 10), (0.35, 12))):
        b = v.tramo_barra(1, jg) ^ caja(xb - 3, xb + nd * v.PASO, -100, 100, -1, 60)
        pb, _ = an.pose(b, (0, 0, 0)); piezas1.append(pb.translate((5, 22 + 16 * k, 0))); vol += b.volume()
    piezas1.append(pz['V7-PI_pinon'].translate((110, 55, 0)))
    (out / 'prueba-engrane-y-union' / 'prueba-1_engrane-y-union.stl').write_bytes(cm.stl_bytes(piezas1))
    print('prueba-1', round(vol / 1000 * 1.27 * 0.5 + 2.7 * 1.27, 1), 'g aprox.')
    # --- prueba 2: brazo con 3 rebanadas del carro (juego de la ranura 0,1 / 0,2 / 0,3 mm)
    xs = v.XSL
    z = v.brazo(0.0) ^ caja(xs - 9, xs + 9, -100, 100, -1, 100)
    pz_, _ = an.pose(z, (0, 0, 0)); piezas2 = [pz_.translate((5, 5, 0))]
    vol = z.volume()
    for k, (jg, w) in enumerate(((0.1, 20), (0.2, 23), (0.3, 26))):
        c = v.carro(0.0, jg) ^ caja(xs - w / 2, xs + w / 2, -100, 100, -1, 100)
        pc, _ = an.pose(c, (0, 0, 0)); piezas2.append(pc.translate((30 + 40 * k, 5, 0))); vol += c.volume()
    for q in piezas2:
        bb = q.bounding_box(); assert bb[3] <= 216 and bb[4] <= 216, bb
    (out / 'prueba-brazo' / 'prueba-2_carro-rebanadas-y-brazo.stl').write_bytes(cm.stl_bytes(piezas2))
    print('prueba-2', round(vol / 1000 * 1.27 * 0.5, 1), 'g aprox.')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
