"""Actividad 5 - El dron es minoría: ¿hay que balancear el dataset?
"""
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

from usar_modelo import es_posible

warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)

NUMERICAS = [
    "distancia_km", "peso_kg", "largo_cm", "ancho_cm", "alto_cm", "volumen_l",
    "fragil", "refrigerado", "valor_declarado_mxn", "hora_salida",
]
CATEGORICAS = ["prioridad", "zona_destino", "clima", "trafico"]
COLUMNAS = NUMERICAS + CATEGORICAS
OBJETIVO = "medio_recomendado"

datos = pd.read_csv("envios_medios.csv")
x = datos[COLUMNAS]
y = datos[OBJETIVO]

# La misma partición de siempre: estos 2 000 envíos de prueba NO se tocan nunca.
x_entreno, x_prueba, y_entreno, y_prueba = train_test_split(
    x, y, test_size=0.2, stratify=y, random_state=42
)
paquetes_prueba = x_prueba.to_dict("records")

# =============================================================================
# Parte A - Pensar antes de tocar los datos
# =============================================================================
print("PARTE A")
print("Distribución real:", y.value_counts(normalize=True).round(3).to_dict())
print("Drones en la prueba:", int((y_prueba == "dron").sum()), "de", len(y_prueba))
print(f"Un 'modelo' que nunca dice dron y acierta lo demás: {1 - (y_prueba == 'dron').mean():.1%}")
print(f"Un 'modelo' que siempre dice moto: {(y_prueba == 'moto').mean():.1%}\n")


