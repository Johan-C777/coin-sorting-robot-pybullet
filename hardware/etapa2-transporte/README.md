# Etapa 2: transporte del cartucho

**Estado:** en rediseño. Nada está impreso todavía. La versión vigente es la v6 (cremallera impresa), modelada y revisada en el modelo, pendiente de la primera prueba física; las versiones anteriores se conservan porque documentan el proceso.

El cartucho de 9 vasos (C02 + 3 C01 + 9 V01) de la etapa 1 v5 debe recorrer 774 mm bajo la torre: el vaso 9 queda bajo el embudo en u = 0, el rechazo en u = 342 mm y el vaso 1 en el punto A en u = 774 mm. Un NEMA17 con A4988 lo mueve en lazo abierto y una barrera infrarroja da el cero. El requisito de diseño es imprimir casi todo, con el mínimo de material, sin soportes y sin comprar piezas.

## Versiones

| Versión | Mecanismo | Plástico | Compras | Por qué se dejó |
|---|---|---|---|---|
| [v3, cadena](v3-cadena/CAMAS.md) | Cadena de 168 eslabones impresos con bastidor de 6 módulos | ≈ 1,5 kg, 46 piezas | NEMA17, A4988, IR | Demasiado material y 168 articulaciones que atascan |
| [v4, varillas](v4-varillas/LEEME.md) | Carro sobre varillas de acero con hilo | ≈ 0,3 kg | Varillas de acero | Obliga a comprar piezas |
| [v5, riel](v5-riel/LEEME.md) | Un riel impreso por tramos, carro que lo abraza e hilo con 3 vueltas al tambor | ≈ 268 g | Solo el hilo | El hilo estira y limita la precisión |
| [**v6, cremallera**](v6-cremallera/LEEME.md) | El mismo riel y carro, con dientes impresos en el riel y el motor con un piñón sobre el carro | ≈ 278 g | Ninguna | Vigente, pendiente de la prueba física |

Visores en 3D: [v6 (vigente)](../../docs/etapa2/v6-cremallera.html). Del proceso de diseño: [v3](../../docs/archivo/banda-etapa2-v3.html), [v4](../../docs/etapa2/proceso/v4-varillas.html) y [v5](../../docs/etapa2/proceso/v5-riel.html).

## v6: cómo funciona

- El riel (5 tramos de PLA+, 912 mm en total) lleva una cremallera de módulo 1,5 en el pie, del lado libre de la torre. El carro de PETG abraza el riel y carga el cartucho de vasos.
- El NEMA17 cuelga de dos brazos del carro con el eje hacia el riel. Un piñón de 18 dientes (4 g, PETG al 100 %) engrana con la cremallera, de modo que el carro avanza 4,712 mm por diente y 37,73 pasos por milímetro con micropasos de 1/16.
- Sin hilo no hay estiramiento: el error de parada es de unas décimas de milímetro, el juego de los dientes (0,11 mm de holgura entre flancos).
- El cero lo da la barrera infrarroja con una aleta del propio carro (u = 2 mm).
- Todo se imprime sin soportes: los brazos y la placa del motor salen verticales desde la cama, igual que las patas.

## Revisado en el modelo

- Cero choques del carro, el motor y el piñón con la torre, el cartucho y el vaso de rechazo en todo el recorrido (u de 0 a 774 mm).
- Siete piezas con 0 voladizos de más de 44°, 0 islas y un solo cuerpo; holgura libre hasta 2 mm de margen.
- Masa total 278 g (PETG 73 g, PLA+ 205 g).
- Por confirmar con la pieza real: los valles de 1 mm de los dientes dependen de la impresora (por eso `prueba-engrane/`), el motor queda en voladizo (unos 280 g a 58 mm, parte del peso la lleva la cremallera) y entre el motor y la torre quedan 2 a 3 mm. Las medidas del NEMA17 usado en el modelo (cara 42,3 mm, cuerpo de 48 mm, boca de Ø22, eje de Ø5 con plano de 24 mm) hay que contrastarlas con el motor real.

## Lo aprendido con la v5

- El agarre del hilo en el tambor no es el problema: con 3 vueltas basta una tensión de 3 a 4,5 N aunque el hilo sea liso.
- Lo que limita es el estiramiento. El carro se queda corto al parar según la fricción por la elasticidad del hilo: con hilo de coser de un cabo hasta 8 mm, con caña trenzada de pescar unos 0,3 mm (simulación en `v5-riel/generador/sim_hilo.py`; las rigideces son valores típicos, no medidos).
- Eso llevó a la cremallera: el error baja a unas décimas de mm, a cambio de unos 10 g más en el riel y de llevar el motor y su cable sobre el carro.

## Orden de impresión recomendado

1. `v6-cremallera/prueba-engrane/`: un trozo de riel de 16 dientes (unos 18 g) y el piñón. Si el piñón rueda suave sobre la cremallera, la parte más delicada está resuelta.
2. `v6-cremallera/camas/cama-1_PETG_carro-y-pinon.stl`: carro y piñón; comprobar el encaje del motor.
3. `cama-2` y `cama-3` (PLA+): los cinco tramos de riel. Antes puede usarse `v6-cremallera/prueba-ajuste/` para el juego de 0,5 mm entre carro y riel.

## Contenido

Cada versión trae sus STL en posición de impresión (`stl/`), las camas acomodadas para la K1C (`camas/`) y el generador en Python (`generador/`, requiere `manifold3d` y `numpy`). En v6: `cd v6-cremallera/generador && python exportar_v6.py salida/`; las comprobaciones son `choques_v6.py`, `holguras_v6.py`, `revisar_v6.py` y `masa_v6.py`.
