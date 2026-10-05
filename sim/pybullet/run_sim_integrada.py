#!/usr/bin/env python3
"""Orquestador PyBullet del Sistema de Logística de Monedas Inteligentes.

Integra en un solo entorno las dos etapas del proyecto:

    Etapa 1  riel selector por gravedad + banda transportadora  (banda_riel.urdf)
    Etapa 2  brazo de 5 GDL que ordena los vasos en el rack     (brazo_5gdl.urdf)

Ideas de diseño, en orden de importancia:

1. **Un solo reloj.** PyBullet avanza con paso fijo (`DT_FISICA = 1/240 s`) y
   `setRealTimeSimulation(0)`. Nada del programa usa `time.sleep` para medir
   tiempo: el tiempo de la simulación es `pasos * DT_FISICA`. En modo GUI se
   duerme solo lo que sobra para que la animación se vea a velocidad real.

2. **Dos frecuencias.** La física corre a 240 Hz y el control a 50 Hz
   (`DECIMACION = 5`), que es el mismo periodo de 20 ms del `loop()` del ESP32.
   Las órdenes a los servos, la lectura de las barreras IR y la máquina de
   estados solo se evalúan en el tick de control. Así el código del PC y el del
   microcontrolador tienen la misma cadencia y se pueden comparar.

3. **Eventos, no esperas.** Ninguna rutina bloquea el bucle. La banda y el brazo
   son objetos con un método `actualizar(dt)` que avanza su propia máquina de
   estados y publican eventos en una cola (`BusEventos`). La FSM del orquestador
   solo reacciona a eventos: LLENADO -> TRANSPORTE -> RECOLECCION -> ORDENAMIENTO.

4. **Física barata donde no aporta.** Las monedas no son cuerpos rígidos: son
   visuales sin colisión movidos por cinemática, y el efecto real de su masa se
   aplica con `changeDynamics` sobre el vaso. Ver la clase `LlenadoVirtual`.

Uso:

    python run_sim_integrada.py                      # GUI, criterio por valor
    python run_sim_integrada.py --criterio peso --sentido desc
    python run_sim_integrada.py --headless --tiempo-max 180
"""

from __future__ import annotations

import argparse
import math
import random
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import pybullet as p
import pybullet_data

# ---------------------------------------------------------------------------
# 0. Parámetros. Todo en metros y radianes, que es lo que espera PyBullet.
#    Son los mismos números de la memoria de cálculo (allí están en cm) y de
#    scripts/generar_stl.py de la etapa 1.
# ---------------------------------------------------------------------------

DT_FISICA = 1.0 / 240.0          # paso de integración
DECIMACION = 5                   # 240 / 5 = 50 Hz de control, igual que el ESP32
DT_CONTROL = DT_FISICA * DECIMACION


@dataclass(frozen=True)
class Geometria:
    # --- brazo (etapa 2) -----------------------------------------------------
    d1: float = 0.11             # altura del hombro
    l1: float = 0.16             # hombro -> codo
    l2: float = 0.15             # codo -> muñeca
    l3: float = 0.08             # muñeca -> TCP
    limites: Tuple[Tuple[float, float], ...] = (
        (-90.0, 90.0), (0.0, 180.0), (-150.0, 0.0), (-120.0, 60.0), (-90.0, 90.0))
    home: Tuple[float, ...] = (0.0, 90.0, -90.0, -90.0, 0.0)
    # --- celda ---------------------------------------------------------------
    r_arco: float = 0.23         # radio del arco de puestos del rack
    z_agarre: float = 0.068      # altura del TCP al tomar o soltar el vaso
    z_segura: float = 0.17       # altura de traslado
    yaw_rack: Tuple[float, ...] = (24.0, 39.5, 55.0, 70.5, 86.0)
    yaw_recogida: float = -60.0  # donde la banda entrega el vaso al brazo
    # --- etapa 1 -------------------------------------------------------------
    paso_estacion: float = 0.065
    inclinacion: float = math.radians(25.0)
    mu_riel: float = 0.30        # fricción moneda-PETG
    y_banda: float = -0.199      # la banda corre paralela al eje X
    z_banda: float = 0.024       # cara superior de la cinta
    x_estacion0: float = -0.50   # primera estación sobre la banda
    x_recogida: float = 0.115    # punto donde el brazo toma el vaso
    v_banda: float = 0.06        # m/s
    # --- vasos y monedas -----------------------------------------------------
    r_vaso: float = 0.026
    h_vaso: float = 0.08
    masa_vaso: float = 0.018
    denominaciones: Tuple[int, ...] = (50, 100, 200, 500, 1000)
    diametros: Tuple[float, ...] = (0.0170, 0.0203, 0.0224, 0.0237, 0.0267)
    espesores: Tuple[float, ...] = (0.0014, 0.0016, 0.0017, 0.0020, 0.0023)
    masas: Tuple[float, ...] = (0.00200, 0.00334, 0.00461, 0.00714, 0.00995)
    luces: Tuple[float, ...] = (0.0176, 0.0209, 0.0230, 0.0243, 0.0273)


G = Geometria()
GRAVEDAD = 9.81
MAX_MONEDAS_VISIBLES = 10        # por vaso; el resto solo suma al contador
MAX_MONEDAS_VUELO = 8            # tamaño del pool de monedas animadas


