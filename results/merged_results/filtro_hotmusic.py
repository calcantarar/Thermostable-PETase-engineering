import pandas as pd

codigo = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E",
          "GLY":"G","HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F",
          "PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}

mutaciones = []
with open("hotmusic_results.hot") as f:
    for linea in f:
        partes = linea.split()
        try:
            if len(partes) >= 7 and partes[1].isdigit():
                pos = int(partes[1]); wt = partes[2]; mut = partes[3]
                sasa = float(partes[5]); dtm = float(partes[6])
            elif len(partes) >= 6 and partes[0].isdigit():
                pos = int(partes[0]); wt = partes[1]; mut = partes[2]
                sasa = float(partes[4]); dtm = float(partes[5])
            else:
                continue
        except ValueError:
            continue
        mutaciones.append({"mutacion": codigo[wt] + str(pos) + codigo[mut],
                           "pos": pos, "sasa": sasa, "dtm": dtm})

df = pd.DataFrame(mutaciones)
df = df[(df["dtm"] > 0) & (df["sasa"] > 20)].sort_values("dtm", ascending=False)
df.to_csv("hotmusic_filtrado.csv", index=False)

print(f"Mutaciones totales: {len(mutaciones)} | pasan filtro: {len(df)}")
