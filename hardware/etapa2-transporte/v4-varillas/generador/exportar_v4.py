"""Escribe stl/ (cada pieza en su posición de impresión) y camas/ (acomodadas en la cama de 220 x 220) de la v4.
    python exportar_v4.py <carpeta_salida>
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v4 as v, analisis as an
import camas as cm

def main(out):
    out = Path(out); (out/'stl').mkdir(parents=True, exist_ok=True); (out/'camas').mkdir(exist_ok=True)
    P = {  # nombre: (modelo, giro de impresión, cantidad)
        'V4-CA_carro': (v.carro(), (0, 0, 0), 1),
        'V4-TO_tope': (v.tope(), (0, 0, 0), 4),
        'V4-BM_bloque-motor': (v.bloque_motor(), (0, 0, 0), 1),
        'V4-BR_bloque-extremo': (v.bloque_extremo(), (0, 0, 0), 1),
        'V4-EJ_eje-polea': (v.eje_libre(), (0, 0, 0), 1),
        'V4-PL_polea-libre': (v.polea_libre(), (0, 0, 0), 1),
        'V4-PM_tambor-motor': (v.polea_motriz(), (0, 0, 0), 1),
        'V4-IR_puente-infrarrojo': (v.puente_ir(), (0, 90, 0), 1),
    }
    pz = {}
    for n, (m, rot, q) in P.items():
        p, box = an.pose(m, rot)
        pz[n] = (p, box, q)
        (out/'stl'/f'{n}.stl').write_bytes(cm.stl_bytes([p]))
        print(f'{n:26s} {box[0]:6.1f} x {box[1]:6.1f} x {box[2]:5.1f}  x{q}')
    def poner(n, x, y, k=0):
        p, box, q = pz[n]
        return p.translate((x, y, 0))
    cama1 = [poner('V4-CA_carro', 5, 5), poner('V4-IR_puente-infrarrojo', 5, 95), poner('V4-PM_tambor-motor', 70, 95),
             poner('V4-PL_polea-libre', 105, 95), poner('V4-EJ_eje-polea', 140, 95)]
    for i, (x, y) in enumerate([(70, 130), (110, 130), (150, 130), (70, 142)]):
        cama1.append(poner('V4-TO_tope', x, y))
    cama2 = [poner('V4-BM_bloque-motor', 5, 5), poner('V4-BR_bloque-extremo', 95, 5)]
    for nom, ms in (('cama-1_PETG_carro-y-poleas', cama1), ('cama-2_PETG_bloques', cama2)):
        bb = [m.bounding_box() for m in ms]
        xs = max(b[3] for b in bb); ys = max(b[4] for b in bb)
        assert xs <= 215 and ys <= 215, (nom, xs, ys)
        # no se tocan
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                assert (ms[i] ^ ms[j]).volume() < 1e-9
                a, b = bb[i], bb[j]
                sep = max(b[0] - a[3], a[0] - b[3], b[1] - a[4], a[1] - b[4])
                assert sep > 3, (nom, i, j, sep)
        (out/'camas'/f'{nom}.stl').write_bytes(cm.stl_bytes(ms))
        print(nom, 'ocupa', round(xs, 1), 'x', round(ys, 1))

if __name__ == '__main__':
    main(sys.argv[1])
