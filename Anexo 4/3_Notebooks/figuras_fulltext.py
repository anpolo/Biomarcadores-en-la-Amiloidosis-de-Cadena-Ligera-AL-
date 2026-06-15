# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 11:55:59 2026

@author: axdrx
"""

import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import textwrap
import os
import pandas as pd

BASE_DIR = r"C:\Users\axdrx\OneDrive\Escritorio\TFM\Extraccion"
FIGS_DIR = os.path.join(BASE_DIR, "figuras")
os.makedirs(FIGS_DIR, exist_ok=True)

biomarks = pd.read_csv(os.path.join(BASE_DIR, "tabla_biomarcadores.csv"), encoding='utf-8-sig')
estudios = pd.read_csv(os.path.join(BASE_DIR, "tabla_estudio.csv"),       encoding='utf-8-sig')

# Estilo
sns.set_theme(style="whitegrid", font="Calibri")
PALETA = ["#1a3a5c", "#2E5FA3", "#5B9BD5", "#8DBDE8", "#B8D5F0", "#D9EAF8"]

def guardar(fig, nombre):
    ruta = os.path.join(FIGS_DIR, f"{nombre}.png")
    fig.savefig(ruta, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ {nombre}.png")
    plt.show()

# Figura 1: Distribución por tipo de biomarcador

conteo_tipo = biomarks["biomarker_type"].value_counts()

fig, ax = plt.subplots(figsize=(7, 7))
wedges, texts, autotexts = ax.pie(
    conteo_tipo.values,
    labels=conteo_tipo.index,
    autopct='%1.1f%%',
    colors=PALETA[:len(conteo_tipo)],
    startangle=140,
    pctdistance=0.78,
    wedgeprops=dict(linewidth=2, edgecolor='white'),
    textprops=dict(fontsize=11)
)
for at in autotexts:
    at.set_fontsize(10)
    at.set_fontweight('bold')
    at.set_color('white')

ax.set_title("Distribución de biomarcadores noveles por tipo",
             fontsize=13, fontweight='bold', pad=20)
fig.tight_layout()
guardar(fig, "fig1_tipo_biomarcador")


# Figura 2: Distribución por tipo de muestra

conteo_muestra = biomarks["sample_type"].value_counts().reset_index()
conteo_muestra.columns = ["Muestra", "n"]
conteo_muestra["Muestra"] = conteo_muestra["Muestra"].apply(
    lambda x: "\n".join(textwrap.wrap(str(x), width=14))
)

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=conteo_muestra, x="Muestra", y="n",
            palette=PALETA[:len(conteo_muestra)], ax=ax,
            edgecolor='white', linewidth=1.5)

for p in ax.patches:
    ax.annotate(f"{int(p.get_height())}",
                (p.get_x() + p.get_width() / 2, p.get_height()),
                ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_xlabel("Tipo de muestra", fontsize=11, labelpad=10)
ax.set_ylabel("Número de biomarcadores", fontsize=11)
ax.set_title("Tipos de muestra utilizados en la evaluación de biomarcadores",
             fontsize=13, fontweight='bold')
ax.set_ylim(0, conteo_muestra["n"].max() + 1.5)
ax.tick_params(axis='x', labelsize=10)
sns.despine()
fig.tight_layout()
guardar(fig, "fig2_tipo_muestra")


# Figura 3: Distribución por propósito clínico
# normalizar: separar entradas múltiples y limpiar
def normalizar_purpose(texto):
    if pd.isna(texto):
        return []
    import re
    resultado = []
    partes = re.split(r'\s+y\s+|,|/', str(texto))
    for p in partes:
        p = p.strip()
        p_low = p.lower()
        if "diagn" in p_low:
            resultado.append("Diagnóstico")
        elif "pron" in p_low:
            resultado.append("Pronóstico")
        elif "monitor" in p_low:
            resultado.append("Monitorización")
    return resultado

purposes = biomarks["clinical_purpose"].apply(normalizar_purpose).explode()
conteo_purpose = purposes.value_counts().reset_index()
conteo_purpose.columns = ["Propósito", "n"]
conteo_purpose["Propósito"] = conteo_purpose["Propósito"].apply(
    lambda x: "\n".join(textwrap.wrap(str(x), width=25))
)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=conteo_purpose, y="Propósito", x="n",
            palette=PALETA[3:3+len(conteo_purpose)], ax=ax,
            edgecolor='white', linewidth=1.5, orient='h')

for p in ax.patches:
    ax.annotate(f"{int(p.get_width())}",
                (p.get_width(), p.get_y() + p.get_height() / 2),
                ha='left', va='center', fontsize=11,
                fontweight='bold', xytext=(4, 0),
                textcoords='offset points')

ax.set_xlabel("Número de biomarcadores", fontsize=11)
ax.set_ylabel("")
ax.set_title("Propósito clínico de los biomarcadores noveles",
             fontsize=13, fontweight='bold')
ax.set_xlim(0, conteo_purpose["n"].max() + 2)
ax.tick_params(axis='y', labelsize=10)
sns.despine()
fig.tight_layout()
guardar(fig, "fig3_proposito")


# Figura 5: Distribución por técnicas

def normalizar_tecnica(texto):
    if pd.isna(texto):
        return []
    import re
    resultado = []
    partes = re.split(r';', str(texto))
    for p in partes:
        p = p.strip()
        if not p:
            continue
        p_low = p.lower()
        if ("prot" in p_low) and ("inteligencia" in p_low or "artificial" in p_low or " ia" in p_low):
            resultado.append("Proteómica")
            resultado.append("Inteligencia Artificial")
        elif "prot" in p_low:
            resultado.append("Proteómica")
        elif "genom" in p_low or "ngs" in p_low or "array" in p_low or "sanger" in p_low:
            resultado.append("Genómica")
        elif "imagen" in p_low or "resonancia" in p_low or "cmr" in p_low:
            resultado.append("Imagen")
        elif "metabol" in p_low:
            resultado.append("Metabolómica")
        elif "hematol" in p_low or "lisis" in p_low:
            resultado.append("Análisis hematológico")
        elif "electrocardiograf" in p_low:
            resultado.append("Electrocardiografía")
        elif "inteligencia" in p_low or "artificial" in p_low:
            resultado.append("Inteligencia Artificial")
    return resultado
    
tecnicas_norm = estudios["techniques"].apply(normalizar_tecnica).explode()
tecnicas_norm = tecnicas_norm[tecnicas_norm.notna() & (tecnicas_norm != "")]
conteo_tec = tecnicas_norm.value_counts().reset_index()
conteo_tec.columns = ["Técnica", "n"]
conteo_tec = conteo_tec.sort_values("n")


fig, ax = plt.subplots(figsize=(11, 6))
sns.barplot(data=conteo_tec, y="Técnica", x="n",
            color=PALETA[0], ax=ax,
            edgecolor='white', linewidth=1.5, orient='h')

for p in ax.patches:
    ax.annotate(f"{int(p.get_width())}",
                (p.get_width(), p.get_y() + p.get_height() / 2),
                ha='left', va='center', fontsize=11,
                fontweight='bold', xytext=(4, 0),
                textcoords='offset points')

ax.set_xlabel("Número de estudios", fontsize=11)
ax.set_ylabel("")
ax.set_title("Técnicas más utilizadas en los estudios incluidos",
             fontsize=13, fontweight='bold')
ax.set_xlim(0, conteo_tec["n"].max() + 1.5)
ax.tick_params(axis='y', labelsize=10)
sns.despine()
fig.tight_layout()
guardar(fig, "fig4_tecnicas_bar")

print(f"\n✓ Figuras guardadas en: {FIGS_DIR}")


import plotly.express as px

ruta_archivo = r"C:\Users\axdrx\OneDrive\Escritorio\TFM\Extraccion\tecnicas.xlsx"
ruta_guardado_png = r"C:\Users\axdrx\OneDrive\Escritorio\TFM\Extraccion\grafico_sunburst.png"

PALETA = ["#1a3a5c", "#2E5FA3", "#5B9BD5", "#8DBDE8", "#B8D5F0", "#D9EAF8"]

try:
    # Leer archivo
    df = pd.read_excel(ruta_archivo)
    df.columns = df.columns.str.strip()
    
    # Crear gráfico
    fig = px.sunburst(
        df, 
        path=['Campo', 'Técnica'], 
        title='Distribución de Campos y Técnicas Metodológicas',
        color_discrete_sequence=PALETA,
        template='plotly_white'
    )

    fig.update_layout(
        font=dict(
            family="Calibri",
            size=11,
            color="black"
        ),
        title_font=dict(size=15, color="black")
    )

    # Texto interior
    fig.update_traces(
        textinfo="label",             
        insidetextorientation='radial',
        textfont=dict(color="black")  
    )
    
    fig.write_image(ruta_guardado_png, scale=3, width=1000, height=800)
