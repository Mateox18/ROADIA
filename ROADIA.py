
"""
MODELO ROADIA BASADO EN LLAMA3
VERSION ALPHA
"""
import os
import sys
import ollama

# Cuando se convierta en .exe va a ser capaz de leer los archivos de chroma y json
def ruta_absoluta(relativa):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relativa)
    return os.path.join(os.path.dirname(__file__), relativa)


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
    pass
#Yo hago esto

def chatbot():
#Consola, terminal interfaz etc revisa esto.
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
