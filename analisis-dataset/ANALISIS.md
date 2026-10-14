# Actividad 1 — El retrato del dataset: resultados

- Con lluvia domina la moto,
- En el centro domina la bicicleta.
- La bicicleta llega exactamente a 7.00 km, el límite.
- Ninguna etiqueta rompe las reglas del negocio.

## 1. ¿Cuándo no aparece el dron?

- **Centro:** 0 drones. Lo explica la regla del espacio aéreo restringido.
- **Rural:** 0 drones. No hay una regla de zona; lo explica la distancia: en rural el mínimo es 15.93 km y el dron tiene tope de 15 km.
- **Lluvia y viento fuerte:** 0 drones en ambos. Lo explica la regla de que solo vuela con clima `despejado`.
- **Horario:** sus horas van de 6 a 20, así que ninguno sale de noche (21:00 a 5:59).

## 2. ¿Por qué la bicicleta casi no va a la periferia?

Ninguna regla se lo prohíbe, pero la distancia sí:

- En periferia, solo 46 de 2 046 envíos (2.2 %) están a 7 km o menos.
- La bicicleta tiene 18 envíos en periferia (0.9 %).
- Entre los envíos que sí caben en bicicleta (≤ 7 km, ≤ 8 kg, ≤ 40 L), en periferia gana 52.9 % de las veces, parecido al resto de zonas. No es que la periferia la desfavorezca: casi no hay envíos cortos allí.

## 3. Máximos contra la tabla `LIMITES`

| Medio | Peso máx. (kg) | Volumen máx. (L) | Distancia máx. (km) |
| --- | --- | --- | --- |
| bicicleta | 7.99 (límite 8) | 39.70 (límite 40) | 7.00 (límite 7) |
| moto | 24.93 (límite 25) | 89.99 (límite 90) | 39.90 (límite 40) |
| dron | 2.50 (límite 2.5) | 11.98 (límite 12) | 14.99 (límite 15) |
| camioneta | 80.00 | 400.57 | 59.12 |

- Bicicleta, moto y dron se adivinan casi exactos mirando solo los máximos.
- La camioneta no se puede adivinar: sus máximos (80 kg, 400 L, 59 km) son los del dataset, no un límite del vehículo. Su límite real (1000 kg, 3000 L, 1000 km) nunca se alcanza porque el generador no produce paquetes tan grandes.

## 4. Camionetas en viajes de menos de 2 km

Hay 107 en total.

- **Con razón clara: 95.** Se reparten en refrigerado (36), peso > 25 kg (47) y volumen > 90 L (61). Las categorías se traslapan, por eso no suman 95.
- **Sin razón clara: 12.** En 10 de ellas había 3 medios posibles y en 2 había 2.
- **Posible explicación:** el ruido del generador. El 8 % de variación en el costo y el 3 % de etiquetas cambiadas por otro medio posible (según el README) producen estos casos.
- En 6 de las 12 el paquete es frágil, lo que penaliza a moto y bicicleta pero no a la camioneta, y eso inclina un costo ya cercano hacia ella.

## Para pensar

**Qué reglas sí se pueden reconstruir desde el CSV**

- Los límites numéricos de bicicleta, moto y dron.
- Las prohibiciones de clima y zona del dron, que aparecen como ceros en las tablas.

**Qué reglas no se reconstruyen bien**

- La regla de que el refrigerado solo va en camioneta se puede intuir, pero con solo 5 % de refrigerados es débil.
- Los límites de la camioneta, por lo explicado arriba.
- El «costo» que desempata entre medios posibles: solo se ve como tendencias.

**Riesgo de dejar que el modelo «descubra» las reglas**

- Puede aprender un límite aproximado (por ejemplo, cortar en 7.4 km en vez de 7) y fallar justo en los bordes.
- Una regla que nunca apareció en los datos, como el tope real de la camioneta, no se aprende.
- Por eso `usar_modelo.py` mantiene `es_posible` escrito a mano: lo que es seguridad o ley no debe depender de lo que el modelo alcanzó a ver.

# Actividad 2 — La hora y el dron: resultados

## Predicción

- A las 3:00 salen 77 envíos y 0 son dron 
- De noche (antes de las 6 o desde las 21) sale el 10.5 % de los envíos: 1 053 de 10 000.

## 1. ¿Qué horas no tienen dron?

