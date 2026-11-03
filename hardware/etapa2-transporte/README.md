# Etapa 2: transporte (banda transportadora)

**Estado:** STL generados, sin imprimir. Empieza por la cama 00 (prueba de tolerancias) de `CAMAS.md`.

Una banda de cadena de tablillas de 1 m bajo la torre de la etapa 1 v5. Desliza el cartucho de 9 vasos (C02 + 3 C01 + 9 V01) para poner el vaso pedido bajo el hueco del embudo o la rampa de rechazo. Un NEMA17 con A4988 la mueve en lazo abierto y una barrera infrarroja da el cero.

Versión **print-and-place**: 46 piezas en 10 camas, sin soportes. La cadena (168 eslabones de 12,3 × 56 × 6 mm, 8 dientes) sale en 12 secciones de 14 eslabones ya articuladas de la impresora y se enlazan a presión; el bastidor son 6 módulos grandes con uniones de rompecabezas y las clavijas están fundidas en las piezas. Sin correa, rodamientos, tornillos ni tuercas.

Se compra: NEMA17 de 48 mm, A4988, LED infrarrojo y fototransistor. Todo lo demás se imprime (≈ 1,5 kg: PETG para lo que gira y el motor, PLA+ para cadena, bastidor y guías; ver CAMAS.md).

| Dato | Valor |
|---|---|
| Marco | X a lo largo de la banda (embudo en X = 0), Y a lo ancho, Z arriba (Z = 0 en la mesa) |
| Fondo del cartucho | 50 mm sobre la mesa |
| Carrera | 774 mm: cero = vaso 9 bajo el embudo; rechazo a 342 mm; vaso 1 en el punto A (X = 470) a 774 mm |
| Resolución | 3.200 micropasos por vuelta de rueda (98,4 mm de cadena), ≈ 32,5 por mm |
| Pines (ESP32-S3) | STEP 10, DIR 11, EN 12, barrera de referencia 13 |
| Pendiente | prueba de la articulación y de la presilla (cama 00); torque (≈ 0,3 N·m estimado) y rozamientos reales; con el vaso 1 en A el cartucho sobresale ≈ 139 mm del último eje; lado del brazo |

Contenido: `CAMAS.md` (camas, ajustes y armado), `stl/` (cada pieza en posición de impresión), `camas/` (cada cama acomodada), `ensamble-etapa2.html` (visor), `generador/` (`generar_banda.py`, `camas.py` y `analisis.py` de voladizos; requieren `manifold3d` y `numpy`).

Para regenerar: `cd generador && python camas.py salida/`.
