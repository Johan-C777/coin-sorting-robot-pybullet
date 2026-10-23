# Etapa 1 v5: piezas, despiece y armado

Prototipo compacto del clasificador. Torre de 33 cm que se para sobre la mesa y pasa por encima de la banda.
Se genera con `python scripts/generar_v5.py --ensamble` (revisa choques, cama y que cada pieza sea un solo cuerpo).

Visor 3D con estas mismas piezas: el artefacto "Clasificador de Canto".

## Cómo funciona

1. **Tolva de disco (H01, H02, H03).** Plato inclinado a 45°. El 28BYJ-48 gira un disco de 8 bolsillos (Ø29). Cada bolsillo sube una moneda; el rascador tumba la que venga montada.
2. **Cae de canto.** Arriba, el bolsillo pasa sobre un hueco y la moneda cae unos 2 cm a la pista. Queda parada contra la placa (simulado: 1728 de 1728, `sim/mujoco/disco.py`).
3. **Pista (L01, B01).** 22° de pendiente, placa a 20° de la vertical. Dos barreras IR a 105 y 129 mm miden el diámetro; el TCS34725 a 152 mm separa las $500.
4. **Embudo (F01, F02).** Borde Ø90, pared a 45°, 60 mm adelante y 50 mm bajo el fin de pista (simulado: 81 de 81, `sim/mujoco/embudo.py`).
5. **Compuerta (G01, G02).** Paleta con bisagra en su borde trasero sobre el eje del SG90. Cerrada sostiene la moneda; abre 60° hacia abajo cuando el vaso ya está debajo.
6. **Cartucho (C01 x3, C02, V01 x9).** La banda lo mueve para poner el vaso correcto bajo el hueco. Para el rechazo pone la rampa C02 y la moneda resbala a un vaso que se pone a mano en la mesa, 60 mm al frente del centro de la banda.

## Piezas

Total aproximado: **842 g de PLA** (3 paredes, 20% relleno). Todas caben en la K1C (220 x 220 mm).

| Código | Pieza | Cant. | Medidas de impresión (mm) | g total | Cómo imprimir |
|---|---|---|---|---|---|
| L01 | Pista con repisa, barreras y sensor de color | 1 | 179 x 60 x 23 | 34 | Acostada sobre la espalda de la placa. Sin soportes. |
| B01 | Porta-emisor IR (se engancha detrás de la placa) | 2 | 27 x 15 x 14 | 4 | De lado. Sin soportes. |
| H01 | Base de la tolva: plato inclinado, aro y soporte del motor | 1 | 128 x 117 x 48 | 52 | Con la cara trasera abajo. Necesita soportes (solo bajo las clavijas del motor y las almohadillas). |
| H02 | Disco de 8 bolsillos | 1 | 98 x 98 x 8 | 6 | Plano, el cubo hacia arriba. Sin soportes. |
| H03 | Rascador (quita la moneda montada) | 1 | 36 x 43 x 4 | 1 | De canto. Sin soportes. Se imprimen 3 alturas: 2,5 / 2,6 / 2,8 mm. |
| K01 | Soporte de la tolva y la pista (caballete 1) | 1 | 91 x 70 x 16 | 57 | De lado (cara plana abajo). Sin soportes. |
| K02 | Soporte de la pista (caballete 2) | 1 | 50 x 35 x 16 | 13 | De lado. Sin soportes. |
| F01 | Embudo con brida | 1 | 136 x 136 x 30 | 28 | Boca abajo (la brida sobre la cama). Pared a 45°, sin soportes. |
| F02 | Campana del embudo con ventana | 1 | 88 x 100 x 60 | 28 | Con la tapa sobre la cama. Sin soportes. |
| G01 | Cuna del servo de la compuerta | 1 | 27 x 24 x 51 | 12 | Boca abajo. Sin soportes. |
| G02 | Compuerta (paleta con bisagra) | 1 | 9 x 38 x 36 | 2 | De canto, el cubo arriba. Sin soportes. |
| T01 | Caballete (marco en forma de puente) | 3 | 206 x 161 x 16 | 273 | Plano. Sin soportes. |
| S01 | Patín largo (caballetes 1 y 2) | 2 | 186 x 24 x 14 | 78 | Plano. Sin soportes. |
| S02 | Patín corto (caballete 3) | 2 | 100 x 24 x 14 | 42 | Plano. Sin soportes. |
| R01 | Larguero entre caballetes 1 y 2 | 2 | 132 x 12 x 12 | 25 | Plano. Sin soportes. |
| R02 | Larguero entre caballetes 2 y 3 (lleva el embudo) | 2 | 170 x 12 x 12 | 32 | Plano. Sin soportes. |
| C01 | Cartucho de 3 vasos (se unen 3 en fila) | 3 | 120 x 52 x 16 | 56 | Plano. Sin soportes. |
| C02 | Rampa de rechazo (va en la punta del cartucho) | 1 | 64 x 74 x 44 | 24 | De lado. Sin soportes. |
| V01 | Vaso Ø34 x 60 | 9 | 34 x 34 x 60 | 67 | De pie. Sin soportes. |
| P01 | Clavija Ø6 x 20 | 17 | 6 x 6 x 20 | 6 | De pie. Imprime todas juntas. |
| P02 | Clavija Ø6 x 12 | 8 | 6 x 6 x 12 | 2 | De pie. Imprime todas juntas. |

