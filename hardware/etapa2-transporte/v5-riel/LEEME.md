# Etapa 2 v5: riel impreso, carro e hilo de casa

Reemplaza la banda de cadena de la v3 (46 piezas, 1.506 g). **No se compra nada.** Un solo riel por tramos, un carro que lo abraza y un hilo que da vueltas al motor y a una polea. Todo se imprime como está, sin soportes (un techo plano de 6 mm en la ranura del eje de la polea es un puente).

| | v3 cadena | v5 riel |
|---|---|---|
| Plástico impreso (3 paredes, 15 % de relleno) | 1.506 g | **≈ 268 g** (118 g PETG, 149 g PLA+) |
| Piezas impresas | 46 | **11 y 6 cuñas** en 3 camas |
| Articulaciones que se pueden trabar | 168 | **0** |
| Soportes | 0 | **0** |
| Compras | ninguna | **ninguna** |

## Qué se usa de la casa

- **Hilo: caña de pescar trenzada (PE) de 0,2 a 0,3 mm (10 a 20 lb), unos 3 m. Es lo único que conviene comprar (unos pocos dólares).** Ver "Qué hilo" abajo. Si no, hilo de coser grueso de poliéster en 4 cabos, con peor precisión.
- Cinta de doble cara o cinta de enmascarar ancha para pegar el pie del riel a la mesa.
- Una brida plástica o una liga gruesa para sujetar el motor.
- Una vela, jabón seco o cera para frotar la cabeza del riel.
- Ya los tienes: NEMA17, A4988, LED infrarrojo y fototransistor.

## Camas (boquilla 0,4, capa 0,2, sin soportes, borde de 3 mm)

| Cama | Contenido | Material |
|---|---|---|
| 1 (hacer primero) | Carro, tambor, polea libre, eje, 6 cuñas y el **tramo 3 del riel** | PETG (carro y poleas) y PLA+ (riel) |
| 2 | Tramos 1, 2 y 4 del riel | PLA+ |
| 3 | Tramo 5, bloque del motor, bloque del extremo | PLA+ (tramo) y PETG (bloques) |

`camas/` trae las 3 camas acomodadas; `stl/` trae cada pieza en su posición de impresión. Con la cama 1 puedes probar el carro sobre el tramo 3 **antes de imprimir el resto**: debe resbalar con un dedo, sin juego visible. Si queda justo, lija la cabeza del riel con una lija de uñas; si baila o traba, se cambia el juego `CL` (0,5 mm hoy) en `generador/generar_v5.py`.

El PETG va en lo que está junto al motor y gira. El riel va en PLA+ porque no trabaja en caliente y PETG sobre PLA+ desliza mejor que PETG sobre PETG.

| Pieza | g | Medida (mm) |
|---|---|---|
| Carro | 59 | 124 × 58 × 45 |
| Bloque del motor | 31 | 98,5 × 95 × 47,5 |
| Bloque del extremo | 14 | 73 × 50 × 35 |
| Tambor del motor | 7 | Ø42 × 13 |
| Polea libre | 6 | Ø42 × 9 |
| Eje de la polea | 1 | 7,8 × 20,4 × 7,8 |
| Riel, tramo 1 (con los postes IR) | 38 | 184 × 82 × 56 |
| Riel, tramos 2 a 4 | 28 c/u | 184 × 28 × 26 |
| Riel, tramo 5 | 27 | 172 × 28 × 26 |
| Cuñas 1, 2 y 3 mm (2 de cada) | < 1 | 8 × 5 × 1 a 3 |

## Cómo funciona

- **Riel:** pie plano de 28 × 2,4 mm que se pega a la mesa, cuello de 7 mm y cabeza de 17 mm con los dos lados a 45°; 912 mm en 5 tramos de 172 mm y dos bloques en los extremos. Los tramos se encajan con una lengüeta en cola de milano (12 mm, 0,25 mm de juego). Se imprime de pie: todo es vertical o a 45°.
- **Carro:** placa de 124 × 58 mm a Z = 46 a 50 con dos zonas de agarre de 34 mm (separadas 90 mm) que abrazan la cabeza con 0,5 mm de juego por todo el contorno. Se apoya en la tapa de la cabeza; los labios debajo de los lados impiden que se levante o se incline. 4 topes a 26,3 mm del centro mantienen el cartucho (52 mm). Dos agujeros de Ø2,6 mm atraviesan el carro a lo largo para los cabos del hilo (Y = 18,5 y 23,5; Z = 43,5).
- **Hilo:** corre en un costado del riel (Y = 21) a Z = 43,5 arriba y a Z = 4,5 abajo. Sale del carro, da 3 vueltas al tambor, baja, rodea la polea libre y vuelve al carro.
- **Motor:** eje a Z = 24, cara a Y = 33, eje hacia −Y. Se apoya en la base (2,85 mm), se centra con el piloto Ø22 en una placa de 5 mm y lo contienen dos paredes. Una brida o una liga pasa por dos ranuras de la base y sobre el motor; el motor queda a 4,85 mm bajo el fondo del cartucho.
- **Tensor:** el eje de la polea libre descansa en una ranura con 6 mm de recorrido. Las cuñas de 1, 2 y 3 mm se meten entre el eje y el extremo −X de la ranura (una por mejilla).
- **Barrera infrarroja:** en el tramo 1, en X = −160, haz a lo largo de Y a Z = 48. El borde trasero de la placa del carro corta el haz cuando u = 70 mm.

## Cálculos

