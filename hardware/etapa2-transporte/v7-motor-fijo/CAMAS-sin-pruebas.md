# Etapa 2 v7 (motor fijo): camas de impresión, sin pruebas

Impresora: Creality K1C, cama 220 × 220 × 250. Capa 0,2 mm, boquilla 0,4. **Sin soportes en ninguna pieza.** Son 4 camas, ≈ 377 g. Cada cama es un solo STL ya acomodado en `camas/`; las piezas sueltas están en `stl/`.

## Filamento

| Cama | Filamento | Temp. | Gramos | Disponible |
|---|---|---|---|---|
| 1 | PETG Azul 4DLAB | 230–250 °C | 110 | 613 g |
| 2 | PLA+ Negro 4DLAB (barras) y PLA+ Mármol 4DLAB (riel 1) | 200–230 °C | 76 + 42 | 429 g / 956 g |
| 3 | PLA+ Negro 4DLAB | 200–230 °C | 32 | 429 g |
| 4 | PLA+ Mármol 4DLAB | 200–230 °C | 117 | 956 g |

Barras en negro y riel en mármol: así se distinguen al armar. La cama 2 mezcla barras y el riel 1; para no cambiar de filamento, imprime todo en Mármol o separa el riel 1 desde `stl/`.

## Ajustes comunes

- Paredes y relleno por pieza en las tablas.
- Las barras (11 mm de ancho, 207 mm de largo) se levantan por las puntas: **borde de 1 mm** (entre barras hay 3 mm) y limpia la cama antes.
- Baja la compensación de «elephant foot» si el perfil la trae alta: las uniones de cola de milano y el piñón necesitan las primeras capas sin rebaba.

## Orden

Imprime en orden de cama y revisar cada una antes de seguir: así un fallo cuesta una cama y no todo.

1. Cama 1: revisa que el motor asienta por el piloto, que el eje entra en el piñón y que el brazo entra por arriba en la ranura del carro.
2. Cama 2: encaja las barras 1, 2 y 3 (la lengüeta debe entrar firme) y rueda el piñón por los dientes.
3. Cama 3: encaja la barra 4 con la 3.
4. Cama 4: encaja los rieles y pégalos a la mesa.

---

## Cama 1 · PETG Azul 4DLAB

Archivo: `camas/cama-1_PETG_carro-brazo-soporte-y-pinon.stl` · ocupa 207 × 115 mm · ≈ 110 g

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `V7-CA_carro.stl` | Carro (con la ranura del brazo) | 1 | 15 %, 3 paredes | 124 × 58 × 45 | 58 |
| `V7-SP_soporte-motor.stl` | Soporte del motor | 1 | 30 %, 4 paredes | 59 × 69 × 47 | 25 |
| `V7-BZ_brazo.stl` | Brazo | 1 | 100 % | 169 × 35 × 37 | 24 |
| `V7-PI_pinon.stl` | Piñón de 16 dientes | 1 | 100 % | 27 × 27 × 8,5 | 3 |

- El brazo va de pie: la placa de 3 mm queda vertical y la cola de milano arriba.

## Cama 2 · PLA+ Negro 4DLAB (barras) y PLA+ Mármol 4DLAB (riel 1)

Archivo: `camas/cama-2_PLA_barras-1-2-3-y-riel-1.stl` · ocupa 213 × 147 mm · ≈ 118 g

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `V7-B1_barra-1.stl` | Barra, tramo 1 (lengüeta adelante) | 1 | 100 % | 207 × 11 × 10,5 | 26 |
| `V7-B2_barra-2.stl` | Barra, tramo 2 | 1 | 100 % | 207 × 11 × 10,5 | 25 |
| `V7-B3_barra-3.stl` | Barra, tramo 3 | 1 | 100 % | 207 × 11 × 10,5 | 25 |
| `V7-R1_riel-1.stl` | Riel, tramo 1 (con los postes infrarrojos) | 1 | 15 %, 3 paredes | 210 × 97 × 56 | 42 |

- Los dientes quedan hacia arriba.
- El riel 1 casi llena el ancho de la cama (210 mm): sin borde en esa pieza.

