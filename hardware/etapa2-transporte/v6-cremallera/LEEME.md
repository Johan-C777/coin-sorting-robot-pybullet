# Etapa 2 v6: cremallera impresa, motor y piñón sobre el carro

Reemplaza el hilo de la v5. El riel conserva su perfil y se imprime por tramos; ahora lleva una **cremallera** en el costado del pie. El carro lleva el motor NEMA17 y un **piñón** que camina por los dientes. Todo se imprime como está, **sin soportes y sin comprar nada**. ≈ **278 g** de plástico (v3 cadena: 1.506 g; v5 hilo: ≈ 268 g).

| | v3 cadena | v5 hilo | **v6 cremallera** |
|---|---|---|---|
| Plástico | 1.506 g | ≈ 268 g | **≈ 278 g** |
| Piezas impresas | 46 | 11 + 6 cuñas | **7** |
| Camas | 10 | 3 | **3** |
| Soportes | 0 | 0 | **0** |
| Error de parada | por medir | 0,3 a 8 mm (hilo estirando) | **≈ 0,1 mm (juego de flancos)** |
| Compras | ninguna | hilo | **ninguna** |

## Piezas, camas y materiales

| Pieza | Material | Peso | Cama |
|---|---|---|---|
| Carro con brazos y placa del motor | PETG | 69 g | 1 |
| Piñón de 18 dientes | PETG, 100 % relleno | 4 g | 1 |
| Riel, tramo 1 (postes infrarrojos) | PLA+ | 50 g | 3 |
| Riel, tramos 2 a 5 | PLA+ | 39 + 39 + 39 + 38 g | 2 |

Los gramos cuentan 3 paredes y 15 % de relleno. Macizas, las piezas pesarían 663 g. Todas las piezas están en su posición de impresión en `stl/` y acomodadas para la K1C en `camas/`.

## Cómo funciona

- **Riel:** el de la v5 (pie plano de 28 mm pegado a la mesa, cuello de 7 mm, cabeza de 17 mm con los lados a 45°), 912 mm de X = −237 a 675 en 5 tramos con lengüeta.
- **Cremallera:** módulo 1,5, 20°, 172 dientes (paso 4,712 mm) de X = −190 a 620, en una franja de 8,5 mm del lado −Y, con la raíz a Z = 6,9 y la punta a Z = 10,25. Los tramos se cortan **en el centro de un valle**, así que los dientes siguen sin saltos de un tramo al siguiente.
- **Carro:** las dos zonas de agarre de la v5 (juego 0,5 mm) más **dos brazos y una placa** que sostienen el motor con el eje apuntando al riel. Brazos y placa se imprimen de pie, desde la cama, igual que las patas del carro.
- **Piñón:** 18 dientes, Ø primitivo 27 mm, en el eje del motor (agujero en D). Queda entre la placa y la pared del carro; la punta del eje entra por un agujero de Ø8 a la cavidad del carro.
- **Motor:** NEMA17 de 48 mm, centrado por el piloto en la placa y entre los brazos (0,35 mm de holgura), sujeto con brida o liga en las ranuras. Pesa ≈ 280 g y cuelga del lado −Y (el lado libre de la torre).
- **Barrera infrarroja:** como en la v5, en el primer tramo; el borde izquierdo de la placa corta el haz en u = 2 mm.

## Cálculos

| Dato | Valor |
|---|---|
| Circunferencia primitiva | 84,82 mm por vuelta |
| Resolución | **37,73 pasos/mm** (1/16, 3.200 por vuelta) |
| Carrera | 774 mm = 29.200 pasos |
| Un vaso (38 mm) | 1.434 pasos |
| Rechazo (u = 342 mm) | 12.902 pasos |
| Cero infrarrojo | u = 2 mm = 75 pasos |
| Empuje del motor | 29,6 N (0,4 N·m ÷ 13,5 mm); el carro pide ≈ 5 N como peor caso |
| Juego entre flancos | 0,11 mm (0,15 mm de holgura entre centros) |
| Engrane del piñón con la cremallera | de u = −10 a 776 mm |

La resolución depende del piñón real: **calibra** mandando 20.000 pasos y midiendo cuánto avanzó el carro (`STEPS_MM = pasos / mm`). Llega siempre a cada vaso desde el mismo sentido.

## Armado

1. Imprime primero la **prueba de engrane** (`prueba-engrane/`, 16 dientes y un piñón). Monta el piñón en el eje del motor y ruédalo a mano por los dientes: debe girar libre, sin saltar ni pegarse. Con `prueba-ajuste/` se prueba además el juego del carro sobre el riel.
2. Imprime las camas 1, 2 y 3.
3. Encaja los 5 tramos por las lengüetas y pega el pie a la mesa con cinta de doble cara, recto con una regla.
4. Monta el piñón en el eje (el plano de la D hacia el plano del eje). Mete el motor por atrás entre los brazos hasta que el piloto asiente en la placa y sujétalo con brida o liga en las ranuras.
5. Desliza el carro por el extremo libre del tramo 5 hasta que el piñón engrane; gíralo con un dedo. Frota los dientes con cera.
6. Deja el cable del motor con holgura, sujeto al carro y sin rozar la mesa.

## Revisiones hechas en el modelo

- **0 choques** del carro, el motor y el piñón con el riel con cremallera, la torre de la etapa 1, el cartucho real (rampa y 9 vasos) y el vaso de rechazo, en 130 posiciones (cada 6 mm de u = 0 a 774).
- **Engrane:** con el piñón girado según el avance, la intersección con la cremallera es 0 en 13 posiciones a lo largo de un paso; bajándolo 0,25 mm interfiere 0,5 mm³ (hay contacto real).
- **Voladizos > 44° y islas de capa:** 0 en las 7 piezas; cada pieza es un solo cuerpo.
- **Holgura motor–torre:** libre inflando el motor y los brazos 2 mm; con 3 mm choca con un patín de la torre.

Los scripts están en `generador/`: `generar_v6.py` (piezas), `choques_v6.py`, `holguras_v6.py`, `revisar_v6.py`, `masa_v6.py`, `numeros_v6.py`, `exportar_v6.py` (stl y camas), `construir_visor6.py` (visor). Requieren `manifold3d` y `numpy`.

## Qué hay que confirmar con el motor real

- Cuerpo de 42,3 mm, largo de 48 mm, piloto Ø22 de 2 mm de alto, eje Ø5 con plano a 2 mm y **24 mm de largo** (con 20 mm el piñón sigue alcanzando).
- Si el motor es más largo, el extremo trasero se acerca a los patines de la torre (hoy 2 a 3 mm de margen).
