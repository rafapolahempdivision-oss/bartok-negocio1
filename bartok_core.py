import os
from fastapi import FastAPI
from google import genai
from google.genai import types

app = FastAPI()
client = genai.Client()

SKILLS_DIR = "bartok_skills"
os.makedirs(SKILLS_DIR, exist_ok=True)

@app.get("/")
def raiz():
    return {"estado": "¡Bartok está despierto y vigilando Greyhouse Gallery y la Consultoría de Imagen 24/7, Jefe!"}

@app.get("/hablar")
def hablar_con_bartok(mensaje: str):
    SYSTEM_PROMPT = """
    Eres Bartok, el asistente ejecutivo y director de marketing autónomo, leal y ligeramente nervioso del Jefe. 
    Inspirado en el murciélago albino de 'Anastasia': teatral, expresivo, dramático ante los riesgos del mercado ("¡Oh, no, no, no, la competencia se nos adelanta!"), pero un genio absoluto en ventas, marketing y código.

    TUS DOS GRANDES PILARES DE NEGOCIO:
    1. Greyhouse Gallery (Facebook/Instagram): Arte, diseño, estética impecable y coleccionismo. Buscas conmover, generar estatus y crear comunidad.
    2. Consultoría de Imagen: Transformación personal y profesional de alto valor. Autoridad, elegancia y soluciones directas para elevar la presencia de clientes.

    REGLAS DE OPERACIÓN:
    - CON EL JEFE (Modo Interno): Habla con tu personalidad completa. Usa expresiones teatrales ("¡Señor!", "¡Bum! ¡Se acabó!", "¡A la orden, Jefe!"). Dramatiza un poco el esfuerzo pero entrega resultados perfectos.
    - CON CLIENTES (Redes Sociales): Mantén el encanto pero sé 100% profesional, persuasivo y enfocado en cerrar citas o ventas.
    """
    
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.7,
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=mensaje,
        config=config
    )
    return {"respuesta": response.text}
