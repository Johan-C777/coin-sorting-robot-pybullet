"""Escribe stl/ (cada pieza en su posición de impresión) y camas/ (acomodadas en la cama de 220 x 220) de la v5.
    python exportar_v5.py <carpeta_salida>
"""
import os, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v5 as v, analisis as an
import camas as cm


def main(out):
    out = Path(out); (out/'stl').mkdir(parents=True, exist_ok=True); (out/'camas').mkdir(exist_ok=True)
    P = {'V5-CA_carro': (v.carro(), (0, 0, 0), 1), 'V5-BM_bloque-motor': (v.bloque_motor(), (0, 0, 0), 1),
         'V5-BR_bloque-extremo': (v.bloque_extremo(), (0, 0, 0), 1), 'V5-PM_tambor-motor': (v.polea_motriz(), (0, 0, 0), 1),
         'V5-PL_polea-libre': (v.polea_libre(), (0, 0, 0), 1), 'V5-EJ_eje-polea': (v.eje_libre(), (0, 0, 0), 1)}
    for i in range(len(v.SEG)):
        P[f'V5-R{i+1}_riel-{i+1}'] = (v.segmento(i), (0, 0, 0), 1)
    for t in (1, 2, 3):
        P[f'V5-CU{t}_cuna-{t}mm'] = (v.cuna(t), (0, 90, 0), 2)
    pz = {}
    for n, (m, rot, q) in P.items():
        p, box = an.pose(m, rot)
        pz[n] = (p, box, q)
        (out/'stl'/f'{n}.stl').write_bytes(cm.stl_bytes([p]))
        print(f'{n:24s} {box[0]:6.1f} x {box[1]:6.1f} x {box[2]:5.1f}  x{q}')

    def poner(n, x, y, k=0):
        return pz[n][0].translate((x, y, 0))
    cama1 = [poner('V5-CA_carro', 5, 5), poner('V5-PM_tambor-motor', 135, 5), poner('V5-PL_polea-libre', 135, 52),
             poner('V5-R3_riel-3', 5, 100), poner('V5-EJ_eje-polea', 183, 5)]
    for i, t in enumerate((1, 2, 3)):
        cama1 += [poner(f'V5-CU{t}_cuna-{t}mm', 183 + 11 * i, 40), poner(f'V5-CU{t}_cuna-{t}mm', 183 + 11 * i, 56)]
    cama2 = [poner('V5-R1_riel-1', 5, 5), poner('V5-R2_riel-2', 5, 93), poner('V5-R4_riel-4', 5, 126)]
    cama3 = [poner('V5-R5_riel-5', 5, 5), poner('V5-BM_bloque-motor', 5, 40), poner('V5-BR_bloque-extremo', 110, 40)]
    for nom, ms in (('cama-1_PETG_carro-poleas-y-un-riel', cama1), ('cama-2_PETG_rieles-1-2-4', cama2), ('cama-3_PETG_riel-5-y-bloques', cama3)):
        bb = [m.bounding_box() for m in ms]
        xs = max(b[3] for b in bb); ys = max(b[4] for b in bb)
        assert xs <= 215 and ys <= 215, (nom, xs, ys)
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                a, b = bb[i], bb[j]
                sep = max(b[0] - a[3], a[0] - b[3], b[1] - a[4], a[1] - b[4])
                assert sep > 2.5, (nom, i, j, sep)
        (out/'camas'/f'{nom}.stl').write_bytes(cm.stl_bytes(ms))
        print(nom, 'ocupa', round(xs, 1), 'x', round(ys, 1))


if __name__ == '__main__':
    main(sys.argv[1])
