# Banda transportadora (etapa 2): camas de impresión

Para la torre de la etapa 1 v5. Impresora: Creality K1C, cama 220 × 220 × 250. Sin tornillos, tuercas, rodamientos ni correa: la banda es una cadena de tablillas impresa; todo se une con clavijas Ø6 × 12, muñones, pasadores Ø3 y un tornillo impreso.

Archivos: `stl/` tiene cada pieza en su posición de impresión; `camas/` tiene cada cama ya acomodada en un solo STL. Si prefieres acomodar tú, usa `stl/`.

## Ajustes

- Capa 0,2 mm, 3 paredes y 20 % de relleno salvo que la tabla diga otra cosa (lo que carga o gira lleva 4 paredes y más relleno).
- Boquilla 0,4. Temperaturas según el filamento (tabla de abajo). Sin soportes salvo donde se indica.
- Compensación de agujeros: ninguna. Las holguras ya están en el modelo.

## Filamentos (inventario del 2026-10-28)

| Filamento | Para qué | Gramos necesarios | Hay | Sobra | Temp. |
|---|---|---|---|---|---|
| PETG Azul 4DLAB | Pasadores, clavijas, ejes, ruedas, tensor, carros, acople, soporte y módulo del motor, tapa del motor (lo que gira, se desgasta o está junto al motor) | 301 g | 429 g | 128 g | 230–250 °C |
| PLA+ Mármol 4DLAB | Módulos 2 a 7, tapa del tensor y patas (bastidor) | 439 g | 1000 g | 561 g | 200–230 °C |
| PLA+ Azul 4DLAB | Las 176 tablillas de la cadena (y la cama 00 de prueba) | 607 g | 1000 g | 393 g | 200–230 °C |
| PLA+ Negro 4DLAB | Guías laterales | 163 g | 647 g | 484 g | 200–230 °C |

- No se usan: PLA+ Verde, Rosado, Silk, Hyper PLA y los rollos casi agotados (sirven para pruebas); ABS Gris queda de reserva para el soporte del motor si el PETG se ablanda; TPU no hace falta.
- Por qué así: el PETG (429 g) no alcanza para todo, así que sólo va a lo que lo necesita (pasadores Ø3 que flexan, ejes y ruedas que giran, y lo que queda pegado al motor, que se calienta). Las tablillas van en PLA+ Azul: son 176 piezas y se necesitan ≈ 580 g. El bastidor y las guías van en PLA+ porque no trabajan en caliente ni a flexión.
- La cama 00 es una prueba dimensional: sale en PLA+ Azul con las tablillas; el pasador, el muñón y la clavija de la prueba luego se hacen en PETG y el juego es el mismo.

## Orden

1. **Cama 00, prueba de tolerancias** (PLA+ Azul). Mete el muñón en el agujero de 10,4, una clavija en el de 6,2, atornilla la rosca en el bloque y dobla las dos tablillas unidas: deben girar libres. Si algo queda flojo o no entra, dime la medida y lo corrijo antes de imprimir lo demás.
2. Camas de PETG Azul (primero pasadores y clavijas, que se necesitan para armar).
3. Camas de tablillas en PLA+ Azul (176 en total; imprime 3 primero y prueba la articulación).
4. Camas de bastidor en PLA+ Mármol y guías en PLA+ Negro.

## Camas

### Cama 00 · PLA+ Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT00_prueba-tolerancias.stl` | Prueba de tolerancias | 1 | 100 % | 100 × 127 × 24 | 35 |

- Muñón en agujero de 10,4, clavija en 6,2, rosca con 0,35 mm de juego y dos tablillas unidas con su pasador (deben girar libres sin holgura exagerada). Imprímela primero.
- Peso aproximado de la cama: 35 g.

