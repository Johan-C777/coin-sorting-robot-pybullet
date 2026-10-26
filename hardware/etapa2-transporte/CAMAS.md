# Banda transportadora (etapa 2): camas de impresión

Para la torre de la etapa 1 v5. Impresora: Creality K1C, cama 220 × 220 × 250. Sin tornillos, tuercas ni rodamientos: todo se une con clavijas Ø6 × 12, muñones y un tornillo impreso.

Archivos: `stl/` tiene cada pieza en su posición de impresión; `camas/` tiene cada cama ya acomodada en un solo STL. Si prefieres acomodar tú, usa `stl/`.

## Ajustes

- Boquilla 0,4, capa 0,2 mm, 3 paredes y 20 % de relleno salvo que la tabla diga otra cosa (lo que carga o gira lleva 4 paredes y más relleno).
- PETG para lo estructural y lo que gira, PLA para las guías. Sin soportes salvo donde se indica.
- Compensación de agujeros: ninguna. Las holguras ya están en el modelo (muñón 10 en 10,4; clavija 6 en 6,2; rosca con 0,35 mm).
- Las estimaciones de peso son aproximadas (relleno y paredes cambian el resultado).

## Orden

1. **Cama 00, prueba de tolerancias.** Mete el muñón en el agujero de 10,4, una clavija en el de 6,2 y atornilla la rosca en el bloque. Si algo queda flojo o no entra, dime la medida y lo corrijo antes de imprimir lo demás.
2. Camas de PETG en el orden de abajo (primero las clavijas, que se necesitan para armar).
3. Cama de guías en PLA al final.

## Camas

### Cama 00 · PETG

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT00_prueba-tolerancias.stl` | Prueba de tolerancias | 1 | 100 % | 60 × 40 × 24 | 29 |

- Muñón en agujero de 10,4, clavija en 6,2 y rosca con 0,35 mm de juego. Imprímela primero.
- Peso aproximado de la cama: 29 g.

### Cama 01 · PETG

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT03_modulo-3.stl` | Módulo 3 (bajo la torre) | 1 | 20 % | 165 × 94 × 30 | 70 |
| `BT04_modulo-4.stl` | Módulo 4 | 1 | 20 % | 165 × 94 × 30 | 71 |
| `BT14_tapa-tensor.stl` | Tapa tensor (−Y) | 1 | 20 % | 30 × 93 × 19 | 8 |
| `BT16_pata.stl` | Pata | 1 | 20 % | 20 × 92 × 48 | 10 |

- Cama abajo.
- Cara interior abajo, oreja hacia arriba.
- Como está: el zócalo plano en la cama y la placa de pie.
- Peso aproximado de la cama: 159 g.

### Cama 02 · PETG

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT05_modulo-5.stl` | Módulo 5 | 1 | 20 % | 165 × 94 × 30 | 69 |
| `BT01_modulo-motor.stl` | Módulo del motor | 1 | 20 % | 158 × 94 × 34 | 59 |
| `BT16_pata.stl` | Pata | 3 | 20 % | 20 × 92 × 48 | 29 |

- Cama abajo.
- Cama de la banda abajo. El cubo del muñón sale de la pared: hay un voladizo corto bajo el cubo.
- Como está: el zócalo plano en la cama y la placa de pie.
- Peso aproximado de la cama: 156 g.

### Cama 03 · PETG

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT02_modulo-2.stl` | Módulo 2 | 1 | 20 % | 155 × 94 × 30 | 68 |
| `BT07_modulo-tensor.stl` | Módulo del tensor | 1 | 20 % | 130 × 100 × 30 | 44 |
| `BT16_pata.stl` | Pata | 3 | 20 % | 20 × 92 × 48 | 29 |
| `BT13_tapa-motor.stl` | Tapa motor (−Y) | 1 | 20 % | 34 × 81 × 11 | 13 |
| `BT12P_carro-tensor-mas-Y.stl` | Carro del tensor +Y | 1 | 40 %, 4 paredes | 36 × 18 × 12 | 4 |

- Cama abajo.
- Cama abajo. La oreja del tornillo queda hacia arriba.
- Cara interior abajo, cubo del muñón hacia arriba.
- Como está: el zócalo plano en la cama y la placa de pie.
- Plano, con el agujero del muñón hacia arriba.
- Peso aproximado de la cama: 158 g.

