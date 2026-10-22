# Análisis de los 6 datasets y de los modelos de árbol de decisión

- Los modelos `modelo_medios_1.joblib` a `modelo_medios_6.joblib` se entrenaron con
  `entrenar_arbol.py` (árbol de decisión, `max_depth=8`, `min_samples_leaf=5`,
  `random_state=42`).
- Para comparar de forma justa se usó la misma partición que el script de
  entrenamiento: 80 % entrenamiento y 20 % prueba, estratificada y con
  `random_state=42`.

## 1. Análisis de cada dataset

| Dataset | Clases | Distribución de etiquetas | Rasgos que lo distinguen |
|---|---|---|---|
| envios1 | 4 | 25,0 % cada una | Perfectamente balanceado. 78,1 % clima despejado; solo 8,2 % rural. Perfiles de clase muy limpios (bicicleta y dron nunca con lluvia ni refrigerado). |
| envios2 | **5** | moto 34,7 %, bicicleta 26,2 %, **eskuter 16,2 %**, camioneta 14,4 %, dron 8,6 % | Único dataset con la clase `eskuter`. 70,2 % despejado, 9,0 % rural, solo 4,5 % refrigerado. |
| envios3 | 4 | moto 73,7 %, camioneta 15,8 %, bicicleta 7,7 %, dron 2,8 % | Muy desbalanceado. Clima adverso: 34,0 % lluvia y 27,5 % viento fuerte; 23,2 % rural. |
| envios4 | 4 | moto 57,2 %, bicicleta 18,8 %, camioneta 16,9 %, dron 7,1 % | 34,8 % lluvia, 9,7 % rural. Similar a envios5 pero con más moto. |
| envios5 | 4 | moto 45,8 %, bicicleta 28,0 %, camioneta 16,8 %, dron 9,5 % | Es el más parecido al dataset por defecto del README. 70,1 % despejado, 10,0 % rural. |
| envios6 | 4 | moto 63,1 %, camioneta 31,9 %, bicicleta 4,2 %, dron 0,7 % | 45,7 % lluvia, 37,8 % rural y 23,6 % refrigerado. Bicicleta y dron son casos raros. |

Ningún dataset contiene etiquetas imposibles según las reglas del README (por
ejemplo, bicicletas en zona rural o drones con lluvia): las 6 fuentes respetan
las restricciones de peso, volumen, distancia, clima, horario y zona.



`eskuter` no existe en el generador `generar_dataset.py` ni en los otros cinco
CSV. En envios2 ocupa el 16,2 % de las filas y tiene un perfil propio:

| Variable | Mediana de eskuter | Comportamiento |
|---|---|---|
| distancia_km | 9,1 | Entre bicicleta (3,5) y camioneta/moto (9-11) |
| peso_kg | 3,3 | Similar a moto/bicicleta |
| volumen_l | 15,0 | Similar a moto |
| zona rural | 0,0 % | Igual que bicicleta y dron |
| refrigerado | 0,0 % | Igual que bicicleta, moto y dron |
| lluvia | 36,1 % | Puede operar con lluvia |
| hora | 6 a 20 | Sin operación nocturna |

Es decir, es una clase intermedia entre bicicleta y moto, con la que se confunde
con facilidad.

## 2. Resultados de cada modelo en su propio dataset

| Modelo | Dataset | Exactitud train | Exactitud test | Brecha (sobreajuste) | Nodos / hojas | Variables dominantes |
|---|---|---|---|---|---|---|
| modelo_1 | envios1 | 99,6 % | **99,2 %** | 0,4 pts | 61 / 31 | peso 0,49, distancia 0,31, refrigerado 0,13 |
| modelo_2 | envios2 | 79,8 % | **76,0 %** | 3,8 pts | 127 / 64 | distancia 0,34, volumen 0,17, peso 0,15 |
| modelo_3 | envios3 | 94,4 % | **94,4 %** | 0,0 pts | 73 / 37 | volumen 0,30, refrigerado 0,22, distancia 0,19 |
| modelo_4 | envios4 | 92,8 % | **91,9 %** | 0,9 pts | 103 / 52 | distancia 0,30, volumen 0,18, refrigerado 0,16 |
| modelo_5 | envios5 | 92,6 % | **92,1 %** | 0,5 pts | 93 / 47 | distancia 0,32, volumen 0,19, refrigerado 0,13 |
| modelo_6 | envios6 | 96,4 % | **95,3 %** | 1,0 pts | 85 / 43 | **refrigerado 0,62**, volumen 0,20, distancia 0,10 |

