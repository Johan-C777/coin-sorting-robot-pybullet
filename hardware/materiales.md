# Materiales y justificación

| Pieza | Material | Por qué |
| --- | --- | --- |
| Eslabones L₁ y L₂, soportes de servo | PETG impreso, 4 perímetros, 35 % de relleno | Más rígido que el PLA y con mejor resistencia a la fluencia bajo carga sostenida; aguanta el calor del servo |
| Plataforma de la base | PETG sobre rodamiento axial 51107 o plato giratorio de 4" | Saca la carga axial y el momento del eje del servo, que queda solo con el par de giro |
| Placa fija | MDF de 9 mm o acrílico de 6 mm, atornillada a la mesa | Evita el vuelco de 1,33 N·m sin necesidad de lastre |
| Uniones eslabón-servo | Bocina metálica de 25 dientes, tornillos M3 con insertos de latón | Las bocinas plásticas se barren con el par del hombro; los insertos permiten desarmar sin romper |
| Dedos de la pinza | PETG con almohadillas de TPU 95A | El TPU sube la fricción a ≈0,5 y absorbe la interferencia de cierre |
| Vasos | Polipropileno transparente, 52 mm de diámetro | Dejan ver el contenido para la cámara del contador y pesan poco |
| Cableado | 18 AWG en potencia, 22 AWG en señal | 10 A en tramos cortos con caída despreciable |
| Control | ESP32 DevKit V1 y PCA9685 | Wi-Fi integrado y PWM por hardware independiente del procesador |

## Impresión 3D

- Altura de capa 0,2 mm, boquilla 0,4 mm.
- Los eslabones se imprimen acostados para que las capas trabajen a compresión.
- Refuerzo de 4 perímetros en los apoyos de servo, que es donde se concentra el par.
