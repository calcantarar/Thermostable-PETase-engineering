import pandas as pd

hot = pd.read_csv("candidatas_distancia_10A.csv")
consurf = pd.read_csv("consurf_filtrado.csv")

tabla = hot[hot["pos"].isin(consurf["pos"])]
tabla = tabla.merge(consurf[["pos", "grado"]], on="pos", how="left")

tabla = tabla.sort_values("dtm", ascending=False)
tabla.to_csv("filtro1_candidatas.csv", index=False)
print(f"Candidatas finales: {len(tabla)}")

