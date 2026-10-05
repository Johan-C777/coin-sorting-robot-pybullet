"""Utilidades mínimas para generar mallas y escribir archivos STL binarios.

Sin dependencias externas: triangulación por recorte de orejas para polígonos
simples, más primitivas de caja, prisma, cilindro y tubo.
"""
from __future__ import annotations

import math
import struct
from typing import Iterable, List, Sequence, Tuple

Punto = Tuple[float, float, float]
Triangulo = Tuple[Punto, Punto, Punto]


class Malla:
    def __init__(self, triangulos: Iterable[Triangulo] = ()):
        self.t: List[Triangulo] = list(triangulos)

    def __add__(self, otra: "Malla") -> "Malla":
        return Malla(self.t + otra.t)

    def mas(self, *otras: "Malla") -> "Malla":
        m = Malla(self.t)
        for o in otras:
            m.t.extend(o.t)
        return m

    def _map(self, f) -> "Malla":
        return Malla([(f(a), f(b), f(c)) for a, b, c in self.t])

    def mover(self, dx=0.0, dy=0.0, dz=0.0) -> "Malla":
        return self._map(lambda p: (p[0] + dx, p[1] + dy, p[2] + dz))

    def escalar(self, sx=1.0, sy=1.0, sz=1.0) -> "Malla":
        m = self._map(lambda p: (p[0] * sx, p[1] * sy, p[2] * sz))
        if sx * sy * sz < 0:                      # el espejo invierte la orientación
            m.t = [(a, c, b) for a, b, c in m.t]
        return m

    def girar_x(self, grados: float) -> "Malla":
        c, s = math.cos(math.radians(grados)), math.sin(math.radians(grados))
        return self._map(lambda p: (p[0], p[1] * c - p[2] * s, p[1] * s + p[2] * c))

    def girar_y(self, grados: float) -> "Malla":
        c, s = math.cos(math.radians(grados)), math.sin(math.radians(grados))
        return self._map(lambda p: (p[0] * c + p[2] * s, p[1], -p[0] * s + p[2] * c))

    def girar_z(self, grados: float) -> "Malla":
        c, s = math.cos(math.radians(grados)), math.sin(math.radians(grados))
        return self._map(lambda p: (p[0] * c - p[1] * s, p[0] * s + p[1] * c, p[2]))

    def caja_envolvente(self):
        xs = [p[0] for t in self.t for p in t]
        ys = [p[1] for t in self.t for p in t]
        zs = [p[2] for t in self.t for p in t]
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def _area(poly: Sequence[Tuple[float, float]]) -> float:
    s = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        s += x1 * y2 - x2 * y1
    return s / 2.0


def _cruz(a, b, p) -> float:
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def _dentro_estricto(p, a, b, c) -> bool:
    """Punto estrictamente dentro del triángulo a-b-c, dado en sentido antihorario."""
    return (_cruz(a, b, p) > 1e-10 and _cruz(b, c, p) > 1e-10 and _cruz(c, a, p) > 1e-10)


def limpiar(poly: Sequence[Tuple[float, float]], tol=1e-7) -> List[Tuple[float, float]]:
    """Quita vértices repetidos consecutivos y puntos colineales redundantes."""
    pts = []
    for p in poly:
        if not pts or math.dist(p, pts[-1]) > tol:
            pts.append(tuple(p))
    while len(pts) > 1 and math.dist(pts[0], pts[-1]) <= tol:
        pts.pop()
    return pts


def triangular(poly: Sequence[Tuple[float, float]]) -> List[Tuple[int, int, int]]:
    """Recorte de orejas para polígonos simples, incluidos los que traen ranuras."""
    pts = list(poly)
    n = len(pts)
    if n < 3:
        return []
    indices = list(range(n))
    if _area(pts) < 0:
        indices.reverse()
    salida: List[Tuple[int, int, int]] = []
    while len(indices) > 2:
        recortado = False
        m = len(indices)
        for k in range(m):
            i0 = indices[(k - 1) % m]
            i1 = indices[k]
            i2 = indices[(k + 1) % m]
            a, b, c = pts[i0], pts[i1], pts[i2]
            if _cruz(a, b, c) <= 1e-10:          # vértice reflejo o degenerado
                continue
            libre = True
            for j in indices:
                if j in (i0, i1, i2):
                    continue
                if _dentro_estricto(pts[j], a, b, c):
                    libre = False
                    break
            if not libre:
                continue
            salida.append((i0, i1, i2))
            indices.pop(k)
            recortado = True
            break
        if not recortado:                         # polígono degenerado: se detiene
            break
    return salida


