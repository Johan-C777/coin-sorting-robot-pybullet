"""Tolva de disco inclinado: la moneda sale por el hueco del disco (a 45°) y cae sobre el inicio de la pista
(placa a LEAN de la vertical, repisa, pendiente PEND). ¿Queda de canto y rueda sola sin aleta ni servo?
Marco y pista iguales a rodar.py (la pendiente se simula inclinando la gravedad)."""
from __future__ import annotations
import math, sys, itertools
import numpy as np
import mujoco
from riel_canto import MONEDAS, _quat
from rodar import xml


def correr(moneda, mu=0.45, disco=45.0, lean=20.0, pend=22.0, x0=25.0, sube=6.0, frente=1.0, v0=60.0, tmax=2.0, x_fin=150.0):
    d, e, m = MONEDAS[moneda]
    g = math.radians(lean)
    ex = np.array([1.0, 0, 0]); p_ = np.array([0, -math.sin(g), math.cos(g)]); n_ = np.array([0, math.cos(g), math.sin(g)])
    a = math.radians(disco)
    nd = np.array([0, math.cos(a), math.sin(a)])            # eje de la moneda = normal del disco
    rel = math.radians(90 - lean - disco)                     # ángulo entre disco y placa
    c = x0 * ex + (d / 2 + sube) * p_ + ((d / 2) * math.sin(rel) + e / 2 + frente) * n_
    q = _quat(np.column_stack([ex, np.cross(nd, ex), nd]))
    mod = mujoco.MjModel.from_xml_string(xml(moneda, c, q, d, L=0.5, mu=mu, lean=lean, pend=pend, pared=True))
    dat = mujoco.MjData(mod)
    dat.mocap_pos[mod.body("bandeja").mocapid[0]] = [0, 0, -1]
    # sale del disco con la velocidad del bolsillo, hacia abajo de la placa
    dat.qvel[:3] = (-v0 * p_) / 1000
    while dat.time < tmax:
        mujoco.mj_step(mod, dat)
        pos = dat.qpos[:3] * 1000
        if pos @ p_ < -10:
            return "cae", dat.time
        if pos[0] > x_fin:
            R = np.zeros(9); mujoco.mju_quat2Mat(R, dat.qpos[3:7]); eje = R.reshape(3, 3)[:, 2]
            de_canto = abs(eje @ n_) > 0.93 and abs(pos @ p_ - d / 2) < 2.5
            return ("ok" if de_canto else "volcada"), dat.time
    return "no_llega", dat.time


if __name__ == "__main__":
    disco = float(sys.argv[1]) if len(sys.argv) > 1 else 45.0
    res = {}
    for mon, mu, sube, fr in itertools.product(MONEDAS, (0.3, 0.45, 0.7), (3.0, 10.0, 20.0), (0.5, 3.0)):
        r, t = correr(mon, mu=mu, disco=disco, sube=sube, frente=fr)
        res.setdefault(r, []).append((mon, mu, sube, fr, round(t, 2)))
    tot = sum(len(v) for v in res.values())
    for k, v in res.items():
        print(k, len(v), "/", tot, v[:6] if k != "ok" else "", "t max %.2f s" % max(x[-1] for x in v) if k == "ok" else "")
