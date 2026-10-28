# Banda transportadora (etapa 2): camas de impresión (versión print-and-place)

Para la torre de la etapa 1 v5. Impresora: Creality K1C, cama 220 × 220 × 250. Sin rodamientos, tornillos, tuercas ni correa. Son **46 piezas** en vez de unas 460: la cadena sale en 12 secciones ya articuladas, el bastidor en 6 módulos grandes con rompecabezas, las clavijas y los pasadores sueltos desaparecieron (van fundidos en la pieza) y no hay piezas de menos de 18 mm salvo las 2 ruedas, el acople y los tornillos.

Archivos: `stl/` tiene cada pieza en su posición de impresión; `camas/` tiene cada cama ya acomodada en un solo STL. Si prefieres acomodar tú, usa `stl/`.

## Ajustes

- Capa 0,2 mm, boquilla 0,4, **sin soportes en ninguna pieza**. Paredes y relleno por pieza en las tablas.
- Compensación de agujeros: ninguna. Las holguras ya están en el modelo (0,3 mm por lado en las articulaciones de la cadena).
- Desactiva el «elephant foot» compensation si tu perfil lo trae muy alto: en la cadena las primeras capas deben quedar libres de rebaba.
- Piezas largas (módulos de 192–204 mm): usa borde (brim) de 3 mm y limpia la cama; son las que más se curvan.

## Filamentos (inventario del 2026-10-28)

| Filamento | Para qué | Gramos necesarios | Hay | Sobra | Temp. |
|---|---|---|---|---|---|
| PETG Azul 4DLAB | Módulo del motor, tapa del motor, ejes, ruedas, acople, soporte NEMA, carros y tornillos del tensor | 212 g | 429 g | 217 g | 230–250 °C |
| PLA+ Mármol 4DLAB | Módulos 2 a 6, tapa del tensor y patas | 435 g | 1000 g | 565 g | 200–230 °C |
| PLA+ Azul 4DLAB | Las 12 secciones de cadena y la cama 00 de prueba | 685 g | 1000 g | 315 g | 200–230 °C |
| PLA+ Negro 4DLAB | Guías laterales (10) | 175 g | 647 g | 472 g | 200–230 °C |

- El PETG (429 g) sólo va a lo que gira o está junto al motor. La cadena va en PLA+ Azul porque necesita ≈ 640 g; el bastidor y las guías van en PLA+ porque no trabajan en caliente ni a flexión.
- Los gramos son una estimación por exceso (el relleno real de 15 % pesa menos).
- Si la presilla de la cadena se parte en la prueba (cama 00), reimprime sólo el primer eslabón de cada sección en PETG o baja la velocidad de las paredes a 60 mm/s y sube 5 °C.

## Orden de impresión

1. **Cama 00 (prueba, ≈ 25 min).** Dobla los dos tramos de eslabones: deben girar libres sin holgura exagerada. Encaja un tramo en el otro por la presilla del primer eslabón: tiene que entrar con un clic y no salirse al jalar. Mete la clavija en el zócalo y el eje en el agujero grande. **Si algo falla, dime la medida y lo corrijo antes de gastar filamento.**
2. Camas 02 a 05, la cadena (PLA+ Azul): 4 camas de 3 secciones. Es lo que más tarda (≈ 4 h por cama), pero ya no hay que armar nada suelto.
3. Cama 01, PETG Azul (ejes, ruedas, carros, tornillos, acople, soporte y módulo del motor).
4. Camas 06 a 08 (módulos, tapa y patas, PLA+ Mármol) y 09 (guías, PLA+ Negro).

## Armado

1. **Bastidor:** une los 6 módulos deslizándolos de arriba hacia abajo por los rompecabezas (cola de milano), con una gota de cianoacrilato en cada junta. Pega las 6 patas (clavijas integradas) en los zócalos de la pared +Y.
2. **Soporte del motor** al módulo 1; pega la tapa del motor y la del tensor con sus lengüetas.
3. **Cadena:** une las 12 secciones sobre la mesa encajando la presilla (primer eslabón) en el último pasador de la sección anterior; la 12 cierra con la 1 y queda un anillo de 168 eslabones. Con las tapas y las guías quitadas, mete el anillo por el costado −Y alrededor de las dos ruedas.
4. Ejes y ruedas en su sitio, carros del tensor en las ranuras y tornillos hasta que la cadena quede tensa pero giren libres a mano.
5. Pon las guías y las tapas. Antes de quitar una tapa, afloja el tensor por completo.

## Camas

### Cama 00 · PLA+ Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT00_prueba-tolerancias.stl` | Prueba de tolerancias | 1 | 100 % | 100 × 136 × 14 | 44 |

- Dos tramos de 3 eslabones, uno con la presilla; un bloque con agujero de eje, zócalo de clavija y una clavija en gota.
- Peso aproximado de la cama: 44 g.

### Cama 01 · PETG Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT01_modulo-1-motor.stl` | Módulo 1 (motor) | 1 | 15 %, 3 paredes | 192 × 84 × 30 | 70 |
| `BT11_eje-motriz.stl` | Eje motriz | 1 | 100 % | 12 × 97 × 10 | 9 |
| `BT12_eje-libre.stl` | Eje libre | 1 | 100 % | 12 × 95 × 10 | 10 |
| `BT07_tapa-motor.stl` | Tapa lateral del motor (−Y) | 1 | 20 %, 3 paredes | 75 × 34 × 11 | 13 |
| `BT15_soporte-nema17.stl` | Soporte del NEMA17 | 1 | 30 %, 4 paredes | 50 × 49 × 92 | 65 |
| `BT17_rueda-dentada.stl` | Rueda dentada de 8 dientes | 2 | 100 % | 34 × 34 × 8 | 15 |
| `BT14_tornillo-tensor.stl` | Tornillo del tensor | 2 | 100 % | 22 × 22 × 58 | 12 |
| `BT16_acople.stl` | Acople hexágono + D | 1 | 100 % | 19 × 19 × 26 | 8 |
| `BT13P_carro-tensor-mas-Y.stl` | Carro del tensor +Y | 1 | 40 %, 4 paredes | 18 × 12 × 50 | 5 |
| `BT13M_carro-tensor-menos-Y.stl` | Carro del tensor −Y | 1 | 40 %, 4 paredes | 18 × 12 × 50 | 5 |

- Acostada sobre la cara interior.
- De pie sobre el extremo de la rosca; la cabeza queda arriba.
- De pie sobre la cola roscada. Sin soportes.
- La base contra la cama; la jaula se cierra en cono. Sin soportes.
- Piso contra la cama. Sin soportes.
- Plana. La motriz y la libre son iguales.
- Sin soportes.
- Tumbado (las capas corren a lo largo del eje). Borde (brim) de 5 mm. Es lo único redondo apoyado en una línea: el arco de abajo es chico y sale limpio.
- Tumbado, igual que el motriz.
- Peso aproximado de la cama: 212 g.

### Cama 02 · PLA+ Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT19_seccion-cadena.stl` | Sección de cadena (14 eslabones articulados) | 3 | 100 % | 179 × 56 × 6 | 160 |

- Print-in-place: sale ya articulada. Tapa lisa contra la cama.
- Peso aproximado de la cama: 160 g.

### Cama 03 · PLA+ Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT19_seccion-cadena.stl` | Sección de cadena (14 eslabones articulados) | 3 | 100 % | 179 × 56 × 6 | 160 |

- Print-in-place: sale ya articulada. Tapa lisa contra la cama.
- Peso aproximado de la cama: 160 g.

### Cama 04 · PLA+ Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT19_seccion-cadena.stl` | Sección de cadena (14 eslabones articulados) | 3 | 100 % | 179 × 56 × 6 | 160 |

- Print-in-place: sale ya articulada. Tapa lisa contra la cama.
- Peso aproximado de la cama: 160 g.

### Cama 05 · PLA+ Azul 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT19_seccion-cadena.stl` | Sección de cadena (14 eslabones articulados) | 3 | 100 % | 179 × 56 × 6 | 160 |

- Print-in-place: sale ya articulada. Tapa lisa contra la cama.
- Peso aproximado de la cama: 160 g.

### Cama 06 · PLA+ Mármol 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT04_modulo-4.stl` | Módulo 4 | 1 | 15 %, 3 paredes | 204 × 81 × 30 | 78 |
| `BT02_modulo-2.stl` | Módulo 2 | 1 | 15 %, 3 paredes | 204 × 81 × 30 | 78 |
| `BT08_tapa-tensor.stl` | Tapa lateral del tensor (−Y) | 1 | 20 %, 3 paredes | 115 × 30 × 19 | 13 |
| `BT18_pata.stl` | Pata | 1 | 20 %, 3 paredes | 92 × 20 × 44 | 10 |

- Acostada sobre la cara interior.
- Acostada. Las clavijas en gota quedan horizontales y salen sin soportes.
- Piso contra la cama. Sin soportes.
- Peso aproximado de la cama: 179 g.

### Cama 07 · PLA+ Mármol 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT03_modulo-3.stl` | Módulo 3 (bajo la torre) | 1 | 15 %, 3 paredes | 204 × 81 × 30 | 78 |
| `BT05_modulo-5.stl` | Módulo 5 | 1 | 15 %, 3 paredes | 204 × 81 × 30 | 78 |
| `BT18_pata.stl` | Pata | 2 | 20 %, 3 paredes | 92 × 20 × 44 | 19 |

- Acostada. Las clavijas en gota quedan horizontales y salen sin soportes.
- Piso contra la cama. Sin soportes.
- Peso aproximado de la cama: 176 g.

