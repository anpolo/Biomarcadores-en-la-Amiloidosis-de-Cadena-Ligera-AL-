# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 11:52:00 2026

@author: axdrx
"""

# Generación de queries
import os
import re


# Primero se configuran las rutas y las carpetas de salida
constructos_dir = "./Constructos/"         # carpeta con los .txt de los constructos
pubmed_dir      = "./queries_pubmed/"       # carpeta de salida queries PubMed
scopus_dir      = "./queries_scopus/"       # carpeta de salida queries Scopus
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
    "constructo_1_enfermedad_general.txt",
    "constructo_2_AL.txt",
    "constructo_3_biomarcadores.txt",
    "constructo_4_bioinformatica.txt",
    "constructo_5_outcomes.txt"
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
