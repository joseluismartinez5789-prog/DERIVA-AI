import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODELO = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.1-flash-lite",
)


MENSAJE_ERROR_TEMPORAL = """
### ⚠️ Nova está teniendo una dificultad temporal

No pude comunicarme con el servicio de inteligencia artificial
en este momento. Espera unos segundos y vuelve a intentarlo.

Tu sesión y el tema seleccionado permanecen disponibles.
""".strip()


def _crear_cliente():
    if not API_KEY:
        raise RuntimeError(
            "No se encontró GEMINI_API_KEY en el archivo .env."
        )

    return genai.Client(api_key=API_KEY)


def _obtener_texto_respuesta(respuesta):
    texto = getattr(respuesta, "text", None)

    if not texto:
        raise RuntimeError(
            "Gemini no devolvió una respuesta de texto."
        )

    return texto.strip()


def preguntar_gemini(mensaje):
    try:
        cliente = _crear_cliente()

        respuesta = cliente.models.generate_content(
            model=MODELO,
            contents=mensaje,
        )

        return _obtener_texto_respuesta(respuesta)

    except Exception:
        return MENSAJE_ERROR_TEMPORAL


def preguntar_gemini_imagen(
    mensaje,
    imagen_bytes,
    mime_type,
):
    if not imagen_bytes:
        raise ValueError("La imagen está vacía.")

    tipos_permitidos = {
        "image/png",
        "image/jpeg",
        "image/webp",
    }

    if mime_type not in tipos_permitidos:
        raise ValueError(
            "El formato de imagen no es compatible. "
            "Utiliza PNG, JPG, JPEG o WEBP."
        )

    try:
        cliente = _crear_cliente()

        parte_imagen = types.Part.from_bytes(
            data=imagen_bytes,
            mime_type=mime_type,
        )

        respuesta = cliente.models.generate_content(
            model=MODELO,
            contents=[
                mensaje,
                parte_imagen,
            ],
        )

        return _obtener_texto_respuesta(respuesta)

    except Exception:
        return MENSAJE_ERROR_TEMPORAL