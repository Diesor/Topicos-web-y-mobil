"""Actividad 3 - Anatomía de los errores.
"""
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

from usar_modelo import es_posible

warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)

NUMERICAS = [
    "distancia_km", "peso_kg", "largo_cm", "ancho_cm", "alto_cm", "volumen_l",
    "fragil", "refrigerado", "valor_declarado_mxn", "hora_salida",
]
CATEGORICAS = ["prioridad", "zona_destino", "clima", "trafico"]
OBJETIVO = "medio_recomendado"

datos = pd.read_csv("envios_medios.csv")
x = datos[NUMERICAS + CATEGORICAS]
y = datos[OBJETIVO]

# Misma partición que usó entrenar_arbol.py: así x_prueba son envíos que el modelo NUNCA vio.
x_entreno, x_prueba, y_entreno, y_prueba = train_test_split(
    x, y, test_size=0.2, stratify=y, random_state=42
)

modelo = joblib.load("modelo_medios.joblib")
prediccion = modelo.predict(x_prueba)
tabla = x_prueba.assign(real=y_prueba, predicho=prediccion)
errores = tabla[tabla["real"] != tabla["predicho"]]
print(f"Exactitud: {(prediccion == y_prueba.values).mean():.1%}  |  errores: {len(errores)}\n")

# --- Pregunta 1: matriz de confusión y las confusiones más frecuentes --------
etiquetas = sorted(y.unique())
print("Matriz de confusión (filas: real, columnas: predicho):")
print(pd.DataFrame(confusion_matrix(y_prueba, prediccion, labels=etiquetas),
                   index=etiquetas, columns=etiquetas), "\n")
print("Confusiones más frecuentes:")
print(errores.groupby(["real", "predicho"]).size().sort_values(ascending=False), "\n")

COLUMNAS_VER = ["distancia_km", "peso_kg", "volumen_l", "fragil", "valor_declarado_mxn",
                "prioridad", "zona_destino", "clima", "hora_salida", "trafico"]

# --- Pregunta 2: moto que el modelo mandó a dron -----------------------------
moto_dron = errores[(errores["real"] == "moto") & (errores["predicho"] == "dron")].copy()
moto_dron["noche"] = (moto_dron["hora_salida"] >= 21) | (moto_dron["hora_salida"] < 6)
moto_dron["dron_posible"] = moto_dron.apply(lambda fila: es_posible("dron", fila), axis=1)
print(f"Moto -> dron: {len(moto_dron)}  |  de noche: {moto_dron['noche'].sum()}  "
      f"|  las reglas lo corrigen: {(~moto_dron['dron_posible']).sum()}  "
      f"|  no lo corrigen: {moto_dron['dron_posible'].sum()}")
print("Los que las reglas no corrigen:")
print(moto_dron[moto_dron["dron_posible"]][COLUMNAS_VER], "\n")

# --- Pregunta 3: moto que el modelo mandó a bicicleta ------------------------
moto_bici = errores[(errores["real"] == "moto") & (errores["predicho"] == "bicicleta")].copy()
moto_bici["bici_posible"] = moto_bici.apply(lambda fila: es_posible("bicicleta", fila), axis=1)
print(f"Moto -> bicicleta: {len(moto_bici)}  |  bicicleta era posible: {moto_bici['bici_posible'].sum()}")
print("Distancia de esos envíos:")
print(moto_bici["distancia_km"].describe().round(2), "\n")

bici_acertadas = tabla[(tabla["real"] == "bicicleta") & (tabla["predicho"] == "bicicleta")]
print(f"Bicicletas que el modelo sí acertó: {len(bici_acertadas)}")
print("Promedios (moto->bici contra bicicletas acertadas):")
numericas_ver = ["distancia_km", "peso_kg", "volumen_l", "fragil", "valor_declarado_mxn", "hora_salida"]
print(pd.DataFrame({"moto->bici": moto_bici[numericas_ver].mean(),
                    "bici acertadas": bici_acertadas[numericas_ver].mean()}).round(2), "\n")
for columna in ["prioridad", "zona_destino", "clima", "trafico"]:
    print(pd.DataFrame({"moto->bici": moto_bici[columna].value_counts(normalize=True),
                        "bici acertadas": bici_acertadas[columna].value_counts(normalize=True)}).round(2), "\n")

# --- Qué corrigen las reglas del negocio sobre todos los errores -------------
errores = errores.assign(corrige=errores.apply(lambda fila: not es_posible(fila["predicho"], fila), axis=1))
print("Errores que corrigen las reglas, por tipo:")
print(errores.groupby(["real", "predicho"])["corrige"].agg(["size", "sum"])
      .sort_values("size", ascending=False), "\n")

probabilidades = modelo.predict_proba(x_prueba)
final = []
for i, (_, fila) in enumerate(x_prueba.iterrows()):
    ranking = sorted(zip(modelo.classes_, probabilidades[i]), key=lambda par: -par[1])
    final.append(next((medio for medio, _ in ranking if es_posible(medio, fila)), "camioneta"))
print(f"Exactitud con las reglas del negocio: {(np.array(final) == y_prueba.values).mean():.2%}\n")

# --- ¿Qué pasa con otro random_state? ----------------------------------------
print("Modelo guardado evaluado con otras particiones:")
for semilla in (0, 1, 7, 42, 123):
    _, x_otro, _, y_otro = train_test_split(x, y, test_size=0.2, stratify=y, random_state=semilla)
    ya_vistos = len(set(x_otro.index) & set(x_entreno.index))
    exactitud = (modelo.predict(x_otro) == y_otro.values).mean()
    print(f"  random_state={semilla:<4} exactitud {exactitud:.2%}  |  ya vistos en el entrenamiento: {ya_vistos} de {len(x_otro)}")
