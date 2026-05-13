# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 11:52:00 2026

@author: axdrx
"""

# Generación de queries
import os
import re


# Primero se configuran las rutas y las carpetas de salida
constructos_dir = "C:/Users/axdrx/OneDrive/Escritorio/TFM/Constructos/"        # carpeta con los .txt de los constructos
pubmed_dir = "C:/Users/axdrx/OneDrive/Escritorio/TFM/queries_pubmed/"
scopus_dir = "C:/Users/axdrx/OneDrive/Escritorio/TFM/queries_scopus/"     # carpetas de salida queries
for folder in [pubmed_dir, scopus_dir]:
    os.makedirs(folder, exist_ok=True)


def rm_headers(text: str) -> str:
    """
    Elimina líneas que empiezan por # (encabezados Markdown).
 
    Args:
        text (str): contenido del constructo como string
    Returns:
        str: texto limpio sin encabezados
    """
    pattern = r'^#.*$'
    cleaned = re.sub(pattern, '', text, flags=re.MULTILINE)
    return cleaned.strip()
 
 
def pubmed_to_scopus(query: str) -> str:
    """
    Convierte una query PubMed a sintaxis Scopus (TITLE-ABS-KEY).
 
    Scopus no tiene vocabulario controlado MeSH, por lo que:
    - Se eliminan todos los sufijos [MeSH] y [tiab]
    - El contenido de cada término queda como búsqueda de texto libre
    - Se envuelve el bloque en TITLE-ABS-KEY()
 
    Args:
        query (str): query en formato PubMed (con [MeSH] y [tiab])
    Returns:
        str: query en formato Scopus
    """
    # Se eliminan los sufijos de campo PubMed
    scopus = query.replace('[tiab]', '').replace('[MeSH]', '')
 
    # Se limpian los OR/AND que puedan quedar 
    scopus = re.sub(r'\bOR\s+OR\b', 'OR', scopus)
    scopus = re.sub(r'\bAND\s+AND\b', 'AND', scopus)
    scopus = re.sub(r'\(\s*OR\s*', '(', scopus)
    scopus = re.sub(r'\s*OR\s*\)', ')', scopus)
    scopus = re.sub(r'\s{2,}', ' ', scopus).strip()
 
    # Se eliminan los paréntesis exteriores
    if scopus.startswith('(') and scopus.endswith(')'):
        scopus = scopus[1:-1].strip()
 
    return f"TITLE-ABS-KEY({scopus})"

# Cargamos los constructos desde .txt
nombres = [
    "constructo_1_AL.txt",
    "constructo_2_biomarcadores.txt",
    "constructo_3_bioinformatica.txt",
    "constructo_4_outcomes.txt"
]
 
constructos_pm     = []   # queries PubMed limpias
constructos_scopus = []   # queries Scopus convertidas
 
separador = 6 * '*'
 
for i, nombre in enumerate(nombres):
    ruta = os.path.join(constructos_dir, nombre)
 
    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read()
 
    # Limpiar encabezados
    query_pm = rm_headers(contenido)
 
    # Convertir a Scopus
    query_scopus = pubmed_to_scopus(query_pm)
 
    constructos_pm.append(query_pm)
    constructos_scopus.append(query_scopus)
 
    # Mostrar resultado en consola
    print(f"\n{separador} CONSTRUCTO {i+1} {separador}")
    print(f"\n--- PubMed ---\n{query_pm}")
    print(f"\n--- Scopus ---\n{query_scopus}")
    

# Se exportan las queries individuales
for i, (pm, scopus) in enumerate(zip(constructos_pm, constructos_scopus), start=1):
    # PubMed
    with open(os.path.join(pubmed_dir, f"PM_query_{i}.txt"), "w", encoding="utf-8") as f:
        f.write(pm)
    # Scopus
    with open(os.path.join(scopus_dir, f"Scopus_query_{i}.txt"), "w", encoding="utf-8") as f:
        f.write(scopus)
 
print("\n✓ Queries individuales exportadas.")

# Combinación de constructos
# C1 = Amiloidosis AL
# C2 = Biomarcadores
# C3 = Bioinformática
# C4 = Outcomes clínicos

def merge_or_pm(indices: list, constructos: list) -> str:
    """Fusiona constructos con OR para PubMed."""
    terminos = []
    for i in indices:
        q = constructos[i].strip()
        if q.startswith('(') and q.endswith(')'):
            q = q[1:-1].strip()
        terminos.append(q)
    return "(\n" + "\nOR\n".join(terminos) + "\n)"
 
 
def merge_or_scopus(indices: list, constructos: list) -> str:
    """Fusiona constructos con OR para Scopus."""
    terminos = []
    for i in indices:
        q = pubmed_to_scopus(constructos[i])
        inner = re.sub(r'^TITLE-ABS-KEY\(', '', q)
        inner = re.sub(r'\)$', '', inner).strip()
        terminos.append(inner)
    return f"TITLE-ABS-KEY({' OR '.join(terminos)})"
 
 
def bloque_pm(i):
    return f"({constructos_pm[i]})"
 
 
def bloque_sc(i):
    return pubmed_to_scopus(constructos_pm[i])

biomark_omics_pm = merge_or_pm([1, 2], constructos_pm)    # C2 OR C3
biomark_omics_sc = merge_or_scopus([1, 2], constructos_pm)
 
q_pm = "\nAND\n".join([bloque_pm(0), biomark_omics_pm, bloque_pm(3)])
q_sc = "\nAND\n".join([bloque_sc(0), biomark_omics_sc, bloque_sc(3)])
 
print(f"\n{separador} COMBINACIÓN FINAL {separador}")
print(f"\nC1 AND (C2 OR C3) AND C4")
print(f"\n--- PubMed ---\n{q_pm}")
print(f"\n--- Scopus ---\n{q_sc}")
 
with open(os.path.join(pubmed_dir, "PM_combinacion_final.txt"), "w", encoding="utf-8") as f:
    f.write(q_pm)
 
with open(os.path.join(scopus_dir, "Scopus_combinacion_final.txt"), "w", encoding="utf-8") as f:
    f.write(q_sc)
 
print("\n✓ Combinación final exportada.")
print(f"\n  PubMed → {pubmed_dir}PM_combinacion_final.txt")
print(f"  Scopus → {scopus_dir}Scopus_combinacion_final.txt")