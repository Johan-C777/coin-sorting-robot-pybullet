"""Riel horizontal de moneda de canto con ventanas por altura y un empujador lento (dedo en mocap)."""
from __future__ import annotations
import math
import numpy as np
import mujoco
from entrada import construir, xml_mundo
from riel_canto import MONEDAS, _quat

VENT = ["N50", "N100", "A50", "N200", "A100", "A500", "A200", "N1000"]


def ventanas(a0=150.0, paso=42.0, dH=0.25, largo_extra=8.0, orden=VENT):
    out = []
    for i, k in enumerate(orden):
        d = MONEDAS[k][0]
        out.append((a0 + i * paso, a0 + i * paso + d + largo_extra, d + dH))
    return out


def correr(moneda, mu=0.4, lean=25.0, v=60.0, s0=60.0, V=None, dedo_dim=(4.0, 14.0, 6.0), dedo_t=None, dedo_n=3.5,
           yaw=0.0, tmax=None, espera=0.3, dH=0.25, pend=0.0, dd=0.0, largo_extra=8.0):
    d, e, m = MONEDAS[moneda]
    d = d + dd
    V = V or ventanas(dH=dH, largo_extra=largo_extra)
    s_fin = V[-1][1] + 60
    P = construir(mu=mu, lean=lean, tau0=90.0 - lean, s_tw0=0.0, s_tw1=0.0, s_fin=s_fin, ventanas=V, pend=pend)
    t1, n1 = P.dirs(P.tau1)
    centro = s0 * P.S + (d / 2 + 0.05) * t1 + (e / 2 + 0.05) * n1
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    ez = n1 * cy + P.S * sy
    ex = np.cross(t1, ez); ex /= np.linalg.norm(ex)
    ey = np.cross(ez, ex)
    q = _quat(np.column_stack([ex, ey, ez]))
    s_d0 = s0 - d / 2 - dedo_dim[0] / 2 - 0.5
    dt = d / 2 if dedo_t is None else dedo_t
    MONEDAS_bak = MONEDAS[moneda]
    MONEDAS[moneda] = (d, e, m)
    xml = xml_mundo(P, moneda, centro, q, dedo_pos=(s_d0, dt, dedo_n), dedo_dim=dedo_dim)
    MONEDAS[moneda] = MONEDAS_bak
    mod = mujoco.MjModel.from_xml_string(xml)
    dat = mujoco.MjData(mod)
    cid = mod.body("dedo").mocapid[0]
    tmax = tmax or (espera + (s_fin - s_d0) / v + 0.5)
    tq = _quat(np.column_stack([P.S, t1, n1]))
    cae = None
    while dat.time < tmax:
        sd = s_d0 + v * max(0.0, dat.time - espera)
        c = sd * P.S + dt * t1 + dedo_n * n1
        dat.mocap_pos[cid] = c / 1000
        mujoco.mj_step(mod, dat)
        p = dat.qpos[:3] * 1000
        if p @ n1 < -10.0:
            cae = float(p @ P.S); break
        if p[2] < -300: cae = float(p @ P.S); break
    p = dat.qpos[:3] * 1000
    w = None
    if cae is not None:
        for i, (a, b, H) in enumerate(V):
            if a - 3 <= cae <= b + 3: w = VENT[i]
    return dict(cae=cae, ventana=w, s=float(p @ P.S), n=float(p @ n1), t=float(p @ t1), tiempo=float(dat.time))
