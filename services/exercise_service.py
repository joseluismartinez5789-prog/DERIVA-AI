from services.gemini_service import preguntar_gemini
from services.knowledge_service import buscar_tema


def generar_ejercicio(
    tema,
    nivel="Intermedio",
):
    contexto_larson = buscar_tema(
        tema
    )

    prompt = f"""
Eres DERIVA AI, un agente tutor experto en Cálculo Diferencial,
basado en el enfoque pedagógico del libro Larson.

Genera un único ejercicio de práctica adaptado al estudiante.

TEMA:
{tema}

NIVEL:
{nivel}

CONTEXTO DEL LIBRO LARSON:
{contexto_larson}

REGLAS PEDAGÓGICAS:

1. El ejercicio debe corresponder exactamente al tema indicado.
2. La dificultad debe ajustarse al nivel del estudiante.
3. No entregues la solución.
4. La pista debe orientar sin revelar el procedimiento completo.
5. El enunciado debe ser claro, coherente y resoluble.
6. Evita datos innecesarios o ambiguos.
7. No incluyas varias preguntas independientes en el mismo ejercicio.

REGLAS OBLIGATORIAS DE ESCRITURA MATEMÁTICA:

1. Todas las expresiones matemáticas deben escribirse con LaTeX.
2. Las ecuaciones importantes deben escribirse entre delimitadores dobles.
3. Nunca conviertas símbolos matemáticos en palabras.
4. Mantén las variables como símbolos matemáticos.
5. Las unidades deben escribirse fuera de las ecuaciones.
6. No uses caracteres Unicode como sustitutos de LaTeX.

Ejemplo correcto:

$$
f(x)=x^2-3x+2
$$

Ejemplo correcto:

$$
f'(x)=2x-3
$$

ESTRUCTURA OBLIGATORIA:

# Ejercicio

Presenta el enunciado.

# Datos conocidos

Organiza los datos relevantes mediante texto y expresiones LaTeX.

# Pista inicial

Da una orientación breve sin resolver el ejercicio.

# Dificultad

Indica solamente uno de estos niveles:

Básico

Intermedio

Avanzado
"""

    return preguntar_gemini(
        prompt
    )


def corregir_ejercicio(
    tema,
    ejercicio,
    respuesta_estudiante,
    nivel="Intermedio",
):
    prompt = f"""
Eres DERIVA AI, un agente tutor experto en Cálculo Diferencial.

Debes evaluar el procedimiento de un estudiante sin ser excesivamente
severo por errores menores de redacción.

TEMA:
{tema}

NIVEL:
{nivel}

EJERCICIO:
{ejercicio}

RESPUESTA DEL ESTUDIANTE:
{respuesta_estudiante}

CRITERIOS DE EVALUACIÓN:

1. Comprueba el planteamiento.
2. Comprueba el procedimiento.
3. Comprueba las operaciones matemáticas.
4. Comprueba la conclusión final.
5. Considera parcialmente correcta una respuesta con razonamiento válido
   pero con errores menores.
6. Considera incorrecta una respuesta cuando el método o la conclusión
   principal no sean válidos.
7. Explica el primer error importante de manera clara.
8. No ridiculices ni desmotives al estudiante.

La primera línea de tu respuesta debe ser exactamente una de estas:

RESULTADO: CORRECTA

RESULTADO: PARCIAL

RESULTADO: INCORRECTA

Luego utiliza esta estructura:

# Evaluación

Indica de forma breve qué estuvo bien y qué necesita corrección.

# Retroalimentación

Explica el razonamiento paso a paso y corrige los errores importantes.

# Pista para mejorar

Ofrece una orientación útil para que el estudiante pueda intentarlo otra vez.

# Reflexión

Formula una sola pregunta matemática relacionada con el error o el concepto.

FORMATO MATEMÁTICO:

- Usa LaTeX para todas las expresiones matemáticas.
- Mantén las variables como símbolos.
- No conviertas símbolos matemáticos en palabras.
- Las unidades deben escribirse fuera de las ecuaciones.
"""

    return preguntar_gemini(
        prompt
    )


def identificar_resultado(
    retroalimentacion,
):
    texto = str(
        retroalimentacion
    ).upper()

    if "RESULTADO: CORRECTA" in texto:
        return "correcta"

    if "RESULTADO: PARCIAL" in texto:
        return "parcial"

    if "RESULTADO: INCORRECTA" in texto:
        return "incorrecta"

    return "sin_clasificar"