import pandas as pd

hot = pd.read_csv("candidates_10A_distance.csv")
consurf = pd.read_csv("consurf_filtered.csv")

tabla = hot[hot["pos"].isin(consurf["pos"])]
tabla = tabla.merge(consurf[["pos", "grado"]], on="pos", how="left")

tabla = tabla.sort_values("dtm", ascending=False)
tabla.to_csv("first_filter_candidates.csv", index=False)
print(f"Final candidates: {len(tabla)}")
