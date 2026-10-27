# ESTADO

## Etapas
| Etapa | Estado |
|---|---|
| 1 Tolva + selección | **v5 torre de canto** (0.7.0): 24 STL + 8 camas; camas 1-6 impresas, falta 7 y armar. ESP32-S3: pines y firmware en `firmware/etapa1_prueba_motor/` |
| 2 Banda transportadora | Cadena de tablillas impresa, PR #5 abierto |
| 3 Brazo A→B + orden | Recibe 9 vasos (9+9 puestos); simulado, firmware probado en PC (61 pytest, 48 C++); falta montar |

## Etapa 1 v5 (vigente, 0.7.0)
- Piezas: `scripts/generar_v5.py --ensamble` → `hardware/etapa1-clasificador/{stl,despiece.csv,ensamble*}`; camas `scripts/armar_camas_v5.py` → `impresion/` (CAMAS.md, orden "sin electrónica primero").
- Docs: `docs/09-clasificador-v5.md`, `docs/11-electronica-etapa1.md` (+ `img/etapa1-cableado.svg`, `img/etapa1-v5.png`).
- Pines S3: tolva 4,5,6,7; SG90 15; IR 1,2 (ADC1); TCS3200 OUT 14, S2 16, S3 17, S0 18, S1 21; banda STEP 10/DIR 11/EN 12, ref 13.
- Pendiente: imprimir cama 7, armar, probar motor con carga, calibrar `K_CUERDA`/`UMBRAL_DORADO`, confirmar shield; `Ajustes.3mf` (perfil K1C del usuario) no está en el repo.
- Archivo: v4 → `hardware/archivo/etapa1-v4/`, probetas v3 → `hardware/archivo/etapa1-v3-canto/`, docs v4 → `docs/archivo/*-v4.md`. `firmware/esp32_contador` es de la v4 (lo usan las pruebas).

## Histórico v4 (archivado)
### Decisiones / parámetros v4
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

## Etapa 1 v5 (prototipo final) lista para imprimir
- Torre de 33 cm de pie sobre la banda (3 caballetes + patines). Tolva de disco inclinado 45° (28BYJ-48, 8 bolsillos, rascador) → la moneda cae de canto a la pista (sim 1728/1728, `sim/mujoco/disco.py`) → 2 barreras IR + TCS34725 → embudo Ø90 a 45° (sim 81/81) → compuerta SG90 con bisagra → cartucho de 9 vasos que mueve la banda. Rechazo: rampa C02 en la punta del cartucho a un vaso puesto a mano.
- Piezas: `scripts/generar_v5.py` → `hardware/etapa1-clasificador/v5/` (STL, despiece, guía de armado). Sin choques, todo cabe en la K1C, ~850 g.
- No validado: una sola moneda por bolsillo, compuerta, posición del cartucho (depende de la banda, etapa 2), sensores reales. Meta 90%.

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
