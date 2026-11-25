# Etapa 2: transporte del cartucho

**Estado:** la v7 (motor fijo con barra dentada) está **impresa, montada y conectada**, y lleva el cartucho bajo la torre movida por una RAMBo con Marlin ([video](../../docs/pruebas/etapa2/video/banda_mueve_cartucho.mp4)). Las versiones anteriores se conservan porque documentan el proceso de diseño.

El cartucho de 9 vasos (C02 + 3 C01 + 9 V01) de la etapa 1 v5 debe recorrer 774 mm bajo la torre: el vaso 9 queda bajo el embudo en u = 0, el rechazo en u = 342 mm y el vaso 1 en el punto A en u = 774 mm. Un NEMA17 controlado por la RAMBo (Marlin 2.1.2.5, 42,44 pasos/mm) lo mueve en lazo abierto; el cero es la posición al encender, con el vaso 9 bajo el embudo. El requisito de diseño es imprimir casi todo, con el mínimo de material, sin soportes y sin comprar piezas.

## Versiones

| Versión | Mecanismo | Plástico | Compras | Por qué se dejó |
|---|---|---|---|---|
| [v3, cadena](v3-cadena/CAMAS.md) | Cadena de 168 eslabones impresos con bastidor de 6 módulos | ≈ 1,5 kg, 46 piezas | NEMA17, A4988, IR | Demasiado material y 168 articulaciones que atascan |
| [v4, varillas](v4-varillas/LEEME.md) | Carro sobre varillas de acero con hilo | ≈ 0,3 kg | Varillas de acero | Obliga a comprar piezas |
| [v5, riel](v5-riel/LEEME.md) | Un riel impreso por tramos, carro que lo abraza e hilo con 3 vueltas al tambor | ≈ 268 g | Solo el hilo | El hilo estira y limita la precisión |
| [v6, cremallera](v6-cremallera/LEEME.md) | El mismo riel y carro, con dientes impresos en el riel y el motor con un piñón sobre el carro | ≈ 278 g | Ninguna | El motor y su cable viajan en el carro (≈ 280 g en voladizo) |
| [**v7, motor fijo**](v7-motor-fijo/LEEME.md) | Motor y piñón quietos en la mesa; una barra dentada de 810 mm en 4 tramos arrastra el carro por un brazo | ≈ 372 g | Ninguna | **Vigente: impresa y montada** |

Visores en 3D: [v7 (vigente)](../../docs/etapa2/v7-motor-fijo.html) y el [conjunto de las etapas 1 y 2 con la electrónica](../../docs/visor-etapas-1-2.html). Del proceso de diseño: [v3](../../docs/archivo/banda-etapa2-v3.html), [v4](../../docs/etapa2/proceso/v4-varillas.html), [v5](../../docs/etapa2/proceso/v5-riel.html) y [v6](../../docs/etapa2/proceso/v6-cremallera.html).

## v7: cómo funciona

- El NEMA17 (Folger 17HS, 0,52 N·m) va quieto en un soporte de PETG pegado a la mesa entre los patines de la torre (X = −49 a 20), del lado −Y. Su piñón de 16 dientes (módulo 1,5, Ø primitivo 24 mm) empuja una barra dentada de PLA+ que descansa sobre la base del soporte.
- La barra mide 810 mm (172 dientes) en 4 tramos unidos por cola de milano; el último lleva una clavija de Ø8 que entra en el ojal del brazo, y el brazo entra por arriba en la ranura del carro. Solo se mueven la barra, el carro y el cartucho: el cable del motor queda quieto.
- El carro y el riel son los de la v5 (riel de 912 mm en 5 tramos de PLA+ mármol). El primer tramo lleva los postes de una barrera infrarroja en u = 2 mm; en la operación, el cero es la posición al encender.
- Resolución: 75,40 mm por vuelta, **42,44 pasos/mm** a 1/16 de paso; carrera de 774 mm = 32.850 pasos; un vaso (38 mm) = 1.613 pasos; rechazo en u = 342 mm.
- Ocupa 1,58 m de mesa en X: detrás de la torre sobresale la cola de la barra (unos 420 mm).

