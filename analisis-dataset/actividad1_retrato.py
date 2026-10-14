"""Actividad 1 - El retrato del dataset.
"""
import pandas as pd

from usar_modelo import es_posible, LIMITES

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

OBJETIVO = "medio_recomendado"
datos = pd.read_csv("envios_medios.csv")
print(f"Envíos: {len(datos)}  |  celdas vacías: {datos.isna().sum().sum()}\n")

# --- ¡qué medio domina con lluvia y en el centro? ------------------
print("Porcentaje de cada medio según el clima:")
print((pd.crosstab(datos["clima"], datos[OBJETIVO], normalize="index") * 100).round(1), "\n")

print("Porcentaje de cada medio según la zona:")
print((pd.crosstab(datos["zona_destino"], datos[OBJETIVO], normalize="index") * 100).round(1), "\n")

print("Conteos por zona:")
print(pd.crosstab(datos["zona_destino"], datos[OBJETIVO]), "\n")

# --- Resumen numérico por medio (máximos de distancia, peso y volumen) -------
resumen = datos.groupby(OBJETIVO)[["distancia_km", "peso_kg", "volumen_l"]].agg(["min", "median", "max"])
print("Resumen por medio:")
print(resumen.round(2), "\n")

# --- ¿Alguna etiqueta rompe las reglas del negocio? --------------------------
es_valida = datos.apply(lambda fila: es_posible(fila[OBJETIVO], fila), axis=1)
print(f"Etiquetas que rompen las reglas: {(~es_valida).sum()}\n")

# --- Pregunta 1: ¿cuándo no aparece el dron? ---------------------------------
dron = datos[datos[OBJETIVO] == "dron"]
print("Drones por zona:", dron["zona_destino"].value_counts().to_dict())
print("Drones por clima:", dron["clima"].value_counts().to_dict())
print("Horas de salida de los drones:", dron["hora_salida"].min(), "a", dron["hora_salida"].max())
print("Distancia mínima por zona:")
print(datos.groupby("zona_destino")["distancia_km"].agg(["min", "median", "max"]).round(2), "\n")

# --- Pregunta 2: ¿por qué la bicicleta casi no va a la periferia? ------------
periferia = datos[datos["zona_destino"] == "periferia"]
print(f"Periferia: {len(periferia)} envíos, "
      f"{(periferia['distancia_km'] <= 7).sum()} a 7 km o menos, "
      f"{(periferia[OBJETIVO] == 'bicicleta').sum()} en bicicleta")
print("% de envíos a 7 km o menos por zona:")
print((datos.groupby("zona_destino")["distancia_km"].apply(lambda s: (s <= 7).mean()) * 100).round(1), "\n")

cabe_en_bici = datos[(datos["distancia_km"] <= 7) & (datos["peso_kg"] <= 8) & (datos["volumen_l"] <= 40)]
print("Entre los envíos que caben en bicicleta, % por medio y zona:")
print((pd.crosstab(cabe_en_bici["zona_destino"], cabe_en_bici[OBJETIVO], normalize="index") * 100).round(1), "\n")

# --- Pregunta 3: máximos contra LIMITES --------------------------------------
maximos = datos.groupby(OBJETIVO)[["peso_kg", "volumen_l", "distancia_km"]].max().round(2)
print("Máximos observados:")
print(maximos)
print("\nLímites escritos en LIMITES:")
print(pd.DataFrame(LIMITES).T, "\n")

# --- Pregunta 4: camionetas en viajes de menos de 2 km -----------------------
cortas = datos[(datos[OBJETIVO] == "camioneta") & (datos["distancia_km"] < 2)]
tiene_razon = (cortas["refrigerado"] == 1) | (cortas["peso_kg"] > 25) | (cortas["volumen_l"] > 90)
print(f"Camionetas a menos de 2 km: {len(cortas)}")
print(f"  refrigerado: {(cortas['refrigerado'] == 1).sum()}  "
      f"peso > 25 kg: {(cortas['peso_kg'] > 25).sum()}  "
      f"volumen > 90 L: {(cortas['volumen_l'] > 90).sum()}")
print(f"  con razón clara: {tiene_razon.sum()}  |  sin razón clara: {(~tiene_razon).sum()}")

sin_razon = cortas[~tiene_razon]
medios_posibles = sin_razon.apply(lambda fila: [m for m in LIMITES if es_posible(m, fila)], axis=1)
print("  cuántos medios eran posibles en las que no tienen razón:",
      medios_posibles.apply(len).value_counts().to_dict())
print("  frágiles entre ellas:", int(sin_razon["fragil"].sum()))
