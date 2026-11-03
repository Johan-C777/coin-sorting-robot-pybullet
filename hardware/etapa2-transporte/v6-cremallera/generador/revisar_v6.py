import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v6 as v, analisis as an
from capas import islas
P = {'CA': v.carro(), 'PI': v.pinon()}
P.update({f'S{i+1}': v.segmento(i) for i in range(len(v.SEG))})
for k, m in P.items():
    mm, box = an.pose(m, (0, 0, 0))
    vol, puente = an.voladizo(mm)
    il = islas(mm, tol=0.21); il2 = islas(mm, tol=0.02)
    print(f'{k}: caja {[round(b,1) for b in box]} partes {len(m.decompose())} voladizo>44° {vol:.1f} mm2 (horizontal {puente:.1f}) islas 45°: {len(il)} area {sum(x[1] for x in il):.1f} | estrictas {len(il2)}')
    for x in il[:4]: print('    ', x)