### Cama 01 · PETG Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT01_modulo-motor.stl` | Módulo del motor | 1 | 20 % | 158 × 94 × 34 | 59 |
| `BT10_eje-motriz.stl` | Eje motriz con espiga hexagonal | 1 | 100 % | 12 × 97 × 10 | 9 |
| `BT11_eje-libre.stl` | Eje libre | 1 | 100 % | 12 × 95 × 10 | 10 |
| `BT13_tapa-motor.stl` | Tapa motor (−Y) | 1 | 20 % | 81 × 34 × 11 | 13 |
| `BT12P_carro-tensor-mas-Y.stl` | Carro del tensor +Y | 1 | 40 %, 4 paredes | 50 × 18 × 12 | 5 |
| `BT12M_carro-tensor-menos-Y.stl` | Carro del tensor −Y | 1 | 40 %, 4 paredes | 50 × 18 × 12 | 5 |
| `BT15_soporte-nema17.stl` | Soporte del NEMA17 | 1 | 30 %, 4 paredes | 50 × 49 × 92 | 38 |
| `BT20_rueda-dentada.stl` | Rueda dentada de 8 dientes | 2 | 100 % | 34 × 34 × 8 | 14 |

- Boca de la bolsa hacia la cama. Puente de 43 mm sobre la bolsa: soporte de árbol sólo bajo la placa.
- Cama de la banda abajo. El cubo del muñón sale de la pared: hay un voladizo corto bajo el cubo.
- Cara interior abajo, cubo del muñón hacia arriba.
- Plana, eje vertical. Imprime la motriz y la libre iguales.
- Plano, con el agujero del muñón hacia arriba.
- Tumbado, igual que el motriz.
- Tumbado: las capas corren a lo largo del eje, que es lo que más aguanta. Usa borde (brim) de 5 mm; el cilindro apoya en una línea.
- Peso aproximado de la cama: 154 g.

### Cama 02 · PETG Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT22_pasador-3x57.stl` | Pasador Ø3 × 57 | 90 | 100 % | 3 × 57 × 3 | 46 |
| `BT18_tornillo-tensor.stl` | Tornillo del tensor | 1 | 100 % | 22 × 22 × 52 | 6 |

- Cabeza abajo. La rosca no necesita soportes.
- Tumbado. 173 + repuestos. Si sale con rebabas, lijar suave; deben girar libres en la tablilla.
- Peso aproximado de la cama: 52 g.

### Cama 03 · PETG Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT22_pasador-3x57.stl` | Pasador Ø3 × 57 | 90 | 100 % | 3 × 57 × 3 | 46 |
| `BT18_tornillo-tensor.stl` | Tornillo del tensor | 1 | 100 % | 22 × 22 × 52 | 6 |

- Cabeza abajo. La rosca no necesita soportes.
- Tumbado. 173 + repuestos. Si sale con rebabas, lijar suave; deben girar libres en la tablilla.
- Peso aproximado de la cama: 52 g.

### Cama 04 · PETG Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT22_pasador-3x57.stl` | Pasador Ø3 × 57 | 8 | 100 % | 3 × 57 × 3 | 4 |
| `BT19_acople.stl` | Acople hexágono + D | 1 | 100 % | 19 × 19 × 26 | 8 |
| `BT17_clavija-6x12.stl` | Clavija Ø6 × 12 (P02) | 72 | 100 % | 6 × 6 × 12 | 31 |

- De pie sobre la boca hexagonal.
- De pie. Imprime todas juntas; 64 + 8 de repuesto.
- Tumbado. 173 + repuestos. Si sale con rebabas, lijar suave; deben girar libres en la tablilla.
- Peso aproximado de la cama: 43 g.

### Cama 05 · PLA+ Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT21_tablilla.stl` | Tablilla de la cadena | 30 | 100 % | 18 × 56 × 6 | 97 |

- Cara de arriba contra la cama (lisa, sin soportes). 173 hacen la cadena; 3 de repuesto. Imprime 3 primero y prueba la articulación.
- Peso aproximado de la cama: 97 g.

### Cama 06 · PLA+ Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT21_tablilla.stl` | Tablilla de la cadena | 30 | 100 % | 18 × 56 × 6 | 97 |