# =============================================================================
# Función de evaluación: un árbol igual al del paso 6, medido SIEMPRE con la misma prueba
# =============================================================================
def construir_modelo(class_weight=None):
    preparacion = ColumnTransformer([
        ("numericas", "passthrough", NUMERICAS),
        ("categoricas", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
    ])
    return Pipeline([
        ("preparacion", preparacion),
        ("arbol", DecisionTreeClassifier(
            max_depth=8, min_samples_leaf=5, random_state=42, class_weight=class_weight
        )),
    ])


def elegir_con_reglas(modelo, x_datos):
    """Como en recomendar_medio: el mejor del ranking del modelo que sí es posible."""
    probabilidades = modelo.predict_proba(x_datos)
    elegidos = []
    for fila, probs in zip(x_datos.to_dict("records"), probabilidades):
        ranking = sorted(zip(modelo.classes_, probs), key=lambda par: -par[1])
        elegidos.append(next((m for m, _ in ranking if es_posible(m, fila)), "camioneta"))
    return np.array(elegidos)


def evaluar(x_ent, y_ent, nombre, class_weight=None, x_eval=None, y_eval=None):
    x_eval = x_prueba if x_eval is None else x_eval
    y_eval = y_prueba if y_eval is None else y_eval
    modelo = construir_modelo(class_weight).fit(x_ent[COLUMNAS], y_ent)
    prediccion = modelo.predict(x_eval[COLUMNAS])
    paquetes = x_eval[COLUMNAS].to_dict("records")
    imposibles = sum(not es_posible(medio, p) for medio, p in zip(prediccion, paquetes))
    con_reglas = elegir_con_reglas(modelo, x_eval[COLUMNAS])
    return modelo, {
        "Estrategia": nombre,
        "Envíos entreno": len(x_ent),
        "Drones entreno": int((y_ent == "dron").sum()),
        "Exactitud": (prediccion == y_eval).mean(),
        "Precision dron": precision_score(y_eval, prediccion, labels=["dron"], average=None)[0],
        "Recall dron": recall_score(y_eval, prediccion, labels=["dron"], average=None)[0],
        "Predice dron": int((prediccion == "dron").sum()),
        "Imposibles": imposibles,
        "Exactitud con reglas": (con_reglas == y_eval).mean(),
        "Recall dron con reglas": recall_score(y_eval, con_reglas, labels=["dron"], average=None)[0],
        "Precision dron con reglas": precision_score(y_eval, con_reglas, labels=["dron"], average=None)[0],
    }


# =============================================================================
# Parte B - Estrategias (todas se aplican SOLO al conjunto de entrenamiento)
# =============================================================================
rng = np.random.default_rng(42)
n_dron = int((y_entreno == "dron").sum())
n_moto = int((y_entreno == "moto").sum())


# 1. Quitar de las clases que sobran: todas bajan al tamaño del dron.
indices = np.concatenate([
    rng.choice(y_entreno.index[y_entreno == medio], size=n_dron, replace=False)
    for medio in sorted(y.unique())
])
x_sub, y_sub = x_entreno.loc[indices], y_entreno.loc[indices]

# 2. Repetir drones (con reemplazo) hasta igualar a la moto.
indices_dron = rng.choice(y_entreno.index[y_entreno == "dron"], size=n_moto, replace=True)
x_sobre = pd.concat([x_entreno[y_entreno != "dron"], x_entreno.loc[indices_dron]])
y_sobre = pd.concat([y_entreno[y_entreno != "dron"], y_entreno.loc[indices_dron]])

# 3. Drones NUEVOS: se corre el generador con otra semilla y se toman solo sus drones.
if not Path("envios_extra.csv").exists():
    subprocess.run([sys.executable, "generar_dataset.py", "--filas", "40000",
                    "--semilla", "7", "--salida", "envios_extra.csv"], check=True)
extra = pd.read_csv("envios_extra.csv")
drones_nuevos = extra[extra[OBJETIVO] == "dron"].sample(n=n_moto - n_dron, random_state=42)
x_nuevos = pd.concat([x_entreno, drones_nuevos[COLUMNAS]])
y_nuevos = pd.concat([y_entreno, drones_nuevos[OBJETIVO]])

# 4 y 5. No se toca el dataset: se le dice al árbol que un dron pesa más.
peso_dron = n_moto / n_dron

resultados, modelos = [], {}
for nombre, args in [
    ("Sin balancear", dict(x_ent=x_entreno, y_ent=y_entreno)),
    ("Quitar sobrantes (submuestreo)", dict(x_ent=x_sub, y_ent=y_sub)),
    ("Repetir drones (sobremuestreo)", dict(x_ent=x_sobre, y_ent=y_sobre)),
    ("Drones nuevos del generador", dict(x_ent=x_nuevos, y_ent=y_nuevos)),
    (f"class_weight dron x{peso_dron:.1f}", dict(x_ent=x_entreno, y_ent=y_entreno,
                                                  class_weight={"dron": peso_dron})),
    ("class_weight='balanced'", dict(x_ent=x_entreno, y_ent=y_entreno, class_weight="balanced")),
]:
    modelo, fila = evaluar(nombre=nombre, **args)
    modelos[nombre] = modelo
    resultados.append(fila)

tabla = pd.DataFrame(resultados).set_index("Estrategia")
formato = tabla.copy()
for columna in ["Exactitud", "Precision dron", "Recall dron", "Exactitud con reglas",
                "Recall dron con reglas", "Precision dron con reglas"]:
    formato[columna] = (formato[columna] * 100).round(1)
print("PARTE B - Tabla (190 drones reales en la prueba; porcentajes):")
print(formato.to_string(), "\n")

# --- Trampa a propósito (NO hacer esto): balancear ANTES de separar -----------
indices_dron_todos = rng.choice(y.index[y == "dron"], size=int((y == "moto").sum()), replace=True)
x_tramposo = pd.concat([x[y != "dron"], x.loc[indices_dron_todos]])
y_tramposo = pd.concat([y[y != "dron"], y.loc[indices_dron_todos]])
xt_ent, xt_prueba, yt_ent, yt_prueba = train_test_split(
    x_tramposo, y_tramposo, test_size=0.2, stratify=y_tramposo, random_state=42
)
_, trampa = evaluar(xt_ent, yt_ent, "TRAMPA: repetir ANTES de separar", x_eval=xt_prueba, y_eval=yt_prueba)
duplicados = int(xt_prueba.merge(xt_ent.drop_duplicates(), how="inner", on=COLUMNAS).shape[0])
print("TRAMPA 1 - repetir drones antes de separar:")
print(f"  exactitud {trampa['Exactitud']:.1%}  precision dron {trampa['Precision dron']:.1%}  "
      f"recall dron {trampa['Recall dron']:.1%}")
print(f"  envíos de prueba que también están, idénticos, en el entrenamiento: "
      f"{duplicados} de {len(xt_prueba)}")

# --- Trampa 2: balancear también la prueba ------------------------------------
n_prueba_dron = int((y_prueba == "dron").sum())
indices_prueba = np.concatenate([
    rng.choice(y_prueba.index[y_prueba == medio], size=n_prueba_dron, replace=False)
    for medio in sorted(y.unique())
])
_, trampa2 = evaluar(x_entreno, y_entreno, "TRAMPA: prueba balanceada",
                     x_eval=x_prueba.loc[indices_prueba], y_eval=y_prueba.loc[indices_prueba])
print("TRAMPA 2 - árbol sin balancear medido con una prueba balanceada "
      f"({len(indices_prueba)} envíos, {n_prueba_dron} de cada medio):")
print(f"  exactitud {trampa2['Exactitud']:.1%}  precision dron {trampa2['Precision dron']:.1%}  "
      f"recall dron {trampa2['Recall dron']:.1%}\n")

# =============================================================================
# Parte C - Interpretar
# =============================================================================
print("PARTE C - Variación entre particiones (validación cruzada de 5; se balancea SOLO el entrenamiento)")
validacion = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
cv = {nombre: {"precision": [], "recall": []} for nombre in ["Sin balancear", "Repetir drones",
                                                              "class_weight='balanced'", "Quitar sobrantes"]}
for ent, pru in validacion.split(x, y):
    xe, ye, xp, yp = x.iloc[ent], y.iloc[ent], x.iloc[pru], y.iloc[pru]
    n_d, n_m = int((ye == "dron").sum()), int((ye == "moto").sum())
    r = np.random.default_rng(1)
    i_sob = r.choice(ye.index[ye == "dron"], size=n_m, replace=True)
    i_sub = np.concatenate([r.choice(ye.index[ye == m], size=n_d, replace=False) for m in sorted(y.unique())])
    configuraciones = {
        "Sin balancear": (xe, ye, None),
        "Repetir drones": (pd.concat([xe[ye != "dron"], xe.loc[i_sob]]), pd.concat([ye[ye != "dron"], ye.loc[i_sob]]), None),
        "class_weight='balanced'": (xe, ye, "balanced"),
        "Quitar sobrantes": (xe.loc[i_sub], ye.loc[i_sub], None),
    }
    for nombre, (xx, yy, cw) in configuraciones.items():
        m = construir_modelo(cw).fit(xx[COLUMNAS], yy)
        pr = m.predict(xp[COLUMNAS])
        cv[nombre]["precision"].append(precision_score(yp, pr, labels=["dron"], average=None)[0])
        cv[nombre]["recall"].append(recall_score(yp, pr, labels=["dron"], average=None)[0])
for nombre, v in cv.items():
    print(f"  {nombre:<26} precision dron {np.mean(v['precision']):.1%} ± {np.std(v['precision']):.1%}   "
          f"recall dron {np.mean(v['recall']):.1%} ± {np.std(v['recall']):.1%}")

# --- ¿Sigue significando lo mismo la «confianza»? ------------------------------
print("\nCalibración de la probabilidad de dron en la prueba "
      "(promedio de lo que el modelo dice vs. fracción que realmente es dron):")
cortes = [0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0001]
for nombre in ["Sin balancear", "class_weight='balanced'", "Quitar sobrantes (submuestreo)"]:
    modelo = modelos[nombre]
    p_dron = modelo.predict_proba(x_prueba[COLUMNAS])[:, list(modelo.classes_).index("dron")]
    print(f"  {nombre}: probabilidad media de dron = {p_dron.mean():.1%} (real: {(y_prueba == 'dron').mean():.1%})")
    grupos = pd.cut(p_dron, cortes, right=False)
    resumen = pd.DataFrame({"dice": p_dron, "es_dron": (y_prueba.values == "dron")}).groupby(grupos).agg(
        envios=("dice", "size"), dice=("dice", "mean"), real=("es_dron", "mean"))
    print((resumen.assign(dice=(resumen["dice"] * 100).round(1), real=(resumen["real"] * 100).round(1))
           .loc[resumen["envios"] > 0]).to_string())

# =============================================================================
# Extras para interpretar y decidir
# =============================================================================
print("\nEXTRAS")
# ¿Cuántas de las copias de la trampa 1 son drones y cuántas son de otros medios?
copias = xt_prueba.reset_index(drop=True).assign(real=yt_prueba.values).merge(
    xt_ent.drop_duplicates(), how="left", on=COLUMNAS, indicator=True)
print("Trampa 1 - envíos de prueba idénticos a uno de entrenamiento, por medio:")
print(copias[copias["_merge"] == "both"]["real"].value_counts().to_dict())
print("Trampa 1 - composición de la prueba:", yt_prueba.value_counts(normalize=True).round(3).to_dict())

# El punto ciego del árbol sin balancear: drones a 6 km o menos.
cortos = (y_prueba == "dron") & (x_prueba["distancia_km"] <= 6)
print(f"\nDrones reales de la prueba a 6 km o menos: {int(cortos.sum())} de {n_prueba_dron}")
for nombre, modelo in modelos.items():
    acertados = int((modelo.predict(x_prueba[COLUMNAS])[cortos.values] == "dron").sum())
    print(f"  {nombre:<34} acierta {acertados} de {int(cortos.sum())}")

# ¿Qué eran en realidad los envíos que cada modelo llamó dron sin serlo?
print("\nFalsos positivos de dron: qué eran en realidad (y cuántos son imposibles)")
for nombre in ["Sin balancear", "Repetir drones (sobremuestreo)", "class_weight='balanced'"]:
    modelo = modelos[nombre]
    prediccion = modelo.predict(x_prueba[COLUMNAS])
    falsos = (prediccion == "dron") & (y_prueba.values != "dron")
    reales = y_prueba.values[falsos]
    imposibles = sum(not es_posible("dron", p) for p, f in zip(paquetes_prueba, falsos) if f)
    print(f"  {nombre:<34} {int(falsos.sum()):>3} falsos positivos "
          f"({pd.Series(reales).value_counts().to_dict()}), imposibles: {imposibles}")

# Término medio: ¿qué pasa con pesos intermedios para el dron? (validación cruzada; reglas aplicadas)
print("\nPeso intermedio para el dron (validación cruzada de 5, con reglas del negocio):")
filas = []
for peso in [1, 1.5, 2, 3, 4.8]:
    exact, prec, rec, pred_dron = [], [], [], []
    for ent, pru in validacion.split(x, y):
        m = construir_modelo({"dron": peso} if peso != 1 else None).fit(x.iloc[ent][COLUMNAS], y.iloc[ent])
        final = elegir_con_reglas(m, x.iloc[pru][COLUMNAS])
        yp = y.iloc[pru]
        exact.append((final == yp.values).mean())
        prec.append(precision_score(yp, final, labels=["dron"], average=None)[0])
        rec.append(recall_score(yp, final, labels=["dron"], average=None)[0])
        pred_dron.append((final == "dron").sum())
    filas.append({"peso dron": peso, "exactitud": np.mean(exact) * 100,
                  "precision dron": np.mean(prec) * 100, "recall dron": np.mean(rec) * 100,
                  "predice dron (por pliegue)": np.mean(pred_dron)})
print(pd.DataFrame(filas).set_index("peso dron").round(1).to_string())
