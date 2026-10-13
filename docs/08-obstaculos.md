# Del punto A al punto B: cuatro obstáculos con nivel de dificultad

Cuando el vaso llega al final de la banda, que es el límite del alcance del
brazo, el brazo lo toma (**punto A**) y debe llevarlo al rack (**punto B**,
puestos R1 a R5). Entre los dos cuelgan cuatro móviles que giran sin parar. Están
puestos en el camino en orden de dificultad: cada uno le exige al planificador
una capacidad que el anterior no pedía.

![Ruta de A a B](img/ruta-obstaculos.png)

| | Posición |
| --- | --- |
| Punto A | Final de la banda, yaw −60°, radio 23 cm |
| Punto B | Rack de cinco puestos, yaw 24° a 86°, radio 23 cm |
| Tránsito nominal | Arco de radio 23 cm a 20 cm de altura, pinza siempre vertical |

## Los cuatro niveles

| Nivel | Obstáculo | Dónde | Qué exige | Maniobra | Cifras |
| --- | --- | --- | --- | --- | --- |
| 1 · Básico | O1 Guardián de banda | yaw −40°, 3 brazos, esferas a 22,0 cm | Una sola variable: la altura | Paso por debajo | baja de 20 a 15,5 cm; 2,1 cm libres sobre el vaso |
| 2 · Intermedio | O2 Muro giratorio | yaw −15°, 2 brazos rápidos (1,8×), esferas a 13,5 cm | Coordinar hombro, codo y muñeca sin inclinar el vaso | Rodeo interior | recoge el TCP hasta ρ = 8,3 cm |
| 3 · Avanzado | O3 Centinela | yaw 10°, colgado a 14 cm del eje, esferas a 14,0 cm | Predecir: no hay hueco geométrico | Espera de ventana | tapa el paso el 49 % de cada vuelta |
| 4 · Experto | O4 Jefe de rack | yaw 40°, 2 brazos, esferas grandes (r = 3 cm) a 23,0 cm | Las dos cosas a la vez, encima del destino | Paso por debajo y bajada cronometrada | tránsito a 16,1 cm; su giro cubre R1 a R4 |

Sin ninguna maniobra cada móvil tapa la ruta directa buena parte del tiempo: el
O1 la tapa siempre (100 % de la vuelta), el O2 el 48 %, el O3 el 49 % y el O4 el
64 %. Con su maniobra, los niveles 1, 2 y 4 quedan despejados en toda la vuelta;
el nivel 3 sigue tapando el 49 %, y por eso el brazo espera el hueco entre brazos.

Para reproducir la tabla:

```bash
cd software && python -m brazo.obstaculos
```

## Cómo decide el planificador

Para cada punto del arco el planificador pregunta, en este orden:

1. **¿Cabe por debajo?** Si `y_esfera − r_esfera − margen − alto del vaso ≥ 12,3 cm`,
   baja la altura de tránsito lo justo (sin bajar de 15,5 cm).
2. **¿Cabe por dentro?** Si al recogerse queda `ρ ≥ 7,2 cm`, el mínimo que admite
   la inversa con la pinza vertical, recoge el brazo y rodea el móvil.
3. **Si no cabe por ningún lado**, simula el cruce completo contra la posición
   **futura** de las esferas y solo se compromete si cabe entero.

En todos los casos el cabeceo se mantiene en φ = −90°: θ₄ compensa a θ₂ y θ₃ y el
vaso nunca se inclina.

Dos reglas más salieron de ver al brazo trabarse en la simulación:

- **El corredor de bajada se cronometra.** Al llegar sobre A o sobre un puesto
  del rack, el descenso se simula en el tiempo contra el giro de las esferas;
  no se exige que toda la columna esté libre a la vez. Esto es lo que hace
  difícil al nivel 4: su giro cubre cuatro de los cinco puestos.
- **Recogerse no siempre ayuda.** El O3 cuelga por dentro del arco; recoger el
  brazo cerca de él lo metería en su giro. Por eso, en la franja del O3 manda la
  espera y el brazo se queda en el radio nominal.

## Las maniobras se encadenan

Las maniobras no son escalones. Cada móvil influye con un peso que vale 1 dentro
de su franja y se desvanece hasta el doble de ella, así que en el recorrido se
mezclan: saliendo de A el brazo ya baja por el O1 y empieza a recogerse por el
O2; entre el O2 y el O3 cruza por ventanas; sobre el rack pasa por debajo del
O4. La franja inferior de la figura muestra qué maniobra manda en cada tramo.

## El mismo modelo en Python y en la simulación

El planificador vive en la simulación web
([`simulacion_sistema_completo.html`](simulacion_sistema_completo.html)) y
también en [`software/brazo/obstaculos.py`](../software/brazo/obstaculos.py),
donde se puede calcular y probar. Que sean el mismo modelo no se da por
supuesto: la prueba `test_python_y_el_simulador_web_calculan_lo_mismo` corre el
JavaScript de la página en Node (con `scripts/verificar_simulador.js`) y compara
las franjas, la maniobra en cada grado del recorrido y la holgura en 400 poses
aleatorias. La diferencia máxima es de 10⁻¹⁴ cm.

| Prueba | Qué comprueba |
| --- | --- |
| `test_el_nivel_sube_en_el_orden_en_que_se_encuentran` | De A hacia B aparecen los niveles 1, 2, 3 y 4 |
| `test_cada_obstaculo_fuerza_su_maniobra` | Por debajo, rodeo, espera y por debajo |
| `test_cifras_de_las_maniobras` | 15,5 cm, ρ = 8,3 cm, 16,1 cm y 2,1 cm de holgura |
| `test_sin_maniobra_cada_obstaculo_tapa_la_ruta` | Ninguno es decorativo |
| `test_las_maniobras_geometricas_despejan_toda_la_vuelta` | Bajar o recogerse deja el paso libre en todo el giro |
| `test_el_centinela_deja_ventana_entre_brazos` | El nivel 3 obliga a esperar, pero la ventana existe |
| `test_los_extremos_de_la_ruta_estan_vigilados` | El O1 vigila A y el O4 al menos tres puestos de B |
| `test_las_poses_de_evasion_las_alcanza_el_brazo` | Cada maniobra tiene inversa y deja la pinza vertical |

## Qué falta

La evasión corre en la simulación y en Python. El firmware del ESP32 todavía
hace el tránsito nominal sin obstáculos; llevar `plan_en()` al secuenciador del
ESP32 es parte de la siguiente entrega, junto con los móviles físicos.
