"""Simulación del brazo clasificador en PyBullet.

    pip install pybullet
    python sim/pybullet/run_sim.py                  # con interfaz gráfica
    python sim/pybullet/run_sim.py --criterio peso --sentido desc
    python sim/pybullet/run_sim.py --headless --video salida.mp4

El planificador, la cinemática y las trayectorias son los mismos módulos que
usa el PC para hablar con el ESP32: aquí solo cambia el destino de las poses.
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "software"))

import pybullet as p                                     # noqa: E402
import pybullet_data                                     # noqa: E402

from brazo.config import HOME, PINZA_ABIERTA_MM          # noqa: E402
from brazo.controller import Controlador                 # noqa: E402
from brazo.cups import lote_aleatorio, lote_demo         # noqa: E402
from celda import crear_celda                            # noqa: E402

URDF = RAIZ / "sim" / "pybullet" / "brazo_clasificador.urdf"
JUNTAS = ["j1_base", "j2_hombro", "j3_codo", "j4_cabeceo", "j5_giro"]
DEDOS = ["dedo_izq", "dedo_der"]
FUERZA = 20.0


def indices(robot):
    mapa = {}
    for i in range(p.getNumJoints(robot)):
        mapa[p.getJointInfo(robot, i)[1].decode()] = i
    return mapa


def aplicar_pose(robot, mapa, q, pinza_mm):
    """Envía la pose a los motores de posición, igual que el PWM a los servos."""
    for nombre, valor in zip(JUNTAS, q):
        p.setJointMotorControl2(robot, mapa[nombre], p.POSITION_CONTROL,
                                targetPosition=math.radians(valor), force=FUERZA)
    apertura = max(0.0, min(pinza_mm, 70.0)) / 2000.0     # mm a m, por dedo
    for dedo in DEDOS:
        p.setJointMotorControl2(robot, mapa[dedo], p.POSITION_CONTROL,
                                targetPosition=apertura, force=FUERZA)


def main() -> int:
    ap = argparse.ArgumentParser(description="Simulación PyBullet del brazo clasificador")
    ap.add_argument("--criterio", default="valor",
                    choices=["denominacion", "cantidad", "valor", "peso"])
    ap.add_argument("--sentido", default="asc", choices=["asc", "desc"])
    ap.add_argument("--velocidad", type=float, default=1.0)
    ap.add_argument("--aleatorio", action="store_true")
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--video", help="graba un mp4 (requiere ffmpeg en el sistema)")
    args = ap.parse_args()

    p.connect(p.DIRECT if args.headless else p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.81)
    p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
    p.resetDebugVisualizerCamera(0.95, 42, -28, [0.05, 0, 0.12])
    p.loadURDF("plane.urdf")

    robot = p.loadURDF(str(URDF), [0, 0, 0], useFixedBase=True)
    mapa = indices(robot)
    aplicar_pose(robot, mapa, HOME, PINZA_ABIERTA_MM)

    vasos = lote_aleatorio() if args.aleatorio else lote_demo()
    crear_celda(vasos)

    if args.video:
        p.startStateLogging(p.STATE_LOGGING_VIDEO_MP4, args.video)

    ctrl = Controlador(vasos, velocidad=args.velocidad, dt=1 / 240)

    reloj = {"t": time.time()}

    def al_avanzar(_t, q, pinza):
        aplicar_pose(robot, mapa, q, pinza)
        p.stepSimulation()
        if not args.headless:
            time.sleep(max(0.0, 1 / 240 - (time.time() - reloj["t"])))
            reloj["t"] = time.time()

    print(f"Clasificando por {args.criterio} ({args.sentido})")
    resumen = ctrl.ordenar(args.criterio, args.sentido, al_avanzar=al_avanzar)
    for i, m in enumerate(resumen["movimientos"], 1):
        print(f"  {i}. {m}")
    print(f"Tiempo simulado: {resumen['segundos']} s")

    if not args.headless:
        print("Ventana abierta. Ctrl+C para salir.")
        try:
            while True:
                p.stepSimulation()
                time.sleep(1 / 240)
        except KeyboardInterrupt:
            pass
    p.disconnect()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
