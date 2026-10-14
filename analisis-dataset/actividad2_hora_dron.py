"""Actividad 2 - La hora y el dron.
"""
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

pd.set_option("display.width", 200)

NUMERICAS = [
    "distancia_km", "peso_kg", "largo_cm", "ancho_cm", "alto_cm", "volumen_l",
    "fragil", "refrigerado", "valor_declarado_mxn", "hora_salida",
]
CATEGORICAS = ["prioridad", "zona_destino", "clima", "trafico"]
OBJETIVO = "medio_recomendado"

datos = pd.read_csv("envios_medios.csv")

# --- Pregunta 1: tabla hora x medio ------------------------------------------
tabla = pd.crosstab(datos["hora_salida"], datos[OBJETIVO])
print(tabla, "\n")
print("Horas sin ningún dron:", list(tabla.index[tabla["dron"] == 0]))
print("Horas con dron:", list(tabla.index[tabla["dron"] > 0]), "\n")

try:
    ax = tabla.plot(kind="bar", stacked=True, figsize=(10, 5))
    ax.figure.savefig("hora_por_medio.png", dpi=120, bbox_inches="tight")
    print("Gráfica guardada en hora_por_medio.png\n")
except ImportError:
    print("(Instala matplotlib para generar la gráfica)\n")

# --- Pregunta 2: noche contra día --------------------------------------------
noche = (datos["hora_salida"] >= 21) | (datos["hora_salida"] < 6)
print(f"De noche: {noche.sum()} ({noche.mean():.1%})  |  de día: {(~noche).sum()}")
print("Reparto de noche:", datos[noche][OBJETIVO].value_counts().to_dict())
print("A las 3:00:", tabla.loc[3].to_dict(), "\n")

# --- Pregunta 3: bicicleta y moto cerca de las 21:00 -------------------------
porcentaje = tabla.div(tabla.sum(axis=1), axis=0) * 100
print("% de bicicleta y moto por hora (17 a 23):")
print(porcentaje[["bicicleta", "moto"]].loc[17:23].round(1), "\n")

# --- Para pensar: una columna nueva, es_noche --------------------------------
datos["es_noche"] = ((datos["hora_salida"] >= 21) | (datos["hora_salida"] < 6)).astype(int)


def construir_modelo(numericas, profundidad):
    preparacion = ColumnTransformer([
        ("numericas", "passthrough", numericas),
        ("categoricas", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
    ])
    return Pipeline([
        ("preparacion", preparacion),
        ("arbol", DecisionTreeClassifier(max_depth=profundidad, min_samples_leaf=5, random_state=42)),
    ])


y = datos[OBJETIVO]
validacion = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)

print("Exactitud del árbol (partición 80/20 de entrenar_arbol.py | validación cruzada de 5):")
for profundidad in (4, 6, 8):
    for nombre, numericas in (("sin es_noche", NUMERICAS), ("con es_noche", NUMERICAS + ["es_noche"])):
        x = datos[numericas + CATEGORICAS]
        x_entreno, x_prueba, y_entreno, y_prueba = train_test_split(
            x, y, test_size=0.2, stratify=y, random_state=42
        )
        modelo = construir_modelo(numericas, profundidad).fit(x_entreno, y_entreno)
        exactitud = (modelo.predict(x_prueba) == y_prueba).mean()
        cruzada = cross_val_score(construir_modelo(numericas, profundidad), x, y, cv=validacion).mean()
        print(f"  profundidad {profundidad}  {nombre:<13} {exactitud:.2%}  |  {cruzada:.2%}")
