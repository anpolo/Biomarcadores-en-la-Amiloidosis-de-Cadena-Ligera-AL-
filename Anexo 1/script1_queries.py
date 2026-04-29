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

# Creamos las combinaciones de los constructos generales para una búsqueda más específica

# Funciones para combinar constructos

def merge_or_pm(indices: list, constructos: list) -> str:
    terminos = []
    for i in indices:
        q = constructos[i].strip()
        if q.startswith('(') and q.endswith(')'):
            q = q[1:-1].strip()
        terminos.append(q)
    return "(\n" + "\nOR\n".join(terminos) + "\n)"

def merge_or_scopus(indices: list, constructos: list) -> str:
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

# Ahora sí, combinaciones finales
# Pero primero se definen bloques reutilizables (utilizando OR)

enfermedad_amplia_pm    = merge_or_pm([0, 1], constructos_pm)      # C1 OR C2
enfermedad_amplia_sc    = merge_or_scopus([0, 1], constructos_pm)

biomarcadores_amplio_pm = merge_or_pm([2, 3], constructos_pm)      # C3 OR C4
biomarcadores_amplio_sc = merge_or_scopus([2, 3], constructos_pm)

combinaciones = {
    "1_AL_biomarkers_outcomes": (
        "C2 AND C3 AND C5",
        [bloque_pm(1), bloque_pm(2), bloque_pm(4)],
        [bloque_sc(1), bloque_sc(2), bloque_sc(4)]
    ),
    "2_AL_omics_outcomes": (
        "C2 AND C4 AND C5",
        [bloque_pm(1), bloque_pm(3), bloque_pm(4)],
        [bloque_sc(1), bloque_sc(3), bloque_sc(4)]
    ),
    "3_AL_biomarkers_omics_outcomes": (
        "C2 AND C3 AND C4 AND C5",
        [bloque_pm(1), bloque_pm(2), bloque_pm(3), bloque_pm(4)],
        [bloque_sc(1), bloque_sc(2), bloque_sc(3), bloque_sc(4)]
    ),
    "4_disease-OR_biomarkers_outcomes": (
        "(C1 OR C2) AND C3 AND C5",
        [enfermedad_amplia_pm, bloque_pm(2), bloque_pm(4)],
        [enfermedad_amplia_sc, bloque_sc(2), bloque_sc(4)]
    ),
    "5_disease-OR_omics_outcomes": (
        "(C1 OR C2) AND C4 AND C5",
        [enfermedad_amplia_pm, bloque_pm(3), bloque_pm(4)],
        [enfermedad_amplia_sc, bloque_sc(3), bloque_sc(4)]
    ),
    "6_AL_biomarkers-OR-omics_outcomes": (
        "C2 AND (C3 OR C4) AND C5",
        [bloque_pm(1), biomarcadores_amplio_pm, bloque_pm(4)],
        [bloque_sc(1), biomarcadores_amplio_sc, bloque_sc(4)]
    ),
    "7_disease-OR_biomarkers-OR-omics_outcomes": (
        "(C1 OR C2) AND (C3 OR C4) AND C5 — Máxima exhaustividad",
        [enfermedad_amplia_pm, biomarcadores_amplio_pm, bloque_pm(4)],
        [enfermedad_amplia_sc, biomarcadores_amplio_sc, bloque_sc(4)]
    ),
    "8_ALL": (
        "C1 AND C2 AND C3 AND C4 AND C5",
        [bloque_pm(0), bloque_pm(1), bloque_pm(2), bloque_pm(3), bloque_pm(4)],
        [bloque_sc(0), bloque_sc(1), bloque_sc(2), bloque_sc(3), bloque_sc(4)]
    ),
}

print(f"\n{separador} COMBINACIONES FINALES {separador}")

for nombre, (descripcion, bloques_pm, bloques_sc) in combinaciones.items():
    q_pm     = "\nAND\n".join(bloques_pm)
    q_scopus = "\nAND\n".join(bloques_sc)

    print(f"\n>> {nombre}  —  {descripcion}")
    print(f"\n--- PubMed ---\n{q_pm}")
    print(f"\n--- Scopus ---\n{q_scopus}")

    with open(os.path.join(pubmed_dir, f"PM_{nombre}.txt"), "w", encoding="utf-8") as f:
        f.write(q_pm)
    with open(os.path.join(scopus_dir, f"Scopus_{nombre}.txt"), "w", encoding="utf-8") as f:
        f.write(q_scopus)

print("\n✓ Todas las combinaciones exportadas.")