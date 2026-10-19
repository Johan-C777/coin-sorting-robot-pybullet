# ESTADO

## Decisiones / parámetros
- `scripts/generar_clasificador.py` (manifold3d) → `hardware/stl/` + `piezas_clasificador.csv`. Sin tornillos ni soportes: clavijas Ø6 (agujero 6,1; `AJUSTE_PRESION`), llaves R04, bridas de nailon.
- Riel 22°, peralte 10°, canal 30; ranuras 17,5/20,8/21,5/22,9/23,4/24,1/24,9. 9 vasos Ø34×60, uno por salida, bajo su tubo (6 mm sobre la boca). Salidas ≥ 37 mm (ALMA_EXTRA en el riel; columnas de D6 a 18,4 mm).
- Ductos: adaptador impreso Dn_adaptador (65 mm: caja IR + embudo + collar) + tubo PVC presión 1" RDE 21 (Ø ext 33,4, int ≈ 30). Cortes 196/181/167/152/128/85/69 mm.
- $500: TCS34725 antes de la ranura 6; plato SG90 55° (antigua, -X) / 125° (nueva, +X); D6 sigue impreso. Firmware `config.h` 55/125.
- Tolva 28BYJ-48, semiángulo 40°. Pines IR 34,35,36,39,32,33,25,26,27; I2C 21/22; servo 13; tolva 16-19; banda 14/4/23.
- Base: lámina MDF 9 mm 560x198 (ranura 357x48), 4 patas PVC 3/4" (134 mm) + 4 tees (11 mm centro-fondo, `F_ACC`) + 2 largueros 490 mm; 2 bases ABS P01 (zócalo + viga 150 mm). Piso -200: 123 mm de ancho libre y 70 mm bajo la banda. Patas R03 y T04 siguen impresas (más livianas que PVC + tapas).

## Archivos
- `scripts/{generar_clasificador,exportar_visor_3d}.py`, `scripts/visor_template.html`, `hardware/stl/*` (24 STL), `hardware/visor/ensamble_etapa1.html`, `docs/08-clasificador-fisico.md`, `hardware/bom-etapa1.csv`, `CHANGELOG.md` 0.4.2.

## Resuelto
- $500 alineada; voladizos y tornillos fuera; STL cerrados y sin trozos; ductos y base en PVC (612 cm³ macizos, antes 1143); sin interferencias (tubos incluidos).

## Pendiente / riesgos
- Probar con una $1000 el tubo de 1" antes de cortar los siete (SCH 40 no sirve). Medir `F_ACC` en la tee real.
- Imprimir R01 + D1 (adaptador) + una pata R03 y D6; medir ajuste; calibrar `COMPENSACION_RANURA`, `umbralDorado`.
- Vasos Ø34 muy justos (holgura 0,8 mm entre D5 y D6a); collares Ø36 a 0,8 mm entre vecinos.
- Margen del plato en simulación ~28 ms; `software/brazo/monedas.py` sigue con el riel de 8 estaciones.

## Siguiente paso
Imprimir camas 1 y 2 de prueba; luego el resto.