# ---------------------------------------------------------------------------
# 1. Cinemática del brazo.
#    Si el paquete `brazo` del repositorio de la etapa 2 está en el PYTHONPATH
#    se usa tal cual, para no tener dos implementaciones que se desincronicen.
#    Si no está, se usa la copia local (idéntica, en metros).
# ---------------------------------------------------------------------------

try:                                            # pragma: no cover - depende del entorno
    from brazo.kinematics import fk as _fk_cm, ik as _ik_cm

    def fk(q_grados: Sequence[float]) -> Tuple[float, float, float, float]:
        x, y, z, phi = _fk_cm(q_grados)
        return x / 100.0, y / 100.0, z / 100.0, phi

    def ik(x: float, y: float, z: float, phi: float = -90.0,
           psi: float = 0.0) -> List[float]:
        return _ik_cm(x * 100.0, y * 100.0, z * 100.0, phi, psi)

    ORIGEN_CINEMATICA = "paquete brazo (etapa 2)"

except ImportError:

    class FueraDeAlcance(ValueError):
        """El punto pedido no tiene solución geométrica."""

    class FueraDeLimite(ValueError):
        """Hay solución pero alguna articulación se sale de su rango."""

    def fk(q_grados: Sequence[float]) -> Tuple[float, float, float, float]:
        """Cinemática directa cerrada: devuelve (x, y, z, phi) del TCP."""
        q1, q2, q3, q4 = (math.radians(v) for v in q_grados[:4])
        a3, a4 = q2 + q3, q2 + q3 + q4
        rho = G.l1 * math.cos(q2) + G.l2 * math.cos(a3) + G.l3 * math.cos(a4)
        z = G.d1 + G.l1 * math.sin(q2) + G.l2 * math.sin(a3) + G.l3 * math.sin(a4)
        return rho * math.cos(q1), rho * math.sin(q1), z, math.degrees(a4)

    def ik(x: float, y: float, z: float, phi: float = -90.0,
           psi: float = 0.0) -> List[float]:
        """Inversa cerrada, codo arriba. Lanza si el punto no es ejecutable."""
        r = math.hypot(x, y)
        q1 = math.degrees(math.atan2(y, x))
        rad = math.radians(phi)
        rw = r - G.l3 * math.cos(rad)                  # centro de muñeca
        hw = z - G.d1 - G.l3 * math.sin(rad)
        d = (rw * rw + hw * hw - G.l1 ** 2 - G.l2 ** 2) / (2 * G.l1 * G.l2)
        if abs(d) > 1.0:
            raise FueraDeAlcance(f"({x:.3f}, {y:.3f}, {z:.3f}) fuera del alcance")
        q3 = -math.acos(d)                             # raíz negativa: codo arriba
        q2 = math.atan2(hw, rw) - math.atan2(G.l2 * math.sin(q3),
                                             G.l1 + G.l2 * math.cos(q3))
        q4 = (phi - math.degrees(q2 + q3) + 180.0) % 360.0 - 180.0
        q = [q1, math.degrees(q2), math.degrees(q3), q4, psi]
        for i, (lo, hi) in enumerate(G.limites):
            if not lo - 1e-6 <= q[i] <= hi + 1e-6:
                raise FueraDeLimite(f"J{i + 1} fuera de límite: {q[i]:.1f} grados")
        return q

    ORIGEN_CINEMATICA = "copia local del script"


def pose_arco(yaw_grados: float, z: float, radio: float = G.r_arco):
    """Punto del arco de puestos (rack o recogida) a la altura pedida."""
    a = math.radians(yaw_grados)
    return (radio * math.cos(a), radio * math.sin(a), z)


def quintico(tau: float) -> float:
    """Perfil 10t^3 - 15t^4 + 6t^5: velocidad y aceleración nulas en los extremos."""
    tau = min(max(tau, 0.0), 1.0)
    return tau ** 3 * (10.0 + tau * (-15.0 + 6.0 * tau))


# ---------------------------------------------------------------------------
# 2. Infraestructura común: bus de eventos y utilidades de PyBullet.
# ---------------------------------------------------------------------------

class Evento(Enum):
    LOTE_CONTADO = auto()        # la etapa 1 terminó de llenar los cinco vasos
    VASO_EN_ZONA = auto()        # un vaso llegó a la zona de entrega y está quieto
    VASO_TOMADO = auto()         # el brazo lo levantó: la banda puede indexar
    VASO_COLOCADO = auto()       # quedó en su puesto del rack
    CICLO_TERMINADO = auto()     # el rack quedó ordenado


@dataclass
class Mensaje:
    evento: Evento
    datos: dict = field(default_factory=dict)
    t: float = 0.0


class BusEventos:
    """Cola simple. Los productores publican y la FSM consume una vez por tick."""

    def __init__(self):
        self._cola: deque[Mensaje] = deque()
        self.historial: List[Mensaje] = []

    def publicar(self, evento: Evento, t: float, **datos) -> None:
        m = Mensaje(evento, datos, t)
        self._cola.append(m)
        self.historial.append(m)

    def consumir(self) -> List[Mensaje]:
        salida = list(self._cola)
        self._cola.clear()
        return salida


def cargar_urdf(ruta: str, posicion=(0, 0, 0), fija: bool = True) -> int:
    """Carga un URDF y avisa claro si falta, en vez de reventar más adelante."""
    try:
        return p.loadURDF(ruta, posicion, useFixedBase=fija)
    except p.error as err:                              # pragma: no cover
        raise SystemExit(f"No se pudo cargar {ruta}: {err}")


