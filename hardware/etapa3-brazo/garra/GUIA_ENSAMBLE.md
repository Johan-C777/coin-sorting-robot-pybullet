# Guía de Impresión 3D y Ensamble — Garra y Último GDL (Pitch) para SG90

Rediseño completo del último grado de libertad (cabeceo / Pitch) y de la garra, calibrado a las medidas reales tomadas con pie de rey de tus **Micro Servos 9g SG90** y sus **palas blancas de 22 mm**, conservando 100% la compatibilidad con el antebrazo (`005`) y biela (`003`) que ya tienes impresos.

---

## 1. Estructura de Carpetas en `garra/`

- **`garra/SolidWorks/`**: Ensamble nativo [`Ensamble_Garra_SG90.SLDASM`](file:///c:/Users/samue/PycharmProjects/REI/CAD/garra/SolidWorks/Ensamble_Garra_SG90.SLDASM) junto con todas sus piezas `.SLDPRT` (incluidos los 2 servos SG90 reales y sus 2 palas de `22 mm`) y respaldo universal [`Ensamble_Garra_SG90.step`](file:///c:/Users/samue/PycharmProjects/REI/CAD/garra/SolidWorks/Ensamble_Garra_SG90.step).
- **`garra/Imprimibles_STL/`**: Las **7 piezas STL** listas para laminar (todas ya orientadas y apoyadas planas en `Z = 0.0 mm`).

---

## 2. Medidas del SG90 y Pala Aplicadas (con tolerancia FDM `+0.25 mm/lado`)

| Parámetro | Medida Real (Pie de Rey) | En CAD (con tolerancia 3D) |
| :--- | :---: | :---: |
| Cuerpo SG90 | `23.0 × 12.0 × 24.0 mm` | Cajera `23.5 × 12.5 mm` + costillas anti-rotación |
| Pestañas de montaje | `32.0 × 12.0 × 2.6 mm` (base a `17.4 mm`) | Apoyo plano a `Z = 20.0 mm` + pilotos `Ø1.70 mm` para tornillos originales |
| Eje de salida | A `6.0 mm` del borde del cable | Paso libre de torreta `Ø12.6 mm` + secundario `Ø6.4 mm` |
| Pala blanca (`22 mm`) | Largo `22.0 mm`, cubo `Ø7.0 × 5.0 mm`, punta `Ø4.4 mm`, espesor `2.0 mm` | Cajera cónica exacta `22.5 mm` (`Ø7.5 → Ø4.9 mm`), profundidad `4.3 mm`, piso `1.3 mm` |

---

## 3. Lista de Piezas a Imprimir (`Imprimibles_STL/`)

| Archivo STL | Cant. | Dimensiones (X × Y × Z) | Soportes | Relleno rec. |
| :--- | :---: | :---: | :---: | :---: |
| `01_Soporte_Muneca_Pitch_020_x1.stl` | **1** | `79.0 × 65.5 × 61.3 mm` | Sí (solo bajo voladizo de orejas W2) | `35–40%` |
| `02_Soporte_Garra_012_x1.stl` | **1** | `65.0 × 43.0 × 18.0 mm` | Mínimo (un bloque pequeño dentro de la cajera de la pala de Pitch) | `35–40%` |
| `03_Dedo_Derecho_Motriz_013_x1.stl` | **1** | `67.8 × 26.4 × 12.0 mm` | **NO** | `40%` (3–4 perímetros) |
| `04_Dedo_Izquierdo_Conducido_014_x1.stl` | **1** | `69.0 × 26.2 × 12.0 mm` | **NO** | `40%` (3–4 perímetros) |
| `05_Pin_Dedo_4mm_x1.stl` | **1** | `8.0 × 8.0 × 16.5 mm` | **NO** | `100%` |
| `06_Pin_Pitch_8mm_x1.stl` | **1** | `12.0 × 12.0 × 14.5 mm` | **NO** | `100%` |
| `07_Arandela_Dedo_2mm_x1.stl` | **1** | `9.0 × 9.0 × 2.0 mm` | **NO** | `100%` |

- **Altura de capa recomendada:** `0.20 mm` (o `0.16 mm` para dientes y cajeras de pala aún más nítidos).
- **Boquilla:** `0.4 mm`, PLA o PETG.

---

## 4. Orden Recomendado de Ensamble (Paso a Paso)

> **Consejo previo:** Antes de atornillar las palas blancas, energiza ambos SG90 y llévalos a su **posición central (`90°`)** para tener el máximo recorrido útil en ambos sentidos.

### Paso 1 — Montar el Servo de Cabeceo (Pitch) en `01_Soporte_Muneca_Pitch_020`
1. Desliza el SG90 de Pitch desde el lado exterior (`-Y`) entre las dos costillas guía hasta que sus pestañas apoyen planas contra la pared y su torreta circular salga hacia adentro.
2. El cable queda mirando hacia atrás (hacia el antebrazo).
3. Fija el servo usando los **2 tornillos originales de las pestañas** del SG90 en los agujeros piloto `Ø1.70 mm`.

### Paso 2 — Montar el Servo de la Pinza y los Dedos en `02_Soporte_Garra_012`
1. Coloca el segundo SG90 desde arriba entre las costillas guía de `012` (con el eje hacia abajo en el lado de los dedos y el cable arriba) y fíjalo con sus **2 tornillos originales**.
2. Coloca la arandela **`07_Arandela_Dedo_2mm`** debajo del agujero `Ø4 mm` de `012`, presenta **`04_Dedo_Izquierdo_Conducido_014`** e inserta desde abajo **`05_Pin_Dedo_4mm`** (gira libre en el dedo y ajusta firme en `012`).
3. Presenta **`03_Dedo_Derecho_Motriz_013`** engranando sus dientes con `014` (con ambos dedos cerrados o semi-abiertos simétricos).
4. Encaja la **pala blanca de `22 mm`** desde abajo dentro de la cajera de `013` hasta que su cubo entre en la estría del SG90, y aprieta desde abajo el **tornillo central original de la pala**.

### Paso 3 — Unir la Garra (`012`) a la Muñeca (`020`)
1. Coloca la segunda **pala blanca de `22 mm`** dentro de la cajera interna de la oreja izquierda de `012`.
2. Desliza `012` dentro de la horquilla de `020` alineando el cubo de la pala con la estría del SG90 de Pitch hasta que asiente por completo.
3. **Truco de armado:** Antes de colocar el pasador derecho, introduce un destornillador Phillips **a través del agujero vacío `Ø8.3 mm` del brazo derecho de `020`** (el espacio entre orejas es 100% libre) y aprieta el **tornillo central original** de la pala de Pitch.
4. Inserta **`06_Pin_Pitch_8mm`** desde el exterior del brazo derecho de `020` hasta hacer tope con su cabeza.

### Paso 4 — Conectar al Brazo Ya Impreso
1. Inserta el antebrazo `005` (`W1`) y la biela superior `003` (`W2`) entre las orejas traseras de `01_Soporte_Muneca_Pitch_020` usando tus pasadores `Pin_8mm_Articulacion` ya impresos.
