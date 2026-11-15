"""Piezas de la torre de la etapa 1 (ens_v5.json, eje Y hacia arriba) pasadas al marco de este generador: X igual, Y = z del ensamble, Z = y del ensamble."""
import base64, json, os
import numpy as np
from manifold3d import Manifold, Mesh
ENS = os.environ.get('ENS_V5', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ens_v5.json'))
def cargar():
    out = []
    for p in json.load(open(ENS))['piezas']:
        vv = np.frombuffer(base64.b64decode(p['v']), dtype=np.float32).reshape(-1, 3)[:, [0, 2, 1]].copy()
        tt = np.frombuffer(base64.b64decode(p['t']), dtype=np.uint32).reshape(-1, 3)[:, [0, 2, 1]].copy()   # el cambio de ejes invierte el giro
        out.append((p['cod'], p['grupo'], Manifold(Mesh(vert_properties=vv, tri_verts=tt))))
    return out
