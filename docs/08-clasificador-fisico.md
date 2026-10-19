# Clasificador físico (etapa 1)

Piezas imprimibles con los alojamientos de la electrónica ya modelados.
Fuente única: `scripts/generar_clasificador.py` → `hardware/stl/`.

```
pip install manifold3d numpy
python scripts/generar_clasificador.py --ensamble
```

## Piezas (Creality K1C, cama 220 × 220 × 250)

Sin tornillos ni soportes: todo encaja con clavijas Ø6 a presión, llaves de
mariposa y bridas de nailon. Detalle y medidas en `hardware/stl/piezas_clasificador.csv`.

| STL | Cant. | Notas |
|---|---|---|
| `R01_riel_modulo_A` / `R02_riel_modulo_B` | 1 + 1 | Riel de 22°, 190 y 215 mm. Tumbados, sin soportes |
| `R04_llave_union` | 3 | Mariposa bajo la junta A-B |
| `R03_pata{1,2,3}_{izq,der}` | 6 | Patas del riel (153, 114 y 44 mm); pie atado a la lámina con brida |
| `D1…D5, D7, D8_adaptador_*` | 1 c/u | Adaptador de 65 mm de alto: caja de la ranura con IR a presión y clavijas al riel, embudo y collar donde entra el tubo PVC de 1" (20 mm) |
| `D6_bifurcador_500` | 1 | Plato basculante, SG90 y barreras IR a presión. **PLA negro** |
| `B02_plato_desvio` | 1 | Plato que el servo inclina ±35° |
| `B03_puente_sensor` | 1 | Cajón colgante del TCS34725 |
| `T01_tolva_cono_40`, `T02_disco_dosificador`, `T03_base_tolva` | 1 c/u | Cono con 3 clavijas; disco en el eje del 28BYJ-48 |
| `T04_pata_tolva` | 4 | Patas de 212 mm |
| `P01_base_extremo` | 2 | Base de ABS de un extremo: dos zócalos para tubo PVC de 3/4" unidos por una viga de 150 mm |

`hardware/stl/ensamble/ensamble_referencia.stl` muestra todo en posición;
`hardware/visor/ensamble_etapa1.html` es el visor 3D con la simulación.

## Parámetros fijados

| | Valor |
|---|---|
| Holgura deslizante / clavija | 0,35 mm / Ø6 en agujero Ø6,1 × 3,1 (`AJUSTE_PRESION`) |
| Pista | 22°, peralte lateral 10° hacia la pared guía, canal 30 mm |
| Ranuras (ancho × largo) | 17,5 · 20,8 · 21,5 · 22,9 · 23,4 · 24,1 · 24,9 mm; extremo abierto 32 mm |
| Barreras IR | 2 × Ø5,2 a presión, opuestas |
| Tolva | Semiángulo 40°, disco Ø80 × 3 con 4 cavidades Ø28; 28BYJ-48 |
| Vasos | 9 de Ø34 × 60 mm sobre la banda, cada uno justo bajo su salida (N50, N100, A50, N200, A100, A500, N500, A200, N1000). Sin mangueras: un tubo PVC de 1" baja hasta 6 mm sobre su boca |
| $500 | TCS34725 lee el anillo antes de la ranura 6; plato SG90 a 55° (antigua, −X) o 125° (nueva, +X). Salen por dos columnas alineadas con los demás ductos, cada una a su vaso |

## Ensamble (sin tornillos)

