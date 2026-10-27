"""Simulación MuJoCo del riel de monedas de canto (placa inclinada con escalones de altura).

Marco de la placa (s, t, n): s a lo largo de la pista (baja), t sube por la placa desde el labio,
n sale de la cara de la placa hacia las monedas. La placa se inclina `lean` grados respecto a la
vertical (hacia atrás) y la pista baja `pend` grados respecto a la horizontal.
"""
from __future__ import annotations
import math
import numpy as np
import mujoco

# diámetro, espesor, masa (g)
MONEDAS = {
    "N50": (17.0, 1.30, 2.00), "N100": (20.3, 1.50, 3.34), "A50": (21.5, 1.40, 4.50),
    "N200": (22.4, 1.70, 4.61), "A100": (23.0, 1.55, 5.31), "A500": (23.7, 2.05, 7.14),
    "N500": (23.7, 2.20, 7.14), "A200": (24.4, 1.70, 7.08), "N1000": (26.7, 2.30, 9.95),
}
ORDEN = ["N50", "N100", "A50", "N200", "A100", "A500", "N500", "A200", "N1000"]


def marco(lean, pend):
    g, b = math.radians(lean), math.radians(pend)
    s0 = np.array([1.0, 0, 0]); t0 = np.array([0, math.sin(g), math.cos(g)]); n0 = np.array([0, -math.cos(g), math.sin(g)])
    c, sn = math.cos(b), math.sin(b)
    R = np.array([[c, 0, sn], [0, 1, 0], [-sn, 0, c]])
    return R @ s0, R @ t0, R @ n0


def _quat(R):
    q = np.zeros(4)
    mujoco.mju_mat2Quat(q, np.asarray(R, float).reshape(9))
    return q


class Mundo:
    def __init__(self, lean, pend, mu=0.35, solref="0.004 1"):
        self.S, self.T, self.N = marco(lean, pend)
        self.mu = mu
        self.solref = solref
        self.geoms = []

    def caja(self, s0, s1, t0, t1, n0, n1, rot=0.0, pivote=(0.0, 0.0)):
        """Caja en coordenadas de placa; `rot` grados alrededor de S (positivo: t hacia -n) por el punto `pivote` (t, n)."""
        c_t, c_n = (t0 + t1) / 2, (n0 + n1) / 2
        if rot:
            a = math.radians(rot)
            dt, dn = c_t - pivote[0], c_n - pivote[1]
            c_t = pivote[0] + dt * math.cos(a) + dn * math.sin(a)
            c_n = pivote[1] - dt * math.sin(a) + dn * math.cos(a)
            Tl = self.T * math.cos(a) - self.N * math.sin(a)
            Nl = self.T * math.sin(a) + self.N * math.cos(a)
        else:
            Tl, Nl = self.T, self.N
        c = (s0 + s1) / 2 * self.S + c_t * self.T + c_n * self.N
        q = _quat(np.column_stack([self.S, Tl, Nl]))
        h = ((s1 - s0) / 2, (t1 - t0) / 2, (n1 - n0) / 2)
        self.geoms.append(
            f'<geom type="box" pos="{c[0]/1000:.6f} {c[1]/1000:.6f} {c[2]/1000:.6f}" '
            f'quat="{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}" size="{h[0]/1000:.6f} {h[1]/1000:.6f} {h[2]/1000:.6f}" '
            f'friction="{self.mu} 0 0" rgba="0.6 0.6 0.7 1" solref="{self.solref}" condim="4"/>')

    def varillas(self, s0, s1, paso, radio, saliente, n0=0.0, n1=9.0):
        """Resaltes cilíndricos (eje a lo largo de n) sobre el labio: sobresalen `saliente` mm."""
        s = s0
        while s < s1:
            c = s * self.S + (saliente - radio) * self.T + (n0 + n1) / 2 * self.N
            # cilindro con eje a lo largo de N
            q = _quat(np.column_stack([self.S, self.T, self.N]))
            self.geoms.append(
                f'<geom type="cylinder" pos="{c[0]/1000:.6f} {c[1]/1000:.6f} {c[2]/1000:.6f}" '
                f'quat="{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}" size="{radio/1000:.6f} {(n1-n0)/2000:.6f}" '
                f'friction="{self.mu} 0 0" solref="{self.solref}" condim="4"/>')
            s += paso

    def xml(self, moneda, s0, n_ini=0.0, yaw=0.0, t_ini=0.0, v0=0.0):
        d, e, m = MONEDAS[moneda]
        pos = s0 * self.S + (d / 2 + 0.05 + t_ini) * self.T + (e / 2 + 0.05 + n_ini) * self.N
        cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        ez = cy * self.N + sy * self.S
        ex = np.cross(self.T, ez); ex /= np.linalg.norm(ex)
        ey = np.cross(ez, ex)
        q = _quat(np.column_stack([ex, ey, ez]))
        return f"""<mujoco>
  <option timestep="0.0004" gravity="0 0 -9.81" cone="elliptic" impratio="5"/>
  <worldbody>
    {' '.join(self.geoms)}
    <body name="moneda" pos="{pos[0]/1000:.6f} {pos[1]/1000:.6f} {pos[2]/1000:.6f}" quat="{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}">
      <freejoint/>
      <geom name="mon" type="cylinder" size="{d/2000:.6f} {e/2000:.6f}" mass="{m/1000:.6f}" friction="{self.mu} {self.mu * 2 * d / 6000:.6f} 0" condim="4" solref="{self.solref}"/>
    </body>
  </worldbody>
</mujoco>"""


