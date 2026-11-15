# Prueba de ajuste del carro sobre el riel (unos 30 g)

Las zonas de agarre del carro y el perfil del riel son los mismos que en la v5, así que esta prueba sirve igual:

- `prueba-1_carro-rebanada.stl`: una rebanada de 36 mm del carro con una zona de agarre. PETG.
- `prueba-2_rieles-con-union.stl`: dos trozos de riel con la lengüeta y la ranura de unión. PLA+. Sin soportes.

La rebanada se pone sobre el riel por un extremo y debe deslizar con un empujón de dedo, sin sacudidas. La lengüeta debe entrar a presión en la ranura. Si traba, sube `CL` (juego carro-riel, hoy 0,5 mm) en `generador/generar_v5.py` a 0,6; si queda floja, bájalo a 0,4.
