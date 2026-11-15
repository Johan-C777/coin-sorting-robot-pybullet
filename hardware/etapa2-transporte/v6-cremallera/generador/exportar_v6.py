"""Escribe stl/ (cada pieza en posición de impresión), camas/ (acomodadas en la cama de 220 x 220) y prueba-engrane/ de la v6.
    python exportar_v6.py <carpeta_salida>
"""
import os, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v6 as v, analisis as an
import camas as cm


def main(out):
    out = Path(out)
    for d in ('stl', 'camas', 'prueba-engrane'): (out / d).mkdir(parents=True, exist_ok=True)
    P = {'V6-CA_carro': v.carro(), 'V6-PI_pinon': v.pinon()}
    for i in range(len(v.SEG)): P[f'V6-R{i+1}_riel-{i+1}'] = v.segmento(i)
    pz = {}
    for n, m in P.items():
        p, box = an.pose(m, (0, 0, 0)); pz[n] = p
        (out / 'stl' / f'{n}.stl').write_bytes(cm.stl_bytes([p]))
        print(f'{n:20s} {box[0]:6.1f} x {box[1]:6.1f} x {box[2]:5.1f}')
    poner = lambda n, x, y: pz[n].translate((x, y, 0))
    cama1 = [poner('V6-CA_carro', 5, 5), poner('V6-PI_pinon', 140, 5)]
    cama2 = [poner(f'V6-R{i}_riel-{i}', 5, 5 + 48 * (i - 2)) for i in (2, 3, 4, 5)]
    cama3 = [poner('V6-R1_riel-1', 5, 5)]
    camas = (('cama-1_PETG_carro-y-pinon', cama1), ('cama-2_PLA_rieles-2-3-4-5', cama2), ('cama-3_PLA_riel-1', cama3))
    for nom, ms in camas:
        bb = [m.bounding_box() for m in ms]
        xs = max(b[3] for b in bb); ys = max(b[4] for b in bb)
        assert xs <= 215 and ys <= 215, (nom, xs, ys)
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                a, b = bb[i], bb[j]
                sep = max(b[0] - a[3], a[0] - b[3], b[1] - a[4], a[1] - b[4])
                assert sep > 2.5, (nom, i, j, sep)
        (out / 'camas' / f'{nom}.stl').write_bytes(cm.stl_bytes(ms))
        print(nom, 'ocupa', round(xs, 1), 'x', round(ys, 1))
    # prueba de engrane: 16 dientes de cremallera sobre un trozo de riel, y el piñón
    xa = v.X_V0 + 60 * v.PASO; xb = xa + 16 * v.PASO
    tr_ = v.riel(xa, xb) + v.cremallera(xa, xb)
    t, _ = an.pose(tr_, (0, 0, 0)); t = t.translate((5, 5, 0))
    pp = pz['V6-PI_pinon'].translate((100, 20, 0))
    (out / 'prueba-engrane' / 'prueba-engrane_cremallera-y-pinon.stl').write_bytes(cm.stl_bytes([t, pp]))
    print('prueba-engrane', [round(b, 1) for b in t.bounding_box()], round(tr_.volume() / 1000 * 1.27 * 0.5, 1), 'g aprox. + piñón')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
