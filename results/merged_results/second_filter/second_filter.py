import pandas as pd, numpy as np, os, sys, re

MAESTRO_FILE = "maestroweb_results.csv"
DYNAMUT_FILE = "dynamut2_results.csv"
OUTPUT_FILE  = "fusion_second_filter.csv"

MAX_DDG_MAESTRO = -0.01   # Negativo = estabilizante
MIN_DDG_DYNAMUT =  0.01   # Positivo = estabilizante
MIN_C_PRED      =  0.80   # Confianza mínima MAESTRO

# PARSERS CORREGIDOS
def parse_maestro(s):
    m = re.match(r"([A-Z])(\d+)\.([A-Z])\{([A-Z])\}", s.strip())
    if m:
        wt, pos, chain, mut = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        return {'wt': wt, 'pos': pos, 'chain': chain, 'mut': mut,
                'key': f"{wt}{pos}{chain}{mut}"}
    return None

def parse_dynamut(s, ch):
    m = re.match(r"([A-Z])(\d+)([A-Z])", s.strip())
    if m:
        wt, pos, mut = m.group(1), int(m.group(2)), m.group(3)
        chain = ch.strip().upper() if ch.strip() else 'A'
        return {'wt': wt, 'pos': pos, 'chain': chain, 'mut': mut,
                'key': f"{wt}{pos}{chain}{mut}"}  # ✅ Clave unificada
    return None

# CARGA DE DATOS
def load_maestro(fp):
    if not os.path.exists(fp): return pd.DataFrame()
    df = pd.read_csv(fp, sep=';')
    rec = []
    for _, r in df.iterrows():
        p = parse_maestro(r['substitution'])
        if p:
            rec.append({
                'key': p['key'],
                'mutation_fmt': r['substitution'].strip(),
                'wt': p['wt'], 'pos': p['pos'], 'chain': p['chain'], 'mut': p['mut'],
                'ddG_maestro': float(r['ddG_pred']),
                'c_pred': float(r['c_pred']),
                'stab_maestro': float(r['ddG_pred']) <= MAX_DDG_MAESTRO,
                'conf_ok': float(r['c_pred']) >= MIN_C_PRED
            })
    return pd.DataFrame(rec)

def load_dynamut(fp):
    if not os.path.exists(fp): return pd.DataFrame()
    df = pd.read_csv(fp, sep=',')
    rec = []
    for _, r in df.iterrows():
        p = parse_dynamut(str(r['mutation']), str(r['chain']))
        if p:
            rec.append({
                'key': p['key'],
                'mutation_fmt': f"{p['wt']}{p['pos']}.{p['chain']}{{{p['mut']}}}",
                'wt': p['wt'], 'pos': p['pos'], 'chain': p['chain'], 'mut': p['mut'],
                'ddG_dynamut': float(r['prediction']),
                'stab_dynamut': float(r['prediction']) >= MIN_DDG_DYNAMUT
            })
    return pd.DataFrame(rec)

df_m = load_maestro(MAESTRO_FILE)
df_d = load_dynamut(DYNAMUT_FILE)
print(f"MAESTRO: {len(df_m)} | DynaMut2: {len(df_d)}")

# FUSIÓN + UNIFICACIÓN DE mutation_fmt
merged = pd.merge(df_m, df_d, on='key', how='outer', suffixes=('_m', '_d'))

# Unificar columnas divididas por sufijos
for col in ['mutation_fmt']:
    c_m, c_d = f"{col}_m", f"{col}_d"
    if c_m in merged.columns and c_d in merged.columns:
        merged[col] = merged[c_m].combine_first(merged[c_d])
        merged.drop(columns=[c_m, c_d], errors='ignore', inplace=True)
    elif c_m in merged.columns:
        merged[col] = merged[c_m]
        merged.drop(columns=[c_m], errors='ignore', inplace=True)
    elif c_d in merged.columns:
        merged[col] = merged[c_d]
        merged.drop(columns=[c_d], errors='ignore', inplace=True)

# FILTRADO
merged['ddg_pass'] = (merged['stab_maestro'] | merged['stab_dynamut'])
merged['consensus_stab'] = merged['stab_maestro'] & merged['stab_dynamut']
merged['high_conf'] = merged['conf_ok'].fillna(True)
filtered = merged[merged['ddg_pass'] & merged['high_conf']].copy()

# CÁLCULO ddG alineado (DynaMut positivo → negativo para promediar)
def calc_ddg_aligned(row):
    vals = []
    if pd.notna(row['ddG_maestro']): vals.append(row['ddG_maestro'])
    if pd.notna(row['ddG_dynamut']): vals.append(-row['ddG_dynamut'])
    return round(np.mean(vals), 3) if vals else None
filtered['ddG_aligned_avg'] = filtered.apply(calc_ddg_aligned, axis=1)

# EXPORT
cols = ['mutation_fmt','ddG_maestro','c_pred','ddG_dynamut','ddG_aligned_avg','consensus_stab','quality']
filtered = filtered.sort_values('ddG_aligned_avg', ascending=True)
filtered[cols].to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

print(f"\n{len(filtered)}/{len(merged)} mutants passed filters")