Observaciones:

- `modelo_1` aprende muy pocas reglas (31 hojas) y aun así acierta el 99,2 %.
  Esto es compatible con que envios1 sea un dataset balanceado y con etiquetas
  casi deterministas. Su señal principal es peso + distancia + refrigerado.
- `modelo_2` es el que menos acierta (76,0 %) y el que más sobreajusta
  (3,8 puntos de brecha). No es solo por el árbol: su dataset tiene una quinta
  clase que se solapa con moto.
- `modelo_6` acierta mucho (95,3 %) pero depende en un 62 % de `refrigerado`.
  Con esa sola variable separa camioneta del resto y acierta la mayoría, porque
  moto + camioneta son el 95 % de las filas. Su macro-F1 es menor (85,3 %).

## 3. Evaluación cruzada: cada modelo sobre los 6 datasets

Exactitud (%) sobre la partición de prueba de cada dataset:

| Modelo \ Datos | envios1 | envios2 | envios3 | envios4 | envios5 | envios6 |
|---|---:|---:|---:|---:|---:|---:|
| modelo_1 | **99,2** | 50,7 | 60,6 | 59,2 | 59,6 | 67,2 |
| modelo_2 | 84,8 | **76,0** | 78,7 | 73,7 | 77,0 | 78,0 |
| modelo_3 | 95,0 | 76,1 | **94,4** | 91,0 | 91,5 | 95,8 |
| modelo_4 | 94,8 | 75,2 | 94,2 | **91,9** | 91,0 | 95,4 |
| modelo_5 | 95,6 | 76,9 | 94,8 | 92,0 | **92,1** | 95,6 |
| modelo_6 | 94,8 | 74,4 | 93,0 | 89,9 | 90,3 | **95,4** |

Macro-F1 (%) sobre la misma partición de prueba:

| Modelo \ Datos | envios1 | envios2 | envios3 | envios4 | envios5 | envios6 |
|---|---:|---:|---:|---:|---:|---:|
| modelo_1 | **99,2** | 42,1 | 47,2 | 54,3 | 56,6 | 48,5 |
| modelo_2 | 70,9 | **76,7** | 68,0 | 66,0 | 68,3 | 62,3 |
| modelo_3 | 95,0 | 66,9 | 88,2 | 87,1 | 90,4 | 85,9 |
| modelo_4 | 94,7 | 65,9 | 87,7 | 88,3 | 89,6 | 84,2 |
| modelo_5 | 95,5 | 68,4 | 89,7 | 88,8 | 91,2 | 86,7 |
| modelo_6 | 94,7 | 65,0 | 84,0 | 85,3 | 88,9 | 85,3 |

### Lectura de la matriz

- **modelo_5 es el que mejor generaliza**: 91,0 % de exactitud media en datasets
  ajenos (94,5 % en los datasets de 4 clases distintos al suyo, excluyendo
  envios2) y 85,8 % de macro-F1 media. Sigue de cerca a modelo_3 y modelo_4:
  los tres se entrenaron
  con datasets parecidos (envios3, 4 y 5) y se transfieren bien entre sí
  (91-96 %).
- **modelo_1 es un especialista**: 99,2 % en su propio dataset, pero solo
  59,5 % de media en los demás. Aprende los umbrales y las proporciones de
  envios1, que no representan a las otras fuentes.
- **modelo_2 es el más plano**: 73,7-84,8 % en todos los datasets. No destaca
  en ninguno, pero tampoco se derrumba. La razón es que arrastra la clase
  `eskuter` y que su dataset es más difícil.
- **Los modelos 3-6 aciertan 94-96 % en envios1**, aunque nunca lo vieron. Eso
  confirma que envios1 es un dataset limpio y fácil, no que esos modelos sean
  mejores en general.
