# Guía de armado: etapa 1 (tolva y selección de monedas)

> **Archivado (v4).** Este diseño (riel de 8 ranuras, ductos y base de PVC) se reemplazó por la torre de canto v5: [hardware/etapa1-clasificador/](../../hardware/etapa1-clasificador/README.md) y [09-clasificador-v5.md](../09-clasificador-v5.md).

Todo lo necesario para imprimir, armar, cablear y probar la etapa 1, en el orden en que conviene hacerlo. Las cotas salen de `scripts/generar_clasificador.py`; el ensamble 3D está en [`docs/ensamble-etapa1.html`](../ensamble-etapa1.html); los STL, en `hardware/archivo/etapa1-v4/stl/`.

**Qué hace la etapa 1:** la tolva suelta una moneda cada 1,5 s al riel de 22°. El riel las separa por diámetro en 7 ranuras y un extremo abierto. Cada moneda cruza una barrera infrarroja (cuenta) y cae por un tubo de PVC a su vaso. Las dos $500 (antigua y nueva) pasan antes bajo un sensor de color que mueve un plato, y salen por dos columnas distintas. Son 9 vasos en total. La banda y los vasos son de la etapa siguiente; aquí solo se deja el espacio y se prueba con vasos sueltos.

---

## 1. Materiales

### 1.1 Filamento (≈ 480 g en total, ±25 %)

| Material | Para qué | Gramos |
|---|---|---|
| PLA+ negro | adaptadores de ducto, D6, plato, puente, tolva (T01, T02, T03) | ≈ 230 |
| PETG azul | riel, patas del riel y de la tolva | ≈ 180 |
| ABS gris | dos bases de extremo | ≈ 75 |

D6 y el puente del sensor van en negro para que no pase luz a las barreras IR y al sensor de color.

### 1.2 Tubos y estructura

| Cant. | Material | Detalle |
|---|---|---|
| 1 | Tubo PVC presión 3/4" | tramo de 2 m (Ø ext 26,7 mm). Cortes en 3.1 |
| 1 | Tubo PVC presión **1" RDE 21** | 1 m (Ø ext 33,4 mm, **interior ≈ 30 mm**). Cortes en 3.1 |
| 4 | Tee PVC presión 3/4" | sin codos |
| 1 | Lámina de MDF de 9 mm | 560 × 198 mm; ranura de 357 × 48 mm; 8 agujeros de 5 mm para bridas |
| 1 | Cemento PVC | opcional, para uniones definitivas |
| 20 | Bridas de nailon 2,5 × 100 mm | patas del riel, patas de la tolva, motor, lámina |
| 1 | Cinta de enmascarar | para ajustar encajes flojos |

El tubo de 1" de pared gruesa (SCH 40, interior ≈ 26,6 mm) atasca la $1000 (26,7 mm). Antes de cortar los siete tubos, pasa una $1000 por el tubo.

### 1.3 Electrónica

| Cant. | Componente | Nota |
|---|---|---|
| 1 | ESP32 DevKit V1 (30 pines) | controlador de la etapa |
| 1 | Motor 28BYJ-48 con driver ULN2003 | mueve el disco de la tolva |
| 1 | Micro-servo SG90 | plato de la $500 |
| 1 | Sensor de color TCS34725 | I2C, dirección 0x29 |
| 9 | LED infrarrojo 5 mm | emisores de las barreras |
| 9 | Fototransistor 5 mm (misma longitud de onda) | receptores |
| 9 | Resistencia 330 Ω | una por LED IR, a 5 V (≈ 11 mA; con 220 Ω serían 17 mA) |
| 9 | Resistencia 10 kΩ | pull-up externo de cada fototransistor a 3,3 V |
| 1 | Fuente 5 V 2 A | alimenta tolva, servo y LED IR; el ESP32 por su USB o por el mismo 5 V |
| 1 | Protoboard o placa perforada, cables Dupont, cable fino de 26 AWG | unos 3 m para las 9 barreras |
| 1 | Condensador electrolítico ≥ 220 µF | en el 5 V del servo, evita reinicios |

La banda (motor, L298N) no es de esta etapa. Los pines ya están reservados en `config.h`.

### 1.4 Contra tu inventario (xlsx del 2026-10-19)

| Ya lo tienes | Cant. | Nota |
|---|---|---|
| ESP32 («Modulo ESP32 + ESP32») | 2 | confirma que es DevKit V1 de 30 pines; si es otra placa, revisa los pines de `config.h` |
| Resistencias 330 Ω / 10 kΩ | 13 / 23 | alcanzan para 9 LED y 9 pull-ups |
| Condensadores 220 µF, 100 µF, 4700 µF | 1 c/u | el de 220 µF va en el servo |
| Fuente 5 VDC; fuente 0-20 V 1,5 A | 1 c/u | revisa la corriente de la de 5 V: necesita ≥ 1,5 A. La de laboratorio ajustada a 5 V sirve para las pruebas |
| Protoboards, kit de cables, jumpers, borneras | varios | |

