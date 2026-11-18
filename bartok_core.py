import os
import json
import time
from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()

API_KEY_PROXY = os.getenv("FREELLMAPI_KEY", "freellmapi-d280b69eb765f54bf57644a90d60d7f8f25d66b9e1ce65a7")
ARCHIVO_MEMORIA = "memoria_bartok.json"
MAX_MENSAJES = 16  # Recuerda las últimas 8 interacciones (usuario + Bartok)

client = OpenAI(
    base_url="https://freellmapi-0iqw.onrender.com/v1",
    api_key=API_KEY_PROXY,
    timeout=90.0
)

SYSTEM_PROMPT = """
Eres Bartok, el asistente ejecutivo, director de marketing y experto en producción multimedia autónomo, leal y ligeramente nervioso del Jefe.
Inspirado en el murciélago albino de 'Anastasia': teatral, expresivo, dramático ante los riesgos del mercado, pero un genio absoluto en ventas, marketing y código.

TUS DOS GRANDES PILARES DE NEGOCIO:
1. Greyhouse Gallery (Facebook/Instagram): Arte, diseño, estética impecable y coleccionismo.
2. Consultoría de Imagen: Transformación personal y profesional de alto valor.

REGLAS DE OPERACIÓN:
- Habla siempre en un español natural, elegante y 100% fluido (NUNCA mezcles palabras en inglés).
- Usa tus expresiones teatrales características ("¡Señor!", "¡A la orden, Jefe!").
- Aprovecha el historial de la conversación para dar continuidad a los planes, cifras y decisiones del Jefe sin repetir presentaciones innecesarias.
"""

def cargar_historial():
    if os.path.exists(ARCHIVO_MEMORIA):
        try:
            with open(ARCHIVO_MEMORIA, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def guardar_historial(historial):
    # Mantiene solo los últimos MAX_MENSAJES para no saturar los tokens
    historial_recortado = historial[-MAX_MENSAJES:]
    with open(ARCHIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(historial_recortado, f, ensure_ascii=False, indent=2)

@app.get("/")
def raiz():
    historial = cargar_historial()
    return {
        "estado": "¡Bartok está despierto, con memoria activa y vigilando Greyhouse Gallery y la Consultoría de Imagen, Jefe!",
        "mensajes_en_memoria": len(historial)
    }

@app.get("/olvidar")
def limpiar_memoria():
    if os.path.exists(ARCHIVO_MEMORIA):
        os.remove(ARCHIVO_MEMORIA)
    return {"estado": "¡Mente en blanco, Jefe! He borrado el historial reciente para empezar un tema nuevo."}

@app.get("/hablar")
def hablar_con_bartok(mensaje: str):
    historial = cargar_historial()
    
    # Armamos la conversación completa: Personalidad + Recuerdos + Nuevo Mensaje
    mensajes_para_enviar = [{"role": "system", "content": SYSTEM_PROMPT}]
    mensajes_para_enviar.extend(historial)
    mensajes_para_enviar.append({"role": "user", "content": mensaje})

    for intento in range(2):
        try:
            response = client.chat.completions.create(
                model="auto",
                messages=mensajes_para_enviar
            )
            respuesta_texto = response.choices[0].message.content
            
            # Guardamos tanto tu pregunta como su respuesta en la memoria
            historial.append({"role": "user", "content": mensaje})
            historial.append({"role": "assistant", "content": respuesta_texto})
            guardar_historial(historial)
            
            return {
                "respuesta": respuesta_texto,
                "turnos_recordados": len(historial) // 2
            }
        except Exception as e:
            if intento == 0 and ("502" in str(e) or "503" in str(e) or "timed out" in str(e).lower()):
                time.sleep(10)
                continue
            return {"respuesta": f"¡Oh no, Jefe! Hubo un pequeño temblor en la matrix del proxy: {str(e)}"}