- Las horas sin ningún dron son 0, 1, 2, 3, 4, 5, 21, 22 y 23.
- Hay drones en todas las horas de 6 a 20.
- Coincide exactamente con la regla de noche (`hora >= 21 or hora < 6`).

## 2. Noche contra día

- Hay 1 053 envíos de noche contra 8 947 de día.
- Por hora, en la madrugada hay entre 59 y 149 envíos, y a mediodía más de 600.
- De noche el reparto es moto 805, camioneta 191 y bicicleta 57.
- Con tan pocos ejemplos, y con `min_samples_leaf=5`, el modelo tiene poca evidencia para refinar reglas nocturnas. Aprende «de noche, casi siempre moto», pero los casos raros apenas los ve.

## 3. ¿Por qué caen las bicicletas a las 21:00?

- El `README.md` lo dice en la parte de riesgos: «la bicicleta de noche y con lluvia también recibe penalizaciones».
- En el generador es una penalización de +30 al costo de la bicicleta cuando es de noche.
- Los números lo confirman: a las 20:00 la bicicleta gana 30.1 % de las veces, y a las 21:00 solo 6.3 %.
- La moto sube de 41.9 % a 75.5 %. Parte de ese salto es que a las 21:00 también desaparece el dron, así que sus envíos se reparten entre los demás medios.

## 4. ¿Por qué le cuesta al árbol representar «de noche»?

- «De noche» son dos tramos separados del reloj: 21 a 23 y 0 a 5. Un árbol solo puede cortar con «hora ≤ X».
- Necesita como mínimo **2 preguntas** (`hora ≤ 5.5` y `hora ≤ 20.5`).
- Además, la noche queda repartida en dos ramas distintas, y cualquier regla posterior (la de la bicicleta, por ejemplo) hay que aprenderla dos veces, cada vez con menos datos.

## Para pensar

### Cómo calcularla

- Con las columnas que ya existen: `es_noche = ((hora_salida >= 21) | (hora_salida < 6)).astype(int)`.
- Así «de noche» se vuelve una sola pregunta (`es_noche ≤ 0.5`) en lugar de dos.

### Cómo comprobar que ayudó

Se entrenó el mismo árbol de `entrenar_arbol.py`, con las mismas semillas, con y sin `es_noche`.

**Partición de `entrenar_arbol.py`**

| Profundidad | Sin `es_noche` | Con `es_noche` |
| --- | --- | --- |
| 4 | 79.05 % | 79.05 % |
| 6 | 84.20 % | 85.60 % |
| 8 | 92.10 % | 92.95 % |

**Validación cruzada de 5 particiones**

| Profundidad | Sin `es_noche` | Con `es_noche` |
| --- | --- | --- |
| 6 | 85.3 % | 86.4 % |
| 8 | 92.1 % | 92.3 % |

# Actividad 3 — Anatomía de los errores: resultados

## Predicción


- Una bicicleta real nunca se predijo como camioneta (0 casos). La confusion mas frecuente es que camionetas reales se predijeron como bicicleta.

## 1. Errores y confusiones

- Hay 158 errores (7.9 %).
- Las tres más frecuentes son moto→bicicleta (46), camioneta→moto (32) y moto→dron (29).
- Se confunden medios parecidos: los tres primeros pares son moto, bicicleta y dron, que compiten por paquetes ligeros y cortos. Casi no hay errores entre medios muy distintos, como dron y camioneta (4), o bicicleta y camioneta (9).
- Eso indica que el modelo entendió la estructura general y falla en las fronteras donde dos medios cuestan casi lo mismo.

## 2. Moto → dron 

- 26 son de noche (entre las 21:00 y las 5:00). Esas las corrigen las reglas del negocio, porque el dron no puede volar de noche.
- Las 3 que no corrigen son de día (7.35 km, 12.14 km y 7.55 km, a las 17, 13 y 18 h), con clima despejado y zona residencial.
- Lo que tienen en común: el dron sí era posible, así que son casos de frontera donde el costo es casi igual. El ruido del generador (8 % en el costo y 3 % en etiquetas) hace que la moto gane algunas veces.
- Se conecta con la Actividad 2: es el problema de representar «de noche» con cortes de hora.

## 3. Moto → bicicleta

