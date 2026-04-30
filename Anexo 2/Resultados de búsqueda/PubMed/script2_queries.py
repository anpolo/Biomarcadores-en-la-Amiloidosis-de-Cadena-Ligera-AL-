# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 10:47:52 2026

@author: axdrx
"""
    
from Bio import Medline
import csv
import os


archivo_entrada = r"C:\Users\axdrx\OneDrive\Escritorio\TFM\Resultados búsqueda\pubmed-amyloidosi-set.txt"
archivo_salida = r"C:\Users\axdrx\OneDrive\Escritorio\TFM\scripts TFM\resultados_pubmed.csv"

# --- PROCESO DE CONVERSIÓN ---
if not os.path.exists(archivo_entrada):
    print(f"ERROR: El archivo no existe en la ruta especificada:\n{archivo_entrada}")
else:
    print("Leyendo archivo de PubMed...")
    with open(archivo_entrada, encoding="utf-8") as handle:
        registros = Medline.parse(handle)
        
        # Columnas: Título, Abstract, Autores, Revista, DOI
        columnas = ['Title', 'Abstract', 'Authors', 'Journal', 'DOI']

        with open(archivo_salida, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columnas)
            writer.writeheader()

            contador = 0
            for registro in registros:
                fila = {
                    'Title': registro.get('TI', 'N/A'),
                    'Abstract': registro.get('AB', 'No abstract available'),
                    'Authors': ", ".join(registro.get('AU', [])),
                    'Journal': registro.get('SO', 'N/A'),
                    'DOI': registro.get('AID', ['N/A'])[0]
                }
                writer.writerow(fila)
                contador += 1
                
    print(f"--- ¡PROCESO COMPLETADO! ---")
    print(f"Se han procesado {contador} artículos.")
    print(f"Tu archivo CSV está en: {archivo_salida}")