# Despiece de la etapa 1

![Vista de despiece](img/etapa1-despiece.png)

La misma vista se puede mover en vivo desde la simulación
(`simulacion-etapa1.html`, pestaña **Despiece**): el deslizador separa las
piezas y al tocar una de la lista se aísla y muestra su ficha.

## Piezas impresas

| Código | Pieza | Cant. | Archivo | Medidas | Material y ajustes |
| --- | --- | --- | --- | --- | --- |
| P01 | Riel selector, tramo de entrada | 2 | `stl/P01_riel_tramo_a.stl` | 200 x 22 x 10 mm | PETG, 0,2 mm, 4 perímetros, 40 % |
| P02 | Riel selector, tramo de salida | 2 | `stl/P02_riel_tramo_b.stl` | 185 x 18,5 x 10 mm | PETG, 0,2 mm, 4 perímetros, 40 % |
| P03 | Canal del costado | 4 | `stl/P03_canal_costado.stl` | 185 x 22 x 20 mm | PETG, 0,2 mm, 3 perímetros, 30 % |
| P04 | Abrazadera de varilla M5 | 4 | `stl/P04_abrazadera.stl` | 38 x 20 x 14 mm | PETG, 0,2 mm, 4 perímetros, 40 % |
| P05 | Tolva de alimentación | 1 | `stl/P05_tolva.stl` | 124 x 110 x 93 mm | PLA o PETG, 0,25 mm, 3 perímetros, 15 % |
| P06 | Paleta dosificadora | 1 | `stl/P06_compuerta.stl` | 18 x 60 x 9 mm | PETG, 0,2 mm, 4 perímetros, 60 % |
| P07 | Embudo de estación | 5 | `stl/P07_canal_salida.stl` | 66 x 66 x 63 mm | PLA, 0,25 mm, 3 perímetros, 15 % |
| P08 | Soporte de sensor infrarrojo | 5 | `stl/P08_soporte_sensor.stl` | 34 x 16 x 27 mm | PETG, 0,2 mm, 3 perímetros, 30 % |
| P09 | Rodillo de la banda | 2 | `stl/P09_rodillo.stl` | 35 x 35 x 70 mm | PETG, 0,2 mm, 4 perímetros, 30 % |
| P10 | Costado de la banda, tramo | 6 | `stl/P10_lateral_banda.stl` | 188 x 62 x 9 mm | PETG, 0,2 mm, 3 perímetros, 25 % |
| P11 | Portavaso | 5 | `stl/P11_portavaso.stl` | 58 x 58 x 15 mm | PETG, 0,2 mm, 3 perímetros, 20 % |
| P12 | Acople motor a rodillo | 1 | `stl/P12_acople_motor.stl` | 18 x 18 x 24 mm | PETG, 0,2 mm, 5 perímetros, 60 % |
| P13 | Pie nivelador | 4 | `stl/P13_pie_nivelador.stl` | 22 x 22 x 14 mm | TPU o PETG, 0,2 mm, 3 perímetros, 30 % |

Todas las piezas caben en una cama de 220 x 220 mm y se imprimen sin soportes
en la orientación en que vienen en el STL. Tiempo total estimado: entre 22 y
26 horas de impresión y unos 900 g de filamento.

## Piezas compradas

| Código | Elemento | Cant. | Nota |
| --- | --- | --- | --- |
| C01 | Servo SG90 | 1 | Mueve la paleta dosificadora, comandado por PWM desde el ESP32 |
| C02 | Barrera infrarroja | 5 | Un canal por estación; cada pulso es una moneda |
| C03 | Motorreductor 12 V y cinta de 70 mm | 1 | Banda transportadora, con puente H L298N |
| C04 | Vaso de polipropileno de 52 mm | 5 | El mismo que recoge el brazo de la etapa 2 |
| C05 | Varilla roscada M5 con tuercas | 4 | Da la altura del riel y permite ajustar la inclinación |

Detalle completo con cantidades y tornillería en
[`hardware/bom-etapa1.csv`](../hardware/bom-etapa1.csv).

## Cómo se arma

1. **Rieles.** Unir P01 y P02 por la solapa a media madera (20 mm) con dos M3 x 12
   y tuerca embebida. Quedan dos rieles de 365 mm; el derecho es el mismo STL
   volteado sobre su eje largo.
