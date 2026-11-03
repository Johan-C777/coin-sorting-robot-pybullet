# Etapa 2: transporte del cartucho

**Estado:** en rediseño. Nada está impreso todavía. Se exploraron tres mecanismos y hay una cuarta idea en estudio; las versiones anteriores se conservan porque documentan el proceso.

El cartucho de 9 vasos (C02 + 3 C01 + 9 V01) de la etapa 1 v5 debe recorrer 774 mm bajo la torre: el vaso 9 queda bajo el embudo en u = 0, el rechazo en u = 342 mm y el vaso 1 en el punto A en u = 774 mm. Un NEMA17 con A4988 lo mueve en lazo abierto y una barrera infrarroja da el cero. El requisito de diseño es imprimir casi todo, con el mínimo de material, sin soportes y sin comprar piezas.

## Versiones

| Versión | Mecanismo | Plástico | Compras | Por qué se dejó |
|---|---|---|---|---|
| [v3, cadena](v3-cadena/CAMAS.md) | Cadena de 168 eslabones impresos con bastidor de 6 módulos | ≈ 1,5 kg, 46 piezas | NEMA17, A4988, IR | Demasiado material y 168 articulaciones que atascan |
| [v4, varillas](v4-varillas/LEEME.md) | Carro sobre varillas de acero con hilo | ≈ 0,3 kg | Varillas de acero | Obliga a comprar piezas |
| [**v5, riel**](v5-riel/LEEME.md) | Un riel impreso por tramos, carro que lo abraza e hilo con 3 vueltas al tambor | ≈ 268 g | Solo el hilo | En duda: el hilo estira y limita la precisión |
| Idea B, cremallera | Dientes impresos en el riel, motor con piñón sobre el carro | ≈ 330 a 350 g (estimado) | Ninguna | En estudio, sin modelar |

Los visores de cada versión están en `docs/etapa2/`: [v5](../../docs/etapa2/v5-riel.html) (actual, con un boceto de la cremallera al final) y, en `docs/etapa2/proceso/`, [v3](../../docs/etapa2/proceso/v3-cadena.html) y [v4](../../docs/etapa2/proceso/v4-varillas.html).

## Lo aprendido con la v5

- El agarre del hilo en el tambor no es el problema: con 3 vueltas basta una tensión de 3 a 4,5 N aunque el hilo sea liso.
- Lo que limita es el estiramiento. El carro se queda corto al parar según la fricción por la elasticidad del hilo: con hilo de coser de un cabo hasta 8 mm, con caña trenzada de pescar unos 0,3 mm (simulación en `v5-riel/generador/sim_hilo.py`; las rigideces son valores típicos, no medidos).
- Antes de imprimir el resto, `v5-riel/prueba-ajuste/` trae una rebanada del carro y dos trozos de riel (unos 30 g) para comprobar el juego de 0,5 mm.
- La cremallera elimina el hilo: el error sería de unas décimas de mm, a cambio de 60 a 80 g más de dientes y de llevar el motor y su cable sobre el carro.

## Contenido

`v3-cadena/`, `v4-varillas/` y `v5-riel/` traen cada uno sus STL en posición de impresión (`stl/`), las camas acomodadas para la K1C (`camas/`) y el generador en Python (`generador/`, requiere `manifold3d` y `numpy`). En v5: `cd v5-riel/generador && python exportar_v5.py salida/`.