### Cama 08 · PLA+ Mármol 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT06_modulo-6-tensor.stl` | Módulo 6 (tensor) | 1 | 15 %, 3 paredes | 192 × 92 × 30 | 52 |
| `BT18_pata.stl` | Pata | 3 | 20 %, 3 paredes | 20 × 92 × 44 | 29 |

- Acostada. Las clavijas en gota quedan horizontales y salen sin soportes.
- Piso contra la cama. Sin soportes.
- Peso aproximado de la cama: 80 g.

### Cama 09 · PLA+ Negro 4DLAB

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `BT09G2_guia-menos-Y.stl` | Guía −Y, tramos 2 a 5 | 4 | 15 %, 3 paredes | 191 × 12 × 18 | 71 |
| `BT10G2_guia-mas-Y.stl` | Guía +Y, tramos 2 a 5 | 4 | 15 %, 3 paredes | 191 × 12 × 18 | 71 |
| `BT09G1_guia-menos-Y-tramo1.stl` | Guía −Y, tramo 1 (hueco del fototransistor) | 1 | 15 %, 3 paredes | 173 × 12 × 18 | 16 |
| `BT10G1_guia-mas-Y-tramo1.stl` | Guía +Y, tramo 1 (hueco del LED) | 1 | 15 %, 3 paredes | 173 × 12 × 18 | 16 |

- Ala abajo, labio arriba.
- Peso aproximado de la cama: 175 g.

Total aproximado: **1507 g** en 10 camas.

## Cantidades

| Pieza | Cant. | Filamento |
|---|---|---|
| `BT01_modulo-1-motor.stl` | 1 | PETG Azul 4DLAB |
| `BT02_modulo-2.stl` | 1 | PLA+ Mármol 4DLAB |
| `BT03_modulo-3.stl` | 1 | PLA+ Mármol 4DLAB |
| `BT04_modulo-4.stl` | 1 | PLA+ Mármol 4DLAB |
| `BT05_modulo-5.stl` | 1 | PLA+ Mármol 4DLAB |
| `BT06_modulo-6-tensor.stl` | 1 | PLA+ Mármol 4DLAB |
| `BT07_tapa-motor.stl` | 1 | PETG Azul 4DLAB |
| `BT08_tapa-tensor.stl` | 1 | PLA+ Mármol 4DLAB |
| `BT09G1_guia-menos-Y-tramo1.stl` | 1 | PLA+ Negro 4DLAB |
| `BT09G2_guia-menos-Y.stl` | 4 | PLA+ Negro 4DLAB |
| `BT10G1_guia-mas-Y-tramo1.stl` | 1 | PLA+ Negro 4DLAB |
| `BT10G2_guia-mas-Y.stl` | 4 | PLA+ Negro 4DLAB |
| `BT11_eje-motriz.stl` | 1 | PETG Azul 4DLAB |
| `BT12_eje-libre.stl` | 1 | PETG Azul 4DLAB |
| `BT13P_carro-tensor-mas-Y.stl` | 1 | PETG Azul 4DLAB |
| `BT13M_carro-tensor-menos-Y.stl` | 1 | PETG Azul 4DLAB |
| `BT14_tornillo-tensor.stl` | 2 | PETG Azul 4DLAB |
| `BT15_soporte-nema17.stl` | 1 | PETG Azul 4DLAB |
| `BT16_acople.stl` | 1 | PETG Azul 4DLAB |
| `BT17_rueda-dentada.stl` | 2 | PETG Azul 4DLAB |
| `BT18_pata.stl` | 6 | PLA+ Mármol 4DLAB |
| `BT19_seccion-cadena.stl` | 12 | PLA+ Azul 4DLAB |

## Qué se hizo contra los fallos

- **Voladizos:** ninguna cara pasa de 45°. Los agujeros horizontales son en gota o rombo, las clavijas en gota, el cubo del eje es octogonal y la ranura del tensor está abierta por abajo. Un análisis automático de las caras que miran hacia abajo, con cada pieza en su posición, deja sólo puentes cortos (≤ 8 mm, como los zócalos de clavija) y el arco de los primeros 0,8 mm de los nudillos de la cadena, que apoyan en la cama.
- **Cadena print-in-place:** juego de 0,3 mm por lado (agujero Ø3,6 sobre pasador Ø3); si en la cama 00 queda dura, se corrige con un número. El pasador es una gota para que no tenga voladizo al imprimirse acostado.
- **Pocas piezas pequeñas:** las clavijas Ø6 se integraron en guías y patas; los pasadores Ø3 son parte de cada eslabón; el rompecabezas de los módulos sustituye a todas las clavijas de unión del bastidor.
- **Riesgos que quedan:** (1) la tolerancia de la articulación (por eso la cama 00 primero); (2) la presilla de la sección, de PLA, puede ser frágil; (3) el juego de 168 articulaciones alarga la cadena, por eso el tensor tiene 24 mm de recorrido; (4) el torque de un NEMA17 de 48 mm con el radio de la rueda de ≈ 0,3 N·m es justo para la carga de monedas: si patina, baja la tensión.
