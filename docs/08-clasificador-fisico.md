# Clasificador físico (etapa 1)

Piezas imprimibles con los alojamientos de la electrónica ya modelados.
Fuente única: `scripts/generar_clasificador.py` → `hardware/stl/`.

```
pip install manifold3d numpy
python scripts/generar_clasificador.py --ensamble
```

## Piezas (Creality K1C, cama 220 × 220 × 250)

| STL | Cant. | Notas de impresión |
|---|---|---|
| `R01_riel_modulo_A` | 1 | Entrada + ranuras 1-4, cola de milano macho. Plano, sin soportes. 201,7 mm |
| `R02_riel_modulo_B` | 1 | Ranuras 5-7 + extremo abierto, cola hembra (puente de 22 mm). 180,4 mm |
| `R03_cuna_22_izq` / `_der` | 4 + 4 | Una por esquina; dan los 22° de la pista |
| `D1…D8_ducto_*` (7) | 1 c/u | Boca abajo (brida en la cama). Tubo a 22°, sin soportes |
| `B01_bifurcacion_500_<sensor>` | 1 | Imprimir solo la del sensor elegido, de pie, **PLA negro** |
| `B02_aguja_desvio` | 1 | Plana, 100 % relleno |
| `B03_tapa_sensor_<sensor>` | 1 | Plana |
| `T01_tolva_cono_40` | 1 | Brida abajo; pared a 40° de la vertical (50° de la horizontal) |
| `T02_disco_dosificador_<motor>` | 1 | Elegir 28BYJ-48 (recomendado) o SG90 continuo |
| `T03_base_tolva_<motor>` | 1 | Igual que el disco |

`hardware/stl/piezas_clasificador.csv` lista medidas y volumen;
`hardware/stl/ensamble/ensamble_referencia.stl` muestra todo en posición.

## Parámetros fijados

| | Valor |
|---|---|
| Holgura deslizante / M3 roscado / M3 pasante | 0,35 mm / Ø3,2 / Ø3,4 (cabeza Ø6,5 × 3) |
| Pista | 22°, peralte lateral 10° hacia la pared guía, canal 30 mm |
| Ranuras (ancho × largo) | 17,5 · 20,8 · 21,5 · 22,9 · 23,4 · 24,1 · 24,9 mm; largo = ancho + 4; extremo abierto 32 mm |
| Barreras IR | 2 × Ø5,2 a presión, opuestas, con tope Ø3 hacia el ducto |
| Tolva | Semiángulo 40°, boca Ø160, disco Ø80 × 3 con 4 cavidades Ø28 a r = 24 |
| Dosificación | 1 moneda / 1,5 s = 10 rpm del disco (28BYJ-48: 679 medios pasos/s) |
| Bifurcación | Embudo en V → ranura de 4,2 mm, rodadura de canto a 25°, sensor a 50 mm, aguja a 110 mm (≈95 ms para el SG90) |

## Ensamble

1. **Riel**: encastrar la cola de A en B y fijar con 2 M3 × 6 desde arriba (Ø3,4 en B → Ø3,2 en la cola).
   Cuñas bajo las alas (M3 × 10 inclinado al riel, M3 vertical al bastidor).
2. **Ductos**: 2 M3 × 10 desde abajo por la brida, en los Ø3,2 de cada ranura.
3. **Tolva**: 28BYJ-48 a la base con 2 M3 × 6 por debajo; disco a presión en el eje
   (0,35 mm sobre la base); cono con 3 M3 × 12 desde abajo de la base. Base al
   bastidor con 4 M3 embutidos. La boca de salida cae sobre la zona de entrada del riel.
4. **Bifurcación**: bajo la ranura 6 con 2 M3 × 10 (los alojamientos verticales
   dan paso al destornillador). TCS34725 en su alojamiento, conector hacia el lado
   abierto de la tapa, tapa con 2 M3 × 6. La aguja entra por la boca inferior del
   ducto N500; se alinea su buje con el agujero lateral y se encaja el SG90 (en 0°,
   aguja a ras del piso) por la cara −X, con sus 2 tornillos M2.
5. **IR**: LED IR en un lado y fototransistor en el otro de cada ducto; colector
   a la entrada del ESP32 con 10 kΩ a 3,3 V (haz libre = bajo, moneda = alto).

## Electrónica (firmware/esp32_contador/config.h)

| Función | GPIO |
|---|---|
| IR ductos 1-9 (N50, N100, A50, N200, A100, A500, N500, A200, N1000) | 34, 35, 36, 39, 32, 33, 25, 26, 27 |
| I2C TCS34725 (SDA, SCL) | 21, 22 |
| SG90 aguja | 13 |
| 28BYJ-48 IN1-IN4 (ULN2003) / SG90 continuo | 16, 17, 18, 19 / 18 |
| Banda L298N (A, B, PWM) | 14, 4, 23 |

## Riesgos conocidos

- Las ranuras pedidas dejan poco apoyo a la moneda siguiente: 0,10 mm para la
  $100 antigua sobre la ranura 4 y para la $500 antigua sobre la ranura 5; 0,20 mm
  para la $50 antigua sobre la ranura 2. El generador lo avisa. Imprimir el
  módulo A, medir con calibrador y corregir con `COMPENSACION_RANURA`.
- Con 3 mm de cavidad caben dos $50 nuevas apiladas (1,3 mm c/u): bajar
  `DISCO_ESP` si el lote es solo de monedas delgadas.
- Las cotas del SG90 (`SG90` en el script) son nominales; si el estriado no
  alcanza la aguja, ajustar `caja_sobre_oreja`/`buje` y regenerar.
- El firmware lee el TCS34725 (I2C). La variante TCS3200 de la bifurcación
  existe en STL, pero ese sensor es de salida en frecuencia y necesitaría otro driver.
- Umbral del color (`Clasificador500::umbralDorado`) por calibrar en banco con el
  registro `C500:<anillo>,<razón>` del puerto serie.
