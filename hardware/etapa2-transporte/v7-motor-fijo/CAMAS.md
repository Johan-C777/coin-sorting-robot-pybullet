# Etapa 2 v7 (motor fijo): camas de impresión

Impresora: Creality K1C, cama 220 × 220 × 250. **Sin soportes en ninguna pieza**, sin tornillos, rodamientos ni hilo. Son **13 piezas** en **4 camas** más las pruebas.

Archivos: `camas/` tiene cada cama ya acomodada en un solo STL; `stl/` tiene cada pieza suelta en su posición de impresión; `prueba-*/` tiene las pruebas. Si prefieres acomodar tú, usa `stl/`.

## Ajustes

- Capa 0,2 mm, boquilla 0,4. Paredes y relleno por pieza en las tablas.
- Compensación de agujeros: ninguna; las holguras ya están en el modelo.
- Baja la compensación de «elephant foot» si tu perfil la trae alta: las primeras capas de las uniones de cola de milano y del piñón deben quedar sin rebaba.
- Las barras (11 mm de ancho, 207 mm de largo) se levantan por las puntas: usa **borde de 1 mm** (entre barras hay 3 mm) y limpia la cama.
- Las piezas de PETG: 230–250 °C. Las de PLA+: 200–230 °C.
- Los gramos son una estimación con 3 paredes y 15 % de relleno donde se indica; brazo, piñón y barras van al 100 %.

## Filamento

| Filamento | Para qué | Gramos |
|---|---|---|
| PETG | Carro, brazo, soporte del motor y piñón | 105 g |
| PLA+ (un color) | Barras 1 a 4 | 108 g |
| PLA+ (otro color, para distinguirlas de la barra) | Rieles 1 a 5 | 158 g |

Total ≈ 372 g. Pon el color de la barra distinto al del riel: así sabes cuál es cuál al armar.

## Orden de impresión

1. **Fase 0, pruebas (≈ 110 g).** Las tres de abajo. Con ellas eliges los juegos antes de imprimir lo grande.
2. **Fase 1 (≈ 23 g).** Solo el soporte del motor y el piñón, sueltos desde `stl/`, no la cama 1 completa. Prueba con tu motor.
3. **Fase 2.** Cama 1 completa y el riel 2 (de la cama 4) para probar el carro.
4. **Fase 3.** Camas 2, 3 y 4.

## Si decides no hacer pruebas

Se puede, a costa de reimprimir si algo no ajusta. Imprime en este orden y revisa cada paso antes de seguir (así un fallo cuesta una pieza, no todo):

1. **Soporte del motor y piñón**, sueltos desde `stl/` (≈ 28 g). Revisa que el motor asiente por el piloto y que el eje entra en el piñón.
2. **Cama 2** (barras 1 a 3 y riel 1). Encaja las barras entre sí (la lengüeta debe entrar firme) y rueda el piñón por los dientes.
3. **Cama 3** (barra 4). Encájala con la 3.
4. **Carro y brazo**, sueltos desde `stl/` (≈ 82 g). El brazo debe entrar por arriba en la ranura del carro.
5. **Cama 4** (rieles 2 a 5) y, con todo, el armado.

Las dos uniones que más se juegan son la lengüeta de la barra y el brazo en el carro (ajustes de décimas de milímetro); por eso, si haces solo una parte de las pruebas, que sean las pruebas B y C (≈ 80 g).

## Pruebas (fase 0)

### Prueba A · carro sobre el riel · `prueba-ajuste/`

| Archivo | Qué es | Material | Relleno | g aprox. |
|---|---|---|---|---|
| `prueba-1_carro-rebanada.stl` | Rebanada de 36 mm del carro con una zona de agarre | PETG | 15 %, 3 paredes | ≈ 15 |
| `prueba-2_rieles-con-union.stl` | Dos trozos de riel con la lengüeta y la ranura de unión | PLA+ | 15 %, 3 paredes | ≈ 15 |

Pasa si la rebanada desliza por el riel con un empujón de dedo y la lengüeta entra a presión. Son piezas de dos materiales: imprime cada STL por separado.

### Prueba B · engrane y unión de la barra · `prueba-engrane-y-union/`

| Archivo | Qué es | Material | Relleno | g aprox. |
|---|---|---|---|---|
| `prueba-1_engrane-y-union.stl` | Un trozo de barra de 16 dientes con la lengüeta, 3 trozos con la ranura (juegos 0,15 / 0,25 / 0,35 mm, de 8, 10 y 12 dientes) y un piñón | PLA+ (todo, para la prueba) | 100 % | ≈ 30 |