def prisma(poly: Sequence[Tuple[float, float]], z0: float, z1: float) -> Malla:
    """Extruye un polígono simple del plano XY entre dos alturas."""
    pts = limpiar(poly)
    if _area(pts) < 0:
        pts.reverse()
    tri = triangular(pts)
    if len(tri) != len(pts) - 2:
        raise ValueError(f"triangulación incompleta: {len(tri)} de {len(pts) - 2}")
    m = Malla()
    for i0, i1, i2 in tri:                       # tapa superior
        m.t.append(((pts[i0][0], pts[i0][1], z1), (pts[i1][0], pts[i1][1], z1),
                    (pts[i2][0], pts[i2][1], z1)))
    for i0, i1, i2 in tri:                       # tapa inferior
        m.t.append(((pts[i0][0], pts[i0][1], z0), (pts[i2][0], pts[i2][1], z0),
                    (pts[i1][0], pts[i1][1], z0)))
    for i in range(len(pts)):                    # paredes
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        m.t.append(((x1, y1, z0), (x2, y2, z0), (x2, y2, z1)))
        m.t.append(((x1, y1, z0), (x2, y2, z1), (x1, y1, z1)))
    return m


def caja(x0, y0, z0, x1, y1, z1) -> Malla:
    return prisma([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1)


def cilindro(cx, cy, z0, z1, r, seg=48) -> Malla:
    poly = [(cx + r * math.cos(2 * math.pi * i / seg),
             cy + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
    return prisma(poly, z0, z1)


def tubo(cx, cy, z0, z1, r_ext, r_int, seg=48) -> Malla:
    """Anillo extruido: se construye por sectores para no necesitar agujeros."""
    m = Malla()
    for i in range(seg):
        a0 = 2 * math.pi * i / seg
        a1 = 2 * math.pi * (i + 1) / seg
        p = [(cx + r_int * math.cos(a0), cy + r_int * math.sin(a0)),
             (cx + r_ext * math.cos(a0), cy + r_ext * math.sin(a0)),
             (cx + r_ext * math.cos(a1), cy + r_ext * math.sin(a1)),
             (cx + r_int * math.cos(a1), cy + r_int * math.sin(a1))]
        m.t.extend(prisma(p, z0, z1).t)
    return m


def cono(cx, cy, z0, z1, r0, r1, seg=48) -> Malla:
    """Tronco de cono hueco cerrado (se usa para tolvas y embudos macizos)."""
    m = Malla()
    for i in range(seg):
        a0 = 2 * math.pi * i / seg
        a1 = 2 * math.pi * (i + 1) / seg
        b0 = (cx + r0 * math.cos(a0), cy + r0 * math.sin(a0), z0)
        b1 = (cx + r0 * math.cos(a1), cy + r0 * math.sin(a1), z0)
        t0 = (cx + r1 * math.cos(a0), cy + r1 * math.sin(a0), z1)
        t1 = (cx + r1 * math.cos(a1), cy + r1 * math.sin(a1), z1)
        m.t.append((b0, b1, t1))
        m.t.append((b0, t1, t0))
        m.t.append(((cx, cy, z0), b1, b0))
        m.t.append(((cx, cy, z1), t0, t1))
    return m


def _normal(t: Triangulo):
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = t
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    n = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return nx / n, ny / n, nz / n


def escribir_stl(ruta: str, malla: Malla, nombre: str = "pieza") -> int:
    """Escribe un STL binario en milímetros. Devuelve el número de triángulos."""
    with open(ruta, "wb") as f:
        cabecera = f"{nombre} - proyecto monedas".encode("ascii", "ignore")[:79]
        f.write(cabecera.ljust(80, b" "))
        f.write(struct.pack("<I", len(malla.t)))
        for t in malla.t:
            nx, ny, nz = _normal(t)
            f.write(struct.pack("<3f", nx, ny, nz))
            for p in t:
                f.write(struct.pack("<3f", *p))
            f.write(struct.pack("<H", 0))
    return len(malla.t)


def hexaedro(p: Sequence[Punto]) -> Malla:
    """Sólido de ocho vértices: 0-3 cara inferior, 4-7 cara superior, en orden."""
    q = list(p)
    caras = [(0, 1, 2, 3)[::-1], (4, 5, 6, 7), (0, 4, 5, 1), (1, 5, 6, 2),
             (2, 6, 7, 3), (3, 7, 4, 0)]
    m = Malla()
    for a, b, c, d in caras:
        m.t.append((q[a], q[b], q[c]))
        m.t.append((q[a], q[c], q[d]))
    return m


def anillo_variable(loop0: Sequence[Tuple[float, float]], z0: float,
                    loop1: Sequence[Tuple[float, float]], z1: float,
                    espesor: float, cx=0.0, cy=0.0) -> Malla:
    """Pared de espesor constante entre dos contornos cerrados (tolvas y embudos)."""
    n = len(loop0)
    m = Malla()

    def adentro(p, e):
        dx, dy = p[0] - cx, p[1] - cy
        d = math.hypot(dx, dy) or 1.0
        return (p[0] - dx / d * e, p[1] - dy / d * e)

    for i in range(n):
        j = (i + 1) % n
        a0, b0 = loop0[i], loop0[j]
        a1, b1 = loop1[i], loop1[j]
        ia0, ib0 = adentro(a0, espesor), adentro(b0, espesor)
        ia1, ib1 = adentro(a1, espesor), adentro(b1, espesor)
        m.t.extend(hexaedro([(ia0[0], ia0[1], z0), (a0[0], a0[1], z0),
                             (b0[0], b0[1], z0), (ib0[0], ib0[1], z0),
                             (ia1[0], ia1[1], z1), (a1[0], a1[1], z1),
                             (b1[0], b1[1], z1), (ib1[0], ib1[1], z1)]).t)
    return m


def placa_con_agujeros(x0, y0, x1, y1, z0, z1, agujeros: Sequence[Tuple[float, float, float]],
                       seg=24, puente=0.3) -> Malla:
    """Placa rectangular con agujeros redondos.

    Cada agujero se conecta al borde inferior con una ranura de 0,3 mm: al
    imprimir queda cerrada por el propio material y el laminador la puentea.
    """
    ags = sorted(agujeros, key=lambda a: a[0])
    poly: List[Tuple[float, float]] = [(x0, y0)]
    for cx, cy, r in ags:
        poly.append((cx - puente / 2, y0))
        poly.append((cx - puente / 2, cy - r))
        for i in range(1, seg):                  # el agujero se recorre al revés
            ang = -math.pi / 2 - 2 * math.pi * i / seg
            poly.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        poly.append((cx + puente / 2, cy - r))
        poly.append((cx + puente / 2, y0))
    poly.extend([(x1, y0), (x1, y1), (x0, y1)])
    return prisma(poly, z0, z1)


def placa_agujereada(x0, y0, x1, y1, z0, z1,
                     agujeros: Sequence[Tuple[float, float, float]],
                     seg=24, puente=0.3) -> Malla:
    """Placa rectangular con agujeros redondos, versión de dos bordes.

    Cada agujero se une por una ranura de 0,3 mm al borde inferior o al
    superior, el que le quede más cerca, así que se pueden poner agujeros en
    las cuatro esquinas sin que las ranuras se crucen. Al imprimir la ranura
    se cierra sola y el laminador la puentea.
    """
    medio = (y0 + y1) / 2.0
    abajo = sorted([a for a in agujeros if a[1] <= medio], key=lambda a: a[0])
    arriba = sorted([a for a in agujeros if a[1] > medio], key=lambda a: -a[0])

    poly: List[Tuple[float, float]] = [(x0, y0)]
    for cx, cy, r in abajo:
        poly.append((cx - puente / 2, y0))
        poly.append((cx - puente / 2, cy - r))
        for i in range(1, seg):
            ang = -math.pi / 2 - 2 * math.pi * i / seg
            poly.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        poly.append((cx + puente / 2, cy - r))
        poly.append((cx + puente / 2, y0))
    poly.append((x1, y0))
    poly.append((x1, y1))
    for cx, cy, r in arriba:
        poly.append((cx + puente / 2, y1))
        poly.append((cx + puente / 2, cy + r))
        for i in range(1, seg):
            ang = math.pi / 2 - 2 * math.pi * i / seg
            poly.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        poly.append((cx - puente / 2, cy + r))
        poly.append((cx - puente / 2, y1))
    poly.append((x0, y1))
    return prisma(poly, z0, z1)


def placa_con_ventana(x0, y0, x1, y1, z0, z1,
                      ventana: Tuple[float, float, float, float],
                      puente=0.3) -> Malla:
    """Placa rectangular con una ventana rectangular (para alojar un servo)."""
    vx0, vy0, vx1, vy1 = ventana
    poly = [(x0, y0),
            (vx0 - puente / 2, y0), (vx0 - puente / 2, vy0),
            (vx1, vy0), (vx1, vy1), (vx0, vy1), (vx0, vy0),
            (vx0 + puente / 2, vy0), (vx0 + puente / 2, y0),
            (x1, y0), (x1, y1), (x0, y1)]
    return prisma(poly, z0, z1)


def barra_redondeada(largo: float, alto: float, seg=20) -> List[Tuple[float, float]]:
    """Contorno de un eslabón: rectángulo con los dos extremos redondeados."""
    r = alto / 2.0
    pts = []
    for i in range(seg + 1):                       # extremo derecho
        a = -math.pi / 2 + math.pi * i / seg
        pts.append((largo + r * math.cos(a), r * math.sin(a)))
    for i in range(seg + 1):                       # extremo izquierdo
        a = math.pi / 2 + math.pi * i / seg
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts
