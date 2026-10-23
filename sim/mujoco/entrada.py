"""Entrada con torsión + riel de canto + tope (dedo) que baja lento. MuJoCo.

Marco de la pista: s baja por la pista (inclinada `pend` grados), el origen de la sección es la arista del labio.
En la sección (perpendicular a s) la placa tiene una inclinación tau(s) respecto a la horizontal: 10° al inicio
(canal plano con pared guía) y 90°-lean al final (placa casi vertical con repisa).
"""
from __future__ import annotations
import math
import numpy as np
import mujoco
from riel_canto import MONEDAS, _quat

PEND = 22.0


def ejes_pista(pend=PEND):
    b = math.radians(pend)
    S = np.array([math.cos(b), 0.0, -math.sin(b)])
    Zc = np.array([math.sin(b), 0.0, math.cos(b)])     # "arriba" perpendicular a la pista
    Yc = np.array([0.0, 1.0, 0.0])
    return S, Yc, Zc


class Pista:
    def __init__(self, mu=0.35, pend=PEND, solref="0.004 1"):
        self.S, self.Yc, self.Zc = ejes_pista(pend)
        self.mu, self.solref = mu, solref
        self.geoms = []
        self.assets = []
        self.pend = pend

    def dirs(self, tau):
        """t (sube por la placa) y n (sale de la placa hacia las monedas) en el mundo, para inclinación tau."""
        a = math.radians(tau)
        t = math.cos(a) * self.Yc + math.sin(a) * self.Zc
        n = -math.sin(a) * self.Yc + math.cos(a) * self.Zc
        return t, n

    def caja(self, s0, s1, t0, t1, n0, n1, tau, nombre=None, rgba="0.6 0.6 0.7 1"):
        t, n = self.dirs(tau)
        c = (s0 + s1) / 2 * self.S + (t0 + t1) / 2 * t + (n0 + n1) / 2 * n
        q = _quat(np.column_stack([self.S, t, n]))
        h = ((s1 - s0) / 2, (t1 - t0) / 2, (n1 - n0) / 2)
        self.geoms.append(
            f'<geom type="box" pos="{c[0]/1000:.6f} {c[1]/1000:.6f} {c[2]/1000:.6f}" quat="{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}" '
            f'size="{h[0]/1000:.6f} {h[1]/1000:.6f} {h[2]/1000:.6f}" friction="{self.mu} 0 0" solref="{self.solref}" condim="3" rgba="{rgba}"/>')


def _cuna(self, s0, c, t0, t1, placa, tau, nombre):
    """Biselado de la arista delantera de la placa tras una ventana: prisma convexo (s, n) con malla."""
    t, n = self.dirs(tau)
    prof = getattr(self, 'prof', None) or c
    pts = [(s0, -prof), (s0 + c, 0.0), (s0 + c, -placa), (s0, -placa)]
    v = []
    for tt in (t0, t1):
        for ss, nn in pts:
            p = ss * self.S + tt * t + nn * n
            v += [p[0] / 1000, p[1] / 1000, p[2] / 1000]
    self.assets.append(f'<mesh name="{nombre}" vertex="' + " ".join(f"{x:.6f}" for x in v) + '"/>')
    self.geoms.append(f'<geom type="mesh" mesh="{nombre}" friction="{self.mu} 0 0" solref="{self.solref}" condim="3" rgba="0.6 0.6 0.7 1"/>')


Pista.cuna = _cuna


def tau_de_s(s, s_ini, s_fin, tau0, tau1, forma="lineal"):
    if s <= s_ini:
        return tau0
    if s >= s_fin:
        return tau1
    u = (s - s_ini) / (s_fin - s_ini)
    if forma == "suave":
        u = 3 * u * u - 2 * u ** 3
    return tau0 + (tau1 - tau0) * u


def construir(mu=0.35, lean=15.0, tau0=10.0, s_tw0=0.0, s_tw1=80.0, s_fin=500.0, ventanas=(), placa=3.0, techo=70.0,
              lab=11.0, paso=1.5, forma="lineal", pend=PEND, dedo=None, chaflan=0.0, prof=None):
    """ventanas: [(s_a, s_b, H)] recortes de la placa (alto H desde el labio). dedo: (s, ...) se maneja aparte (mocap)."""
    P = Pista(mu, pend)
    P.prof = prof
    tau1 = 90.0 - lean
    s = -40.0
    # entrada previa a la torsión: canal plano (tau0)
    P.caja(-40, s_tw0, 0.0, techo, -placa, 0.0, tau0)
    P.caja(-40, s_tw0, -3.0, 0.0, 0.0, lab, tau0)
    # torsión: rebanadas
    s = s_tw0
    while s < s_tw1:
        tau = tau_de_s(s + paso / 2, s_tw0, s_tw1, tau0, tau1, forma)
        P.caja(s, s + paso + 0.05, 0.0, techo, -placa, 0.0, tau)
        P.caja(s, s + paso + 0.05, -3.0, 0.0, 0.0, lab, tau)
        s += paso
    # sección final: placa con ventanas
    cortes = sorted(ventanas)
    xs = [s_tw1]
    for a, b, H in cortes:
        xs += [a, b]
    xs.append(s_fin)
    # tramos alternos: sólido (sin ventana) / ventana
    pos = s_tw1
    for k, (a, b, H) in enumerate(cortes):
        if a > pos:
            c = chaflan if k > 0 else 0.0
            if c:
                P.cuna(pos, c, 0.0, cortes[k - 1][2], placa, tau1, f"cu{k}")
            P.caja(pos + c, a, 0.0, techo, -placa, 0.0, tau1)
            if c:
                P.caja(pos, pos + c, cortes[k - 1][2], techo, -placa, 0.0, tau1)
            P.caja(pos + c, a, -6.0, 0.0, -placa, 0.0, tau1)
        P.caja(a, b, H, techo, -placa, 0.0, tau1)          # solo por encima de la ventana
        pos = b
    if pos < s_fin:
        P.caja(pos, s_fin, 0.0, techo, -placa, 0.0, tau1)
        P.caja(pos, s_fin, -6.0, 0.0, -placa, 0.0, tau1)
    P.caja(s_tw1, s_fin, -3.0, 0.0, 0.0, lab, tau1)
    P.tau1 = tau1
    return P