- No es la distancia. El rango es de 1.35 a 6.89 km, con promedio de 4.08 km; solo 3 pasan de 6.7 km, así que casi ninguno está cerca del límite de 7 km.
- 44 de 46 eran posibles en bicicleta (solo 2 pesan más de 8 kg), así que las reglas casi no los corrigen.
- Lo que los distingue de las 539 bicicletas bien acertadas:

| Columna | moto→bici (errores) | bicicletas acertadas |
| --- | --- | --- |
| Prioridad `mismo_dia` | 48 % | 12 % |
| Prioridad `normal` | 22 % | 58 % |
| Clima despejado | 52 % | 85 % |
| Lluvia | 24 % | 2 % |
| Viento fuerte | 24 % | 13 % |

- La distancia sí cambia un poco (4.08 km contra 3.55 km), pero lo decisivo es la combinación de urgencia y clima. En el generador, cada minuto pesa 2 veces más en `mismo_dia` que en `express`, y la lluvia frena a la bicicleta y suma +40 de penalización.

## Reglas del negocio sobre todos los errores

- Las reglas corrigen 31 de los 158 errores (26 moto→dron, 3 camioneta→moto y 2 moto→bicicleta).
- La exactitud sube de 92.1 % a 93.65 %. Los otros 127 errores son decisiones «posibles pero no óptimas», y las reglas no pueden ver eso.

## ¿Qué pasa con otro `random_state`?

- Con otro valor se obtiene una partición de prueba distinta. Esos envíos habrían sido, en gran parte, datos de entrenamiento del modelo guardado: entre 1 578 y 1 628 de los 2 000 envíos de prueba nuevos ya estaban en el entrenamiento.
- Medido con las semillas 0, 1, 7 y 123, el modelo guardado dio entre 90.85 % y 93 %, pero esos números no son una evaluación honesta, porque el modelo ya vio la mayoría de esos envíos.
- Con este árbol (profundidad 8, `min_samples_leaf=5`) el efecto es leve, pero con un modelo más profundo o un Random Forest sería grave.
- Si se quiere analizar otra partición, hay que reentrenar con ese mismo `random_state`.

## Para pensar 

- Arreglaría moto→bicicleta: es el error más frecuente (46) y las reglas casi no lo tocan.
- Lo arreglaría cambiando el modelo, no los datos ni las reglas:
  - **Reglas:** no hay nada que prohibir, porque la bicicleta era posible en 44 de 46.
  - **Datos:** el problema no parece de calidad, porque la información que lo explica (urgencia y clima) ya está en las columnas.
  - **Modelo:** es una interacción (urgencia × clima × distancia) que un árbol de profundidad 8 representa con dificultad. Se puede probar más profundidad, un Random Forest o una columna que combine urgencia y clima, y comprobarlo con validación cruzada.
- Otro argumento válido sería elegir moto→dron de noche, que cuesta cero en producción porque las reglas ya lo corrigen, o priorizar por el costo real de equivocarse. Se califica el argumento, no la conclusión.

# Actividad 4 — ¿Qué columnas usa de verdad el modelo?: resultados

## Predicción
Catorce columnas de la más importante a la menos importante para elegir el medio. 
distancia_km ✓
peso_kg ✓
volumen_l ✓
refrigerado ✓
zona_destino ✓
prioridad ✓
clima ✓
hora_salida ✓
trafico ✓
fragil ✓
valor_declarado_mxn ✓
largo_cm ✓
ancho_cm ✓
alto_cm ✓

## 1. Las cuatro columnas más importantes

- Son `distancia_km` (0.322), `volumen_l` (0.193), `clima` (0.144) y `refrigerado` (0.131). `peso_kg` queda muy cerca, en quinto lugar (0.126).
- Coinciden con las primeras preguntas del árbol del paso 8: la raíz pregunta `distancia_km ≤ 7.01`; en ambas ramas la segunda es `volumen_l` (≤ 90.1); después aparece `clima_lluvia` en la rama corta y `refrigerado` en la larga; `peso_kg` y `fragil` entran un nivel más abajo.
- Contra su predicción: la comparación es suya. Una sorpresa frecuente es `refrigerado`: solo el 5 % de los envíos lo son, pero separa a la camioneta de todo lo demás con una sola pregunta, y por eso pesa tanto.

## 2. Qué pasa al quitar una columna