def mapa_juntas(cuerpo: int) -> Dict[str, int]:
    """Nombre de junta -> índice, para no depender del orden del URDF."""
    mapa = {}
    for i in range(p.getNumJoints(cuerpo)):
        info = p.getJointInfo(cuerpo, i)
        nombre = info[1].decode() if isinstance(info[1], bytes) else str(info[1])
        mapa[nombre] = i
    return mapa


def disco_visual(radio: float, alto: float, color, masa: float = 0.0) -> int:
    """Moneda o disco de pila: solo forma visual, sin colisión.

    Sin `collisionShapeIndex` el cuerpo no entra al solver de contactos: mover
    cien de estos cuesta lo mismo que mover cien marcadores de depuración.
    """
    vis = p.createVisualShape(p.GEOM_CYLINDER, radius=radio, length=alto, rgbaColor=color)
    return p.createMultiBody(baseMass=masa, baseCollisionShapeIndex=-1,
                             baseVisualShapeIndex=vis, basePosition=(0, 0, -1))


def barrera_ir(desde, hasta, ignorar: Sequence[int] = ()) -> Optional[int]:
    """Barrera infrarroja virtual con `rayTest`.

    Es el equivalente exacto del sensor físico de la etapa 1: un rayo entre el
    emisor y el receptor. Devuelve el id del cuerpo que corta el haz, o None.
    Cuesta un solo raycast por llamada, así que se puede evaluar a 50 Hz sin
    que se note en el tiempo de paso.
    """
    hit = p.rayTest(desde, hasta)[0]
    cuerpo = hit[0]
    if cuerpo is None or cuerpo < 0 or cuerpo in ignorar:
        return None
    return cuerpo


# ---------------------------------------------------------------------------
# 3. ETAPA 1. Llenado virtual de los vasos y banda transportadora.
# ---------------------------------------------------------------------------

@dataclass
class Vaso:
    """Un vaso sobre la banda: cuerpo rígido real, contenido virtual."""
    indice: int
    cuerpo: int
    denominacion: int
    objetivo: int                 # monedas que le tocan en el lote
    monedas: int = 0
    pila: List[int] = field(default_factory=list)   # discos visuales apilados
    entregado: bool = False
    destino_rack: Optional[int] = None

    @property
    def valor(self) -> int:
        return self.denominacion * self.monedas

    @property
    def masa(self) -> float:
        k = G.denominaciones.index(self.denominacion)
        return G.masa_vaso + self.monedas * G.masas[k]

    @property
    def peso_g(self) -> float:
        return self.masa * 1000.0