## Cama 3 · PLA+ Negro 4DLAB

Archivo: `camas/cama-3_PLA_barra-4-en-diagonal.stl` · ocupa 178 × 182 mm · ≈ 32 g

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `V7-B4_barra-4.stl` | Barra, tramo 4 (ranura atrás, clavija y su lengüeta) | 1 | 100 % | 173 × 177 × 30 | 32 |

- Mide 234 mm de largo: va **en diagonal** (el STL ya viene girado 45°). La clavija de Ø8 sube de pie.

## Cama 4 · PLA+ Mármol 4DLAB

Archivo: `camas/cama-4_PLA_rieles-2-3-4-5.stl` · ocupa 197 × 135 mm · ≈ 117 g

| Pieza | Qué es | Cant. | Relleno | Medidas en cama (mm) | g aprox. |
|---|---|---|---|---|---|
| `V7-R2_riel-2.stl` | Riel, tramo 2 | 1 | 15 %, 3 paredes | 186 × 28 × 26 | 29 |
| `V7-R3_riel-3.stl` | Riel, tramo 3 | 1 | 15 %, 3 paredes | 186 × 28 × 26 | 29 |
| `V7-R4_riel-4.stl` | Riel, tramo 4 | 1 | 15 %, 3 paredes | 186 × 28 × 26 | 29 |
| `V7-R5_riel-5.stl` | Riel, tramo 5 | 1 | 15 %, 3 paredes | 192 × 28 × 26 | 30 |

- Pie plano contra la cama.

---

## Resumen

| Cama | Material | Piezas | g |
|---|---|---|---|
| 1 | PETG Azul | Carro, soporte del motor, brazo, piñón | 110 |
| 2 | PLA+ Negro y Mármol | Barras 1 a 3, riel 1 | 118 |
| 3 | PLA+ Negro | Barra 4 | 32 |
| 4 | PLA+ Mármol | Rieles 2 a 5 | 117 |
| | | **Total** | **≈ 377** |

Los gramos son estimaciones mías, no medidas.

---

## Si algo queda mal: qué se arregla con lija o pegamento

Sirve cola de cianoacrilato en gel y una lima fina o lija de grano 200 a 400. Es una guía mía, no una garantía.

| Falla | Arreglo | Alcanza |
|---|---|---|
| Un tramo de la barra no entra en el siguiente (lengüeta apretada) | Lijar 2 a 3 pasadas la lengüeta por los flancos, nunca el techo, y probar de nuevo | Sí |
| Un tramo de la barra queda flojo | Una gota de gel de cianoacrilato en la lengüeta y juntar. PLA+ con PLA+ pega bien. Después ya no se separa | Sí |
| Dos tramos de barra o riel con una pequeña diferencia de altura | Lijar la cresta del diente que sobra | Sí |
| El brazo no entra en la ranura del carro | Lijar las caras planas de la cola de milano del brazo, no la punta | Sí |
| El brazo queda flojo en la ranura | Rugosear con lija, gel de cianoacrilato y mantener 30 s. En PETG pega mal: si se suelta, reimprimir el brazo en PLA+ (24 g) | A medias |
| El piñón no entra en el eje de Ø5 | Pasar una broca de 5 mm o una lima redonda por el agujero | Sí |
| El piñón patina en el eje | Una gota de cianoacrilato entre el eje y el piñón, en el lado plano. Queda fijo | Sí |
| El piñón roza o salta en la barra | Pasar una lija por los dientes de la barra para quitar rebabas y frotar cera; si sigue, subir `BL` en `generar_v7.py` y reimprimir solo la barra | A medias |
| El carro no desliza en el riel | Lijar la cabeza del riel y el interior del carro; cera o grafito | Sí |
| Una pieza se despega de la cama y se curva (warping) | Reimprimir con más borde y sin corrientes de aire | No |
| La clavija de la barra 4 se rompe | Reimprimir la barra 4 (32 g). Un pegado queda débil porque la clavija está en el sentido débil de la capa | No |
