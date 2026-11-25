# Etapa 2 v7: motor fijo, barra dentada en la mesa

> **Estado (noviembre de 2026):** impresa, montada y movida por la RAMBo con Marlin; lleva el cartucho bajo la torre ([video](../../../docs/pruebas/etapa2/video/banda_mueve_cartucho.mp4)). Las secciones de plan por fases y de riesgos se conservan como registro de cómo se planeó la impresión; el resultado está al final.

El motor NEMA17 y su piñón **no se mueven**. Una **barra dentada** impresa descansa en la mesa pegada al piñón y arrastra el carro por un **brazo** con cola de milano. Al girar el motor solo se mueven la barra, el carro y los vasos; el cable queda quieto. Todo se imprime como está, **sin soportes y sin comprar nada**. ≈ **372 g** de plástico.

| | v5 hilo | v6 motor en el carro | **v7 motor fijo** |
|---|---|---|---|
| Plástico | ≈ 268 g | ≈ 278 g | **≈ 372 g** |
| Piezas impresas | 11 + 6 cuñas | 7 | **13** |
| Camas | 3 | 3 | **4** |
| Motor y cable en movimiento | no | sí (280 g en voladizo) | **no** |
| Mesa que ocupa en X | — | ≈ 1,16 m | **≈ 1,58 m** |
| Soportes | 0 | 0 | **0** |
| Error de parada | 0,3 a 8 mm | ≈ 0,1 mm | **≈ 0,1 mm (más juego por 4 uniones)** |
| Compras | hilo | ninguna | **ninguna** |

## Por qué la barra es tan larga

Un piñón fijo solo puede empujar mientras haya dientes bajo él. La carrera es de 774 mm y el cartucho mide 386 mm, así que no basta con poner los dientes bajo el cartucho: la barra mide 810 mm (172 dientes) y detrás del carro queda una **cola de unos 420 mm** que sobresale de la mesa de la etapa 1 hacia −X. De X = −807 a 778 mm son **1,58 m de mesa** (la v6 pedía 1,16 m).

## Piezas, camas y materiales

| Pieza | Material | Peso | Cama |
|---|---|---|---|
| Carro con ranura de cola de milano | PETG | 58 g | 1 |
| Brazo (carro → clavija de la barra) | PETG | 24 g | 1 |
| Soporte del motor | PETG | 20 g | 1 |
| Piñón de 16 dientes (100 % de relleno) | PETG | 3 g | 1 |
| Barra, tramos 1 a 3 | PLA+ | 26 + 25 + 25 g | 2 |
| Riel, tramo 1 (postes infrarrojos) | PLA+ | 42 g | 2 |
| Barra, tramo 4 (con la clavija), en diagonal a 45° | PLA+ | 32 g | 3 |
| Riel, tramos 2 a 5 | PLA+ | 29 + 29 + 29 + 30 g | 4 |

Los gramos cuentan 3 paredes y 15 % de relleno (brazo, barras y piñón al 100 %). Macizas, las piezas pesarían 714 g. Las piezas están en su posición de impresión en `stl/` y acomodadas para la K1C (220 × 220) en `camas/`; qué va en cada cama está en `CAMAS.md`.

## Cómo funciona

- **Motor y soporte:** el NEMA17 va en un soporte impreso pegado a la mesa en el hueco entre los patines de la torre (X = −49 a 20), del lado −Y. Base con rampas, placa piloto, dos brazos y una pared guía que mantiene la barra contra el piñón. Queda 5,5 mm de margen a cada lado.
- **Piñón:** módulo 1,5, 20°, 16 dientes (Ø primitivo 24 mm, punta Ø27), en el eje con agujero en D. Está en X = −14,5.
- **Barra:** 4 tramos de 43 dientes (202,6 mm), perfil de 11 mm de ancho y 10,5 mm de alto (raíz de los dientes a 7,1 mm, punta a 10,5 mm); descansa sobre la base del soporte. Cada tramo lleva una lengüeta de cola de milano hacia adelante y una ranura atrás; se juntan deslizándolos de lado. Los cortes caen **en el centro de un valle**: el paso sigue sin saltos.
- **Brazo:** una placa de pie, pegada a la pared −Y del carro, con una cola de milano que entra **por arriba** en la ranura del carro (la tapa del cartucho la cierra) y un ojal alargado en Y para la clavija de Ø8 del último tramo de la barra. El ojal deja que la barra y el carro no tengan que quedar paralelos al milímetro.
- **Carro y riel:** los de la v5 (juego de 0,5 mm en las zonas de agarre); el carro solo suma la ranura del brazo. El riel es el de la v6 sin dientes.
- **Barrera infrarroja:** como en la v6, en el primer tramo; el borde de la placa del carro corta el haz en u = 2 mm. El poste del lado −Y quedó fuera del carril de la barra.