- **envios6 es el dataset más "fácil" en apariencia**: los modelos 3-6
  aciertan 95-96 %. Pero se debe a su fuerte desbalance (moto + camioneta =
  95 %) y a la señal de `refrigerado`; su macro-F1 se queda en 84-87 %.

## 4. Por qué envios2 y sus modelos rinden distinto

El modelo 2 es el único que puede predecir `eskuter`. Los otros cinco modelos
**nunca predicen esa clase** (0 veces en los cinco datasets de 4 clases). Por
eso, sobre envios2 tienen un techo estructural del 83,8 % de exactitud: aunque
clasifiquen perfecto las otras cuatro clases, la clase `eskuter` siempre les
cuenta como error. En la práctica logran 74-77 %, cerca de ese techo.

Desempeño de modelo_2 en la prueba de envios2:

| Clase real | Precisión | Recall | F1 |
|---|---:|---:|---:|
| bicicleta | 0,860 | 0,929 | 0,893 |
| camioneta | 1,000 | 0,813 | 0,897 |
| dron | 0,746 | 0,842 | 0,791 |
| eskuter | 0,479 | 0,625 | 0,542 |
| moto | 0,776 | 0,654 | 0,710 |
| **global (exactitud)** | | | **0,760** |

Los errores se concentran en el par moto/eskuter:

- 196 filas de moto predichas como eskuter.
- 86 filas de eskuter predichas como moto.
- 24 de eskuter como bicicleta y 11 como dron.

Es un problema de solapamiento real entre clases, no solo de falta de datos.
Retirar `eskuter` de envios2 (o añadirla a los otros datasets) cambiaría por
completo la comparación.

## 5. Comparación de las estructuras aprendidas

| Modelo | Variables más usadas (importancia) | Qué está aprendiendo |
|---|---|---|
| modelo_1 | peso 0,49; distancia 0,31; refrigerado 0,13 | Reglas simples de capacidad y distancia. Dataset balanceado. |
| modelo_2 | distancia 0,34; volumen 0,17; peso 0,15; refrigerado 0,11; lluvia 0,09 | Más reglas (64 hojas) para separar cinco clases que se solapan. |
| modelo_3 | volumen 0,30; refrigerado 0,22; distancia 0,19; peso 0,12 | Prioriza capacidad y refrigeración; dataset con clima adverso. |
| modelo_4 | distancia 0,30; volumen 0,18; refrigerado 0,16; peso 0,15 | Similar a modelo_5, con más peso a la distancia. |
| modelo_5 | distancia 0,32; volumen 0,19; refrigerado 0,13; peso 0,13 | El más equilibrado en el uso de variables. |
| modelo_6 | refrigerado 0,62; volumen 0,20; distancia 0,10 | Casi todo lo decide con `refrigerado`: separa camioneta del resto. |

## 6. Conclusiones

1. Los seis datasets comparten el mismo esquema y respetan las reglas de
   negocio, pero **no son muestras equivalentes**: cambian el balance de clases,
   el clima, la zona y hasta el conjunto de etiquetas (envios2).
2. No se debe comparar a los modelos solo por exactitud. Los datasets
   desbalanceados (envios3 y envios6) inflan la exactitud; macro-F1 y el recall
   por clase muestran el costo real en bicicleta y dron.
3. **modelo_1 es el mejor en su dataset (99,2 %) pero el peor al transferir**
   (59,5 % de media). envios1 está balanceado artificialmente (25 % por clase),
   algo que no ocurre en las demás fuentes ni en el dataset por defecto del
   README.
4. **modelo_2 es el único que reconoce `eskuter`** y el más estable entre
   datasets, pero su exactitud propia (76,0 %) es la más baja por el
   solapamiento moto/eskuter.
5. **modelo_5 es el mejor candidato para un modelo único** si se busca
   transferencia entre datasets de 4 clases, con 94,5 % medio en los datasets
   ajenos de 4 clases (excluyendo envios2).
6. Para producción conviene **unificar el conjunto de etiquetas** y entrenar con
   datos de todas las fuentes. Si `eskuter` es un medio real, hay que incluirla
   en todos los datasets; si no, hay que filtrar esas filas de envios2.