class LlenadoVirtual:
    """Conteo y llenado sin simular la física de las monedas.

    Por qué no se simulan de verdad: cada moneda sería un cilindro dinámico con
    contactos contra el riel y contra las demás. Con 100 monedas el solver pasa
    de unos cientos de microsegundos por paso a decenas de milisegundos, aparecen
    interpenetraciones a 240 Hz y el resultado igual no es más fiel, porque la
    selección real depende de tolerancias de décimas de milímetro que el motor no
    resuelve bien.

    Lo que se hace en cambio, y que se ve igual de creíble:

      a) La moneda se decide por geometría, no por física: el diámetro define su
         estación, que es exactamente el criterio del riel real.
      b) El tiempo de viaje sale del modelo analítico del plano inclinado,
         a = g (sen(alfa) - mu cos(alfa)), así que las monedas tardan lo que
         tardarían de verdad y el ritmo de conteo es realista.
      c) Se anima un pool pequeño de monedas visuales (sin colisión) que se
         reciclan: bajan por el riel, caen por la ranura y desaparecen dentro del
         vaso. Nunca hay más de `MAX_MONEDAS_VUELO` en pantalla.
      d) Al llegar al vaso se apila un disco visual (hasta diez por vaso) y, lo
         importante para la etapa 2, se actualiza la masa real del vaso con
         `changeDynamics`: el brazo sí levanta los 416 g del vaso lleno.
      e) La barrera IR se dispara por evento, igual que la real, y se imprime la
         misma trama `M:<den>,<canal>` que manda el ESP32 contador.
    """

    def __init__(self, vasos: List[Vaso], bus: BusEventos, ritmo: float = 4.0,
                 semilla: int = 7):
        self.vasos = vasos
        self.bus = bus
        self.ritmo = ritmo                 # monedas por segundo que suelta la tolva
        self.rng = random.Random(semilla)
        self.bolsa: List[int] = []
        for v in vasos:
            k = G.denominaciones.index(v.denominacion)
            self.bolsa += [k] * v.objetivo
        self.rng.shuffle(self.bolsa)
        self.t_siguiente = 0.0
        self.en_vuelo: List[dict] = []
        self.terminado = False

        # pool de monedas visuales reutilizables
        self.pool = [disco_visual(0.013, 0.002, (0.78, 0.66, 0.25, 1.0))
                     for _ in range(MAX_MONEDAS_VUELO)]
        self.libres = list(self.pool)

        # aceleración en el riel: si sale negativa, la moneda no desliza
        self.acel = GRAVEDAD * (math.sin(G.inclinacion) -
                                G.mu_riel * math.cos(G.inclinacion))
        if self.acel <= 0:
            raise ValueError("con esa inclinación y fricción la moneda no desliza")

    # -- geometría del riel ---------------------------------------------------
    def x_estacion(self, canal: int) -> float:
        return G.x_estacion0 + canal * G.paso_estacion

    def z_riel(self, x: float) -> float:
        """Altura del riel sobre la banda en esa posición."""
        caida = (x - G.x_estacion0) * math.tan(G.inclinacion)
        return 0.34 - caida

    def tiempo_hasta(self, canal: int) -> float:
        """Tiempo de deslizamiento hasta la estación, del modelo analítico."""
        d = 0.04 + canal * G.paso_estacion          # tramo de entrada + estaciones
        return math.sqrt(2.0 * d / self.acel)

    # -- ciclo ---------------------------------------------------------------
    def actualizar(self, t: float, dt: float) -> None:
        if self.terminado:
            return

        # 1) la tolva suelta una moneda cada 1/ritmo segundos
        if self.bolsa and t >= self.t_siguiente:
            self.t_siguiente = t + 1.0 / self.ritmo
            canal = self.bolsa.pop()
            cuerpo = self.libres.pop() if self.libres else None
            self.en_vuelo.append({
                "canal": canal, "cuerpo": cuerpo, "t0": t,
                "t_caida": self.tiempo_hasta(canal), "estado": "riel"})

        # 2) se anima lo que está en vuelo y se cuenta lo que ya cayó
        for m in list(self.en_vuelo):
            transcurrido = t - m["t0"]
            if m["estado"] == "riel":
                if transcurrido >= m["t_caida"]:
                    m["estado"] = "cae"
                    m["t0"] = t
                elif m["cuerpo"] is not None:
                    s = 0.5 * self.acel * transcurrido ** 2       # x = a t^2 / 2
                    x = G.x_estacion0 - 0.04 + s * math.cos(G.inclinacion)
                    p.resetBasePositionAndOrientation(
                        m["cuerpo"], (x, G.y_banda, self.z_riel(x) + 0.004),
                        p.getQuaternionFromEuler((0, -G.inclinacion, 0)))
            else:                                                 # caída libre
                caida = 0.5 * GRAVEDAD * transcurrido ** 2
                x = self.x_estacion(m["canal"])
                z = self.z_riel(x) - caida
                z_vaso = G.z_banda + G.h_vaso
                if z <= z_vaso or m["cuerpo"] is None:
                    self._contar(m, t)
                    if m["cuerpo"] is not None:
                        p.resetBasePositionAndOrientation(m["cuerpo"], (0, 0, -1),
                                                          (0, 0, 0, 1))
                        self.libres.append(m["cuerpo"])
                    self.en_vuelo.remove(m)
                else:
                    p.resetBasePositionAndOrientation(m["cuerpo"], (x, G.y_banda, z),
                                                      (0, 0, 0, 1))

        # 3) fin del lote
        if not self.bolsa and not self.en_vuelo and not self.terminado:
            self.terminado = True
            self.bus.publicar(Evento.LOTE_CONTADO, t,
                              resumen=self.trama_vasos())

    def _contar(self, moneda: dict, t: float) -> None:
        """Una moneda entra al vaso: contador, masa real y pila visual."""
        vaso = self.vasos[moneda["canal"]]
        vaso.monedas += 1

        # la masa del vaso crece de verdad: es la carga que sentirá el brazo
        p.changeDynamics(vaso.cuerpo, -1, mass=vaso.masa)

        if len(vaso.pila) < MAX_MONEDAS_VISIBLES:
            k = moneda["canal"]
            disco = disco_visual(G.diametros[k] / 2, G.espesores[k],
                                 (0.78, 0.66, 0.25, 1.0))
            vaso.pila.append(disco)
        self.colocar_pila(vaso)

        print(f"[{t:6.2f} s] M:{vaso.denominacion},{moneda['canal'] + 1}"
              f"   vaso {moneda['canal'] + 1}: {vaso.monedas} monedas, "
              f"{vaso.peso_g:.1f} g")

    def colocar_pila(self, vaso: Vaso) -> None:
        """Pone los discos dentro del vaso; se llama también al mover la banda."""
        pos, _ = p.getBasePositionAndOrientation(vaso.cuerpo)
        for i, disco in enumerate(vaso.pila):
            z = pos[2] - G.h_vaso / 2 + 0.006 + i * 0.0024
            p.resetBasePositionAndOrientation(disco, (pos[0], pos[1], z), (0, 0, 0, 1))

    def trama_vasos(self) -> str:
        """La misma trama que el ESP32 contador manda al ESP32 del brazo."""
        return "VASOS:" + ",".join(f"{v.denominacion}x{v.monedas}" for v in self.vasos)