- Cara de arriba contra la cama (lisa, sin soportes). 173 hacen la cadena; 3 de repuesto. Imprime 3 primero y prueba la articulación.
- Peso aproximado de la cama: 97 g.

### Cama 07 · PLA+ Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT21_tablilla.stl` | Tablilla de la cadena | 30 | 100 % | 18 × 56 × 6 | 97 |

- Cara de arriba contra la cama (lisa, sin soportes). 173 hacen la cadena; 3 de repuesto. Imprime 3 primero y prueba la articulación.
- Peso aproximado de la cama: 97 g.

### Cama 08 · PLA+ Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT21_tablilla.stl` | Tablilla de la cadena | 30 | 100 % | 18 × 56 × 6 | 97 |

- Cara de arriba contra la cama (lisa, sin soportes). 173 hacen la cadena; 3 de repuesto. Imprime 3 primero y prueba la articulación.
- Peso aproximado de la cama: 97 g.

### Cama 09 · PLA+ Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT21_tablilla.stl` | Tablilla de la cadena | 30 | 100 % | 18 × 56 × 6 | 97 |

- Cara de arriba contra la cama (lisa, sin soportes). 173 hacen la cadena; 3 de repuesto. Imprime 3 primero y prueba la articulación.
- Peso aproximado de la cama: 97 g.

### Cama 10 · PLA+ Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT21_tablilla.stl` | Tablilla de la cadena | 26 | 100 % | 18 × 56 × 6 | 84 |

- Cara de arriba contra la cama (lisa, sin soportes). 173 hacen la cadena; 3 de repuesto. Imprime 3 primero y prueba la articulación.
- Peso aproximado de la cama: 84 g.

### Cama 11 · PLA+ Mármol 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT03_modulo-3.stl` | Módulo 3 (bajo la torre) | 1 | 20 % | 165 × 94 × 30 | 69 |
| `BT04_modulo-4.stl` | Módulo 4 | 1 | 20 % | 165 × 94 × 30 | 69 |
| `BT14_tapa-tensor.stl` | Tapa tensor (−Y) | 1 | 20 % | 30 × 115 × 19 | 10 |
| `BT16_pata.stl` | Pata | 1 | 20 % | 20 × 92 × 44 | 9 |

- Cama abajo.
- Cara interior abajo, oreja hacia arriba.
- Como está: el zócalo plano en la cama y la placa de pie.
- Peso aproximado de la cama: 157 g.

### Cama 12 · PLA+ Mármol 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT05_modulo-5.stl` | Módulo 5 | 1 | 20 % | 165 × 94 × 30 | 67 |
| `BT02_modulo-2.stl` | Módulo 2 | 1 | 20 % | 155 × 94 × 30 | 67 |
| `BT16_pata.stl` | Pata | 3 | 20 % | 20 × 92 × 44 | 27 |

- Cama abajo.
- Como está: el zócalo plano en la cama y la placa de pie.
- Peso aproximado de la cama: 161 g.

### Cama 13 · PLA+ Mármol 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT07_modulo-tensor.stl` | Módulo del tensor | 1 | 20 % | 152 × 100 × 30 | 46 |
| `BT06_modulo-6.stl` | Módulo 6 | 1 | 20 % | 120 × 94 × 30 | 49 |
| `BT16_pata.stl` | Pata | 3 | 20 % | 20 × 92 × 44 | 27 |

- Cama abajo.
- Cama abajo. La oreja del tornillo queda hacia arriba.
- Como está: el zócalo plano en la cama y la placa de pie.
- Peso aproximado de la cama: 122 g.

