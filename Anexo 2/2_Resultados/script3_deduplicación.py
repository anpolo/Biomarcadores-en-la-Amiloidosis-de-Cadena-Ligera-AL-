# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 11:08:46 2026

@author: axdrx
"""
# DEDUPLICACIÓN

import pandas as pd
import re
import os


pubmed_csv  = r"C:\Users\axdrx\OneDrive\Escritorio\TFM\Resultados\resultados_pubmed.csv"
scopus_csv  = r"C:\Users\axdrx\OneDrive\Escritorio\TFM\Resultados\resultado_scopus.csv"
output_dir  = r"C:\Users\axdrx\OneDrive\Escritorio\TFM\Resultados"

# Cargar ficheros

pm = pd.read_csv(pubmed_csv, dtype=str, encoding="utf-8-sig")
pm["Source"] = "PubMed"
pm = pm.rename(columns={
    "Publication_Type": "Document_Type",
    "Journal_ref":      "Journal"
})

sc = pd.read_csv(scopus_csv, dtype=str, encoding="utf-8-sig",
                 doublequote=True, on_bad_lines="skip")
sc["Source"] = "Scopus"
sc = sc.rename(columns={
    "Document Type": "Document_Type",
    "Source title":  "Journal"
})

print(f"Columnas PubMed:  {list(pm.columns)}")
print(f"Columnas Scopus:  {list(sc.columns)}")
print("\n--- MUESTRA DOIs PubMed ---")
print(pm["DOI"].dropna().head(5).tolist())

print("\n--- MUESTRA DOIs Scopus ---")
print(sc["DOI"].dropna().head(5).tolist())

# Columnas comunes
columnas = ["Title", "Abstract", "DOI", "Authors",
            "Year", "Document_Type", "Journal", "Source"]

pm = pm.reindex(columns=columnas)
sc = sc.reindex(columns=columnas)

# Unir

df = pd.concat([pm, sc], ignore_index=True)

print(f"\nRegistros PubMed:  {len(pm)}")
print(f"Registros Scopus:  {len(sc)}")
print(f"Total combinado:   {len(df)}")

# Deduplicar

def normalizar_titulo(titulo):
    if pd.isna(titulo):
        return ""
    texto = str(titulo).lower().strip()
    texto = re.sub(r'[^\w\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto

# Deduplicar por título normalizado para todos los registros
total_antes = len(df)

df["Title_norm"] = df["Title"].apply(normalizar_titulo)
df_dedup = df.drop_duplicates(subset=["Title_norm"], keep="first")
df_dedup = df_dedup.drop(columns=["Title_norm"])

total_despues   = len(df_dedup)
duplicados_elim = total_antes - total_despues

print(f"\nDuplicados eliminados: {duplicados_elim}")
print(f"Registros únicos:      {total_despues}")

#Exportar

ruta_dedup = os.path.join(output_dir, "registros_deduplicados.csv")
df_dedup.to_csv(ruta_dedup, index=False, encoding="utf-8-sig")

print(f"\n✓ Exportado: registros_deduplicados.csv")
print(f"  → {ruta_dedup}")