- La que más baja la exactitud es `distancia_km`: de 92.10 % a 79.30 % (−12.8 puntos).
- Le siguen `clima` (−7.65), `refrigerado` (−4.25) y `hora_salida` (−3.00).
- No la cambian nada `zona_destino`, `valor_declarado_mxn` y `trafico` (0.00); `prioridad` incluso sube 0.05, es decir, un envío más de 2 000. Con la validación cruzada las diferencias de estas columnas están dentro de 0.1 puntos, que es ruido.
- `largo_cm`, `ancho_cm` y `alto_cm` bajan solo 0.05 puntos (un envío): `volumen_l` ya se calcula con ellas.
- Ojo con dos casos donde la importancia engaña:
  - `volumen_l` tiene la segunda importancia más alta, pero quitarlo cuesta solo 1.5 puntos, y `peso_kg` igual (1.7). Se parecen entre sí (en los datos, el volumen se genera a partir del peso), así que el árbol se apoya en una cuando falta la otra.
  - `hora_salida` tiene importancia 0.059, pero quitarla cuesta más que quitar `peso_kg` o `volumen_l`. La importancia mide cuánto se usa la columna en el árbol; el experimento mide qué tan reemplazable es.

## 3. Zona con importancia cero, pero sin drones en el centro

La zona de destino vale 0.0000 y, aun así, el modelo nunca predice dron en el centro. Hay dos razones distintas:

- **El modelo lo logra sin la zona, con la distancia.** El centro nunca pasa de 5.91 km, y el modelo solo predice dron a partir de 7.01 km (justo la primera pregunta del árbol). Así, `distancia_km` hace de sustituto de la zona: de los 952 drones que predice en todo el dataset, 659 son residenciales y 293 de periferia, ninguno del centro.
- **Las reglas del negocio lo garantizan.** `es_posible` sí usa la zona, y no deja pasar un dron al centro.

Para comprobarlo se hicieron dos experimentos:

- Cambiar la zona de los 10 000 envíos a `centro`, `residencial`, `periferia` o `rural`: cambian 0 predicciones en todos los casos.
- Mover al centro los 948 drones reales: el modelo sigue diciendo dron en 800, pero `es_posible` no deja pasar ninguno (0 de 948).

Esto tiene un lado malo: de los 948 drones reales, 87 (9 %) están a 6 km o menos, y el modelo no puede acertarlos porque nunca predice dron por debajo de 7.01 km. Es una limitación que se le ve a un árbol que ignora la zona.

## Para pensar (un punto de partida)

**El modelo funciona igual con menos datos**

| Columnas usadas | Exactitud en prueba | Validación cruzada |
| --- | --- | --- |
| Las 14 | 92.10 % | 92.12 % |
| 10 (sin zona, tráfico, valor y prioridad) | 92.15 % | 92.09 % |
| 7 (y además sin largo, ancho y alto) | 92.10 % | 92.02 % |

**Razones para seguir pidiendo un dato que el modelo no usa**

- **Las reglas lo necesitan.** `es_posible` usa la zona (para el dron en el centro y la bicicleta en zonas rurales), aunque el modelo la ignore. Esto es independiente del modelo.
- **El modelo no es definitivo.** `prioridad` casi no se usa (importancia 0.003), pero en la Actividad 3 los envíos `mismo_dia` eran el 48 % de las confusiones moto→bicicleta. Es un indicio de que el árbol la está desaprovechando, no de que sobre. Un modelo mejor podría usarla.
- **Razones del negocio.** El valor declarado puede servir para seguros o cobros, y la prioridad para tarifas y plazos, aunque no influyan en el medio recomendado.
- **Dato derivado.** Si la app pide largo, ancho y alto, puede calcular `volumen_l` sola, en lugar de pedir un cuarto dato.

**Razones para dejar de pedir o pedir distinto**

- Cada campo extra cuesta tiempo y errores de captura.
- Varios no hace falta preguntarlos a la persona: `clima`, `tráfico`, `hora_salida`, `zona_destino` y `distancia_km` pueden obtenerse de la dirección y de servicios externos.

**Una conclusión posible:** quitar los campos que ni el modelo ni las reglas ni el negocio necesitan, obtener automáticamente los que no dependen de la persona, y no eliminar un dato solo porque este árbol, con esta exactitud, no lo use. Se califica el argumento, no la conclusión.