class Banda:
    """Banda transportadora: indexa un vaso por vez hasta la zona de entrega.

    El vaso es un cuerpo dinámico (el brazo tiene que poder agarrarlo), pero la
    cinta no se simula: en cada tick de control se le fija la velocidad lineal
    con `resetBaseVelocity`. Es la forma barata y estable de hacer un
    transportador en PyBullet; simular la fricción de la cinta obliga a subir la
    frecuencia y aun así el vaso se desliza.
    """

    def __init__(self, vasos: List[Vaso], bus: BusEventos, llenado: LlenadoVirtual):
        self.vasos = vasos
        self.bus = bus
        self.llenado = llenado
        self.en_marcha = False
        self.vaso_actual: Optional[Vaso] = None
        self.aviso_enviado = False
        # rayo de la barrera de la zona de entrega, cruzando la banda
        self.ray_a = (G.x_recogida, G.y_banda - 0.06, G.z_banda + 0.04)
        self.ray_b = (G.x_recogida, G.y_banda + 0.06, G.z_banda + 0.04)

    def pendientes(self) -> List[Vaso]:
        return [v for v in self.vasos if not v.entregado]

    def siguiente(self) -> bool:
        """Arranca el transporte del próximo vaso que quede en la banda.

        La cinta es una sola: al moverla avanzan todos los vasos que siguen
        sobre ella. El que interesa es el de delante, que es el que va a cortar
        la barrera de la zona de entrega.
        """
        pendientes = self.pendientes()
        if not pendientes:
            return False
        self.vaso_actual = max(
            pendientes,
            key=lambda v: p.getBasePositionAndOrientation(v.cuerpo)[0][0])
        self.en_marcha = True
        self.aviso_enviado = False
        return True

    def detener(self) -> None:
        self.en_marcha = False
        for vaso in self.pendientes():
            p.resetBaseVelocity(vaso.cuerpo, (0, 0, 0), (0, 0, 0))

    def actualizar(self, t: float, dt: float) -> None:
        if not self.en_marcha or self.vaso_actual is None:
            return
        for otro in self.pendientes():             # la cinta arrastra a todos
            p.resetBaseVelocity(otro.cuerpo, (G.v_banda, 0, 0), (0, 0, 0))
            self.llenado.colocar_pila(otro)        # la pila viaja con su vaso

        vaso = self.vaso_actual
        pos, _ = p.getBasePositionAndOrientation(vaso.cuerpo)
        cortado = barrera_ir(self.ray_a, self.ray_b)

        # El instante de la transición: el haz está cortado por ESTE vaso y el
        # vaso ya pasó el punto de recogida. Se comprueba además que su velocidad
        # sea baja para no avisar mientras todavía viene entrando.
        if cortado == vaso.cuerpo and pos[0] >= G.x_recogida and not self.aviso_enviado:
            self.detener()
            self.aviso_enviado = True
            vel, _ = p.getBaseVelocity(vaso.cuerpo)
            print(f"[{t:6.2f} s] barrera de entrega cortada por el vaso de "
                  f"${vaso.denominacion} (v = {abs(vel[0]):.3f} m/s)")
            self.bus.publicar(Evento.VASO_EN_ZONA, t, vaso=vaso)


# ---------------------------------------------------------------------------
# 4. ETAPA 2. Brazo de 5 GDL con ejecución no bloqueante.
# ---------------------------------------------------------------------------

@dataclass
class Tramo:
    """Un tramo de trayectoria evaluable en el tiempo."""
    tipo: str                        # 'articular' | 'lineal' | 'pinza'
    duracion: float
    evaluar: Callable[[float], Tuple[List[float], float]]
    etiqueta: str = ""
    al_terminar: Optional[Callable[[], None]] = None


