import os
from dotenv import load_dotenv
from google import genai

# Cargar variables del archivo .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

print("Clave encontrada:", API_KEY is not None)

if API_KEY:
    print("Longitud:", len(API_KEY))

# Crear cliente Gemini
client = genai.Client(
    api_key=API_KEY
)

# Probar conexión
respuesta = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents="Responde solamente: conexión exitosa"
)

print("\nRespuesta de Gemini:")
print(respuesta.text)
