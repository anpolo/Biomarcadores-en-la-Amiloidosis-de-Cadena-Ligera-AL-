# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 10:42:13 2026

@author: axdrx
"""

# UDFs para la extracción de datos de los estudios seleccionados

import pandas as pd
import re
import os


BASE_DIR    = r"C:\Users\axdrx\OneDrive\Escritorio\TFM\Extraccion"
STUDIES_CSV = os.path.join(BASE_DIR, "tabla_estudios.csv")
BIOMARK_CSV = os.path.join(BASE_DIR, "tabla_biomarcadores.csv")

os.makedirs(BASE_DIR, exist_ok=True)

# Primero se crean las tablas vacías

def create_studies_table():
    """
    Tabla de características generales de los estudios.
    Una fila por artículo.
    """
    columns = [
        'article_id',    # Primer autor + año (ej. Lin2018)
        'article',       # Referencia: Primer autor et al., año, revista
        'journal',       # Revista
        'study_design',  # Diseño del estudio
        'subgroups',     # Subgrupos de pacientes (todos en una sola columna)
        'techniques',    # Técnicas utilizadas
    ]
    return pd.DataFrame(columns=columns)


def create_biomarkers_table():
    """
    Tabla de biomarcadores.
    Una fila por biomarcador — un artículo puede tener varias filas.
    """
    columns = [
        'article_id',       # ID del artículo asociado
        'biomarker_name',   # Nombre/s del biomarcador
        'biomarker_type',   # Tipo
        'sample_type',      # Tipo de muestra
        'clinical_purpose', # Propósito: diagnóstico, pronóstico, monitorización...
        'validation_status',# Estado de validación
        'main_findings',    # Hallazgos principales 
        'limitations',      # Limitaciones
    ]
    return pd.DataFrame(columns=columns)

# Función para añadir un estudio

def add_study(article_id, article, journal, study_design,
              subgroups, techniques):
    """Añade un estudio a la tabla de características generales."""
    try:
        df = pd.read_csv(STUDIES_CSV, encoding='utf-8-sig')
    except FileNotFoundError:
        df = create_studies_table()

    new_row = {
        'article_id':   article_id,
        'article':      article,
        'journal':      journal,
        'study_design': study_design,
        'subgroups':    subgroups,
        'techniques':   techniques,
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(STUDIES_CSV, index=False, encoding='utf-8-sig')
    print(f"✓ Estudio añadido: {article_id}")
    return df

# Función para añadir un biomarcador

def add_biomarker(article_id, biomarker_name, biomarker_type,
                  sample_type, clinical_purpose, validation_status,
                  main_findings, limitations):
    """
    Añade un biomarcador a la tabla de biomarcadores.
    Un mismo artículo puede generar varias llamadas a esta función.
    """
    try:
        df = pd.read_csv(BIOMARK_CSV, encoding='utf-8-sig')
    except FileNotFoundError:
        df = create_biomarkers_table()

    new_row = {
        'article_id':        article_id,
        'biomarker_name':    biomarker_name,
        'biomarker_type':    biomarker_type,
        'sample_type':       sample_type,
        'clinical_purpose':  clinical_purpose,
        'validation_status': validation_status,
        'main_findings':     main_findings,
        'limitations':       limitations,
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(BIOMARK_CSV, index=False, encoding='utf-8-sig')
    print(f"✓ Biomarcador añadido: {biomarker_name}  (artículo: {article_id})")
    return df

# Función para añadir un artículo

def choose_study(author, df):
    """Busca un artículo en el DataFrame por nombre de autor."""
    c1 = df["Autores"].str.contains(author, case=False, na=False)
    return df.loc[c1]

# Función para la revisión interactiva

def review(author, include, reviewed, studies_df):
    """
    Revisión interactiva de un artículo.
    Extrae los datos del estudio y sus biomarcadores.

    Uso en Jupyter:
        include, reviewed, studies_df = mf.review(
            "Autor", include, reviewed, studies_df)
    """
    affirmative = ["y", "yes", "sí", "si"]

    study = choose_study(author, include)

    if len(study) == 0:
        raise ValueError("Artículo no encontrado — revisa el nombre del autor.")

    print(f"\nTítulo: {study['Título'].values[0]}")
    print(f"Autor:  {study['Autores'].values[0]}")
    print(f"DOI:    {study['DOI'].values[0]}")

    decision = input("\n¿Extraer datos de este artículo? (y/n): ")

   # Extracción
    if decision.casefold() in affirmative:

        print("\n── Tabla de características generales ───────────────")
        year         = input("Año de publicación: ")
        journal      = input("Revista: ")
        study_design = input("Diseño del estudio: ")
        subgroups    = input("Subgrupos de pacientes (ej. n=50 AL, n=20 controles sanos, n=15 MGUS): ")
        techniques   = input("Técnicas utilizadas: ")

        # Generar article_id: primer apellido + año
        surname    = re.match(r"(\w+)", author).group(1)
        article_id = f"{surname}{year}"

        # Generar referencia
        article_ref = f"{author} et al., {year}, {journal}"

        studies_df = add_study(
            article_id=article_id,
            article=article_ref,
            journal=journal,
            study_design=study_design,
            subgroups=subgroups,
            techniques=techniques,
        )

        # Biomarcadores
        print("\n── Tabla de biomarcadores ───────────────────────────")
        otro = "y"
        while otro.casefold() in affirmative:
            print(f"\nBiomarcador de {article_id}:")
            bm_name    = input("Nombre/s del biomarcador: ")
            bm_type    = input("Tipo (proteómico/genómico/imagen/circulante/panel): ")
            bm_sample  = input("Tipo de muestra (suero/plasma/orina/tejido/imagen): ")
            bm_purpose = input("Propósito clínico (diagnóstico/pronóstico/monitorización/varios): ")
            bm_val     = input("Estado de validación: ")
            bm_find    = input("Hallazgos principales: ")
            bm_lim     = input("Limitaciones: ")

            add_biomarker(
                article_id=article_id,
                biomarker_name=bm_name,
                biomarker_type=bm_type,
                sample_type=bm_sample,
                clinical_purpose=bm_purpose,
                validation_status=bm_val,
                main_findings=bm_find,
                limitations=bm_lim,
            )
            otro = input("\n¿Añadir otro biomarcador de este artículo? (y/n): ")

        # Mover de include a reviewed
        c        = include["DOI"].isin(study["DOI"])
        include  = include.loc[~c]
        reviewed = pd.concat([reviewed, study], ignore_index=True)

        include.to_csv(os.path.join(BASE_DIR, "tabla_incluidos.csv"),
                       index=False, encoding='utf-8-sig')
        reviewed.to_csv(os.path.join(BASE_DIR, "tabla_revisados.csv"),
                        index=False, encoding='utf-8-sig')

        print(f"\n✓ {article_id} extraído y movido a revisados.")
        return include, reviewed, studies_df

    # Omitir
    else:
        print("Artículo omitido.")
        return include, reviewed, studies_df

# Recargar tablas

def reload():
    """Recarga todas las tablas desde los CSVs guardados."""
    def safe_read(path):
        try:
            return pd.read_csv(path, encoding='utf-8-sig')
        except FileNotFoundError:
            return pd.DataFrame()

    include    = safe_read(os.path.join(BASE_DIR, "tabla_incluidos.csv"))
    reviewed   = safe_read(os.path.join(BASE_DIR, "tabla_revisados.csv"))
    studies_df = safe_read(STUDIES_CSV)
    biomark_df = safe_read(BIOMARK_CSV)

    print("✓ Tablas recargadas:")
    print(f"  Incluidos pendientes: {len(include)}")
    print(f"  Revisados:            {len(reviewed)}")
    print(f"  Estudios extraídos:   {len(studies_df)}")
    print(f"  Biomarcadores:        {len(biomark_df)}")

    return include, reviewed, studies_df, biomark_df