| **Te falta** | Cant. | Nota |
|---|---|---|
| Motor 28BYJ-48 con driver ULN2003 | 1 | el motor de la tolva |
| Micro-servo SG90 | 2 | 1 de uso y 1 de repuesto |
| Sensor de color TCS34725 | 1 | módulo con I2C |
| LED infrarrojo 5 mm + fototransistor 5 mm | 10 + 10 | uno de cada por ducto, más 1 de repuesto; que sean del mismo kit |
| Cable fino 26 AWG, 3 m | 1 | para las barreras |
| Bridas de nailon, PVC, tees, MDF, cemento PVC | ver 1.2 | |

El 4N25 (2 unidades) trae LED IR y fototransistor en un solo encapsulado: sirve solo para probar el firmware sobre la mesa, no para las barreras.

### 1.5 Herramientas

Sierra para PVC o cortatubos, lima o lija fina, calibrador, regla, marcador, destornillador pequeño, soldador de estaño, pegamento instantáneo o pistola de silicona, 4 vasos o tubos de ensayo de Ø34 mm para pruebas, una moneda de cada denominación (nueva y antigua).

---

## 2. Impresión

Ajustes para todas las camas: **no girar ni escalar** (las piezas ya vienen orientadas), soportes apagados, capa 0,2 mm, 3 paredes (4 en rieles y adaptadores), relleno 15 % (25 % en las bases ABS), velocidad al 70 % en piezas altas, brim de 3 mm en adaptadores, D6 y patas T04, sin falda en R02 (mide 215 mm). Seca el PETG y el ABS antes de cada cama.

| Cama | Material | Piezas | Gramos / tiempo |
|---|---|---|---|
| **1** (prueba) | PETG azul | R01, R03_pata1_izq, R03_pata1_der | 56 g · 3 h |
| **2** (prueba) | PLA+ negro | D1_adaptador, D6, B02, B03 | 82 g · 5,5 h |
| 3 | PETG azul | R02, R04 ×3, R03_pata2 ×2, R03_pata3 ×2 | 80 g · 4,5 h |
| 4 | PLA+ negro | adaptadores D2, D3, D4, D5, D7, D8 | 82 g · 7 h |
| 5 | PLA+ negro | T02, T03 | 35 g · 3 h |
| 6 | PETG azul | T04 ×4 | 45 g · 4 h |
| 7 | PLA+ negro | T01 | 30 g · 1,5 h |
| 8 | ABS gris | P01_base_extremo ×2, lado a lado | 74 g · 4 h |

**Total ≈ 480 g y ≈ 33 h.** Imprime primero las camas 1 y 2 y haz la prueba de la sección 4.1 antes de seguir.

---

## 3. Corte del PVC y de la lámina

### 3.1 Cortes

| Tubo | Cortes |
|---|---|
| 3/4" presión | 4 patas de **134 mm** · 4 tramos de **29 mm** · 2 largueros de **490 mm** |
| 1" RDE 21 | D1 **196** · D2 **181** · D3 **167** · D4 **152** · D5 **128** · D7 **85** · D8 **69** mm |

Los cortes de 3/4" suponen 11 mm del centro de la tee al fondo de su copa (`F_ACC` en el generador). Mide la copa de tu tee: si da otro valor, corrige cada corte en 2 × (valor − 11) mm, o dime y los recalculo. Corta recto, lima el borde y marca la profundidad de inserción con marcador.

### 3.2 Lámina de MDF

560 × 198 mm (largo × ancho), 9 mm de espesor. Con la lámina en vista de planta, el borde izquierdo a tu izquierda y el borde de adelante hacia ti:

- **Ranura** de 357 × 48 mm: empieza a **113 mm del borde izquierdo** y a **72 mm del borde de adelante**.
- **8 agujeros de 5 mm** para las bridas, dos por pata. Las cuatro patas quedan a 24 mm de los bordes cortos y largos (esquinas en 24/24, 536/24, 24/174 y 536/174 mm desde la esquina izquierda-delantera). En cada una, un agujero a 18 mm a cada lado de la pata, a lo largo de la lámina.

Sella el MDF con pintura o barniz si quieres que no se hinche.

---

## 4. Armado

### 4.1 Prueba de ajuste (camas 1 y 2)

