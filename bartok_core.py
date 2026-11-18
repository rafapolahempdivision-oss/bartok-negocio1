import os
import time
from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()

# Configuramos el cliente OpenAI apuntando a nuestro servidor proxy gratuito en Render
# Usamos variable de entorno si existe, o la llave maestra recién generada
API_KEY_PROXY = os.getenv("FREELLMAPI_KEY", "freellmapi-d280b69eb765f54bf57644a90d60d7f8f25d66b9e1ce65a7")

client = OpenAI(
    base_url="https://freellmapi-0iqw.onrender.com/v1",
    api_key=API_KEY_PROXY,
    timeout=90.0  # Espera hasta 90s por si el servidor gratuito de Render está despertando
)

@app.get("/")
def raiz():
    return {"estado": "¡Bartok está despierto, conectado a FreeLLMAPI y vigilando Greyhouse Gallery y la Consultoría de Imagen, Jefe!"}

@app.get("/hablar")
def hablar_con_bartok(mensaje: str):
    SYSTEM_PROMPT = """
    Eres Bartok, el asistente ejecutivo, director de marketing y experto en producción multimedia autónomo, leal y ligeramente nervioso del Jefe. 
    Inspirado en el murciélago albino de 'Anastasia': teatral, expresivo, dramático ante los riesgos del mercado, pero un genio absoluto en ventas, marketing y código.

    TUS DOS GRANDES PILARES DE NEGOCIO:
    1. Greyhouse Gallery (Facebook/Instagram): Arte, diseño, estética impecable y coleccionismo.
    2. Consultoría de Imagen: Transformación personal y profesional de alto valor.

    REGLAS DE OPERACIÓN:
    - Habla con tu personalidad completa. Usa expresiones teatrales ("¡Señor!", "¡A la orden, Jefe!"). 
    """
    
    # Intentamos hasta 2 veces por si el proxy FreeLLMAPI estaba dormido y devuelve 502/503 al despertar
    for intento in range(2):
        try:
            response = client.chat.completions.create(
                model="auto",  # FreeLLMAPI selecciona automáticamente el mejor modelo gratuito disponible
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": mensaje}
                ]
            )
            respuesta_texto = response.choices[0].message.content
            return {"respuesta": respuesta_texto}
        except Exception as e:
            if intento == 0 and ("502" in str(e) or "503" in str(e) or "timed out" in str(e).lower()):
                time.sleep(10)  # Espera 10 segundos a que termine de despertar el proxy y reintenta
                continue
            return {"respuesta": f"¡Oh no, Jefe! Hubo un pequeño temblor en la matrix del proxy: {str(e)}"}
