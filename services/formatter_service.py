import re


def limpiar_markdown(texto: str) -> str:
    """
    Limpia algunos errores frecuentes que Gemini produce
    al generar contenido matemático en Markdown.
    """

    reemplazos = {
        "incógnita": "x",
        "calle": "s",
        "medios": "media",
        "Delta": r"\Delta",
        "​​": "",
        " ": " ",
    }

    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)

    # Elimina líneas vacías repetidas
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto