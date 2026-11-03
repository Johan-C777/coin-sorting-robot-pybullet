# Etapa 2 v4: carro sobre dos varillas y un hilo

Reemplaza la banda de cadena de la v3 (46 piezas, 1.506 g de plástico). El cartucho de vasos va sobre un carro que corre por **dos varillas de acero** y lo mueve un **hilo** enrollado en el eje del NEMA17.

| | v3 cadena | v4 varillas |
|---|---|---|
| Plástico impreso (3 paredes, 15 % de relleno) | 1.506 g | **≈ 143 g** |
| Piezas impresas | 46 | **10** (en 2 camas) |
| Articulaciones que se pueden trabar | 168 | **0** |
| Soportes al imprimir | 0 | **0** |
| Compras | ninguna | 2 varillas, hilo, tensor |

## Qué comprar

- 2 varillas lisas de acero de **3/8" (9,525 mm) × 1 m**. Rectas: ruédalas sobre un vidrio. Si sólo hay 10, 12 o 12,7 mm sirven; se cambia `D_ROD` en `generador/generar_v4.py` y se regeneran las piezas. Más grueso es más rígido (flecha en el centro con 0,5 kg: 3/8" 1,25 mm, 10 mm 1,09 mm, 12 mm 0,66 mm, 1/2" 0,57 mm).
- 3 m de hilo de pesca **trenzado** de 0,4 a 0,6 mm (30 a 50 lb). Sin monofilamento, sin elástico.
- 1 tensor de ojo (turnbuckle) pequeño, o un resorte pequeño con un pasador.
- 4 tornillos M3 × 10 (el motor) y grasa blanca o aceite de máquina de coser para las varillas.
- Ya los tienes: NEMA17, A4988, LED infrarrojo y fototransistor.

## Piezas y camas (PETG, boquilla 0,4, capa 0,2, sin soportes)

| Cama | Pieza | Cant. | Medida en la cama | g aprox. |
|---|---|---|---|---|
| 1 | `V4-CA_carro` | 1 | 165 × 77 × 19 | 33 |
| 1 | `V4-TO_tope` | 4 | 35 × 6 × 8,5 | 1 c/u |
| 1 | `V4-PM_tambor-motor` | 1 | Ø29 × 13 | 4 |
| 1 | `V4-PL_polea-libre` | 1 | Ø29 × 7,6 | 3 |
| 1 | `V4-EJ_eje-polea` | 1 | 7,8 × 19,2 × 7,8 | 1 |
| 1 | `V4-IR_puente-infrarrojo` (acostado) | 1 | 55 × 108 × 16 | 14 |
| 2 | `V4-BM_bloque-motor` | 1 | 85 × 94 × 47,5 | 47 |
| 2 | `V4-BR_bloque-extremo` | 1 | 67 × 92 × 47,5 | 38 |

`camas/` trae las dos camas ya acomodadas; `stl/` trae cada pieza en su posición de impresión. Paredes 3 (1,2 mm), relleno 15 %, borde (brim) de 3 mm en la cama 2. La cama 1 es la que hay que imprimir primero: antes de seguir, comprueba que el carro desliza en una varilla.

## Cómo funciona

- Las varillas están a |Y| = 30 mm y Z = 39,5 mm, de X = −280 a 718 mm (998 mm). Bloques motor y extremo a 948 mm entre caras.
- El carro (centro X = −168 + u, u de 0 a 774 mm) tiene 4 manguitos de 30 mm (2 pares a 130 mm) con agujero de 10,0 mm (0,24 mm de juego por lado), una placa de 4 mm en Z 46 a 50 donde se apoya el cartucho y una oreja central con dos agujeros de hilo.
- Los 4 topes en L se pegan al carro junto a los bordes del cartucho (|Y| = 26,5 mm).
- Hilo: oreja del carro (lado motor) → tambor del motor (3 vueltas) → tramo de abajo con el tensor → polea libre → oreja del carro (lado polea).
- El eje del motor queda a Z = 25,75 mm con el tambor entre Y = −6 y 7; el hilo de arriba va a Z ≈ 38,5 mm, a la altura de la oreja.
- Barrera infrarroja en X = −228 mm, haz a lo largo de Y a Z = 48 mm; la placa del carro la interrumpe a partir de u ≈ 22,5 mm.

## Cálculos

| Dato | Valor |
|---|---|
| Radio útil del tambor | 12,7 + 0,25 = 12,95 mm (fondo Ø25,4 más medio hilo de 0,5 mm) |
| Avance por vuelta | 81,4 mm con hilo de 0,5 mm (80 mm nominal) |
| Resolución con A4988 a 1/16 | 39,3 pasos/mm (40 nominal), 0,025 mm por paso |
| Carrera 774 mm | 30.960 pasos nominales |
| Un vaso (38 mm) | 1.520 pasos |
| Rechazo (u = 342 mm) | 13.680 pasos |
| Referencia IR | u ≈ 22,5 mm = 900 pasos |
| Luz libre de las varillas | 948 mm |
| Flecha de la varilla 3/8" | 0,54 mm por la carga (0,5 kg) más 0,71 mm por su peso: 1,25 mm |
| Roce supuesto | 5 N (muy alto a propósito) |
| Par que pide el carro | 5 N × 12,95 mm = 0,065 N·m |
| Par del NEMA17 | ≈ 0,4 N·m: margen ×6 |
| Agarre del hilo en el tambor | e^(0,2 × 3 × 2π) = ×43 sobre la tensión previa |
| Hilo necesario | 2,85 m: compra 3 m |
| Masa de las dos varillas de 3/8" × 1 m | ≈ 1,1 kg (0,56 kg cada una) |

La resolución depende del hilo real: **calibra** mandando 20.000 pasos y midiendo cuánto avanzó el carro (`STEPS_MM = pasos / mm`). Un error de 2 % son 15 mm en la carrera completa. Se corrige la posición con la barrera cada ciclo.

## Armado

1. Imprime la cama 1. Pasa una varilla por un manguito: debe deslizar con la mano. Si queda justa, repasa el agujero con una broca de 10 mm a mano.
2. Imprime la cama 2. Fija el NEMA17 al bloque del motor con 4 tornillos M3; mete el tambor en el eje (el agujero lleva el plano de la D; una gota de cianoacrilato o cinta de teflón lo asegura).
3. Monta el eje y la polea libre entre las mejillas del bloque del extremo.
4. Pasa las dos varillas por el bloque del motor, por el carro (los cuatro manguitos) y por el bloque del extremo. Engrasa las varillas.
5. Pega los 4 topes al carro, tocando el borde del cartucho.
6. Ata un cabo del hilo a la oreja, da 3 vueltas al tambor, sigue por abajo hasta la polea libre, sube y ata el otro cabo al otro agujero de la oreja. El tensor va en el tramo de abajo. Tensa hasta que suene como cuerda floja; a las 20 corridas retensa.
7. Pon el puente infrarrojo bajo el carro en X = −228 mm, el LED en el lado +Y y el fototransistor en el lado −Y.

## Comprobaciones hechas en el modelo

- 0 choques entre carro, topes, varillas, bloques, poleas, puente IR y cartucho en 7 posiciones del carro (u = 0, 100, 250, 342, 500, 650, 774). La única intersección que marca el programa es el eje redondo del NEMA con el plano de la D del tambor (11 mm³): es el modelo del eje, que no lleva el plano.
- Voladizos: capa por capa, 0 islas sin apoyo en las 8 piezas en su posición de impresión.
- Nada bajo el cartucho pasa de Z = 47,5 mm (el fondo está en Z = 50).

## Qué queda por confirmar con piezas reales

- El diámetro real de las varillas y que sean rectas.
- El juego de los manguitos en PETG (la impresión puede cerrar el agujero 0,1 mm).
- El tipo de hilo y su estiramiento.
- Las medidas del NEMA17 (cuerpo 42,3 mm, piloto Ø22, eje Ø5 con plano a 2 mm del centro): mídelas en el que tengas.

## Archivos

`generador/` tiene `generar_v4.py`, `exportar_v4.py`, `numeros_v4.py`, `masa_v4.py`, `revisar_v4.py` y `analisis.py`; necesitan `pip install manifold3d numpy` y `generar_banda.py` de `../generador/`.
`visor/visor-v4.html` es el visor 3D.