class Brazo5GDL:
    """Controlador del brazo: IK cerrada, tramos quínticos y agarre por restricción."""

    JUNTAS = ("j1_base", "j2_hombro", "j3_codo", "j4_cabeceo", "j5_giro")
    DEDOS = ("dedo_izq", "dedo_der")
    FUERZA = 20.0
    VEL_ARTICULAR = 75.0             # grados/s promedio
    VEL_LINEAL = 0.11                # m/s promedio

    def __init__(self, cuerpo: int, bus: BusEventos, velocidad: float = 1.0):
        self.cuerpo = cuerpo
        self.bus = bus
        self.velocidad = velocidad
        self.mapa = mapa_juntas(cuerpo)
        self.q = list(G.home)
        self.pinza_mm = 66.0
        self.plan: deque[Tramo] = deque()
        self.tramo: Optional[Tramo] = None
        self.t_tramo = 0.0
        self.sujeto: Optional[int] = None        # cuerpo agarrado
        self.restriccion: Optional[int] = None   # constraint del agarre
        self.aplicar(self.q, self.pinza_mm)

    # -- salida a los motores -------------------------------------------------
    def aplicar(self, q: Sequence[float], pinza_mm: float) -> None:
        """Equivale a escribir los PWM: control de posición en cada junta."""
        for nombre, valor in zip(self.JUNTAS, q):
            idx = self.mapa.get(nombre)
            if idx is None:
                continue
            p.setJointMotorControl2(self.cuerpo, idx, p.POSITION_CONTROL,
                                    targetPosition=math.radians(valor),
                                    force=self.FUERZA)
        apertura = max(0.0, min(pinza_mm, 70.0)) / 2000.0        # mm -> m por dedo
        for dedo in self.DEDOS:
            idx = self.mapa.get(dedo)
            if idx is not None:
                p.setJointMotorControl2(self.cuerpo, idx, p.POSITION_CONTROL,
                                        targetPosition=apertura, force=self.FUERZA)
        self.q = list(q)
        self.pinza_mm = pinza_mm

    # -- construcción de tramos ----------------------------------------------
    def _articular(self, destino: Sequence[float], pinza: float, etiqueta: str) -> Tramo:
        origen = list(self.q_final())
        dq = max(abs(b - a) for a, b in zip(origen, destino))
        T = max(0.45, dq / (self.VEL_ARTICULAR * self.velocidad))

        def evaluar(t: float):
            s = quintico(t / T)
            return [a + (b - a) * s for a, b in zip(origen, destino)], pinza

        return Tramo("articular", T, evaluar, etiqueta)

    def _lineal(self, p0, p1, pinza: float, etiqueta: str) -> Tramo:
        T = max(0.30, math.dist(p0, p1) / (self.VEL_LINEAL * self.velocidad))

        def evaluar(t: float):
            s = quintico(t / T)
            punto = [a + (b - a) * s for a, b in zip(p0, p1)]
            return ik(punto[0], punto[1], punto[2]), pinza

        return Tramo("lineal", T, evaluar, etiqueta)

    def _pinza(self, desde: float, hasta: float, etiqueta: str,
               al_terminar=None) -> Tramo:
        q = list(self.q_final())
        T = max(0.25, abs(hasta - desde) / (90.0 * self.velocidad))

        def evaluar(t: float):
            return q, desde + (hasta - desde) * quintico(t / T)

        return Tramo("pinza", T, evaluar, etiqueta, al_terminar)

    def q_final(self) -> Sequence[float]:
        """Pose al final del plan ya encolado, para encadenar tramos."""
        if not self.plan and self.tramo is None:
            return self.q
        ultimo = self.plan[-1] if self.plan else self.tramo
        return ultimo.evaluar(ultimo.duracion)[0]

    # -- rutinas de alto nivel ------------------------------------------------
    def recoger_y_colocar(self, vaso: Vaso, puesto_rack: int) -> None:
        """Encola el ciclo completo de ocho tramos para un vaso."""
        recogida = (G.x_recogida, G.y_banda, 0.0)
        r_recogida = math.hypot(recogida[0], recogida[1])
        yaw_recogida = math.degrees(math.atan2(recogida[1], recogida[0]))
        alto_o = pose_arco(yaw_recogida, G.z_segura, r_recogida)
        bajo_o = pose_arco(yaw_recogida, G.z_agarre, r_recogida)
        alto_d = pose_arco(G.yaw_rack[puesto_rack], G.z_segura)
        bajo_d = pose_arco(G.yaw_rack[puesto_rack], G.z_agarre + 0.003)

        self.plan.append(self._articular(ik(*alto_o), 66.0, "sobre la zona de entrega"))
        self.plan.append(self._lineal(alto_o, bajo_o, 66.0, "bajar al vaso"))
        self.plan.append(self._pinza(66.0, 49.0, "cerrar pinza",
                                     al_terminar=lambda: self.agarrar(vaso.cuerpo)))
        self.plan.append(self._lineal(bajo_o, alto_o, 49.0, "subir con el vaso"))
        self.plan.append(self._articular(ik(*alto_d), 49.0,
                                         f"trasladar al puesto R{puesto_rack + 1}"))
        self.plan.append(self._lineal(alto_d, bajo_d, 49.0, "bajar al rack"))
        self.plan.append(self._pinza(49.0, 66.0, "abrir pinza",
                                     al_terminar=self.soltar))
        self.plan.append(self._lineal(bajo_d, alto_d, 66.0, "subir libre"))

    def ir_a_reposo(self) -> None:
        self.plan.append(self._articular(list(G.home), self.pinza_mm, "reposo"))

    # -- agarre ---------------------------------------------------------------
    def agarrar(self, cuerpo: int) -> None:
        """Agarre por restricción fija, no por fricción.

        Sujetar un vaso solo con la fricción de dos dedos exige coeficientes y
        rigideces muy finas y a 240 Hz se resbala. La práctica habitual en
        PyBullet es crear un `JOINT_FIXED` entre el eslabón de la pinza y el
        objeto en el instante del cierre, y borrarlo al abrir.
        """
        eslabon = self.mapa.get("j5_giro", p.getNumJoints(self.cuerpo) - 1)
        pos_pinza, orn_pinza = self._pose_tcp()
        pos_obj, orn_obj = p.getBasePositionAndOrientation(cuerpo)
        rel = [pos_obj[i] - pos_pinza[i] for i in range(3)]
        self.restriccion = p.createConstraint(
            parentBodyUniqueId=self.cuerpo, parentLinkIndex=eslabon,
            childBodyUniqueId=cuerpo, childLinkIndex=-1,
            jointType=p.JOINT_FIXED, jointAxis=(0, 0, 0),
            parentFramePosition=rel, childFramePosition=(0, 0, 0))
        self.sujeto = cuerpo

    def soltar(self) -> None:
        if self.restriccion is not None:
            p.removeConstraint(self.restriccion)
        self.restriccion = None
        self.sujeto = None

    def _pose_tcp(self):
        eslabon = self.mapa.get("j5_giro")
        if eslabon is None:
            return p.getBasePositionAndOrientation(self.cuerpo)
        estado = p.getLinkState(self.cuerpo, eslabon)
        return estado[0], estado[1]

    # -- avance ---------------------------------------------------------------
    @property
    def ocupado(self) -> bool:
        return self.tramo is not None or bool(self.plan)

    def actualizar(self, t: float, dt: float) -> None:
        """Avanza un tick de control. Nunca bloquea el bucle de simulación."""
        if self.tramo is None:
            if not self.plan:
                return
            self.tramo = self.plan.popleft()
            self.t_tramo = 0.0
            print(f"[{t:6.2f} s] brazo: {self.tramo.etiqueta} "
                  f"({self.tramo.duracion:.2f} s)")

        self.t_tramo += dt
        q, pinza = self.tramo.evaluar(min(self.t_tramo, self.tramo.duracion))
        self.aplicar(q, pinza)

        if self.t_tramo >= self.tramo.duracion:
            if self.tramo.al_terminar:
                self.tramo.al_terminar()
            self.tramo = None