## Cálculos

| Dato | Valor |
|---|---|
| Circunferencia primitiva | 75,40 mm por vuelta |
| Resolución | **42,44 pasos/mm** (1/16, 3.200 por vuelta) |
| Carrera | 774 mm = 32.850 pasos |
| Un vaso (38 mm) | 1.613 pasos |
| Rechazo (u = 342 mm) | 14.515 pasos |
| Cero infrarrojo | u = 2 mm = 85 pasos |
| Empuje del motor | 33,3 N (0,4 N·m ÷ 12 mm); el carro pide ≈ 5 N como peor caso |
| Juego entre flancos | ≈ 0,45 mm (holgura de 0,35 mm entre centros y dientes de la barra 0,1 mm más delgados por lado); la impresión lo estrecha a ≈ 0,25 mm |
| Fase del piñón | 333,5° con u = 0; gira 1° cada 0,209 mm de u |

La resolución depende del piñón real: **calibra** mandando 20.000 pasos y midiendo cuánto avanzó el carro. Llega siempre a cada vaso desde el mismo sentido.

## Plan de impresión por etapas (para no gastar filamento a ciegas)

Lo máximo que se pierde antes de saber si funciona es la fase 0. Cada fase se imprime solo si la anterior pasó.

| Fase | Qué se imprime | Plástico | Pasa si |
|---|---|---|---|
| 0 | `prueba-ajuste/` (carro sobre riel), `prueba-engrane-y-union/` y `prueba-brazo/` | ≈ 110 g | El carro desliza sobre el riel con un empujón de dedo; la lengüeta entra firme en una de las 3 ranuras; el piñón rueda libre por los dientes; el brazo asienta en una de las 3 rebanadas |
| 1 | Soporte del motor + piñón (cama 1, solo esas dos piezas) | ≈ 23 g | El NEMA17 asienta por el piloto, el eje entra en el piñón y el piñón rueda sobre un trozo de barra de la fase 0 |
| 2 | Carro y brazo (cama 1) y un tramo de riel | ≈ 110 g | El carro desliza en el riel y el brazo asienta con el juego elegido |
| 3 | Barras (camas 2 y 3) y el resto de los rieles (camas 2 y 4) | ≈ 237 g | Armado completo y calibración de pasos |

Antes de imprimir, **mide el NEMA17**: cuerpo (lado y largo), diámetro y altura del piloto y largo del eje. Con esos números se ajusta el soporte en un minuto.

## Armado

1. Imprime la fase 0 y elige los juegos (tres pruebas, un número cada una).
2. Imprime las fases 1 a 3.
3. Encaja los 5 tramos del riel y pégalo a la mesa. Encaja los 4 tramos de la barra deslizándolos de lado.
4. Pega la base del soporte a la mesa entre los patines, recta. Monta el piñón en el eje (plano de la D hacia el plano del eje), mete el motor por atrás hasta que el piloto asiente y sujétalo con brida o liga en las ranuras.
5. Pon el carro en el riel; la barra se apoya en la base del soporte y pasa entre la pared guía y el piñón. **Pega una regla o una tira de cartón a lo largo de la cola de la barra**, para que no se vaya de lado. Mete el brazo por arriba en la ranura del carro y encaja su clavija en la barra.
6. Gira el piñón a mano hasta que engrane y mueve el carro de punta a punta. Frota los dientes con cera.

## Riesgos evaluados en el diseño

Antes de imprimir se estimó la probabilidad de que cada punto funcionara a la primera. Es un juicio de ingeniería que sirvió para decidir qué probar primero.

