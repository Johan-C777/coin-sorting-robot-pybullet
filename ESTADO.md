# ESTADO

## Etapas
| Etapa | Estado |
|---|---|
| 1 Tolva + selección | Diseño cerrado, 24 STL listos. Siguiente: imprimir camas 1-2 de prueba |
| 2 Banda transportadora | En diseño (hilo propio); restricciones en `hardware/etapa2-transporte/README.md` |
| 3 Brazo A→B + orden | Recibe 9 vasos (9+9 puestos); simulado, firmware probado en PC (61 pytest, 48 C++); falta montar |

## Decisiones / parámetros (etapa 1)
- Generador único `scripts/generar_clasificador.py` (manifold3d) → `hardware/etapa1-clasificador/stl/`; visor `scripts/exportar_visor_3d.py` → `docs/ensamble-etapa1.html`.
- Sin tornillos ni soportes: clavijas Ø6 (agujero 6,1; `AJUSTE_PRESION`), llaves R04, bridas.
- Riel 22°, ranuras 17,5/20,8/22,0/22,8/23,4/24,1/24,9 + extremo (diámetros oficiales Banrep). 9 salidas ≥ 37 mm → 9 vasos Ø34×60, uno por tipo.
- $500: TCS34725 antes de ranura 6; plato D6 SG90 55° antigua / 125° nueva.
- Ductos: adaptador impreso + PVC 1" RDE 21 (cortes 196/181/167/152/128/85/69). Base: MDF 9 mm 560×198, PVC 3/4" (4×134, 4×29, 2×490) + 4 tees + 2 P01 ABS. Hueco banda 123×490, 70 mm bajo banda.
- Pines: IR 34,35,36,39,32,33,25,26,27; I2C 21/22; servo 13; tolva 16-19; banda 14/4/23.
- Impresión: 8 camas, ≈480 g (PLA+ negro 230, PETG azul 180, ABS 75), ≈33 h.

## Archivos (0.5.0)
- Repo por etapa: `hardware/{etapa1-clasificador,etapa2-transporte,etapa3-brazo,archivo/etapa1-v1}`, `hardware/README.md`.
- Docs: `09-clasificador-fisico.md`, `10-guia-armado-etapa1.md`, `archivo/despiece-etapa1-v1.md`, `ensamble-etapa1.html`; README, 00-entrega, index.html, CHANGELOG.
- `bom-etapa1.csv` rehecho; `software/tests/test_monedas.py` (9 ductos vs 8 estaciones).

## Resuelto
- $500 alineada, STL cerrados, PVC en ductos y base, sin choques.
- Prueba firmware↔modelo de monedas fallando desde 0.4.0 → corregida.

## Pendiente / riesgos
- Probar la $1000 en el tubo de 1" antes de cortar (SCH 40 atasca). Medir la tee real (`F_ACC` 11 mm).
- Calibrar `COMPENSACION_RANURA`, `umbralDorado`; vasos Ø34 con 0,8 mm de holgura entre D5 y D6a.
- **Reimprimir R01** si ya se imprimió con la ranura 3 de 21,5 mm: la $50 antigua mide 21,5 y no caía (ahora 22,0; ranura 4 a 22,8).
- PyBullet no se ejecutó (no compila aquí): correr `python sim/pybullet/run_sim_integrada.py --headless` en el PC.
- Rack de 9 puestos con vasos Ø34 a 9,5°: solo 4 mm libres entre vasos; el brazo del CAD (r_arco 9,7 cm) no los alcanza en su arco.
- `MONEDAS_POR_VASO = 40` es carga de diseño (416 g); un vaso Ø34×60 admite ≈ 26 monedas de $1.000.
- `docs/memoria-calculo.html` aún muestra las cifras del perfil de 5 vasos (lleva aviso).
- Confirmar diámetros de $50 y $500 antiguas con moneda real (ahora los oficiales: 21,5 / 23,7 mm; 7,14 g).

## Siguiente paso
Imprimir camas 1 y 2 de prueba (R01, patas R03_1, D1 adaptador, D6, B02, B03) y medir; en paralelo, diseñar la banda.