# Actividad 5 — El dron es minoría: ¿hay que balancear el dataset?: resultados


## Parte A — Pensar antes de tocar los datos

### 1. La exactitud engaña

- Un «modelo» que nunca dice dron y acierta todo lo demás tendría 90.5 % de exactitud. Uno que siempre dice moto tendría 45.8 %.
- El árbol real acierta 92.1 %: solo 1.6 puntos más que un «modelo» que ignora al dron por completo. La exactitud casi no se entera de lo que pasa con la clase minoritaria.
- En su lugar, las medidas del paso 7: precision, recall y f1 de cada clase, y la matriz de confusión. Para el dron, el recall responde «¿cuántos drones reales encontró?» y la precision «¿cuántos de los que llamó dron lo eran?».

### 2. ¿Por qué hay pocos drones?

- No es un error de los datos: refleja cómo funciona la empresa. Según el `README.md`, el dron solo se puede usar con paquetes de hasta 2.5 kg y 12 L, a 15 km o menos, con clima despejado, de 6:00 a 20:59 y fuera del centro.
- Eso cambia la decisión: la proporción de 9.5 % es información real. Balancear no corrige un defecto de los datos; cambia lo que el modelo cree sobre qué tan frecuente es el dron. Hay que justificarlo por el costo de los errores, no por «verse parejo».

### 3. ¿Antes o después de separar?

- Después, y solo el conjunto de entrenamiento. La prueba no se balancea.
- Si se repiten ejemplos antes de separar, copias idénticas terminan en entrenamiento y en prueba: el modelo ya vio lo que se le pregunta. Y la prueba tiene que parecerse a la realidad que el modelo va a enfrentar (9.5 % de drones); si se balancea, la precision cambia de significado (se ve en las trampas).

## Parte B — Probar estrategias

Todas se evaluaron con los mismos 2 000 envíos de prueba, con un árbol igual al del paso 6 (profundidad 8, `min_samples_leaf=5`). Cada estrategia se aplica solo al entrenamiento:

- **Quitar sobrantes:** todas las clases se reducen a 758 envíos, el tamaño del dron.
- **Repetir drones:** se repiten drones (con reemplazo) hasta igualar a la moto (3 663).
- **Drones nuevos:** se corre `generar_dataset.py --filas 40000 --semilla 7` y se agregan drones de ese archivo hasta igualar a la moto.
- **class\_weight:** el dataset no cambia; se le dice al árbol que un dron pesa 4.8 veces más (la proporción moto/dron), o `'balanced'`, que equilibra las cuatro clases.

| Estrategia | Envíos de entrenamiento | Exactitud | Precision dron | Recall dron | Veces que predice dron | Sugerencias imposibles |
| --- | --- | --- | --- | --- | --- | --- |
| Sin balancear | 8 000 | 92.1 % | 83.9 % | 90.5 % | 205 | 31 |
| Quitar sobrantes | 3 032 | 91.4 % | 86.8 % | 93.2 % | 204 | 25 |
| Repetir drones | 10 905 | 90.4 % | 75.7 % | 100.0 % | 251 | 44 |
| Drones nuevos del generador | 10 905 | 90.0 % | 72.2 % | 100.0 % | 263 | 56 |
| class\_weight dron ×4.8 | 8 000 | 90.4 % | 75.7 % | 100.0 % | 251 | 44 |
| class\_weight='balanced' | 8 000 | 90.3 % | 76.6 % | 100.0 % | 248 | 35 |

Las sugerencias imposibles se cuentan con `es_posible` sobre las 2 000 predicciones, de cualquier medio.

Si además se aplican las reglas del negocio (se elige el mejor del ranking que sí es posible, como en `recomendar_medio`):

| Estrategia | Exactitud con reglas | Precision dron con reglas | Recall dron con reglas |
| --- | --- | --- | --- |
| Sin balancear | 93.6 % | 96.1 % | 90.5 % |
| Quitar sobrantes | 91.7 % | 92.2 % | 93.2 % |
| Repetir drones | 92.2 % | 83.7 % | 100.0 % |
| Drones nuevos del generador | 92.2 % | 83.7 % | 100.0 % |
| class\_weight dron ×4.8 | 92.2 % | 83.7 % | 100.0 % |
| class\_weight='balanced' | 91.6 % | 83.7 % | 100.0 % |