def xml_mundo(P, moneda, pos, quat, dedo_pos=None, dedo_dim=(3.0, 20.0, 4.0), tau_dedo=None, solref="0.004 1"):
    d, e, m = MONEDAS[moneda]
    ded = ""
    if dedo_pos is not None:
        t, n = P.dirs(P.tau1)
        s, tt, nn = dedo_pos
        c = s * P.S + tt * t + nn * n
        q = _quat(np.column_stack([P.S, t, n]))
        ded = (f'<body name="dedo" mocap="true" pos="{c[0]/1000:.6f} {c[1]/1000:.6f} {c[2]/1000:.6f}" quat="{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}">'
               f'<geom type="box" size="{dedo_dim[0]/2000:.6f} {dedo_dim[1]/2000:.6f} {dedo_dim[2]/2000:.6f}" friction="{P.mu} 0 0" solref="{solref}" rgba="1 0.3 0.3 1"/></body>')
    activos = "<asset>" + " ".join(P.assets) + "</asset>" if P.assets else ""
    return f"""<mujoco>
  <option timestep="0.0004" gravity="0 0 -9.81" cone="elliptic" impratio="5"/>
  {activos}
  <worldbody>
    {' '.join(P.geoms)}
    {ded}
    <body name="moneda" pos="{pos[0]/1000:.6f} {pos[1]/1000:.6f} {pos[2]/1000:.6f}" quat="{quat[0]:.6f} {quat[1]:.6f} {quat[2]:.6f} {quat[3]:.6f}">
      <freejoint/>
      <geom type="cylinder" size="{d/2000:.6f} {e/2000:.6f}" mass="{m/1000:.6f}" friction="{P.mu} {P.mu*2*d/6000:.6f} 0" condim="4" solref="{solref}"/>
    </body>
  </worldbody>
</mujoco>"""


def soltar(P, moneda, s_caida, y_caida, altura=25.0, yaw=0.0, vuelco=0.0, tmax=4.0, dedo=None, v_dedo=0.0, traza=False,
           ventanas=(), seed=None):
    """Suelta la moneda plana desde `altura` mm sobre la entrada. dedo=(s0, t, n) mueve un tope a v_dedo (mm/s) tras t_espera."""
    d, e, m = MONEDAS[moneda]
    tau0 = P.taus0
    t0, n0 = P.dirs(tau0)
    # punto sobre el piso de la entrada: n=0 es la placa; la moneda plana se apoya en la placa (cara en n=0) en t=y_caida
    centro = s_caida * P.S + y_caida * t0 + (e / 2 + altura) * n0
    # eje de la moneda a lo largo de n0 (plana sobre la placa), con yaw y un pequeño vuelco
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    ez = n0
    ex = P.S * cy + t0 * sy
    ey = np.cross(ez, ex)
    if vuelco:
        v = math.radians(vuelco)
        ez = ez * math.cos(v) + ex * math.sin(v)
        ex = np.cross(ey, ez)
    q = _quat(np.column_stack([ex, ey, ez]))
    xml = xml_mundo(P, moneda, centro, q, dedo_pos=dedo)
    mod = mujoco.MjModel.from_xml_string(xml)
    dat = mujoco.MjData(mod)
    cid = mod.body("dedo").mocapid[0] if dedo is not None else None
    tr = []
    k = 0
    t_espera = 1.2
    t_dedo, n_dedo = P.dirs(P.tau1)
    estado = dict(rebote=0)
    while dat.time < tmax:
        if cid is not None:
            sd = dedo[0] + (v_dedo / 1000.0 * max(0.0, dat.time - t_espera)) * 1000.0
            c = sd * P.S + dedo[1] * t_dedo + dedo[2] * n_dedo
            dat.mocap_pos[cid] = c / 1000
        mujoco.mj_step(mod, dat)
        k += 1
        p = dat.qpos[:3] * 1000
        if traza and k % 50 == 0:
            tr.append((dat.time, float(p @ P.S), *map(float, dat.qpos[:7])))
        if p[2] < -400:
            break
    p = dat.qpos[:3] * 1000
    # posición en el marco final
    q = dat.qpos[3:7]
    R = np.zeros(9); mujoco.mju_quat2Mat(R, q); R = R.reshape(3, 3)
    eje = R[:, 2]                                         # eje de la moneda
    t1, n1 = P.dirs(P.tau1)
    return dict(s=float(p @ P.S), t=float((p) @ t1), n=float((p) @ n1), eje_n=float(eje @ n1), eje_s=float(eje @ P.S),
                tiempo=float(dat.time), traza=tr)