### Cama 14 · PLA+ Negro 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT08G2_guia-menos-Y.stl` | Guía −Y, tramos 2 a 5 | 4 | 20 % | 191 × 12 × 12 | 67 |
| `BT09G2_guia-mas-Y.stl` | Guía +Y, tramos 2 a 5 | 4 | 20 % | 191 × 12 × 12 | 67 |
| `BT08G1_guia-menos-Y-tramo1.stl` | Guía −Y, tramo 1 (con el hueco del fototransistor) | 1 | 20 % | 173 × 12 × 12 | 15 |
| `BT09G1_guia-mas-Y-tramo1.stl` | Guía +Y, tramo 1 (con el hueco del LED) | 1 | 20 % | 173 × 12 × 12 | 15 |

- Ala abajo, labio hacia arriba.
- Peso aproximado de la cama: 163 g.

Total aproximado: **1510 g** en 15 camas.

## Cantidades que hay que imprimir

| Pieza | Cant. | Filamento |
|---|---|---|
| `BT01_modulo-motor.stl` | 1 | PETG Azul 4DLAB |
| `BT02_modulo-2.stl` | 1 | PLA+ Mármol 4DLAB |
| `BT03_modulo-3.stl` | 1 | PLA+ Mármol 4DLAB |
| `BT04_modulo-4.stl` | 1 | PLA+ Mármol 4DLAB |
| `BT05_modulo-5.stl` | 1 | PLA+ Mármol 4DLAB |
| `BT06_modulo-6.stl` | 1 | PLA+ Mármol 4DLAB |
| `BT07_modulo-tensor.stl` | 1 | PLA+ Mármol 4DLAB |
| `BT08G1_guia-menos-Y-tramo1.stl` | 1 | PLA+ Negro 4DLAB |
| `BT08G2_guia-menos-Y.stl` | 4 | PLA+ Negro 4DLAB |
| `BT09G1_guia-mas-Y-tramo1.stl` | 1 | PLA+ Negro 4DLAB |
| `BT09G2_guia-mas-Y.stl` | 4 | PLA+ Negro 4DLAB |
| `BT10_eje-motriz.stl` | 1 | PETG Azul 4DLAB |
| `BT11_eje-libre.stl` | 1 | PETG Azul 4DLAB |
| `BT12P_carro-tensor-mas-Y.stl` | 1 | PETG Azul 4DLAB |
| `BT12M_carro-tensor-menos-Y.stl` | 1 | PETG Azul 4DLAB |
| `BT13_tapa-motor.stl` | 1 | PETG Azul 4DLAB |
| `BT14_tapa-tensor.stl` | 1 | PLA+ Mármol 4DLAB |
| `BT15_soporte-nema17.stl` | 1 | PETG Azul 4DLAB |
| `BT16_pata.stl` | 7 | PLA+ Mármol 4DLAB |
| `BT17_clavija-6x12.stl` | 72 | PETG Azul 4DLAB |
| `BT18_tornillo-tensor.stl` | 2 | PETG Azul 4DLAB |
| `BT19_acople.stl` | 1 | PETG Azul 4DLAB |
| `BT20_rueda-dentada.stl` | 2 | PETG Azul 4DLAB |
| `BT21_tablilla.stl` | 176 | PLA+ Azul 4DLAB |
| `BT22_pasador-3x57.stl` | 188 | PETG Azul 4DLAB |

## Cosas a vigilar al imprimir

- **Cadena:** son 176 tablillas y 188 pasadores; cada tablilla pesa unos 3 g. Imprime primero 3 tablillas con 2 pasadores (o la cama 00) y comprueba que giran libres. Si quedan duras, lima el agujero de pasador; si quedan flojas, avísame.
- **Armado de la cadena:** se une sobre la mesa y se cierra con el último pasador. Si al tensar sobra cadena (por el juego de las articulaciones), quita eslabones.
- **Ejes y ruedas:** los ejes se imprimen tumbados con borde; las ruedas planas. Una gota de grasa de silicona en los muñones al armar.
- **Clavijas de módulos, patas y soporte del motor:** se pegan con cianoacrilato. Las de guías y tapas no, porque se sacan para meter la cadena.
- **Bolsa del motor:** el NEMA17 entra por atrás con un poco de fuerza. Si queda flojo, una gota de cianoacrilato en las esquinas.