1. **Riel**: unir A y B con las 3 llaves R04. Patas R03 a presión en el riel; pie con brida a la mesa.
2. **Ductos**: adaptador con clavijas Ø6 a presión en las orejas del riel; IR a presión; el tubo PVC de 1" entra 20 mm en el collar (cinta o una gota de pegamento si queda flojo).
3. **Tolva**: 28BYJ-48 en T03 con 2 bridas de nailon; disco a presión en el eje; cono sobre las 3 clavijas de T03; patas T04.
4. **Bifurcador**: D6 bajo la ranura 6; SG90 a presión en su bolsillo; plato B02 en el estriado; B03 cuelga de su guía con la TCS34725.
5. **Vasos**: cada tubo termina 6 mm sobre la boca de su vaso (Ø34); los nueve quedan en línea sobre la banda, separados al menos 35 mm. El riel crece unos 5 mm en el módulo A para que los collares de 36 mm de las salidas no se toquen.
6. **Base (sin tornillos)**: lámina de MDF de 9 mm (560 × 198 mm, ranura de 357 × 48 mm bajo los tubos) sobre 4 patas de PVC de presión de 3/4" y dos bases ABS P01 (una por extremo). Cada pata entra 32 mm en su zócalo y sube 134 mm hasta una tee (salida lateral hacia adentro, centro 49 mm bajo la lámina); sobre la tee, un tramo corto sostiene la lámina. Un larguero de 490 mm por lado une las tees. Hueco libre para la banda: 123 mm de ancho × 490 mm de largo, con 70 mm bajo la cara de arriba de la banda para motor, rodillos y electrónica. Patas del riel y de la tolva atadas a la lámina con bridas.

### Cortes de PVC

| Tubo | Cortes |
|---|---|
| 3/4" presión (Ø ext 26,7) | 4 patas de 134 mm · 4 tramos de 29 mm sobre las tees · 2 largueros de 490 mm |
| 1" presión RDE 21 (Ø ext 33,4, int ≈ 30) | D1 196 · D2 181 · D3 167 · D4 152 · D5 128 · D7 85 · D8 69 mm |
| Accesorios | 4 tees de 3/4" (sin codos) |

Los largos de las tees suponen 11 mm del centro al fondo de la copa (`F_ACC`): mide la tuya y, si cambia, corre el generador.

## Electrónica (firmware/esp32_contador/config.h)

| Función | GPIO |
|---|---|
| IR ductos 1-9 (N50, N100, A50, N200, A100, A500, N500, A200, N1000) | 34, 35, 36, 39, 32, 33, 25, 26, 27 |
| I2C TCS34725 (SDA, SCL) | 21, 22 |
| SG90 plato (55° / 125°) | 13 |
| 28BYJ-48 IN1-IN4 (ULN2003) / SG90 continuo | 16, 17, 18, 19 / 18 |
| Banda L298N (A, B, PWM) | 14, 4, 23 |

## Riesgos conocidos

- Las ranuras pedidas dejan poco apoyo a la moneda siguiente: 0,10 mm para la
  $100 antigua sobre la ranura 4 y para la $500 antigua sobre la ranura 5; 0,20 mm
  para la $50 antigua sobre la ranura 2. El generador lo avisa. Imprimir el
  módulo A, medir con calibrador y corregir con `COMPENSACION_RANURA`.
- Con 3 mm de cavidad caben dos $50 nuevas apiladas (1,3 mm c/u): bajar
  `DISCO_ESP` si el lote es solo de monedas delgadas.
- Cotas del SG90 nominales: imprimir D6 solo para probar el bolsillo antes del resto.
- Margen del plato: en la simulación llega solo ~28 ms antes de la $500 (a 0,22 de fricción); conviene mover el sensor aguas arriba si en la prueba falla.
- Probar primero R01 + D1 + una pata (ajuste de clavijas, `AJUSTE_PRESION`).
- Los tubos de PVC de 1" deben tener ≥ 28 mm de interior para la $1000 (26,7 mm): sirve RDE 21 (≈ 30 mm); el SCH 40 (≈ 26,6 mm) la atasca. Probar con una $1000 antes de cortar los siete.
- Los adaptadores se imprimen de pie (65 mm); el collar de Ø36 deja 0,8 mm entre vecinos: no escalar la pieza.
- El firmware lee el TCS34725 (I2C). La variante TCS3200 de la bifurcación
  existe en STL, pero ese sensor es de salida en frecuencia y necesitaría otro driver.
- Umbral del color (`Clasificador500::umbralDorado`) por calibrar en banco con el
  registro `C500:<anillo>,<razón>` del puerto serie.
