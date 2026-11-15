"""Voladizos: para cada orientación de impresión (una cara plana abajo) suma el área de caras que miran hacia abajo a más de 45 grados
de la vertical y que no están en la cama. Elige la orientación con menos área colgada."""
import numpy as np
from manifold3d import Manifold

ORIENT = {'tal cual': (0, 0, 0), 'volteada': (180, 0, 0), 'sobre +Y': (-90, 0, 0), 'sobre -Y': (90, 0, 0), 'sobre +X': (0, 90, 0), 'sobre -X': (0, -90, 0)}


def pose(m, rot):
    m = m.rotate(rot) if any(rot) else m
    x0, y0, z0, x1, y1, z1 = m.bounding_box()
    return m.translate((-x0, -y0, -z0)), (x1 - x0, y1 - y0, z1 - z0)


def voladizo(m, umbral_deg=44.0, cama=0.25):
    mm = m.to_mesh()
    v = np.asarray(mm.vert_properties, dtype=np.float64)[:, :3]
    t = np.asarray(mm.tri_verts, dtype=np.int64)
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    n = np.cross(b - a, c - a)
    ar = np.linalg.norm(n, axis=1) / 2
    nz = n[:, 2] / np.maximum(np.linalg.norm(n, axis=1), 1e-12)
    zmin = np.minimum(np.minimum(a[:, 2], b[:, 2]), c[:, 2])
    lim = -np.cos(np.radians(umbral_deg))
    mal = (nz < lim) & (zmin > cama)
    plano = (nz < -0.98) & (zmin > cama)           # puentes (cara horizontal mirando abajo)
    return float(ar[mal].sum()), float(ar[plano].sum())


def mejor(m, maxx=212.0, maxy=212.0, maxz=245.0):
    res = []
    for nom, rot in ORIENT.items():
        p, (w, d, h) = pose(m, rot)
        ok = h <= maxz and ((w <= maxx and d <= maxy) or (d <= maxx and w <= maxy))
        if not ok:
            continue
        vol, puente = voladizo(p)
        res.append((vol, h, nom, rot, puente, (w, d, h)))
    res.sort(key=lambda r: (round(r[0], 0), r[1]))
    return res
