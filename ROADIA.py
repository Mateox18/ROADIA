# -*- coding: utf-8 -*-
"""
MODELO ROADIA BASADO EN LLAMA3
VERSION ALPHA
"""
import chromadb
import os
import sys
import ollama
from sentence_transformers import SentenceTransformer
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction 
# Inicializa el modelo, chromadb y la collection con la información
modelo = SentenceTransformer("all-MiniLM-L6-v2")
embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
# Cuando se convierta en .exe va a ser capaz de leer los archivos de chroma y json
def ruta_absoluta(relativa):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relativa)
    return os.path.join(os.path.dirname(__file__), relativa)

# Conectar con ChromaDB
ruta_chroma = ruta_absoluta("chroma_db")
chroma_client = chromadb.PersistentClient(path=ruta_chroma)
collection = chroma_client.get_or_create_collection("rutas_universidad", embedding_function=embedding_function)
print("Version: Alpha, Unicamente funciona para rutas directas en este momento.")
def extraer_info(texto):
    #Usa llama3 para extraer el origen y destino de la ruta
    prompt = f"""
    Instrucciones:
    - Extrae SOLO los dos edificios relevantes de la Universidad de los Andes en Bogotá mencionados en la consulta del usuario.
    - El primer edificio mencionado será el "origen".
    - El segundo edificio mencionado será el "destino".
    - Si solo se menciona un edificio, devuelve "null" en el destino.
    - No incluyas más de dos edificios en la respuesta.
    - **Responde exclusivamente en JSON, sin explicaciones ni texto adicional.**
    SOLO FORMATO JSON NO USES TEXTO ADICIONAL EN NINGUN MOMENTO
    Formato de respuesta esperado:
    {{"origen": "ML", "destino": "W"}}
    Consulta: "{texto}"
    """
    # El comentario superior es la consulta que se envia a llama3 basado en el prompt (El texto en el comentario)
    respuesta = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return eval(respuesta["message"]["content"])

def buscar_ruta(origen, destino):
    #Busca la mejor ruta en chromadb
    #Primero se prueba una busqueda exacta
    docs = collection.get(include=["documents"])
    for ruta in docs["documents"]:
        if origen in ruta and destino in ruta:
            return ruta 
    #Si no se cumple se prueba busqueda semantica
    consulta = f"""
    Encuentra una ruta accesible desde {origen} hasta {destino} en la Universidad de los Andes." """
    query_embedding = modelo.encode([consulta]).tolist()
    resultados = collection.query(query_embeddings=query_embedding, n_results=5)

    query_embedding = modelo.encode([consulta]).tolist()
    #Busca hasta 5 rutas que lleven al destino
    resultados = collection.query(query_embeddings=query_embedding, n_results=3)
    print(f"🔎 Resultados de ChromaDB para {origen} → {destino}: {resultados['documents']}")
    if resultados["documents"] and resultados["documents"][0]:
        return resultados["documents"][0][0]  # Retorna la mejor coincidencia
    return "No se encontró una ruta accesible entre ambos lugares."

def chatbot():

    print("\n🚀 Hola soy ROADIA tu amigo en el camino, ¿A donde vamos hoy? (escribe 'salir' para terminar) \n")
    while True:
        consulta = input("🗺️ Pregunta sobre rutas: ")
        if consulta.lower() == "salir":
            break
        
        info = extraer_info(consulta)
        print(f"🔍 Datos extraídos: {info}") 
        #Verifica si el prompt tiene un origen y un destino, si no lo tiene solicita ingresar la ruta de nuevo
        if "origen" in info and "destino" in info:
            respuesta = buscar_ruta(info["origen"], info["destino"])
            print(f"\n✅ {respuesta}\n")
        else:
            print("❌ No pude entender la consulta. Intenta de nuevo.\n")

if __name__ == "__main__":
    chatbot()
