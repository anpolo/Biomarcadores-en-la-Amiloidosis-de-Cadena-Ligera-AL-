# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 12:36:43 2026

@author: axdrx
"""

# SCREENING AUTOMÁTICO

import pandas as pd
import re
import os


input_csv  = r"C:\Users\axdrx\OneDrive\Escritorio\TFM\Resultados\registros_deduplicados.csv"
output_dir = r"C:\Users\axdrx\OneDrive\Escritorio\TFM\Resultados"


df = pd.read_csv(input_csv, dtype=str, encoding="utf-8-sig")
print(f"Registros cargados: {len(df)}")

# Criterios de exclusión (si aparecen se excluyen directamente)

excluir_por = {

    # Otras amiloidosis — no son AL
    "otra_amiloidosis": [
        "ATTR amyloidosis", "transthyretin amyloidosis",
        "wild-type amyloidosis", "wildtype amyloidosis",
        "AA amyloidosis", "senile amyloidosis",
        "apolipoprotein amyloidosis", "fibrinogen amyloidosis",
        "lysozyme amyloidosis", "gelsolin amyloidosis",
        "leukocyte chemotactic factor",
    ],

    # Enfermedades que no son amiloidosis
    "otra_enfermedad": [
        "alzheimer", "parkinson", "huntington",
        "prion disease", "type 2 diabetes amyloid",
        "islet amyloid", "IAPP", "multiple sclerosis",
    ],

    # Modelos no humanos
    "no_humano": [
        "mouse model", "rat model", "murine model",
        "animal model", "in vitro", "cell line",
        "zebrafish", "drosophila", "caenorhabditis",
        "yeast model",
    ],

    # Tipos de publicación no elegibles
    "tipo_publicacion": [
        ": a review", ": review", "systematic review",
        "narrative review", "scoping review",
        "meta-analysis", "letter to the editor",
        "case report", "case series", "erratum",
        "retraction", "editorial",
    ],
}

# Criterios de inclusión

mencionar_AL = [
    "AL amyloidosis",
    "light chain amyloidosis",
    "amyloidosis AL",
    "immunoglobulin light chain amyloidosis",
    "primary amyloidosis",
    "amyloid light-chain",
    "amyloid light chain",
] # Obligatorio que mencione amiloidosis AL

# Además de mencionar AL, debe incluir lo siguiente

bioinfo = [
    "proteom", "genom", "metabolom", "transcriptom",
    "machine learning", "deep learning", "artificial intelligence",
    "multiomics", "multi-omics", "bioinformatics",
    "mass spectrometry", "RNA-seq", "next generation sequencing", "GWAs"
    "microRNA", "miRNA", "cell-free DNA", "cfDNA",
    "extracellular vesicle", "exosome",
]
 

biomarcador_novel = [
    "novel biomarker", "emerging biomarker", "new biomarker", "candidate biomarker", "potential biomarker"
    "circulating biomarker", "plasma biomarker", "serum biomarker",
]
 

outcomes = [
    "diagnostic accuracy", "AUC", "sensitivity", "specificity",
    "overall survival", "hematologic response", "organ response",
    "treatment response", "prognostic value", "diagnostic value",
    "progression-free survival", "monitoring",
]

# Función de screening

def screening(row) -> tuple:
    titulo   = str(row.get("Title", "")).lower()
    abstract = str(row.get("Abstract", "")).lower()
    doctype  = str(row.get("Document_Type", "")).lower()
    texto    = titulo + " " + abstract + " " + doctype
 
    # 1: exclusión automática
    for motivo, keywords in excluir_por.items():
        for kw in keywords:
            if kw.lower() in texto:
                return "EXCLUIDO", f"{motivo}: {kw}"
 
    # 2: debe mencionar AL amyloidosis específicamente
    menciona_AL = any(kw.lower() in texto for kw in mencionar_AL)
    if not menciona_AL:
        return "EXCLUIDO", "No menciona AL amyloidosis específicamente"
 
    # paso 3: debe cumplir los tres grupos de inclusión
    tiene_bioinfo         = any(kw.lower() in texto for kw in bioinfo)
    tiene_novel          = any(kw.lower() in texto for kw in biomarcador_novel)
    tiene_outcomes       = any(kw.lower() in texto for kw in outcomes)
 
    # incluido solo si cumple ómicas O novel + outcomes
    if (tiene_bioinfo or tiene_novel) and tiene_outcomes:
        kw_match = next((kw for kw in bioinfo + biomarcador_novel if kw.lower() in texto), "")
        return "INCLUIDO", f"Cumple criterios — {kw_match}"
 
    # menciona AL y algo de inclusión pero no todo → dudoso
    if menciona_AL and (tiene_bioinfo or tiene_novel or tiene_outcomes):
        return "DUDOSO", "Menciona AL con criterios parciales — revisión manual"
 
    return "EXCLUIDO", "Menciona AL pero sin criterios de inclusión"



df[["DECISION", "MOTIVO"]] = df.apply(
    lambda row: pd.Series(screening(row)), axis=1
)

# Resumen

vc = df["DECISION"].value_counts()
print(f"""
{'='*50}
RESULTADOS SCREENING
{'='*50}
INCLUIDOS:  {vc.get('INCLUIDO', 0)}
DUDOSOS:    {vc.get('DUDOSO', 0)}
EXCLUIDOS:  {vc.get('EXCLUIDO', 0)}
Total:      {len(df)}
{'='*50}
""")

# Motivos de exclusión más frecuentes
print("Top motivos de exclusión:")
excluidos = df[df["DECISION"] == "EXCLUIDO"]
print(excluidos["MOTIVO"].value_counts().head(15).to_string())

# Exportar

# Fichero completo con decisiones
df.to_csv(os.path.join(output_dir, "screening_completo.csv"),
          index=False, encoding="utf-8-sig")

# Incluidos
df[df["DECISION"] == "INCLUIDO"].to_csv(
    os.path.join(output_dir, "incluidos.csv"),
    index=False, encoding="utf-8-sig")

# Dudosos para revisión manual
df[df["DECISION"] == "DUDOSO"].to_csv(
    os.path.join(output_dir, "dudosos_revision_manual.csv"),
    index=False, encoding="utf-8-sig")

# Excluidos con motivo
df[df["DECISION"] == "EXCLUIDO"].to_csv(
    os.path.join(output_dir, "excluidos.csv"),
    index=False, encoding="utf-8-sig")

print("\n✓ Ficheros exportados:")
print("  → screening_completo.csv")
print("  → incluidos.csv")
print("  → dudosos_revision_manual.csv")
print("  → excluidos.csv")