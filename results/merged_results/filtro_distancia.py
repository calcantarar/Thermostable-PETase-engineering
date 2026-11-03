import re
import pandas as pd

excluidos = set()
with open("sitio_activo_10A.txt") as f:
    for linea in f:
        for num in re.findall(r"\d+", linea):
            excluidos.add(int(num))

excluidos.update([160, 206, 237, 87, 161, 185])

df = pd.read_csv("hotmusic_filtrado.csv")
df_final = df[~df["pos"].isin(excluidos)]
df_final.to_csv("candidatas_distancia_10A.csv", index=False)

print(f"Candidatos: {len(df_final)}")