Ajustes sugeridos: PLA, capa 0,2 mm, 3 paredes, 20% relleno. Las clavijas al 100% de relleno.
Si las clavijas entran muy duras o flojas, cambia `HOLGURA` (0,3 mm por lado) en el script y vuelve a generar.

## Armado (sin tornillos)

1. **Patines y caballetes.** Mete las patas de los caballetes T01 en los encajes de los patines: S01 (largo) lleva los caballetes 1 y 2; S02 (corto) el caballete 3. Uno de cada lado.
2. **Largueros.** R01 entre los caballetes 1 y 2 (los de afuera), R02 entre 2 y 3. Cada punta con una clavija P01.
3. **Soportes.** K01 sobre el caballete 1 y K02 sobre el caballete 2, cada uno con clavijas P01.
4. **Pista.** Pon los porta-emisores B01 (se enganchan en el borde de abajo, detrás de la placa) con sus LED IR. Mete los fototransistores en los postes de adelante y el TCS34725 en su rebaje. Apoya la pista en K01 y K02 con una clavija P01 en cada uno.
5. **Tolva.** Fija el 28BYJ-48 detrás de H01 (las orejas en sus dos clavijas y una brida por los pasos). Pon el disco H02 en el eje y el rascador H03a en su ranura. Apoya H01 en K01 (el motor entra en su hueco) y únela a la pista con dos clavijas P02.
6. **Embudo.** F01 sobre los largueros R02 con 4 clavijas P02. La campana F02 se asienta en su ranura, con la ventana hacia la pista.
7. **Compuerta.** El SG90 entra en la cuna G01 con el eje hacia el centro. Cuelga G01 de la brida con 2 clavijas P02. Pega el brazo simple del servo en el rebaje de G02 y ponlo en el eje con la compuerta cerrada (horizontal).
8. **Cartucho.** Une C02 + C01 + C01 + C01 por sus colas de milano, con la rampa al lado opuesto al punto A. Pon los 9 vasos en orden: $50 n, $100 n, $50 a, $200 n, $100 a, $500 a, $500 n, $200 a, $1000 n.
9. **Sobre la banda.** Para la torre encima de la banda con el hueco del embudo sobre el centro (perdona ±5 mm). El vaso de rechazo va en la mesa, al frente, bajo la punta de la rampa.

## Primera prueba (antes de imprimir todo)

Imprime L01, B01 (x2), H01, H02 y los tres H03. Con eso, apoyados con calces, revisas:

- que el disco tome una sola moneda (prueba H03a de 2,5 mm; si roza el disco usa H03b),
- que la moneda caiga de canto y ruede,
- el ruido real de las barreras con tus monedas (modo calibración).

## Conexiones (propuesta)

| Elemento | ESP32 |
|---|---|
| 28BYJ-48 (ULN2003 IN1..IN4) | 19, 18, 5, 17 |
| SG90 compuerta | 13 |
| LED IR de las 2 barreras (modulados, por un transistor) | 25 |
| Receptor barrera 1 / barrera 2 | 34 / 35 |
| TCS34725 (I2C) | SDA 21, SCL 22 |
| Banda (etapa 2): A4988 STEP / DIR / EN, barrera de posición | 26 / 27 / 14, 32 |

## Qué no está validado

Que el disco tome siempre una sola moneda, la compuerta, el posicionamiento del cartucho (depende de la banda) y los sensores reales. Meta del prototipo: 90%.
