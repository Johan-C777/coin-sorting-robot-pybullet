"""Ruta del punto A al punto B entre cuatro obstáculos de dificultad creciente.

Al final de la banda (punto A, yaw −60°) el brazo toma el vaso y debe llevarlo
al rack (punto B, puestos R1 a R5 entre 24° y 86°). Sobre ese recorrido cuelgan
cuatro móviles que giran sin parar. Cada uno está puesto para exigirle al
planificador una capacidad distinta, y en ese orden aparecen en el camino:

    Nivel 1  O1 Guardián de banda   bajar la altura de tránsito (una variable)
    Nivel 2  O2 Muro giratorio      recoger el brazo y rodear por dentro (tres juntas a la vez)
    Nivel 3  O3 Centinela           no hay hueco geométrico: predecir el giro y esperar la ventana
    Nivel 4  O4 Jefe de rack        pasar por debajo y además cronometrar la bajada al rack

Es el mismo modelo que corre en docs/simulacion_sistema_completo.html, escrito
en Python para poder calcularlo y probarlo. Longitudes en cm y ángulos en
grados. Las coordenadas de las esferas están en el marco de la escena 3D
(x adelante, y arriba, z = −Y del robot); las distancias no dependen de eso.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from .config import GRASP_DZ, VASO_ALTO, VASO_ANCHO_MM, YAW_RACK

# --- celda de la simulación --------------------------------------------------
R_ARCO = 23.0
YAW_A = -60.0                                 # punto A: zona de entrega de la banda
YAW_B = tuple(YAW_RACK)                       # punto B: puestos R1 a R9
Z_TRANSITO = 20.0                             # altura nominal del TCP en el arco
Z_BAJO = 15.5                                 # lo mínimo que se baja en tránsito
BAJO_MIN = 12.3                               # por debajo de esto no hay maniobra "por debajo"
VASO_H = VASO_ALTO                            # 6,0 cm
VASO_R = VASO_ANCHO_MM / 20.0                 # 1,7 cm
MARGEN = 1.4                                  # holgura mínima vaso-esfera
RHO_MIN = 7.2                                 # radio mínimo con la pinza vertical
RHO_MAX = 25.0
SOBRE_TCP = VASO_H - GRASP_DZ + 0.4           # lo que el vaso sobresale encima del TCP
VEL_OBSTACULOS = 45.0                         # °/s de giro base de los móviles


@dataclass(frozen=True)
class Obstaculo:
    codigo: str
    nombre: str
    nivel: int
    yaw: float            # dirección del pivote vista desde la base
    r_pivote: float       # distancia del pivote al eje de la base
    brazos: int
    radio: float          # radio de giro de las esferas
    y_esfera: float       # altura del centro de las esferas
    r_esfera: float
    fase: float           # ángulo inicial, rad
    giro: int             # +1 o −1
    vel: float            # multiplicador de VEL_OBSTACULOS

    @property
    def pivote(self) -> Tuple[float, float]:
        """(x, z) del pivote en la escena."""
        a = math.radians(self.yaw)
        return self.r_pivote * math.cos(a), -self.r_pivote * math.sin(a)

    @property
    def velocidad_angular(self) -> float:
        return VEL_OBSTACULOS * self.vel


OBSTACULOS: List[Obstaculo] = [
    Obstaculo("O1", "Guardián de banda", 1, -40.0, 23.0, 3, 6.5, 22.0, 2.6, 0.0, 1, 1.1),
    Obstaculo("O2", "Muro giratorio", 2, -15.0, 23.0, 2, 8.5, 15.5, 2.2, 1.1, -1, 1.8),
    Obstaculo("O3", "Centinela", 3, 10.0, 14.0, 3, 6.0, 16.0, 1.9, 0.6, 1, 0.7),
    Obstaculo("O4", "Jefe de rack", 4, 40.0, 23.0, 2, 7.0, 23.0, 3.0, 2.0, -1, 1.3),
]

NIVELES: Dict[int, Tuple[str, str]] = {
    1: ("Básico", "se resuelve con una sola variable: bajar la altura de tránsito"),
    2: ("Intermedio", "obliga a recoger el brazo y rodear por dentro, moviendo hombro, "
                      "codo y muñeca a la vez sin inclinar el vaso"),
    3: ("Avanzado", "no deja hueco geométrico: hay que predecir dónde estarán las "
                    "esferas y cruzar en la ventana entre brazos"),
    4: ("Experto", "combina las dos cosas: paso por debajo con esferas grandes y "
                   "bajada al rack cronometrada contra su giro"),
}


# --- geometría de las maniobras ----------------------------------------------
def altura_bajo(o: Obstaculo) -> float:
    """Altura máxima del TCP para que el vaso pase por debajo de las esferas."""
    return o.y_esfera - o.r_esfera - MARGEN - SOBRE_TCP


def radio_interior(o: Obstaculo) -> float:
    """Radio al que hay que recogerse para pasar por dentro del giro."""
    return o.r_pivote - o.radio - o.r_esfera - VASO_R - MARGEN


def zona_angular(o: Obstaculo) -> float:
    """Semiancho, en grados de yaw, de la franja del arco que el móvil alcanza."""
    alcance = o.radio + o.r_esfera + VASO_R + MARGEN
    return min(60.0, math.degrees(math.asin(min(1.0, alcance / R_ARCO))) + 4.0)


@dataclass(frozen=True)
class Maniobra:
    modo: str             # 'bajo', 'rodeo' o 'espera'
    z: float              # altura del TCP al cruzar
    rho: float            # radio del TCP al cruzar
    holgura: float        # espacio libre real que queda, cm (0 si hay que esperar)

    @property
    def descripcion(self) -> str:
        if self.modo == "bajo":
            return f"paso por debajo a {self.z:.1f} cm"
        if self.modo == "rodeo":
            return f"rodeo interior con ρ = {self.rho:.1f} cm"
        return "espera de la ventana entre brazos"


def maniobra(o: Obstaculo) -> Maniobra:
    """Misma regla de preferencia que el planificador de la simulación."""
    bajo = altura_bajo(o)
    if bajo >= BAJO_MIN:                              # 1) por debajo
        z = max(Z_BAJO, bajo - 0.3)
        holgura = (o.y_esfera - o.r_esfera) - (z + VASO_H - GRASP_DZ)
        return Maniobra("bajo", z, R_ARCO, round(holgura, 2))
    r_int = radio_interior(o)
    if r_int >= RHO_MIN:                                    # 2) rodeo por dentro
        r_int = max(RHO_MIN, min(RHO_MAX, r_int))
        return Maniobra("rodeo", Z_TRANSITO, r_int, round(MARGEN, 2))
    return Maniobra("espera", Z_TRANSITO, R_ARCO, 0.0)     # 3) sin maniobra


def plan_en(yaw: float, obstaculos: Sequence[Obstaculo] = OBSTACULOS) -> Tuple[float, float, str, str]:
    """Altura y radio del TCP que el planificador pide en un punto del arco.

    Las maniobras no son escalones: cada móvil influye con un peso que vale 1
    dentro de su franja y se desvanece hasta el doble de ella, así que en el
    recorrido se mezclan (bajar por O1 mientras se empieza a recoger por O2).
    Si en ese punto manda un móvil sin maniobra geométrica (O3), el brazo se
    queda en el arco nominal y cruza por ventanas: recogerse lo metería en el
    giro de un móvil que cuelga por dentro del arco.
    Devuelve (z, rho, modo, código del móvil que manda).
    """
    z, rho, modo, quien = Z_TRANSITO, R_ARCO, "directo", ""
    espera = None
    for o in obstaculos:
        d, zona = abs(yaw - o.yaw), zona_angular(o)
        if d > zona * 2.0:
            continue
        peso = 1.0 if d <= zona * 0.9 else max(0.0, (zona * 2.0 - d) / (zona * 1.1))
        bajo = altura_bajo(o)
        if bajo >= BAJO_MIN:
            zo = max(Z_BAJO, bajo - 0.3)
            z = min(z, Z_TRANSITO + (zo - Z_TRANSITO) * peso)
            if peso > 0.12 and modo == "directo":
                modo, quien = "bajo", o.codigo
            continue
        r_int = radio_interior(o)
        if r_int >= RHO_MIN:
            rho = min(rho, R_ARCO + (r_int - R_ARCO) * peso)
            if peso > 0.12:
                modo, quien = "rodeo", o.codigo
            continue
        if peso > 0.12:
            espera = o
    if espera is not None:
        modo, quien, rho = "espera", espera.codigo, R_ARCO
    return z, max(RHO_MIN, min(RHO_MAX, rho)), modo, quien


# --- choque con las esferas en el tiempo -------------------------------------
def esferas(o: Obstaculo, giro: float) -> List[Tuple[float, float, float]]:
    """Centros (x, y, z) de las esferas cuando el móvil ha girado `giro` rad."""
    px, pz = o.pivote
    res = []
    for b in range(o.brazos):
        a = 2 * math.pi * b / o.brazos - giro
        res.append((px + o.radio * math.cos(a), o.y_esfera, pz + o.radio * math.sin(a)))
    return res


def holgura(yaw: float, altura: float, rho: float, o: Obstaculo, giro: float,
            con_vaso: bool = True) -> float:
    """Distancia libre entre la carga (vaso o pinza) y la esfera más cercana."""
    a = math.radians(yaw)
    tx, ty, tz = rho * math.cos(a), altura, -rho * math.sin(a)
    y_bajo = ty - (GRASP_DZ if con_vaso else 1.2)
    y_alto = ty + (SOBRE_TCP if con_vaso else 1.2)
    radio_carga = VASO_R if con_vaso else 1.4
    m = math.inf
    for ex, ey, ez in esferas(o, giro):
        dh = max(0.0, math.hypot(tx - ex, tz - ez) - radio_carga)
        dv = (y_bajo - ey) if ey < y_bajo else ((ey - y_alto) if ey > y_alto else 0.0)
        m = min(m, math.hypot(dh, dv) - o.r_esfera)
    return m


def fraccion_bloqueada(o: Obstaculo, altura: float = Z_TRANSITO, rho: float = R_ARCO,
                       yaw: float | None = None, muestras: int = 720) -> float:
    """Fracción de una vuelta del móvil en la que la carga chocaría en ese punto."""
    yaw = o.yaw if yaw is None else yaw
    choques = sum(1 for k in range(muestras)
                  if holgura(yaw, altura, rho, o, 2 * math.pi * k / muestras) < 0)
    return choques / muestras


def bloqueo_en_franja(o: Obstaculo, altura: float = Z_TRANSITO, rho: float = R_ARCO,
                      muestras_giro: int = 360) -> float:
    """Fracción de la vuelta en la que algún punto de su franja del arco está tapado."""
    zona = zona_angular(o)
    yaws = [o.yaw + zona * (i / 10.0 - 1.0) for i in range(21)]
    choques = 0
    for k in range(muestras_giro):
        g = 2 * math.pi * k / muestras_giro
        if any(holgura(y, altura, rho, o, g) < 0 for y in yaws):
            choques += 1
    return choques / muestras_giro


def puntos_vigilados(o: Obstaculo) -> List[str]:
    """Puntos de bajada (A y R1..R5) que caen dentro de la franja del móvil."""
    zona = zona_angular(o)
    puntos = [("A", YAW_A)] + [(f"R{i + 1}", y) for i, y in enumerate(YAW_B)]
    return [nombre for nombre, y in puntos if abs(y - o.yaw) <= zona]


@dataclass(frozen=True)
class Tramo:
    obstaculo: Obstaculo
    maniobra: Maniobra
    bloqueo_directo: float     # fracción de la vuelta que tapa la ruta sin maniobra
    bloqueo_con_maniobra: float
    vigila: Tuple[str, ...]


def ruta(obstaculos: Sequence[Obstaculo] = OBSTACULOS) -> List[Tramo]:
    """Los obstáculos en el orden en que el vaso los encuentra de A hacia B."""
    tramos = []
    for o in sorted(obstaculos, key=lambda x: x.yaw):
        m = maniobra(o)
        tramos.append(Tramo(o, m,
                            round(bloqueo_en_franja(o), 3),
                            round(bloqueo_en_franja(o, m.z, m.rho), 3),
                            tuple(puntos_vigilados(o))))
    return tramos


def tabla_ruta() -> str:
    filas = [f"Punto A (yaw {YAW_A:.0f}°) -> Punto B (rack, yaw {YAW_B[0]:.0f}° a {YAW_B[-1]:.0f}°)",
             "nivel  obstáculo              yaw    maniobra                          "
             "tapa sin maniobra  con maniobra  vigila"]
    for t in ruta():
        o = t.obstaculo
        filas.append(f"  {o.nivel}    {o.codigo} {o.nombre:<18} {o.yaw:+5.0f}°  "
                     f"{t.maniobra.descripcion:<33} {t.bloqueo_directo:6.0%}"
                     f"            {t.bloqueo_con_maniobra:6.0%}     {','.join(t.vigila) or '-'}")
    return "\n".join(filas)


if __name__ == "__main__":
    print(tabla_ruta())