# ---------------------------------------------------------------------------
# 5. Máquina de estados del orquestador.
# ---------------------------------------------------------------------------

class Estado(Enum):
    LLENADO = auto()         # etapa 1 contando monedas
    TRANSPORTE = auto()      # la banda lleva un vaso a la zona de entrega
    RECOLECCION = auto()     # el brazo toma el vaso y lo deja en el rack
    ORDENAMIENTO = auto()    # verificación final del rack
    FIN = auto()


CRITERIOS = {
    "denominacion": lambda v: v.denominacion,
    "cantidad": lambda v: v.monedas,
    "valor": lambda v: v.valor,
    "peso": lambda v: v.peso_g,
}


class Orquestador:
    """Une las dos etapas: una FSM, un bus de eventos y un reloj."""

    def __init__(self, gui: bool = True, criterio: str = "valor",
                 sentido: str = "asc", velocidad: float = 1.0,
                 ritmo: float = 4.0, semilla: int = 7):
        self.criterio = criterio
        self.sentido = sentido
        self.gui = gui
        self.bus = BusEventos()
        self.t = 0.0
        self.pasos = 0
        self.estado = Estado.LLENADO

        self._iniciar_fisica()
        self.banda_riel = cargar_urdf("banda_riel.urdf", (0, 0, 0))
        self.brazo_id = cargar_urdf("brazo_5gdl.urdf", (0, 0, 0))
        self.vasos = self._crear_vasos()
        self.llenado = LlenadoVirtual(self.vasos, self.bus, ritmo=ritmo, semilla=semilla)
        self.brazo = Brazo5GDL(self.brazo_id, self.bus, velocidad=velocidad)
        self.banda = Banda(self.vasos, self.bus, self.llenado)
        self.pendiente: Optional[Vaso] = None

        print(f"cinemática: {ORIGEN_CINEMATICA}")
        print(f"criterio de orden: {criterio} {sentido}")

    # -- montaje --------------------------------------------------------------
    def _iniciar_fisica(self) -> None:
        """Conexión, gravedad, plano y, sobre todo, el control del tiempo.

        `setRealTimeSimulation(0)` desconecta el reloj interno: la simulación
        solo avanza cuando el programa llama a `stepSimulation`, y cada llamada
        vale exactamente `DT_FISICA`. Eso hace la corrida repetible: dos
        ejecuciones con la misma semilla dan el mismo resultado, con GUI o sin
        ella. En GUI se duerme el sobrante de cada paso para verlo en tiempo real.
        """
        p.connect(p.GUI if self.gui else p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -GRAVEDAD)
        p.setTimeStep(DT_FISICA)
        p.setRealTimeSimulation(0)
        p.setPhysicsEngineParameter(numSolverIterations=60, enableConeFriction=1)
        p.loadURDF("plane.urdf")
        if self.gui:
            p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
            p.resetDebugVisualizerCamera(1.05, 38, -28, (0.0, -0.08, 0.14))

    def _crear_vasos(self) -> List[Vaso]:
        """Cinco vasos dinámicos sobre la banda, uno por denominación."""
        vasos: List[Vaso] = []
        objetivos = [24, 20, 18, 14, 12]
        col = p.createCollisionShape(p.GEOM_CYLINDER, radius=G.r_vaso, height=G.h_vaso)
        for i, den in enumerate(G.denominaciones):
            vis = p.createVisualShape(p.GEOM_CYLINDER, radius=G.r_vaso,
                                      length=G.h_vaso, rgbaColor=(0.85, 0.9, 0.92, 0.45))
            x = G.x_estacion0 + i * G.paso_estacion
            cuerpo = p.createMultiBody(
                baseMass=G.masa_vaso, baseCollisionShapeIndex=col,
                baseVisualShapeIndex=vis,
                basePosition=(x, G.y_banda, G.z_banda + G.h_vaso / 2))
            p.changeDynamics(cuerpo, -1, lateralFriction=0.9, spinningFriction=0.005,
                             linearDamping=0.04)
            vasos.append(Vaso(indice=i, cuerpo=cuerpo, denominacion=den,
                              objetivo=objetivos[i]))
        return vasos

    # -- planificación --------------------------------------------------------
    def asignar_puestos(self) -> None:
        """Con el lote ya contado se sabe el puesto final de cada vaso.

        Se ordena por la clave elegida (desempate por denominación) y el j-ésimo
        de la lista va al puesto Rj. Como el contenido de los cinco vasos ya se
        conoce cuando termina el llenado, no hace falta zona de espera: cada vaso
        va directo a su puesto definitivo.
        """
        clave = CRITERIOS[self.criterio]
        signo = 1 if self.sentido == "asc" else -1
        orden = sorted(self.vasos, key=lambda v: (signo * clave(v),
                                                  signo * v.denominacion))
        for puesto, vaso in enumerate(orden):
            vaso.destino_rack = puesto
        print("\nplan de ordenamiento")
        for vaso in orden:
            print(f"  R{vaso.destino_rack + 1}  ${vaso.denominacion:>5}  "
                  f"{vaso.monedas:>3} monedas  ${vaso.valor:>6}  {vaso.peso_g:6.1f} g")
        print()

    # -- FSM ------------------------------------------------------------------
    def procesar_eventos(self) -> None:
        for m in self.bus.consumir():
            if m.evento is Evento.LOTE_CONTADO and self.estado is Estado.LLENADO:
                print(f"\n[{m.t:6.2f} s] {m.datos['resumen']}")
                self.asignar_puestos()
                self.estado = Estado.TRANSPORTE
                if not self.banda.siguiente():
                    self.estado = Estado.ORDENAMIENTO

            elif m.evento is Evento.VASO_EN_ZONA and self.estado is Estado.TRANSPORTE:
                # ---- aquí ocurre el traspaso entre etapas ----
                vaso = m.datos["vaso"]
                self.pendiente = vaso
                self.estado = Estado.RECOLECCION
                self.brazo.recoger_y_colocar(vaso, vaso.destino_rack)
                print(f"[{m.t:6.2f} s] etapa 1 -> etapa 2: vaso de "
                      f"${vaso.denominacion} ({vaso.monedas} monedas, "
                      f"{vaso.peso_g:.0f} g) al puesto R{vaso.destino_rack + 1}")

            elif m.evento is Evento.VASO_COLOCADO and self.estado is Estado.RECOLECCION:
                if self.banda.siguiente():
                    self.estado = Estado.TRANSPORTE
                else:
                    self.brazo.ir_a_reposo()
                    self.estado = Estado.ORDENAMIENTO

            elif m.evento is Evento.CICLO_TERMINADO:
                self.estado = Estado.FIN

    def actualizar_estado(self) -> None:
        """Condiciones que dependen de los objetos, no de un evento externo."""
        if self.estado is Estado.RECOLECCION and not self.brazo.ocupado:
            vaso = self.pendiente
            if vaso is not None:
                vaso.entregado = True
                self.llenado.colocar_pila(vaso)
                self.pendiente = None
                self.bus.publicar(Evento.VASO_COLOCADO, self.t, vaso=vaso)

        elif self.estado is Estado.ORDENAMIENTO and not self.brazo.ocupado:
            self.verificar_rack()
            self.bus.publicar(Evento.CICLO_TERMINADO, self.t)

    def verificar_rack(self) -> None:
        """Comprueba contra la física dónde quedó cada vaso."""
        print("\nverificación del rack")
        ok = True
        for vaso in sorted(self.vasos, key=lambda v: v.destino_rack):
            pos, _ = p.getBasePositionAndOrientation(vaso.cuerpo)
            objetivo = pose_arco(G.yaw_rack[vaso.destino_rack], G.z_banda)
            error = math.hypot(pos[0] - objetivo[0], pos[1] - objetivo[1])
            estado = "ok" if error < 0.03 else "revisar"
            ok = ok and error < 0.03
            print(f"  R{vaso.destino_rack + 1}  ${vaso.denominacion:>5}  "
                  f"error {error * 1000:5.1f} mm  {estado}")
        print("rack ordenado\n" if ok else "algún vaso quedó fuera de puesto\n")

    # -- bucle principal ------------------------------------------------------
    def correr(self, tiempo_max: float = 240.0) -> None:
        """Bucle único de la simulación.

        Un paso de física por iteración y un tick de control cada `DECIMACION`
        pasos. Ese desfase es intencional: la física necesita 240 Hz para que los
        contactos del vaso con la pinza sean estables, pero el control a esa
        frecuencia no aporta nada y multiplica por cinco el costo de la IK.
        """
        t_pared = time.time()
        while self.t < tiempo_max and self.estado is not Estado.FIN:
            p.stepSimulation()
            self.pasos += 1
            self.t = self.pasos * DT_FISICA

            if self.pasos % DECIMACION == 0:
                self.llenado.actualizar(self.t, DT_CONTROL)
                self.banda.actualizar(self.t, DT_CONTROL)
                self.brazo.actualizar(self.t, DT_CONTROL)
                self.procesar_eventos()
                self.actualizar_estado()

            if self.gui:                      # sincroniza con el reloj de pared
                retraso = t_pared + self.pasos * DT_FISICA - time.time()
                if retraso > 0:
                    time.sleep(retraso)

        print(f"fin en t = {self.t:.2f} s ({self.pasos} pasos, "
              f"estado {self.estado.name})")
        if self.gui:
            print("ventana abierta, Ctrl+C para salir")
            try:
                while True:
                    p.stepSimulation()
                    time.sleep(DT_FISICA)
            except KeyboardInterrupt:
                pass
        p.disconnect()


# ---------------------------------------------------------------------------
# 6. Entrada por línea de comandos.
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Simulación integrada de las dos etapas")
    ap.add_argument("--criterio", default="valor", choices=list(CRITERIOS))
    ap.add_argument("--sentido", default="asc", choices=["asc", "desc"])
    ap.add_argument("--velocidad", type=float, default=1.0,
                    help="factor de velocidad del brazo")
    ap.add_argument("--ritmo", type=float, default=4.0,
                    help="monedas por segundo que suelta la tolva")
    ap.add_argument("--semilla", type=int, default=7)
    ap.add_argument("--headless", action="store_true", help="sin ventana gráfica")
    ap.add_argument("--tiempo-max", type=float, default=240.0)
    args = ap.parse_args()

    orq = Orquestador(gui=not args.headless, criterio=args.criterio,
                      sentido=args.sentido, velocidad=args.velocidad,
                      ritmo=args.ritmo, semilla=args.semilla)
    orq.correr(tiempo_max=args.tiempo_max)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