1. Mete la clavija de una pata R03 en su agujero de R01: debe entrar con un empujón y no bailar.
2. Mete las dos clavijas de D1_adaptador en R01: igual.
3. Mete el SG90 en el bolsillo de D6, por la cara −Y: queda a presión.
4. Inserta el tubo de 1" (196 mm) en el collar de D1_adaptador: debe entrar con un empujón; 20 mm de inserción.
5. Pasa una $1000 por el tubo y por un adaptador: tiene que caer sin rozar.

Si algo queda flojo o apretado, anota el valor y ajusta `AJUSTE_PRESION` (+ afloja, − aprieta, en mm) en `scripts/generar_clasificador.py`, regenera y reimprime solo las piezas afectadas. Una vuelta de cinta resuelve un tubo flojo.

### 4.2 Base

1. Pega con cemento PVC (o deja a presión para probar) cada **pata de 134 mm** en el zócalo de una base P01: entra 32 mm hasta el fondo.
2. Pon una tee a cada pata, con la salida lateral **hacia adentro** (hacia la otra tee del mismo lado). Mete un **tramo de 29 mm** en el otro extremo de la tee.
3. Une las dos tees de un lado con un **larguero de 490 mm**; repite del otro lado.
4. Repite para las 4 patas: son dos bases P01 (una por extremo) separadas 150 mm y dos largueros paralelos.
5. Apoya la lámina de MDF sobre los 4 tramos cortos y átala: una brida por cada par de agujeros, rodeando el tubo de la pata.
6. Revisa que el conjunto no balancee. Si baila, apriétalo contra una mesa plana y pega las tees.

Resultado: hueco libre de 123 mm de ancho × 490 mm de largo para la banda, con 70 mm bajo la cara de arriba de la banda para motor y rodillos. Vasos Ø34 × 60 mm van sobre la banda, con su boca 70 mm bajo la lámina.

### 4.3 Riel

1. Une R01 y R02 con las tres llaves de mariposa R04: entran desde abajo en su alojamiento, con 0,2 mm de holgura.
2. Pon las patas R03 en el riel, por pares: **pata 1 (153 mm), pata 2 (114 mm) y pata 3 (44 mm)** a cada lado, con la clavija en el agujero del ala.
3. Pon el riel sobre la lámina: las patas izquierdas quedan a un lado de la ranura y las derechas al otro, con los pies sobre la lámina. Ata cada pie con 2 bridas por sus ranuras.
4. Revisa con un nivel de burbuja: la pista baja 22° en el sentido de las ranuras (la entrada queda arriba).

### 4.4 Adaptadores y tubos

1. Sobre cada ranura (1 a 5, 7 y 8) clava las dos clavijas del adaptador correspondiente en las orejas del riel. **Los adaptadores no son intercambiables:** el nombre del STL lleva el número de ranura.
2. Inserta en cada adaptador su tubo de 1" por abajo (20 mm de inserción). Los tubos bajan por la ranura de la lámina.
3. Mide que cada tubo termine **6 mm sobre la boca de su vaso**: D1 a 196 mm y D8 a 69 mm cumplen eso con los vasos a 70 mm bajo la lámina. Si no coincide, recorta el tubo.
4. Barreras IR: LED en una cavidad Ø5,2 y fototransistor en la opuesta, a presión (el LED queda contra el tope de 3 mm). Pasa los cables por fuera, pegados al tubo, con bridas.

### 4.5 Bifurcador de $500 (ranura 6)

1. Mete el servo SG90 en el bolsillo de D6 por la cara −Y (las orejas hacia abajo).
2. Mete el plato B02 por abajo: el pasador de 4 mm en la pared +Y y el estriado de 4,6 mm en el eje del servo. Centra el servo en 90° antes de fijarlo.
3. Pon D6 bajo la ranura 6 con sus dos clavijas. Las dos columnas de salida quedan separadas 36,8 mm; cada una cae en su vaso.
4. Barreras IR: una en cada columna (cavidades a presión).
5. B03 va a horcajadas sobre las paredes del riel, antes de la ranura 5. Desliza la placa del TCS34725 desde el lado −X bajo sus dos labios; el sensor queda a 4 mm de la moneda y mirando hacia abajo.

### 4.6 Tolva

1. Pon el 28BYJ-48 bajo T03 y átalo con 2 bridas por las ranuras.
2. Encaja T02 (disco) a presión en el eje del motor, a 0,35 mm sobre la base.
3. Coloca T01 (cono) sobre las 3 clavijas de T03.
4. Pon las 4 patas T04 en las orejas de T03 con su clavija y átalas a la lámina con 2 bridas cada una (sobre la entrada del riel, a la izquierda).

