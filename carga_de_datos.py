# -*- coding: utf-8 -*-
"""
CARGA DE DATOS PARA ROADIA
"""

import json
import chromadb
from sentence_transformers import SentenceTransformer
import os
import sys
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
# Cuando se convierta en .exe va a ser capaz de leer los archivos de chroma y json
def ruta_absoluta(relativa):
    if getattr(sys, 'frozen', False):  # Si está en un .exe
        return os.path.join(sys._MEIPASS, relativa)
    return os.path.join(os.path.dirname(__file__), relativa)

#Este modelo transformara la informacion en embeddings para que ROADIA tenga mayor precision en sus respuestas
modelo = SentenceTransformer("all-MiniLM-L6-v2") 
embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
# Este apartado transforma el json en chromadb
ruta_json = ruta_absoluta("RUTAS.json")
def cargar_datos():
# Este apartado importa la info desde el json al programa
    with open(ruta_json, "r", encoding="utf-8") as file:
        datos = json.load(file)
# Carga de base de datos de ROADIA
# Se transforma la base de datos en chromadb para que el modelo la lea usando busqueda semantica
# Se convierte en una base de datos vectorial para la busqueda semantica, esto haciendo uso de embeddings (Modelos entrenados con este proposito)
    rutas_procesadas = []
# Se crea una lista vacia que contendra los archivos de la base de datos
    ids = []
    contador_id = 0
# Esta lista almacenara los ids de cada ruta
    for categoria in ["plazas", "bloques"]:
        if categoria in datos:
            for plaza, info in datos[categoria].items():
                for piso, datos_piso in info.get("pisos", {}).items():
                #  Verificar que el piso tenga conexiones antes de continuar
                    if "conexiones" not in datos_piso:
                        continue  # Evita errores si no hay conexiones en ese piso
                    for conexion in datos_piso["conexiones"]:
                        #  Verifica todas las conexiones en la ruta almacenadas en el JSON
                        #  Se transforma todo en texto legible incluyendo la mayor información posible
                        descripcion = (
                                    f"Desde {plaza} puedes ir a {', '.join(conexion['destino'])} "
                                    f"usando {conexion['tipo_conexion']}. "
                                    f"{'Hay rampa disponible.' if conexion['accesibilidad']['rampa'] else ''} "
                                    f"{'También hay ascensor.' if conexion['accesibilidad']['ascensor'] else ''}"
                        )

                        # Este comando agrega a la lista rutas_procesadas la información procesada en descripción
                        rutas_procesadas.append(descripcion)
                        # Genera un ID para cada ruta y lo almacena en la ruta
                        ids.append(f"{plaza}_{conexion['destino'][0]}_{conexion['tipo_conexion']}_{contador_id}")
                        # Modelo.encode transforma las rutas_procesadas en vectores para la búsqueda semántica
                        # .tolist() los vuelve listas de Python para almacenarlos
                        print(f" Total IDs: {len(ids)}")
                        embeddings = modelo.encode(rutas_procesadas).tolist()
                        print(f" Total embeddings generados: {len(embeddings)}")
                        contador_id += 1 # Para evitar ID duplicados
    
    min_length = min(len(rutas_procesadas), len(ids), len(embeddings))
    rutas_procesadas = rutas_procesadas[:min_length]
    ids = ids[:min_length]
    embeddings = embeddings[:min_length]
    # Conectar a la base de datos
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    # Crea una base de datos persistente (de ahi el .PersistentClient) en un directorio llamado /chroma_db en la carpeta ROADIA
    collection = chroma_client.get_or_create_collection("rutas_universidad")
    print("📌 Todas las rutas procesadas antes de agregar a ChromaDB:")
    for ruta in rutas_procesadas:
        print(ruta)
    # Crea una tabla con la informacion de las rutas en chromadb
    collection.add(
        ids=ids,  # Lista de IDs únicos
        documents=rutas_procesadas,  # Texto de las rutas
        embeddings=embeddings  # Vectores generados en los embeddings
        )
        #IMPORTANTE: CADA RUTA DEBE TENER UN VALOR DE ID, DOCUMENT Y EMBEDDING PARA CADA RUTA SI NO EL PROCESO FALLARA

        # Cuenta las rutas almacenadas en la coleccion (La tabla anterior)
    num_rutas = collection.count()
    print(f"✅ ChromaDB contiene {num_rutas} rutas accesibles en embeddings.")
    # Imprimir algunas rutas almacenadas
    docs = collection.get(include=["documents"], limit=5)  # Obtiene 5 rutas de muestra
    ("📂 Ejemplo de rutas almacenadas en ChromaDB:")
    for i, doc in enumerate(docs["documents"]):
        print(f"{i+1}. {doc}")
    docs = collection.get(include=["documents"])
    rutas_filtradas = [ruta for ruta in docs["documents"] if "ML" in ruta and "W" in ruta]

    print("🔎 Rutas exactas que contienen ML y W:")
    for ruta in rutas_filtradas:
        print(ruta)

    if not rutas_filtradas:
        print("❌ No se encontraron rutas directas entre ML y W en ChromaDB.")
cargar_datos()
