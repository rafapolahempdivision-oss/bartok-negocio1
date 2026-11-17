import os
from fastapi import FastAPI
from openai import OpenAI
from bartok_skills.editor_video import procesar_video_prueba
from bartok_skills.conexion_freellmapi import probar_freellmapi

app = FastAPI()

# Configuramos el cliente OpenAI apuntando a nuestro servidor proxy gratuito en Render
client = OpenAI(
    base_url="https://freellmapi-0iqw.onrender.com/v1",
    api_key="not-needed" # FreeLLMAPI gestiona las llaves internamente de forma gratuita
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
    
    try:
        # Usamos el motor masivo conectado a través de FreeLLMAPI
        response = client.chat.completions.create(
            model="gpt-4o-mini", # O el modelo gratuito de tu preferencia disponible en el proxy
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": mensaje}
            ]
        )
        respuesta_texto = response.choices[0].message.content
    except Exception as e:
        respuesta_texto = f"¡Oh no, Jefe! Hubo un pequeño temblor en la matrix del proxy: {str(e)}"

    return {"respuesta": respuesta_text}
