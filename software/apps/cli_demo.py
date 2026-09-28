"""Corre un ciclo completo de clasificación sin hardware.

    python software/apps/cli_demo.py --criterio valor --sentido asc
    python software/apps/cli_demo.py --puerto /dev/ttyUSB0      # a un ESP32 real
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brazo.controller import Controlador           # noqa: E402
from brazo.cups import lote_aleatorio, lote_demo   # noqa: E402
from brazo.links import EnlaceNulo, EnlaceSerie    # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Demostración del brazo clasificador")
    ap.add_argument("--criterio", default="valor",
                    choices=["denominacion", "cantidad", "valor", "peso"])
    ap.add_argument("--sentido", default="asc", choices=["asc", "desc"])
    ap.add_argument("--velocidad", type=float, default=1.0)
    ap.add_argument("--puerto", help="puerto serie del ESP32; sin esto corre en seco")
    ap.add_argument("--aleatorio", action="store_true", help="lote de vasos al azar")
    ap.add_argument("--tramas", type=int, default=5, help="cuántas tramas mostrar")
    args = ap.parse_args()

    enlace = EnlaceSerie(args.puerto) if args.puerto else EnlaceNulo()
    ctrl = Controlador(lote_aleatorio() if args.aleatorio else lote_demo(),
                       enlace=enlace, velocidad=args.velocidad)

    print("Lote de entrada")
    for v in ctrl.vasos:
        print(f"  {v.puesto.etiqueta}  {v}  ->  ${v.valor:,}".replace(",", ".") +
              f"  {v.peso_g:.1f} g")

    res = ctrl.ordenar(args.criterio, args.sentido)
    print(f"\nPlan por {args.criterio} {args.sentido}: {len(res['movimientos'])} movimientos, "
          f"{res['segundos']} s a velocidad {args.velocidad}x")
    for i, m in enumerate(res["movimientos"], 1):
        print(f"  {i}. {m}")

    print("\nRack final")
    for v in sorted((v for v in ctrl.vasos if v.puesto.zona == "rack"),
                    key=lambda v: v.puesto.indice):
        print(f"  {v.puesto.etiqueta}  {v}  ->  ${v.valor:,}".replace(",", ".") +
              f"  {v.peso_g:.1f} g")

    if isinstance(enlace, EnlaceNulo) and enlace.tramas:
        print(f"\nPrimeras {args.tramas} tramas de las {len(enlace.tramas)} generadas")
        for t in enlace.tramas[:args.tramas]:
            print("  " + t)
    enlace.cerrar()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