| Punto | Antes de la fase 0 | Después de la fase 0 | Por qué |
|---|---|---|---|
| Engrane piñón–barra (módulo 1,5, 20°) | ≈ 85 % | ≈ 95 % | Es un engrane corriente en impresión 3D. Juego de flancos ≈ 0,45 mm; Lewis: ≈ 12 MPa con 33 N, el PLA+ aguanta ≈ 40 |
| Uniones de cola de milano de la barra (3) | ≈ 65 % | ≈ 92 % | Ajuste de décimas de milímetro; la prueba lo fija con 3 juegos |
| Brazo en la ranura del carro | ≈ 65 % | ≈ 90 % | Igual: ajuste fino, 3 juegos |
| Carro sobre el riel | ≈ 80 % | ≈ 93 % | Perfil de la v5, nunca impreso; `prueba-ajuste/` |
| Barra recta y sin atascos (rozamiento, alineación) | ≈ 75 % | ≈ 85 % | Depende de la mesa y de pegar una regla guía; no se prueba con piezas |
| NEMA17 en el soporte | ≈ 70 % | ≈ 95 % | Cotas supuestas; se miden y se ajustan antes |

**El conjunto, funcionando tras como mucho un ajuste y una reimpresión pequeña (25 a 60 g): ≈ 80 %. Perder más de 250 g de plástico sin remedio: ≈ 5 a 10 %.** Esa cifra sube más cuanto antes midas el motor y pases la fase 0.

## Revisiones hechas en el modelo

- **0 choques** en 130 posiciones (cada 6 mm de u = 0 a 774) del carro, el brazo, las 4 barras y el cartucho real contra el riel, el soporte, el motor, el piñón (con su fase), la torre de la etapa 1 y el vaso de rechazo.
- **Engrane:** con el piñón girado según el avance, la intersección con la barra es 0 en las posiciones revisadas.
- **Hinchazón de la impresión (simulada con la geometría real):** si cada flanco engorda `e` mm por lado, se mide el solape del piñón con la barra a lo largo de un paso completo. Con el engrane anterior (holgura 0,15 mm, dientes sin recortar) atascaba desde `e` ≈ 0,03 mm y pedía 0,16 mm más de distancia entre centros con `e` = 0,05 mm. Con el engrane actual (holgura 0,35 mm y dientes de la barra 0,1 mm más delgados) gira libre hasta `e` = 0,10 mm por lado y roza a partir de ≈ 0,12 mm. Una impresora bien calibrada engorda 0,03 a 0,08 mm por lado.
- **Voladizos > 44° y islas de capa:** 0 islas en las 13 piezas. Voladizo: 0 en el carro, el soporte, el piñón, las barras y los rieles; 60 mm² de escalones de 0,2 mm en el brazo.
- **Uniones:** solape 0 entre tramos de barra; con la lengüeta engordada 0,1 mm hay contacto (4 mm³), lo que da un ajuste de unos 0,25 mm. El brazo entra en el carro con ajuste apretado: engordado 0,1 mm choca.
- **Soporte y motor:** libres de la torre inflándolos hasta 5 mm.
- **Pandeo de la barra** (compresión de un tramo de 810 mm apoyado en la mesa): margen ≈ 5 veces con PLA+.

Los scripts están en `generador/`: `generar_v7.py` (piezas), `choques_v7.py`, `holguras_v7.py`, `revisar_v7.py`, `masa_v7.py`, `numeros_v7.py`, `exportar_v7.py` (stl, camas y pruebas), `construir_visor7.py` (visor). Requieren `manifold3d` y `numpy`.

## Resultado del montaje

- Las 13 piezas están impresas y montadas; el carro recorre el riel completo arrastrado por la barra
  y lleva el cartucho de 9 vasos bajo la torre.
- El NEMA17 real (Folger 17HS) asienta en el soporte por el piloto; el soporte va pegado a la mesa
  entre los patines.
- Firmware de la RAMBo con **42,44 pasos/mm** y **38 mm entre vasos**; el cero de operación es la
  posición al encender, con el vaso 9 bajo el embudo.
- Mejoras para una siguiente versión: prisionero M3 en el cubo del piñón, brida en el soporte del
  motor y búsqueda automática del cero con la barrera infrarroja del tramo 1.
- La v6 (motor en el carro) se conserva en el repositorio como alternativa de diseño.
