# Etapa 2: transporte (banda transportadora)

**Estado:** en diseño. Aquí van los STL, la lista de materiales y el visor de la banda cuando se aprueben.

Restricciones que deja la etapa 1 (salen de `scripts/generar_clasificador.py`):

| Dato | Valor |
|---|---|
| Hueco libre bajo la lámina | 123 mm de ancho × 490 mm de largo, más 40 mm a la derecha para el motor |
| Altura disponible | 70 mm bajo la cara superior de la banda para motor, rodillos y electrónica |
| Vasos | 9, de Ø34 × 60 mm, uno por tipo de moneda, con la boca 6 mm bajo su tubo |
| Salidas de los tubos (X, mm) | 42,4 · 79,3 · 116,1 · 153,0 · 211,6 · 246,5 · 283,3 · 318,3 · 357,7 |
| Pines reservados en el ESP32 del contador | banda en 14 / 4 / 23 (L298N) |

Al final de la banda queda el punto A, en el límite del alcance del brazo (etapa 3).
