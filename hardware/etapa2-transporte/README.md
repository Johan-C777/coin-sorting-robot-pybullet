# Etapa 2: transporte (banda transportadora)

**Estado:** STL generados, sin imprimir. Empieza por la cama 00 (prueba de tolerancias) de `CAMAS.md`.

Una banda de 1 m bajo la torre de la etapa 1 v5. Desliza el cartucho de 9 vasos (C02 + 3 C01 + 9 V01) para poner el vaso pedido bajo el hueco del embudo o la rampa de rechazo. Un NEMA17 con A4988 la mueve en lazo abierto y una barrera infrarroja da el cero. No lleva rodamientos, tornillos ni tuercas: muñones impresos, clavijas Ø6 × 12 (la P02 de la etapa 1), tornillo de tensor impreso y bolsa impresa para el motor.

Se compra: cinta de PU de 56 × 1,5 mm (corte de 2.085 mm), NEMA17, A4988, LED infrarrojo y fototransistor.

| Dato | Valor |
|---|---|
| Marco | X a lo largo de la banda (embudo en X = 0), Y a lo ancho, Z arriba (Z = 0 en la mesa) |
| Fondo del cartucho | 50 mm sobre la mesa |
| Carrera | 774 mm: cero = vaso 9 bajo el embudo; rechazo a 342 mm; vaso 1 en el punto A (X = 470) a 774 mm |
| Resolución | 3.200 micropasos por vuelta del rodillo, 31,5 por mm |
| Pines propuestos | STEP 14, DIR 4, EN 23 (reservados por la etapa 1), barrera de referencia GPIO 5 (por confirmar) |
| Pendiente | con el vaso 1 en A el cartucho sobresale ≈ 139 mm del último rodillo; lado del brazo; torque y rozamientos reales |

Contenido: `CAMAS.md` (camas y ajustes), `stl/` (cada pieza en posición de impresión), `camas/` (cada cama acomodada), `generador/` (`generar_banda.py` y `camas.py`, requieren `manifold3d` y `numpy`).

Para regenerar: `python generador/camas.py salida/`.