2. **Canales.** Atornillar dos P03 por lado a lo largo del riel, con tres M3 x 10
   cada uno. El riel entra en el canal y queda enrasado con la pared.
3. **Altura.** Montar las cuatro P04 sobre varilla roscada M5 y ajustar con
   tuercas hasta que el riel quede a 340 mm en la entrada y 186 mm en la salida:
   son los 25 grados de inclinación.
4. **Comprobación de la luz.** Antes de seguir, pasar una moneda de cada
   denominación por las cinco estaciones. Cada moneda debe caer en su estación y
   ninguna antes. Si una se cuela, la luz quedó ancha: ver la calibración de abajo.
5. **Tolva.** Fijar P05 sobre la entrada del riel con dos M3, montar el servo
   SG90 con P06 en el eje y ajustar los topes por firmware
   (`SERVO_CERRADO_US` y `SERVO_ABIERTO_US`).
6. **Embudos y bajantes.** Colgar un P07 bajo cada ranura y completar con tubo de
   28 mm hasta la boca del vaso, con la longitud de la tabla siguiente.
7. **Sensores.** Montar los P08 a cada lado de la ranura, con el emisor y el
   receptor enfrentados y el haz cruzando el centro del hueco.
8. **Banda.** Unir tres P10 por lado con las solapas, montar los dos P09 sobre
   ejes de 5 mm, tensar la cinta corriendo el eje en la ranura y acoplar el motor
   con P12. Los cinco P11 van sobre la cinta separados 65 mm.
9. **Pies.** Poner los cuatro P13 y nivelar con un nivel de burbuja: si el riel
   no está a escuadra, las monedas se recuestan contra un lado y se traban.

### Longitud del tubo de bajada por estación

| Estación | Denominación | Riel sobre la mesa | Salida del embudo | Tubo de 28 mm |
| --- | --- | --- | --- | --- |
| 1 | $50 | 309 mm | 236 mm | 120 mm |
| 2 | $100 | 282 mm | 209 mm | 92 mm |
| 3 | $200 | 254 mm | 181 mm | 65 mm |
| 4 | $500 | 227 mm | 154 mm | 37 mm |
| 5 | $1.000 | 200 mm | 127 mm | 10 mm |

## Tolerancias y calibración

La luz de cada ranura es el diámetro de su moneda más 0,6 mm:

| Estación | Moneda | Diámetro | Luz | Margen con la siguiente moneda |
| --- | --- | --- | --- | --- |
| 1 | $50 | 17,0 mm | 17,6 mm | 2,7 mm |
| 2 | $100 | 20,3 mm | 20,9 mm | 1,5 mm |
| 3 | $200 | 22,4 mm | 23,0 mm | **0,7 mm** |
| 4 | $500 | 23,7 mm | 24,3 mm | 2,4 mm |
| 5 | $1.000 | 26,7 mm | 27,3 mm | — |

La pareja crítica es $200 y $500: solo 1,3 mm las separan, así que la estación 3
apenas tiene 0,7 mm de margen. Antes de imprimir los rieles completos conviene
sacar una probeta de 40 mm de la estación 3 y medir la luz real con calibrador:
si la impresora saca las paredes anchas, hay que compensar el flujo o correr
`LUZ_EXTRA` en `scripts/generar_stl.py` y volver a generar los STL.

Otros puntos que valen la calibración:

- **Inclinación.** Con 25 grados la moneda desliza sola sobre PETG. Si se queda
  pegada, lijar el canal en el sentido del avance o subir a 27 grados; si salta,
  bajar a 23.
- **Rebote del sensor.** `REBOTE_US` está en 25 ms. Si el conteo sube de a dos,
  subirlo; si se pierden monedas seguidas, bajarlo.
- **Cierre del dosificador.** `SERVO_MS_ABIERTO` controla cuántas monedas pasan
  por ciclo. Se ajusta hasta que pase una sola.

## Regenerar los STL

```bash
python scripts/generar_stl.py
```

El script parte de `MONEDAS`, `LUZ_EXTRA`, `PASO` e `INCLINACION`: cambiar un
valor ahí y volver a correrlo deja las trece piezas y `stl/piezas.csv` al día.