| Dato | Valor |
|---|---|
| Radio útil del tambor | 19,25 + 0,25 = 19,5 mm (fondo Ø38,5 más medio hilo de 0,5 mm) |
| Avance por vuelta | 122,5 mm |
| Resolución con A4988 a 1/16 | 26,1 pasos/mm, 0,038 mm por paso |
| Carrera 774 mm | 20.215 pasos |
| Un vaso (38 mm) | 992 pasos |
| Rechazo (u = 342 mm) | 8.932 pasos |
| Referencia IR | u = 70 mm = 1.828 pasos |
| Largo del riel | 912 mm; el carro recorre de X = −230 a 668 |
| Roce supuesto | 5 N (carro y cartucho 0,35 kg × 0,4 = 1,4 N, el resto es margen) |
| Par que pide el carro | 5 N × 19,5 mm = 0,098 N·m |
| Par del NEMA17 | ≈ 0,4 N·m: margen ×4 |
| Agarre del hilo en el tambor | e^(0,2 × 3 × 2π) = ×43 |
| Hilo | 2,7 m: usa 3 m |
| Juego carro–riel | 0,5 mm (medido en el modelo, todo el contorno) |

La resolución depende del hilo real: **calibra** mandando 20.000 pasos y midiendo cuánto avanzó el carro (`STEPS_MM = pasos / mm`). Un error de 2 % son 15 mm al final de la carrera. La referencia infrarroja corrige la posición en cada ciclo.

## Armado

1. Imprime la cama 1 y prueba el carro sobre el tramo 3.
2. Imprime las camas 2 y 3.
3. Encaja en orden: bloque del motor, tramos 1 a 5.
4. Desliza el carro por el extremo libre del tramo 5 y encaja el bloque del extremo.
5. Pega el pie del riel a la mesa con cinta, centrado en la banda y recto con una regla.
6. Pon el motor en su cuna con la brida; monta el tambor en el eje (el agujero lleva el plano de la D del eje) y el eje octogonal con la polea libre entre las mejillas.
7. Hilo: pasa un cabo por el agujero del lado Y = 18,5 hasta el otro extremo del carro y anúdalo; dale 3 vueltas al tambor, baja por el tramo de abajo, rodea la polea y sube; pasa el otro cabo por el agujero del lado Y = 23,5 y anúdalo. Tensa con las cuñas: con trenzado, una cuña de 1 mm da unos 3 N; busca 3 a 5 N (el hilo suena como cuerda de guitarra floja). Anuda con 3 nudos y una gota de pegamento.
8. Frota la cabeza del riel con cera o jabón seco.

## Comprobaciones hechas en el modelo

- **0 choques** entre el carro, los bloques, los tramos, las poleas, el motor, la torre de la etapa 1, el vaso de rechazo y el cartucho real (rampa y 9 vasos), con el carro en 129 posiciones (cada 6 mm de u = 0 a 774) y el hilo como una caja de 1 mm. La única intersección que marca el programa en el motor es el eje redondo del modelo con el plano de la D del tambor (11 mm³), que es el modelo del eje.
- **Voladizos:** capa por capa, 0 islas sin apoyo en las 11 piezas grandes en su posición de impresión (las cuñas son placas planas), salvo el techo plano de 6 mm de cada ranura del eje de la polea en el bloque del extremo: es un puente corto que se imprime sin soporte.
- El motor llega a Y = 81 y los patines de la torre empiezan en |Y| = 83; además no coinciden en X con la base del motor. El motor queda a 4,85 mm bajo el fondo del cartucho.
- El hilo de abajo queda a 4,5 mm de la mesa y a 1,6 mm sobre la base de los bloques.

## Qué queda por confirmar con piezas reales

- El juego carro–riel (0,5 mm) en tu impresora: se mide con la cama 1.
- El hilo que uses y cuánto estira.
- El motor: medidas del NEMA17 (cuerpo 42,3 mm, piloto Ø22, eje Ø5 con plano a 2 mm del centro): mídelas en el que tengas. Si el cuerpo es más largo que 48 mm, avisa.
- El motor queda a 4,85 mm bajo el cartucho: una brida normal cabe; si es gruesa, usa una liga.

## Archivos

`generador/` tiene `generar_v5.py`, `exportar_v5.py`, `numeros_v5.py`, `masa_v5.py`, `revisar_v5.py`, `choques_v5.py`, `torre_ref.py`, `analisis.py`, `capas.py` y `camas.py`; necesitan `pip install manifold3d numpy`. `visor/visor-v5.html` es el visor 3D.

## Qué hilo (simulación, `generador/sim_hilo.py`)

El agarre en el tambor no es el problema: con 3 vueltas basta una tensión del lazo de 3 a 4,5 N aunque el hilo sea liso (μ entre 0,08 y 0,3). **El problema es que el hilo estira**: el carro queda atrás de donde lo manda el motor en (fricción del carro × elasticidad del hilo), y más aún en el extremo lejano del riel.

Error de parada tras mover 38 mm, con el carro y el cartucho a 0,6 kg (valores de EA estimados de hojas típicas, no medidos):

| Hilo | Fricción del carro 1 N | 2,5 N | 5 N |
|---|---|---|---|
| Costura, 1 cabo | hasta 4 mm | hasta 8 mm | hasta 38 mm |
| Costura, 4 cabos | hasta 2 mm | hasta 2,4 mm | hasta 8 mm |
| Nylon liso 0,4 mm | hasta 0,6 mm | hasta 2,3 mm | hasta 5 mm |
| **Trenzado PE de caña** | **0,0 mm** | **0,3 mm** | **0,6 mm** |

El trenzado también deja sin problema la tensión: la fuerza máxima en el hilo es 4 N en una carrera larga. El carro debe deslizar con un empujón de dedo (fricción real esperada: 1 a 1,5 N con cera).