def riel(lean, pend, escalones, s_fin, mu=0.35, rampa=0.0, guarda=5.0, ancho_lab=9.0, placa=3.0, techo=70.0,
         s_ini=-60.0, tope=True, resaltes=None):
    """escalones: [(s_i, H_i)]: desde s_i el techo está a H_i del labio. `rampa`: pendiente (grados) hacia atrás del
    antepecho dentro de las ventanas. `guarda`: distancia del borde de la guarda a la placa (ancho del canal)."""
    w = Mundo(lean, pend, mu)
    xs = [s_ini] + [s for s, _ in escalones] + [s_fin]
    for k in range(len(escalones) + 1):
        H = 0.0 if k == 0 else escalones[k - 1][1]
        w.caja(xs[k], xs[k + 1], H, techo, -placa, 0.0)
    # antepecho bajo el labio; en las ventanas con rampa hacia atrás
    for k in range(len(escalones) + 1):
        a, b = xs[k], xs[k + 1]
        if k == 0 or not rampa:
            w.caja(a, b, -6.0, 0.0, -placa, 0.0)
        else:
            w.caja(a, b, -8.0, 0.0, -placa - 12.0, 0.0, rot=-rampa, pivote=(0.0, 0.0))
    w.caja(s_ini, s_fin, -3.0, 0.0, 0.0, ancho_lab)
    if guarda:
        w.caja(s_ini, s_fin, 0.0, 4.0, guarda, guarda + 2.0)
    if tope:
        w.caja(s_fin, s_fin + 3, 0.0, techo, -placa, ancho_lab)
    if resaltes:
        w.varillas(*resaltes)
    return w


def correr(w, moneda, tmax=3.0, s0=10.0, n_ini=0.0, yaw=0.0, t_ini=0.0, v0=0.0, traza=False, paso_traza=25):
    mod = mujoco.MjModel.from_xml_string(w.xml(moneda, s0, n_ini, yaw, t_ini))
    dat = mujoco.MjData(mod)
    if v0:
        dat.qvel[:3] = v0 / 1000.0 * w.S
    tr = []
    k = 0
    cae = None
    while dat.time < tmax:
        mujoco.mj_step(mod, dat)
        k += 1
        p = dat.qpos[:3] * 1000
        if traza and k % paso_traza == 0:
            tr.append((dat.time, float(p @ w.S), float(p @ w.T), float(p @ w.N), *map(float, dat.qpos[3:7])))
        if p @ w.N < -10.0 and cae is None:
            cae = (float(p @ w.S), dat.time)
            break
        if p @ w.T < -20.0 and cae is None:      # cayó por delante
            cae = (float(p @ w.S), -dat.time)
            break
    p = dat.qpos[:3] * 1000
    return dict(s=float(p @ w.S), t=float(p @ w.T), n=float(p @ w.N), tiempo=float(dat.time), cae=cae, traza=tr)
