# Prueba de ajuste (unos 30 g)

Para saber si el carro desliza en el riel antes de gastar filamento en el resto. Son 2 archivos:

- `prueba-1_carro-rebanada.stl`: una rebanada de 36 mm del carro, con una de las dos zonas de agarre. Imprímela con el filamento del carro (PETG).
- `prueba-2_rieles-con-union.stl`: dos trozos de riel (57 y 35 mm) con la lengüeta y la ranura de unión. Imprímelos con el filamento de los rieles. Sin soportes.

Qué mirar:
1. La rebanada se pone sobre el riel por un extremo y debe deslizar con un empujón de dedo, sin sacudidas.
2. La lengüeta del trozo largo debe entrar a presión en la ranura del corto.
3. Si traba, sube `CL` (juego carro-riel, hoy 0,5 mm) en `generador/generar_v5.py` a 0,6; si queda floja, bájalo a 0,4.