### Cama 04 · PETG

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT06_modulo-6.stl` | Módulo 6 | 1 | 20 % | 120 × 94 × 30 | 50 |
| `BT15_soporte-nema17.stl` | Soporte del NEMA17 | 1 | 30 %, 4 paredes | 50 × 49 × 84 | 35 |
| `BT12M_carro-tensor-menos-Y.stl` | Carro del tensor −Y | 1 | 40 %, 4 paredes | 36 × 18 × 12 | 4 |
| `BT11_rodillo-libre.stl` | Rodillo libre | 1 | 40 %, 4 paredes | 31 × 31 × 95 | 21 |
| `BT10_rodillo-motriz.stl` | Rodillo motriz | 1 | 40 %, 4 paredes | 31 × 31 × 97 | 20 |

- Boca de la bolsa hacia la cama. Puente de 43 mm sobre la bolsa: soporte de árbol sólo bajo la placa.
- Cama abajo.
- De pie sobre el muñón corto. Soportes de árbol sólo bajo el disco de la base.
- De pie sobre el muñón corto. Soportes de árbol sólo bajo el disco de la base. Las estrías de agarre quedan en la pared del cilindro.
- Plano, con el agujero del muñón hacia arriba.
- Peso aproximado de la cama: 130 g.

### Cama 05 · PETG

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT18_tornillo-tensor.stl` | Tornillo del tensor | 2 | 100 % | 22 × 22 × 36 | 10 |
| `BT19_acople.stl` | Acople hexágono + D | 1 | 100 % | 19 × 19 × 26 | 8 |
| `BT17_clavija-6x12.stl` | Clavija Ø6 × 12 (P02) | 72 | 100 % | 6 × 6 × 12 | 31 |

- Cabeza abajo. La rosca no necesita soportes.
- De pie sobre la boca hexagonal.
- De pie. Imprime todas juntas; 64 + 8 de repuesto.
- Peso aproximado de la cama: 49 g.

### Cama 06 · PLA

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT08G2_guia-menos-Y.stl` | Guía −Y, tramos 2 a 5 | 4 | 20 % | 191 × 12 × 8 | 45 |
| `BT09G2_guia-mas-Y.stl` | Guía +Y, tramos 2 a 5 | 4 | 20 % | 191 × 12 × 8 | 45 |
| `BT08G1_guia-menos-Y-tramo1.stl` | Guía −Y, tramo 1 (con el hueco del fototransistor) | 1 | 20 % | 173 × 12 × 8 | 10 |
| `BT09G1_guia-mas-Y-tramo1.stl` | Guía +Y, tramo 1 (con el hueco del LED) | 1 | 20 % | 173 × 12 × 8 | 10 |

- Ala abajo, labio hacia arriba.
- Peso aproximado de la cama: 110 g.

Total aproximado: **791 g** en 7 camas.

## Cantidades que hay que imprimir

| Pieza | Cant. | Material |
|---|---|---|
| `BT01_modulo-motor.stl` | 1 | PETG |
| `BT02_modulo-2.stl` | 1 | PETG |
| `BT03_modulo-3.stl` | 1 | PETG |
| `BT04_modulo-4.stl` | 1 | PETG |
| `BT05_modulo-5.stl` | 1 | PETG |
| `BT06_modulo-6.stl` | 1 | PETG |
| `BT07_modulo-tensor.stl` | 1 | PETG |
| `BT08G1_guia-menos-Y-tramo1.stl` | 1 | PLA |
| `BT08G2_guia-menos-Y.stl` | 4 | PLA |
| `BT09G1_guia-mas-Y-tramo1.stl` | 1 | PLA |
| `BT09G2_guia-mas-Y.stl` | 4 | PLA |
| `BT10_rodillo-motriz.stl` | 1 | PETG |
| `BT11_rodillo-libre.stl` | 1 | PETG |
| `BT12P_carro-tensor-mas-Y.stl` | 1 | PETG |
| `BT12M_carro-tensor-menos-Y.stl` | 1 | PETG |
| `BT13_tapa-motor.stl` | 1 | PETG |
| `BT14_tapa-tensor.stl` | 1 | PETG |
| `BT15_soporte-nema17.stl` | 1 | PETG |
| `BT16_pata.stl` | 7 | PETG |
| `BT17_clavija-6x12.stl` | 72 | PETG |
| `BT18_tornillo-tensor.stl` | 2 | PETG |
| `BT19_acople.stl` | 1 | PETG |

## Cosas a vigilar al imprimir

- **Rodillos:** quedan con el eje vertical para que giren redondos, pero así las capas cruzan el muñón. Imprímelos con 4 paredes y mira que el muñón no tenga huecos. Si uno se parte, avísame y lo paso a otra orientación.
- **Muñones:** una gota de grasa de silicona en los agujeros al armar. Si aparece juego, se reimprime el rodillo.
- **Clavijas de módulos, patas y soporte del motor:** se pegan con cianoacrilato. Las de guías y tapas no, porque se sacan para meter la cinta.
- **Bolsa del motor:** el NEMA17 entra por atrás con un poco de fuerza. Si queda flojo, una gota de cianoacrilato en las esquinas.