Hy solo 190 drones en la prueba. Con validación cruzada de 5 (balanceando solo el entrenamiento de cada pliegue), el árbol sin balancear tiene recall de 83.9 % ± 2.8, no 90.5 %: esta partición le favorece. La conclusión sobre el recall es más fuerte de lo que sugiere la tabla anterior.

| Estrategia (validación cruzada) | Precision dron | Recall dron |
| --- | --- | --- |
| Sin balancear | 83.9 % ± 1.5 | 83.9 % ± 2.8 |
| Repetir drones | 75.5 % ± 2.8 | 98.1 % ± 1.3 |
| class\_weight='balanced' | 75.4 % ± 1.1 | 98.1 % ± 1.3 |
| Quitar sobrantes | 73.0 % ± 3.6 | 98.2 % ± 1.4 |

### Trampa a propósito

**Trampa 1: repetir drones antes de separar.** Se repitieron los drones en todo el dataset y después se separó 80/20.

- Resultado: exactitud 91.6 %, precision dron 92.3 %, recall dron 98.3 %.
- Frente al árbol sin balancear (83.9 % y 90.5 %), parece que mejoran precision y recall a la vez, algo que ninguna estrategia honesta consiguió.
- Por qué es falso: 901 de los 2 726 envíos de prueba (33 %) son copias idénticas de drones que están en el entrenamiento, así que el árbol los reconoce porque los memorizó. Además, la prueba ahora tiene 33.6 % de drones en lugar de 9.5 %, y con tantos drones los falsos positivos pesan menos en la precision.
- El modelo no mejoró: cambió la medición.

**Trampa 2: balancear también la prueba.** Se midió el árbol sin balancear con una prueba de 760 envíos (190 de cada medio).

- Resultado: la precision del dron sube de 83.9 % a 95.6 %, con el mismo recall (90.5 %) y el mismo modelo.
- Por qué es falso: al quitar envíos de otros medios, el modelo tiene menos oportunidades de llamar dron a algo que no lo es. En la plataforma la proporción real es 9.5 %, así que esa precision no la va a ver nunca.

## Parte C — Interpretar

### 1. Recall sube, precision baja

- Las estrategias de balanceo encuentran los 190 drones (recall 100 %), pero llaman dron a 248–263 envíos en lugar de 205. Los falsos positivos pasan de 33 a 58–61, y 37 de ellos son bicicletas.
- Mecanismo: repetir un dron, o pesarlo más, hace que equivocarse con él cueste más al construir el árbol, y la frontera se mueve hacia el dron. Entra todo lo que antes quedaba fuera, incluidos casos de la frontera que no eran dron.
- Una parte de la ganancia es aprendizaje real: hay 9 drones de la prueba a 6 km o menos, y el árbol sin balancear no acierta ninguno (nunca predice dron por debajo de 7.01 km); los balanceados aciertan los 9. Otra parte es simplemente decir «dron» más veces.
- Un modelo que llamara dron a todo tendría recall de 100 % y precision de 9.5 %: por eso hay que mirar las dos medidas juntas.

### 2. ¿Menos datos de entrenamiento?

- «Quitar sobrantes» entrena con 3 032 envíos en lugar de 8 000 (62 % menos): descarta 4 968 ejemplos de moto, bicicleta y camioneta.
- Se pierde información de las otras tres clases: la exactitud con reglas baja de 93.6 % a 91.7 % y es la estrategia más inestable en validación cruzada (±3.6 en precision).

### 3. Estrategias que son la misma idea

- «Repetir drones» y «class\_weight dron ×4.8» dan números idénticos (90.4 %, 75.7 %, 100 %, 251 predicciones, 44 imposibles). Repetir un ejemplo 4.8 veces equivale a darle peso 4.8, porque el árbol cuenta ejemplos para calcular las proporciones en cada hoja.
- `class_weight='balanced'` y «Drones nuevos» también dan números parecidos: aunque los ejemplos sean nuevos, el efecto que domina es el mismo, que el modelo ve muchos más drones (33.6 % del entrenamiento, en lugar de 7.6 %... ver nota) y mueve su frontera igual.
- Se diferencian en el costo: `class_weight` no necesita guardar ni generar datos; repetir y generar sí.

### 4. ¿Sigue significando lo mismo la «confianza»?

