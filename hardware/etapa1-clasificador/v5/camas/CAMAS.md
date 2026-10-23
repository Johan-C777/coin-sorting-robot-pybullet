# Camas de impresión, etapa 1 v5 (Creality K1C)

Cada archivo `.3mf` trae las piezas ya acomodadas y orientadas. Ábrelo en Creality Print, elige el material y lamina.
Ajustes: capa 0,2 mm, 3 paredes, 20 % de relleno. Gramos aproximados con esos ajustes.

| Cama | Material | Piezas | g aprox | Soportes |
|---|---|---|---|---|
| 1 | PLA+ negro | L01 pista, H01 base tolva, B01 x2, H03 a/b/c | 95 | Sí, solo en H01 (marca "solo en la cama") |
| 2 | PLA+ negro | H02 disco, K01, K02, G01, G02, P01 x17, P02 x8 | 100 | No. Clavijas al 100 % de relleno |
| 3 | PETG azul | T01 caballete, S01 patín largo, R02 larguero largo | 145 | No |
| 4 | PETG azul | T01 caballete, S01 patín largo, R02 larguero largo | 145 | No |
| 5 | PETG azul | T01 caballete, S02 x2, R01 x2 | 160 | No |
| 6 | PLA+ negro | F01 embudo, C01 cartucho x2, C02 rampa de rechazo | 90 | No |
| 7 | PLA verde manzana | V01 vaso x9, C01 cartucho | 85 | No |
| 8 (opcional) | Cualquiera | F02 campana del embudo | 28 | No |

Necesario: unos 820 g (PLA+ negro ~370 g, PETG azul ~450 g, PLA verde ~85 g).

Por qué así: la pista y la tolva en negro para que el IR y el sensor de color no tengan reflejos; el marco en PETG porque te alcanza el carrete y es firme; los vasos en otro color para verlos fácil.

Orden: imprime la cama 1 y la 2 y prueba la tolva con monedas antes de seguir. La cama 8 solo si en la prueba las monedas saltan fuera del embudo.

Se regeneran con `python3 scripts/armar_camas_v5.py <salida.3mf> <pieza>[x<cantidad>] ...`.