---

## 5. Cableado

Todo está definido en `firmware/esp32_contador/config.h`.

| Función | Pin del ESP32 |
|---|---|
| Fototransistores 1 a 9 (N50, N100, A50, N200, A100, A500, N500, A200, N1000) | 34, 35, 36, 39, 32, 33, 25, 26, 27 |
| TCS34725 SDA / SCL | 21 / 22 |
| SG90 del plato | 13 |
| 28BYJ-48 (IN1 a IN4 del ULN2003) | 16, 17, 18, 19 |
| Banda (L298N A, B, PWM), reservado | 14, 4, 23 |

**Cada barrera:** LED IR + resistencia de 330 Ω entre 5 V y GND. Fototransistor con el emisor a GND y el colector al pin del ESP32, y una resistencia de **10 kΩ del pin a 3,3 V** (los pines 34 a 39 no tienen pull-up interno). Con el haz libre el pin está en bajo; cuando una moneda lo corta, sube.

**Alimentación:** 5 V de la fuente al ULN2003, al servo y a los LED; GND común con el ESP32. Pon el condensador de 220 µF en el 5 V del servo.

El orden de las barreras importa: el ducto 1 es la ranura 1 ($50 nueva), y así sucesivamente hasta el 9 ($1000 nueva). El ducto 6 (A500) es la columna −X de D6 y el 7 (N500) la +X.

---

## 6. Firmware

1. Arduino IDE con el paquete **ESP32**; placa «ESP32 Dev Module». No necesita librerías externas.
2. Copia `secrets_example.h` como `secrets.h` y pon tu red Wi-Fi y la IP del brazo (etapa 2).
3. Abre `firmware/esp32_contador/esp32_contador.ino` y sube. Abre el monitor serie a 115200.
4. Las pruebas del código sin hardware: `make -C firmware/tests`.

---

## 7. Pruebas y calibración (en este orden)

1. **Sin monedas.** Con el monitor serie, tapa cada barrera con un dedo: debe contar una moneda en su ducto. Si cuenta al revés, cambia `FLANCO_MONEDA`.
2. **Tolva.** Pon 5 monedas en el cono: el disco debe soltar una cada ≈ 1,5 s. Si gira al revés, cambia `SENTIDO_TOLVA`.
3. **Plato.** El servo debe ir a 55° y a 125°: el plato se inclina hacia −X o +X. Ajusta `AGUJA_A500_GRADOS` y `AGUJA_N500_GRADOS`.
4. **Riel.** Suelta a mano una moneda de cada denominación sobre la entrada: debe caer por **su** ranura, no por una anterior. Si una moneda se cuela por la ranura de arriba, esa ranura queda grande: reduce `COMPENSACION_RANURA` y reimprime el módulo. Revisa en particular la $100 antigua, la $500 antigua y la $50 antigua (apoyo de 0,1 a 0,2 mm).
5. **Color de la $500.** Pasa 10 monedas de $500 antigua y 10 nuevas. El monitor imprime `C500:<anillo>,<razón>`: elige `umbralDorado` entre los dos grupos.
6. **Conjunto.** Carga 20 monedas mezcladas en la tolva y comprueba que cada vaso recibe solo lo suyo. Meta: 0 monedas en un vaso equivocado en 20.

### Si algo falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| Una moneda cae por una ranura anterior | ranura demasiado grande | `COMPENSACION_RANURA` negativo y reimprimir |
| Una moneda atraviesa sin pasar por su ducto | ranura demasiado chica o la moneda rebota | `COMPENSACION_RANURA` positivo |
| La moneda se atasca dentro del tubo | tubo de interior < 28 mm | cambiar a RDE 21 |
| La barrera cuenta doble | rebote | subir `REBOTE_US` |
| El plato llega tarde | sensor muy cerca de la ranura 6 | mover B03 aguas arriba |
| Un ducto cuenta sin moneda | luz ambiente o pin 36/39 | tapar el tubo con cinta negra; el .ino ya apaga el modem-sleep |
| Tubo flojo en el collar | tolerancia de impresión | cinta o una gota de pegamento |

---

## 8. Criterios de aceptación de la etapa 1

- Las 9 barreras cuentan y no hay conteo doble.
- La tolva entrega una moneda cada ≈ 1,5 s sin trabarse en 100 monedas.
- 20 de 20 monedas llegan a su vaso, incluidas las dos $500.
- La estructura no se mueve al tocar el riel o la tolva.
- El hueco de 123 × 490 mm bajo la lámina está libre para la banda.

Con esto se pasa a la etapa 2 (banda y brazo).
