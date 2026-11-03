import pandas as pd

residuos = []
with open("consurf_results.txt") as f:
    for linea in f:
        partes = linea.split()
        if not partes or not partes[0].isdigit():
            continue
        grado = None
        for tok in partes[3:8]:
            if tok.replace("*", "").isdigit() and 1 <= int(tok.replace("*", "")) <= 9:
                grado = int(tok.replace("*", "")); break
        exposicion = None
        for tok in partes[5:]:
            if tok.lower() in ["e", "b", "f", "s", "x"]:
                exposicion = tok.lower(); break
        if grado and exposicion:
            residuos.append({"pos": int(partes[0]), "grado": grado, "exposicion": exposicion})

df = pd.DataFrame(residuos).drop_duplicates(subset="pos")
df = df[(df["grado"] <= 4) & (df["exposicion"] == "e")]
df.to_csv("consurf_filtered.csv", index=False)

print(f"Residuos modificables: {len(df)}")
