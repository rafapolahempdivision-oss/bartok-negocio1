import os
import time
import requests
from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()

API_KEY_PROXY = os.getenv("FREELLMAPI_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
MAX_MENSAJES = 16  # Recuerda las últimas 8 interacciones completas

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
- Aprovecha tu memoria persistente para dar continuidad a los planes, cifras y decisiones del Jefe sin repetir presentaciones innecesarias.
"""

def headers_supabase():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

def cargar_historial():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    try:
        url = f"{SUPABASE_URL}/rest/v1/memoria_bartok?select=rol,contenido&order=id.desc&limit={MAX_MENSAJES}"
        resp = requests.get(url, headers=headers_supabase(), timeout=10)
        if resp.status_code == 200:
            datos = resp.json()
            return [{"role": item["rol"], "content": item["contenido"]} for item in reversed(datos)]
    except Exception:
        pass
    return []

def guardar_mensaje(rol: str, contenido: str):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return
    try:
        url = f"{SUPABASE_URL}/rest/v1/memoria_bartok"
        requests.post(
            url,
            headers=headers_supabase(),
            json={"rol": rol, "contenido": contenido},
            timeout=10
        )
    except Exception:
        pass

@app.get("/")
def raiz():
    historial = cargar_historial()
    return {
        "estado": "¡Bartok está despierto, con memoria eterna en Supabase y vigilando Greyhouse Gallery y la Consultoría de Imagen, Jefe!",
        "recuerdos_activos": len(historial)
    }

@app.get("/olvidar")
def limpiar_memoria():
    if SUPABASE_URL and SUPABASE_KEY:
        url = f"{SUPABASE_URL}/rest/v1/memoria_bartok?id=gt.0"
        requests.delete(url, headers=headers_supabase(), timeout=10)
    return {"estado": "¡Memoria purgada en la base de datos, Jefe! Listo para iniciar una nueva estrategia."}

@app.get("/hablar")
def hablar_con_bartok(mensaje: str):
    historial = cargar_historial()
    
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
            
            guardar_mensaje("user", mensaje)
            guardar_mensaje("assistant", respuesta_texto)
            
            return {
                "respuesta": respuesta_texto,
                "memoria_en_nube": "Activa (Supabase)"
            }
        except Exception as e:
            if intento == 0 and ("502" in str(e) or "503" in str(e) or "timed out" in str(e).lower()):
                time.sleep(10)
                continue
            return {"respuesta": f"¡Oh no, Jefe! Hubo un pequeño temblor en la matrix del proxy: {str(e)}"}
