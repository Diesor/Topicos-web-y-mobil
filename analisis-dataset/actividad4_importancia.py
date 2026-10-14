"""Actividad 4 - ¿Qué columnas usa de verdad el modelo?
"""
import warnings

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier, export_text

warnings.filterwarnings("ignore")
pd.set_option("display.width", 200)

NUMERICAS = [
    "distancia_km", "peso_kg", "largo_cm", "ancho_cm", "alto_cm", "volumen_l",
    "fragil", "refrigerado", "valor_declarado_mxn", "hora_salida",
]
CATEGORICAS = ["prioridad", "zona_destino", "clima", "trafico"]
OBJETIVO = "medio_recomendado"

datos = pd.read_csv("envios_medios.csv")
x = datos[NUMERICAS + CATEGORICAS]
y = datos[OBJETIVO]

# Misma partición del paso 4: los mismos 2 000 envíos de prueba en todas las comparaciones.
x_entreno, x_prueba, y_entreno, y_prueba = train_test_split(
    x, y, test_size=0.2, stratify=y, random_state=42
)

# --- Pregunta 1: importancias del modelo guardado ----------------------------
modelo = joblib.load("modelo_medios.joblib")
arbol = modelo.named_steps["arbol"]
nombres = [n.split("__", 1)[1] for n in modelo.named_steps["preparacion"].get_feature_names_out()]
por_columna_dummy = pd.Series(arbol.feature_importances_, index=nombres)

# Cada categoría se volvió varias columnas de 0/1 (one-hot): se suman para recuperar
# la importancia de la columna original (por ejemplo, clima_lluvia + clima_despejado + ...).
def columna_original(nombre):
    for c in CATEGORICAS:
        if nombre.startswith(c + "_"):
            return c
    return nombre

importancia = por_columna_dummy.groupby(columna_original).sum().sort_values(ascending=False)
print("Importancia por columna original (suma 1):")
print(importancia.round(4).to_string(), "\n")
print("Columnas con importancia 0:", list(importancia.index[importancia == 0]), "\n")

print("Primeros niveles del árbol (paso 8):")
print(export_text(arbol, feature_names=nombres, max_depth=3))

# --- Pregunta 2: quitar una columna y medir la exactitud ---------------------
def entrenar_sin(columna=None):
    numericas = [c for c in NUMERICAS if c != columna]
    categoricas = [c for c in CATEGORICAS if c != columna]
    preparacion = ColumnTransformer([
        ("numericas", "passthrough", numericas),
        ("categoricas", OneHotEncoder(handle_unknown="ignore"), categoricas),
    ])
    nuevo = Pipeline([
        ("preparacion", preparacion),
        ("arbol", DecisionTreeClassifier(max_depth=8, min_samples_leaf=5, random_state=42)),
    ])
    columnas = numericas + categoricas
    nuevo.fit(x_entreno[columnas], y_entreno)
    exactitud = (nuevo.predict(x_prueba[columnas]) == y_prueba).mean()
    cruzada = cross_val_score(
        nuevo, x[columnas], y, cv=StratifiedKFold(5, shuffle=True, random_state=0)
    ).mean()
    return exactitud, cruzada

base, base_cv = entrenar_sin()
print(f"\nÁrbol con las 14 columnas: {base:.2%} (prueba)  |  {base_cv:.2%} (validación cruzada)\n")

filas = []
for columna in NUMERICAS + CATEGORICAS:
    exactitud, cruzada = entrenar_sin(columna)
    filas.append({
        "columna": columna,
        "importancia": importancia[columna],
        "exactitud_sin": exactitud,
        "cambio_prueba": exactitud - base,
        "cambio_cruzada": cruzada - base_cv,
    })
tabla = pd.DataFrame(filas).sort_values("cambio_prueba").set_index("columna")
print("Qué pasa al quitar cada columna (cambio en puntos porcentuales):")
print((tabla.assign(
    importancia=tabla["importancia"].round(4),
    exactitud_sin=(tabla["exactitud_sin"] * 100).round(2),
    cambio_prueba=(tabla["cambio_prueba"] * 100).round(2),
    cambio_cruzada=(tabla["cambio_cruzada"] * 100).round(2),
)).to_string())

# --- Pregunta 3: ¿cómo evita el dron en el centro si la zona vale cero? ------
from usar_modelo import es_posible

centro = datos[datos["zona_destino"] == "centro"]
prediccion_total = modelo.predict(x)
drones_predichos = datos[prediccion_total == "dron"]
print(f"\nEnvíos al centro: {len(centro)}  |  distancia máxima en el centro: {centro['distancia_km'].max():.2f} km")
print(f"El modelo solo predice dron a partir de {drones_predichos['distancia_km'].min():.2f} km "
      f"(la primera pregunta del árbol es distancia <= 7.01)")
print("Predicciones de dron por zona:", pd.Series(drones_predichos["zona_destino"]).value_counts().to_dict())

# Experimento: cambiar solo la zona de todos los envíos y ver si cambia alguna predicción.
for zona in ["centro", "residencial", "periferia", "rural"]:
    cambiada = x.copy()
    cambiada["zona_destino"] = zona
    print(f"  zona = {zona:<12} predicciones que cambian: {(modelo.predict(cambiada) != prediccion_total).sum()}")

# Experimento: mandar al centro los drones reales. El modelo no se entera; las reglas sí.
drones = datos[datos[OBJETIVO] == "dron"][NUMERICAS + CATEGORICAS].copy()
drones["zona_destino"] = "centro"
sigue_dron = (modelo.predict(drones) == "dron").sum()
permitido = drones.apply(lambda fila: es_posible("dron", fila), axis=1).sum()
print(f"Drones reales movidos al centro: el modelo sigue diciendo dron en {sigue_dron} de {len(drones)}; "
      f"es_posible deja pasar {permitido}")
print(f"Drones reales a 6 km o menos: {(datos[datos[OBJETIVO] == 'dron']['distancia_km'] <= 6).sum()} "
      f"de {len(drones)} (el modelo no los puede acertar)")

# --- Para pensar: quitar varias columnas a la vez -----------------------------
print("\nQuitar varias columnas juntas (exactitud en prueba | validación cruzada):")
for nombre, quitar in [
    ("las 14 columnas", []),
    ("sin zona, tráfico, valor y prioridad", ["zona_destino", "trafico", "valor_declarado_mxn", "prioridad"]),
    ("y además sin largo, ancho y alto", ["zona_destino", "trafico", "valor_declarado_mxn", "prioridad",
                                          "largo_cm", "ancho_cm", "alto_cm"]),
]:
    numericas = [c for c in NUMERICAS if c not in quitar]
    categoricas = [c for c in CATEGORICAS if c not in quitar]
    preparacion = ColumnTransformer([
        ("numericas", "passthrough", numericas),
        ("categoricas", OneHotEncoder(handle_unknown="ignore"), categoricas),
    ])
    reducido = Pipeline([
        ("preparacion", preparacion),
        ("arbol", DecisionTreeClassifier(max_depth=8, min_samples_leaf=5, random_state=42)),
    ])
    columnas = numericas + categoricas
    reducido.fit(x_entreno[columnas], y_entreno)
    exactitud = (reducido.predict(x_prueba[columnas]) == y_prueba).mean()
    cruzada = cross_val_score(reducido, x[columnas], y, cv=StratifiedKFold(5, shuffle=True, random_state=0)).mean()
    print(f"  {nombre:<40} {len(columnas):>2} columnas  {exactitud:.2%} | {cruzada:.2%}")
