from services.gemini_service import preguntar_gemini_imagen


def analizar_ejercicio_imagen(
    imagen_bytes,
    mime_type,
    nivel="Intermedio",
):
    prompt = f"""
Eres DERIVA AI, un agente tutor experto en Cálculo Diferencial.

Analiza cuidadosamente la imagen proporcionada. Puede contener un ejercicio
impreso, manuscrito o parte del procedimiento realizado por un estudiante.

NIVEL DEL ESTUDIANTE:
{nivel}

OBJETIVOS:

1. Determina si la imagen contiene contenido matemático legible.
2. Transcribe únicamente el ejercicio relevante.
3. Identifica el tema principal.
4. Explica claramente qué se pide.
5. Orienta al estudiante mediante razonamiento paso a paso.
6. No inventes datos que no estén visibles.
7. Si una expresión no se distingue, indícalo claramente.
8. Si no es un ejercicio de Cálculo Diferencial, dilo.
9. Si contiene un procedimiento, revísalo y señala el primer error importante.
10. Mantén un tono motivador, claro y pedagógico.

REGLAS MATEMÁTICAS:

- Escribe las expresiones matemáticas con LaTeX.
- Usa bloques LaTeX para ecuaciones importantes.
- Conserva las variables como símbolos.
- No conviertas símbolos matemáticos en palabras.
- No uses caracteres Unicode como sustitutos de LaTeX.
- Escribe las unidades fuera de las ecuaciones.
- No uses HTML.
- No inventes una solución cuando el contenido sea ilegible.

La primera línea debe ser exactamente una de estas:

ESTADO_IMAGEN: VALIDA
ESTADO_IMAGEN: BORROSA
ESTADO_IMAGEN: NO_MATEMATICA

La segunda línea debe tener exactamente este formato:

TEMA_DETECTADO: nombre del tema

Después utiliza esta estructura:

# Transcripción

Transcribe el ejercicio visible. Si algo no puede leerse, escribe
**[parte no legible]**.

# ¿Qué se pide?

Explica en palabras sencillas el objetivo del ejercicio.

# Conceptos necesarios

Indica brevemente los conceptos matemáticos que se utilizarán.

# Orientación paso a paso

Guía el procedimiento y explica por qué se realiza cada operación.

# Comprobación

Explica cómo verificar el resultado o procedimiento.

# Pregunta de Nova

Formula una pregunta socrática breve para comprobar la comprensión.

Cuando la imagen esté borrosa o no contenga un ejercicio matemático, adapta
las secciones y explica qué debe corregir el estudiante para obtener un buen
análisis.
"""

    return preguntar_gemini_imagen(
        mensaje=prompt,
        imagen_bytes=imagen_bytes,
        mime_type=mime_type,
    )


def extraer_estado_imagen(analisis):
    texto = str(analisis).upper()

    if "ESTADO_IMAGEN: VALIDA" in texto:
        return "valida"

    if "ESTADO_IMAGEN: BORROSA" in texto:
        return "borrosa"

    if "ESTADO_IMAGEN: NO_MATEMATICA" in texto:
        return "no_matematica"

    return "desconocido"


def extraer_tema_detectado(analisis):
    for linea in str(analisis).splitlines():
        if linea.strip().upper().startswith("TEMA_DETECTADO:"):
            tema = linea.split(":", 1)[1].strip()
            return tema or "No identificado"

    return "No identificado"


def limpiar_metadatos_analisis(analisis):
    lineas_limpias = []

    for linea in str(analisis).splitlines():
        linea_mayuscula = linea.strip().upper()

        if linea_mayuscula.startswith("ESTADO_IMAGEN:"):
            continue

        if linea_mayuscula.startswith("TEMA_DETECTADO:"):
            continue

        lineas_limpias.append(linea)

    return "\n".join(lineas_limpias).strip()