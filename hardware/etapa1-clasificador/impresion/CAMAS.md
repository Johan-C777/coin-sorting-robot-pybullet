# Camas de la etapa 1 v5 (Creality K1C)

Ajustes: capa 0,2 mm, 3 paredes, 20 % de relleno, sin soportes. Clavijas P01/P02/P03 al 100 %.
Las piezas ya están acomodadas en cada `.3mf`: no girarlas ni escalarlas.
Orden pensado para probar la mecánica sin electrónica primero.

| Orden | Material | Piezas | g | Para qué prueba | Archivo |
|---|---|---|---|---|---|
| 1 | PLA+ negro | L01, H01, B01 x2, H03 a/b/c, P03 x3 | 95 | Pista, base de la tolva, remaches del motor | `cama1_PLA+negro_prueba_tolva.3mf` |
| 2 | PLA+ negro | H02 disco, K01, K02, P01 x19 | 83 | Tolva + pista a mano, rascador, caída de canto, ajuste de clavijas | `cama2_PLA+negro_disco_soportes_clavijas.3mf` |
| 3 | PLA+ negro | F01 embudo, C02 rampa, C01 x1, V01 x2, P02 x6 | 87 | Caída pista → embudo → vaso, cola de milano del cartucho | `cama3_PLA+negro_embudo_cartucho_prueba.3mf` |
| 4 | PETG azul | T01, S01, R02 | 145 | Marco | `cama4_PETG_azul_caballete.3mf` |
| 5 | PETG azul | T01, S01, R02 | 145 | Marco | `cama5_PETG_azul_caballete.3mf` |
| 6 | PETG azul | T01, S02 x2, R01 x2 | 160 | Marco | `cama6_PETG_azul_caballete.3mf` |
| 7 | PLA verde | V01 x7, C01 x2, G01, G02 (con brim) | 103 | Vasos, cartucho completo y compuerta (SG90) | `cama7_PLA_verde_vasos_cartuchos_compuerta.3mf` |
| 8 (opc.) | Cualquiera | F02 campana | 28 | Solo si las monedas saltan del embudo | `cama8_OPCIONAL_campana_embudo.3mf` |

Totales: PLA+ negro 265 g, PETG azul 450 g, PLA verde 103 g (≈ 820 g).

Las camas 2, 3 y 7 se regeneran desde `stl/` con
`python scripts/armar_camas_v5.py hardware/etapa1-clasificador/stl hardware/etapa1-clasificador/impresion`.
