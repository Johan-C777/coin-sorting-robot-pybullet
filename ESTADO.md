# ESTADO

## Decisiones / parámetros
- `scripts/generar_clasificador.py` (manifold3d) → `hardware/stl/` + `piezas_clasificador.csv`. Sin tornillos ni soportes: clavijas Ø6 (agujero 6,1; `AJUSTE_PRESION`), llaves R04, bridas de nailon.
- Riel 22°, peralte 10°, canal 30; ranuras 17,5/20,8/21,5/22,9/23,4/24,1/24,9. 9 vasos Ø34×60 uno por salida, justo bajo cada ducto (sin mangueras: ductos alargados hasta 6 mm sobre la boca). Salidas ≥35 mm: ALMA_EXTRA en el riel (R02 215 mm) y columnas de D6 a 18,4 mm.
- $500: TCS34725 antes de la ranura 6; plato SG90 55° (antigua, -X) / 125° (nueva, +X); dos columnas alineadas con los ductos, cada una a su vaso. Firmware `config.h` 55/125.
- Tolva 28BYJ-48, semiángulo 40°. Pines IR 34,35,36,39,32,33,25,26,27; I2C 21/22; servo 13; tolva 16-19; banda 14/4/23.

- Base: lámina 6 mm 514x158 con ranura 38 mm sobre 4 patas PVC 3/4" (120 mm) + codos impresos P01/P02; largueros altos/bajos PVC; banda pasa entre patas. Visor: grupo Base.

## Archivos
- Reescritos: `scripts/{generar_clasificador,exportar_visor_3d}.py`, `scripts/visor_template.html` (ensamble + simulación), `hardware/stl/*`, `docs/08-clasificador-fisico.md`, `hardware/bom-etapa1.csv`.
- Modificados: `firmware/esp32_contador/config.h`, `CHANGELOG.md`.

## Resuelto
- Las salidas de la $500 estaban 100-137 mm fuera de la línea de vasos: rediseñado D6.
- Voladizos y tornillos eliminados; sin interferencias; `make -C firmware/tests` OK.

## Pendiente / riesgos
- Ductos largos (hasta 239 mm) impresos de pie: imprimir D1 primero. Vasos Ø34 muy justos (holgura 0,8 mm en D5-D6a).
- Margen del plato en simulación: ~28 ms antes de la $500 (fricción 0,22); considerar sensor más arriba.
- Probar R01 + D1 + una pata (clavijas) y D6 (bolsillo SG90); calibrar `COMPENSACION_RANURA`, `umbralDorado`.
- Tubo flexible ≥ 32 mm interno; D6 baja 38 mm bajo la mesa (ranura).
- `software/brazo/monedas.py` y simulación siguen con el riel de 8 estaciones. TCS3200 sin driver.

## Siguiente paso
Imprimir R01 + D1 + una pata R03 y D6; medir ajuste; luego el resto.