Pasa si la lengüeta entra firme en una ranura sin bailar y el piñón rueda libre por los dientes.

### Prueba C · brazo y ranura del carro · `prueba-brazo/`

| Archivo | Qué es | Material | Relleno | g aprox. |
|---|---|---|---|---|
| `prueba-2_carro-rebanadas-y-brazo.stl` | Un trozo de brazo y 3 rebanadas del carro con juegos de 0,1 / 0,2 / 0,3 mm (anchos de 20, 23 y 26 mm) | PETG | rebanadas 15 %, brazo 100 % | ≈ 50 |

Pasa si el brazo entra por arriba con un empujón firme, asienta la tapa y no se sale al sacudir.

## Camas definitivas

### Cama 1 · PETG · `camas/cama-1_PETG_carro-brazo-soporte-y-pinon.stl` · ocupa 207 × 115 mm

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `V7-CA_carro.stl` | Carro (con la ranura del brazo) | 1 | 15 %, 3 paredes | 124 × 58 × 45 | 58 |
| `V7-SP_soporte-motor.stl` | Soporte del motor | 1 | 30 %, 4 paredes | 59 × 69 × 47 | 25 |
| `V7-BZ_brazo.stl` | Brazo | 1 | 100 % | 169 × 35 × 37 | 24 |
| `V7-PI_pinon.stl` | Piñón de 16 dientes | 1 | 100 % | 27 × 27 × 8,5 | 3 |

- El brazo se imprime de pie (como en el modelo): la placa de 3 mm queda vertical y la cola de milano arriba.
- Peso de la cama: ≈ 110 g.

### Cama 2 · PLA+ · `camas/cama-2_PLA_barras-1-2-3-y-riel-1.stl` · ocupa 213 × 147 mm

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `V7-B1_barra-1.stl` | Barra, tramo 1 (con la lengüeta adelante) | 1 | 100 % | 207 × 11 × 10,5 | 26 |
| `V7-B2_barra-2.stl` | Barra, tramo 2 | 1 | 100 % | 207 × 11 × 10,5 | 25 |
| `V7-B3_barra-3.stl` | Barra, tramo 3 | 1 | 100 % | 207 × 11 × 10,5 | 25 |
| `V7-R1_riel-1.stl` | Riel, tramo 1 (con los postes infrarrojos) | 1 | 15 %, 3 paredes | 210 × 97 × 56 | 42 |

- Los dientes quedan hacia arriba y la ranura de unión, al aire por los lados y abajo.
- El riel 1 casi llena el ancho de la cama (210 mm): no uses borde ahí. Peso de la cama: ≈ 118 g.

### Cama 3 · PLA+ · `camas/cama-3_PLA_barra-4-en-diagonal.stl` · ocupa 178 × 182 mm

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `V7-B4_barra-4.stl` | Barra, tramo 4 (con la ranura atrás, la clavija y su lengüeta) | 1 | 100 % | 173 × 177 × 30 (en diagonal a 45°) | 32 |

- Mide 234 mm de largo, así que va **en diagonal** (el STL ya viene girado 45°). La clavija de Ø8 sube de pie.
- Peso de la cama: ≈ 32 g.

### Cama 4 · PLA+ (el color del riel) · `camas/cama-4_PLA_rieles-2-3-4-5.stl` · ocupa 197 × 135 mm

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `V7-R2_riel-2.stl` | Riel, tramo 2 | 1 | 15 %, 3 paredes | 186 × 28 × 26 | 29 |
| `V7-R3_riel-3.stl` | Riel, tramo 3 | 1 | 15 %, 3 paredes | 186 × 28 × 26 | 29 |
| `V7-R4_riel-4.stl` | Riel, tramo 4 | 1 | 15 %, 3 paredes | 186 × 28 × 26 | 29 |
| `V7-R5_riel-5.stl` | Riel, tramo 5 | 1 | 15 %, 3 paredes | 192 × 28 × 26 | 30 |

- Pie plano contra la cama. Peso de la cama: ≈ 117 g.

## Resumen

| Cama | Material | Piezas | g aprox. |
|---|---|---|---|
| 1 | PETG | Carro, soporte del motor, brazo, piñón | 110 |
| 2 | PLA+ | Barras 1 a 3, riel 1 | 118 |
| 3 | PLA+ | Barra 4 | 32 |
| 4 | PLA+ | Rieles 2 a 5 | 117 |
| | | **Total** | **≈ 377** (372 con el soporte al 15 %) |
