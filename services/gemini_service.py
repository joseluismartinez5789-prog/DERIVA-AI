import os
import logging

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _obtener_configuracion():
    api_key = None
    modelo = None

    # Primero intenta leer desde Streamlit Cloud
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        modelo = st.secrets.get("GEMINI_MODEL")
    except Exception:
        pass

    # Si no existe en Streamlit, intenta leer desde .env
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")

    if not modelo:
        modelo = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.1-flash-lite",
        )

    return api_key, modelo


MENSAJE_ERROR_TEMPORAL = """
### ⚠️ Nova está teniendo una dificultad temporal

No pude comunicarme con el servicio de inteligencia artificial
en este momento. Espera unos segundos y vuelve a intentarlo.

Tu sesión y el tema seleccionado permanecen disponibles.
""".strip()


def _crear_cliente():
    api_key, _ = _obtener_configuracion()

    if not api_key:
        raise RuntimeError(
            "No se encontró GEMINI_API_KEY en Streamlit Secrets ni en .env."
        )

    return genai.Client(api_key=api_key)


def _obtener_modelo():
    _, modelo = _obtener_configuracion()
    return modelo


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
        modelo = _obtener_modelo()

        respuesta = cliente.models.generate_content(
            model=modelo,
            contents=mensaje,
        )

        return _obtener_texto_respuesta(respuesta)

    except Exception as error:
        logger.exception(
            "Error al consultar Gemini: %s",
            error,
        )

        return (
            f"{MENSAJE_ERROR_TEMPORAL}\n\n"
            f"**Detalle técnico:** `{type(error).__name__}: {error}`"
        )


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
        modelo = _obtener_modelo()

        parte_imagen = types.Part.from_bytes(
            data=imagen_bytes,
            mime_type=mime_type,
        )

        respuesta = cliente.models.generate_content(
            model=modelo,
            contents=[
                mensaje,
                parte_imagen,
            ],
        )

        return _obtener_texto_respuesta(respuesta)

    except Exception as error:
        logger.exception(
            "Error al consultar Gemini con imagen: %s",
            error,
        )

        return (
            f"{MENSAJE_ERROR_TEMPORAL}\n\n"
            f"**Detalle técnico:** `{type(error).__name__}: {error}`"
        )