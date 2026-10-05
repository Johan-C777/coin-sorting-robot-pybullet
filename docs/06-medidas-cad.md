# Medidas del CAD frente a las del código

El brazo físico está modelado en SolidWorks (`hardware/Modelos3D/PLANOS BRACITO.pdf`). Sus cotas
no coinciden con las que usan la simulación y la memoria de cálculo, así que el
código trae dos perfiles y se cambia de uno a otro en un solo sitio:

```bash
BRAZO_PERFIL=cad python software/apps/cli_demo.py      # Python
#define PERFIL_CAD                                     # firmware/esp32_brazo/config.h
```

## Tabla comparativa

| Parámetro | De dónde sale en el plano | Perfil CAD | Perfil simulación | Diferencia |
| --- | --- | --- | --- | --- |
| d₁, eje del hombro sobre la mesa | hoja 3 (base 50 mm) + hoja 4 (hombro 36,61 mm) | 87 mm | 110 mm | −23 mm |
| L₁, hombro a codo | hoja 5: 140 mm totales menos los cubos R17,5 y R22,5 | 100 mm | 160 mm | −60 mm |
| L₂, codo a muñeca | hojas 6, 7 y 8: acotadas por caras, no entre ejes | 95 mm **por medir** | 150 mm | — |
| L₃, muñeca al TCP | hojas 10 y 12: pinza de 65,31 mm y base de 47,50 mm | 60 mm **por medir** | 80 mm | — |
| Alcance | suma de los tres eslabones | 255 mm | 390 mm | −135 mm |
| Radio del arco de puestos | calculado, no está en el plano | 97 mm | 230 mm | −133 mm |

Otras cotas del plano que ya están en el código: base Ø100 × 50 mm (hoja 3),
disco del hombro Ø110 mm (hoja 4), apertura útil de la pinza y vaso de 52 mm.

## Las dos cotas que faltan

El plano acota el codo y la mano por sus caras, no entre ejes. En SolidWorks,
sobre el ensamble, mide estas dos distancias y reemplázalas en los dos archivos:

1. **L₂**: del eje del codo (agujero Ø18 de la hoja 6) al eje de cabeceo de la
   muñeca (agujero Ø5 de Mano 1, hoja 7).
2. **L₃**: del eje de cabeceo al punto de agarre entre los dedos, con la pinza
   cerrada sobre un vaso de 52 mm.

## Consecuencia: el arco de la celda cambia

Con las medidas del CAD el brazo no llega a 230 mm. La verificación lo dice:

```
$ python scripts/verificar_alcance.py --perfil cad
perfil cad: d1=8.7 L1=10.0 L2=9.5 L3=6.0 cm
alcance máximo desde el hombro: 25.5 cm

radios con pinza vertical a 6.8 cm (agarre):   3.00 a 19.05 cm
radios con pinza vertical a 17.0 cm (traslado): 5.30 a 11.15 cm

radios válidos en las dos alturas: 5.30 a 11.15 cm
R_ARCO sugerido: 9.7 cm
```

El cuello de botella es la altura de traslado: con el brazo corto, subir el vaso
a 17 cm obliga a trabajar cerca de la base. Tres salidas, en orden de esfuerzo:

1. Bajar `Z_SEGURA` de 17 a 13 cm y volver a correr la verificación; el vaso
   sigue pasando por encima de los demás (los vasos llenos llegan a 8,9 cm).
2. Acercar el rack a 97 mm de radio, que es lo que ya quedó en el perfil CAD.
3. Alargar L₂ unos 40 mm en el CAD si se quiere conservar la celda actual.

## Qué revisar después de cambiar de perfil

```bash
python scripts/verificar_alcance.py --perfil cad    # alcance y radio del arco
pytest software/tests -q                            # ida y vuelta, límites, trama
make -C firmware/tests                              # mismo núcleo en C++
```

Las pruebas con valores fijos (24,00°, 49,02°, `S:114,49,83,64,90,85`) pertenecen
al perfil de simulación. Con el perfil CAD valen las invariantes: ida y vuelta de
la cinemática, respeto de límites y postura igual en todos los puestos.