## Control

- **Controlador:** RAMBo con Marlin 2.1.2.5, NEMA17 en el driver X (42,44 pasos/mm, corriente por `M907`). La ESP32-S3 de la etapa 1 pide cada vaso en G-code y espera el `ok` de `M400` ([arquitectura](../../docs/14-estado-final.md)).
- **Mejoras para una siguiente versión:** prisionero M3 en el cubo del piñón, brida de sujeción del soporte del motor y búsqueda automática del cero con la barrera IR.

## v6 (proceso): cómo funcionaba


- El riel (5 tramos de PLA+, 912 mm en total) lleva una cremallera de módulo 1,5 en el pie, del lado libre de la torre. El carro de PETG abraza el riel y carga el cartucho de vasos.
- El NEMA17 cuelga de dos brazos del carro con el eje hacia el riel. Un piñón de 18 dientes (4 g, PETG al 100 %) engrana con la cremallera, de modo que el carro avanza 4,712 mm por diente y 37,73 pasos por milímetro con micropasos de 1/16.
- Sin hilo no hay estiramiento: el error de parada es de unas décimas de milímetro, el juego de los dientes (0,11 mm de holgura entre flancos).
- El cero lo da la barrera infrarroja con una aleta del propio carro (u = 2 mm).
- Todo se imprime sin soportes: los brazos y la placa del motor salen verticales desde la cama, igual que las patas.

### v6: revisión en el modelo (versión reemplazada por la v7)

- Cero choques del carro, el motor y el piñón con la torre, el cartucho y el vaso de rechazo en todo el recorrido (u de 0 a 774 mm).
- Siete piezas con 0 voladizos de más de 44°, 0 islas y un solo cuerpo; holgura libre hasta 2 mm de margen.
- Masa total 278 g (PETG 73 g, PLA+ 205 g).
- Puntos que llevaron a la v7: los valles de 1 mm de los dientes dependen de la impresora (por eso `prueba-engrane/`), el motor queda en voladizo (unos 280 g a 58 mm, parte del peso la lleva la cremallera) y entre el motor y la torre quedan 2 a 3 mm. Las medidas del NEMA17 usado en el modelo (cara 42,3 mm, cuerpo de 48 mm, boca de Ø22, eje de Ø5 con plano de 24 mm) se contrastaron con el motor real.

## Lo aprendido con la v5

- El agarre del hilo en el tambor no es el problema: con 3 vueltas basta una tensión de 3 a 4,5 N aunque el hilo sea liso.
- Lo que limita es el estiramiento. El carro se queda corto al parar según la fricción por la elasticidad del hilo: con hilo de coser de un cabo hasta 8 mm, con caña trenzada de pescar unos 0,3 mm (simulación en `v5-riel/generador/sim_hilo.py`; las rigideces son valores típicos, no medidos).
- Eso llevó a la cremallera: el error baja a unas décimas de mm, a cambio de unos 10 g más en el riel y de llevar el motor y su cable sobre el carro.

## Orden de impresión (v7)

Las 4 camas están en `v7-motor-fijo/camas/` y se describen en [`v7-motor-fijo/CAMAS-directas.md`](v7-motor-fijo/CAMAS-directas.md): cama 1 PETG azul (carro, brazo, soporte y piñón), camas 2 y 3 PLA+ negro (barras) y cama 4 PLA+ mármol (rieles). Las piezas de prueba (`prueba-ajuste/`, `prueba-engrane-y-union/`, `prueba-brazo/`) sirven para ajustar holguras antes de reimprimir una pieza.

## Contenido

Cada versión trae sus STL en posición de impresión (`stl/`), las camas acomodadas para la K1C (`camas/`) y el generador en Python (`generador/`, requiere `manifold3d` y `numpy`). En v7: `cd v7-motor-fijo/generador && python exportar_v7.py`; las comprobaciones son `choques_v7.py`, `holguras_v7.py`, `tolerancias_v7.py`, `revisar_v7.py` y `masa_v7.py`, y el visor se arma con `construir_visor7.py`.
