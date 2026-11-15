# Prueba 1: engrane y unión de la barra (≈ 30 g)

`prueba-1_engrane-y-union.stl`, sin soportes: un trozo de barra de 16 dientes con la lengüeta de cola de milano (PLA+), **tres trozos con la ranura y juegos distintos** (PLA+) y un piñón (PETG).

| Trozo con ranura | Dientes | Juego de la ranura |
|---|---|---|
| El corto | 8 | 0,15 mm |
| El mediano | 10 | **0,25 mm (el de las piezas finales)** |
| El largo | 12 | 0,35 mm |

1. Mete la lengüeta en cada ranura deslizando de lado. Buscas la que entra con un empujón firme y no se sale sola ni baila.
2. Monta el piñón en el eje del motor (plano de la D hacia el plano del eje) y ruédalo a mano por los dientes: debe girar libre, sin saltar ni pegarse.
3. El resultado cambia un solo número: `juego` en `tramo_barra(j, juego=0.25)` de `generador/generar_v7.py`.