No.

- Sin balancear, el modelo está bien calibrado: cuando dice 84 % (205 envíos) el 83.9 % son drones, y su probabilidad media de dron es 10.2 % contra 9.5 % real.
- Con `class_weight='balanced'` la probabilidad media sube a 11.6 %, y en los envíos donde dice entre 50 % y 70 % (68 envíos, media 68.8 %) solo 26.5 % son drones.
- Con «Quitar sobrantes» hay 8 envíos donde dice 72.7 % y ninguno es dron.
- El modelo vio drones en 25–33 % del entrenamiento en lugar de 9.5 %, así que sobreestima la probabilidad. Después de balancear, «confianza 84 %» ya no significa que 84 de cada 100 así sean dron: sirve para ordenar, no como frecuencia real.

## Parte D — Decidir

### Qué cuesta más

- El dataset no trae dinero. En el generador, el dron cuesta más que la bicicleta (tarifa base 40 contra 20, y 3 contra 2 por km) y tiene penalizaciones por valor alto y fragilidad; los falsos positivos de los modelos balanceados son sobre todo bicicletas (37 de 61) y motos (16).
- Como la etiqueta es el costo mínimo con ruido de 8 %, las alternativas casi empatan, así que ambos errores suelen ser baratos. Para decidir hace falta que la empresa ponga números: cuánto cuesta un dron de más y cuánto un dron perdido.

### Qué errores corrigen las reglas

- Las reglas solo vetan, nunca agregan. Corrigen las sugerencias de dron que son imposibles (de noche, en el centro, con lluvia o muy pesadas): 26 de los 33 falsos positivos del árbol sin balancear, y 24 de 61 en el que repite drones.
- No pueden recuperar un dron que el modelo no sugirió: con reglas, el recall queda igual (90.5 % y 100 %). El error «no usar dron cuando convenía» es el que las reglas no tocan.
- Tras las reglas, el árbol sin balancear tiene precision dron de 96.1 % y exactitud de 93.6 %; los balanceados, 83.7 % y entre 91.6 % y 92.2 %.

### Pesos intermedios (validación cruzada de 5, con reglas del negocio)

| Peso del dron | Exactitud | Precision dron | Recall dron | Veces que predice dron (por pliegue) |
| --- | --- | --- | --- | --- |
| 1 (sin balancear) | 93.3 % | 94.9 % | 83.9 % | 167.6 |
| 1.5 | 93.2 % | 94.9 % | 83.9 % | 167.6 |
| 2 | 93.1 % | 94.7 % | 84.0 % | 168.0 |
| 3 | 93.0 % | 92.4 % | 87.7 % | 180.6 |
| 4.8 (balanceo completo) | 92.3 % | 83.6 % | 97.9 % | 222.2 |

De 1 a 4.8, el modelo encuentra unos 27 drones más por pliegue (de unos 190) y manda en dron unos 28 envíos que no lo eran: cerca de uno por uno, con un punto menos de exactitud.

### Si mañana la empresa compra el doble de drones

- El dataset no tiene una columna de flota: la etiqueta es «el mejor medio si existe». Comprar más drones no cambia las etiquetas por sí solo; las cambia si baja el costo o el tiempo de espera del dron, y entonces el dron ganaría en más casos de frontera.
- En ese caso la proporción de drones sube y el modelo sin balancear, que aprendió 9.5 %, se quedaría corto. Un peso fijado para la proporción actual también quedaría desajustado. Con cualquiera de los dos hay que reentrenar con datos nuevos (el generador sirve para simularlo) y volver a elegir el peso.

### Recomendación 

- **No usar el balanceo completo** en la plataforma. Mejora el recall del dron a costa de casi doblar los falsos positivos, pierde algo de exactitud y deja de dar probabilidades interpretables.
- **Mantener el modelo sin balancear con las reglas del negocio.** Con reglas es el más exacto (93.6 %), el más preciso con el dron (96.1 %) y su «confianza» sigue siendo una frecuencia real.
- **Si la empresa decide que perder un dron cuesta más que mandar uno de más,** probar un peso moderado (alrededor de 3) y reentrenar cuando cambie la flota.
- Su punto débil, que conviene decir con claridad: no sugiere dron por debajo de 7.01 km (0 de 9 drones cortos en la prueba), y las reglas no pueden arreglarlo.
