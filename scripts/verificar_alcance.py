"""Comprueba si un perfil de medidas alcanza todos los puestos de la celda.

    python scripts/verificar_alcance.py                 # perfil activo
    python scripts/verificar_alcance.py --perfil cad
    python scripts/verificar_alcance.py --perfil cad --d1 9.2 --l1 10.0 --l2 9.5 --l3 6.0

Resuelve la inversa con la pinza vertical en las dos alturas de trabajo, barre
el radio del arco y dice qué radios son factibles y cuál conviene usar.
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "software"))


def cargar(perfil, sobrescribir):
    os.environ["BRAZO_PERFIL"] = perfil
    from brazo import config as c
    for clave, valor in sobrescribir.items():
        if valor is not None:
            setattr(c, clave.upper(), valor)
    c.ALCANCE_MAX = c.L1 + c.L2 + c.L3
    return c


def ik_valida(c, r, z, phi=-90.0):
    """True si el punto (radio r, altura z) es alcanzable y respeta los límites."""
    rw = r - c.L3 * math.cos(math.radians(phi))
    hw = z - c.D1 - c.L3 * math.sin(math.radians(phi))
    d = (rw * rw + hw * hw - c.L1 ** 2 - c.L2 ** 2) / (2 * c.L1 * c.L2)
    if abs(d) > 1.0:
        return False
    q3 = -math.acos(d)
    q2 = math.atan2(hw, rw) - math.atan2(c.L2 * math.sin(q3), c.L1 + c.L2 * math.cos(q3))
    q4 = (phi - math.degrees(q2 + q3) + 180.0) % 360.0 - 180.0
    q = [0.0, math.degrees(q2), math.degrees(q3), q4, 0.0]
    return all(lo - 1e-6 <= q[i] <= hi + 1e-6 for i, (lo, hi) in enumerate(c.LIMITES))


def rango_radios(c, z, paso=0.05):
    r, dentro, tramos = 0.0, False, []
    while r <= c.ALCANCE_MAX + 1:
        ok = ik_valida(c, r, z)
        if ok and not dentro:
            ini, dentro = r, True
        if not ok and dentro:
            tramos.append((ini, r - paso))
            dentro = False
        r += paso
    if dentro:
        tramos.append((ini, r - paso))
    return tramos


def main() -> int:
    ap = argparse.ArgumentParser(description="Verificación de alcance de la celda")
    ap.add_argument("--perfil", default=os.environ.get("BRAZO_PERFIL", "simulacion"))
    for k in ("d1", "l1", "l2", "l3"):
        ap.add_argument(f"--{k}", type=float, default=None, help=f"sobrescribe {k.upper()} en cm")
    ap.add_argument("--radio", type=float, default=None, help="radio del arco a comprobar")
    args = ap.parse_args()

    c = cargar(args.perfil, {k: getattr(args, k) for k in ("d1", "l1", "l2", "l3")})
    radio = args.radio if args.radio is not None else c.R_ARCO

    print(f"perfil {args.perfil}: d1={c.D1} L1={c.L1} L2={c.L2} L3={c.L3} cm")
    print(f"alcance máximo desde el hombro: {c.ALCANCE_MAX:.1f} cm\n")

    tramos = {}
    for nombre, z in (("agarre", c.Z_AGARRE), ("traslado", c.Z_SEGURA)):
        tramos[nombre] = rango_radios(c, z)
        texto = ", ".join(f"{a:.2f} a {b:.2f} cm" for a, b in tramos[nombre]) or "sin solución"
        print(f"radios con pinza vertical a {z:.1f} cm ({nombre}): {texto}")

    comunes = []
    for a1, b1 in tramos["agarre"]:
        for a2, b2 in tramos["traslado"]:
            lo, hi = max(a1, a2), min(b1, b2)
            if hi > lo:
                comunes.append((lo, hi))
    if not comunes:
        print("\nno hay ningún radio que sirva para las dos alturas: revisa d1, L2 o L3")
        return 1

    lo, hi = max(comunes, key=lambda t: t[1] - t[0])
    sugerido = round(lo + 0.75 * (hi - lo), 1)          # cerca del borde exterior
    print(f"\nradios válidos en las dos alturas: {lo:.2f} a {hi:.2f} cm")
    print(f"R_ARCO sugerido: {sugerido:.1f} cm")

    print(f"\ncomprobación de los once puestos con R_ARCO = {radio:.1f} cm")
    fallos = 0
    puestos = [("entrada", c.YAW_ENTRADA), ("rack", c.YAW_RACK)]
    for zona, yaws in puestos:
        for i, yaw in enumerate(yaws, start=1):
            ok = all(ik_valida(c, radio, z) for z in (c.Z_AGARRE, c.Z_SEGURA))
            fallos += 0 if ok else 1
            print(f"  {zona[0].upper()}{i} (yaw {yaw:+6.1f}°): {'ok' if ok else 'FUERA DE ALCANCE'}")
    entrega_ok = all(ik_valida(c, radio, z) for z in (c.Z_AGARRE, c.Z_SEGURA))
    print(f"  zona de entrega (yaw -60,0°): {'ok' if entrega_ok else 'FUERA DE ALCANCE'}")

    if fallos or not entrega_ok:
        print(f"\nhay {fallos + (0 if entrega_ok else 1)} puestos fuera de alcance: "
              f"usa R_ARCO = {sugerido:.1f} cm o alarga L2")
        return 1
    print("\ntodos los puestos quedan dentro del espacio de trabajo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
