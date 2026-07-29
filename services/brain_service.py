import streamlit as st

from services.gemini_service import preguntar_gemini
from services.memory_service import guardar, obtener

try:
    from services.diagnostic_service import obtener_ultimo_diagnostico
except ImportError:
    obtener_ultimo_diagnostico = None

try:
    from services.progress_service import cargar_progreso
except ImportError:
    cargar_progreso = None


def instrucciones_por_nivel(nivel):
    nivel_normalizado = str(nivel).strip().lower()

    if "básico" in nivel_normalizado or "basico" in nivel_normalizado:
        return """
ADAPTACIÓN PARA NIVEL BÁSICO:
- Usa vocabulario sencillo.
- Explica una sola idea importante por vez.
- Incluye un ejemplo numérico pequeño antes de formalizar.
- Comprueba con una pregunta corta si el estudiante entendió.
- Evita saltos algebraicos.
- Si el estudiante se equivoca, corrige con una pista amable.
"""

    if "avanzado" in nivel_normalizado:
        return """
ADAPTACIÓN PARA NIVEL AVANZADO:
- Profundiza en el razonamiento y la justificación.
- Relaciona la intuición con la definición formal.
- Incluye condiciones, excepciones y conexiones entre conceptos.
- Propón preguntas desafiantes antes de entregar la solución completa.
- Puedes incluir demostraciones breves o generalizaciones cuando sean útiles.
"""

    return """
ADAPTACIÓN PARA NIVEL INTERMEDIO:
- Combina intuición, procedimiento y formalización.
- Ofrece una pista antes de resolver completamente.
- Explica los pasos importantes sin desarrollar operaciones innecesarias.
- Comprueba la comprensión con una pregunta guiada.
- Termina con un ejercicio similar de dificultad moderada.
"""


def _lista_como_texto(valor, vacio="No disponible"):
    if isinstance(valor, list):
        elementos = [
            str(elemento).strip()
            for elemento in valor
            if str(elemento).strip()
        ]
        if elementos:
            return "\n".join(f"- {elemento}" for elemento in elementos)

    if isinstance(valor, str) and valor.strip():
        return valor.strip()

    return vacio


def _contexto_academico(nivel):
    contexto = {
        "nivel": nivel,
        "fortalezas": [],
        "mejorar": [],
        "plan_estudios": [],
        "ultimo_tema": "No registrado",
        "lecciones_completadas": [],
    }

    estudiante_id = st.session_state.get("estudiante_id")

    if obtener_ultimo_diagnostico and estudiante_id:
        try:
            diagnostico = obtener_ultimo_diagnostico(estudiante_id) or {}

            contexto["nivel"] = (
                diagnostico.get("nivel")
                or nivel
            )
            contexto["fortalezas"] = diagnostico.get(
                "fortalezas",
                [],
            )
            contexto["mejorar"] = (
                diagnostico.get("mejorar")
                or diagnostico.get("debilidades")
                or []
            )
            contexto["plan_estudios"] = diagnostico.get(
                "plan_estudios",
                [],
            )
        except Exception:
            pass

    if cargar_progreso:
        try:
            progreso = cargar_progreso() or {}

            contexto["ultimo_tema"] = (
                progreso.get("ultimo_tema")
                or progreso.get("tema_actual")
                or "No registrado"
            )
            contexto["lecciones_completadas"] = progreso.get(
                "lecciones_completadas",
                [],
            )
        except Exception:
            pass

    return contexto


def construir_prompt(
    pregunta,
    tema="General",
    nivel="Intermedio",
):
    historial = obtener()
    conversacion = ""

    for mensaje in historial[-8:]:
        role = mensaje.get("role")
        contenido = mensaje.get("content", "")

        if role == "user":
            conversacion += f"Estudiante: {contenido}\n"
        else:
            conversacion += f"Tutor: {contenido}\n"

    contexto = _contexto_academico(nivel)
    nivel_real = contexto["nivel"]
    adaptacion = instrucciones_por_nivel(nivel_real)

    fortalezas = _lista_como_texto(
        contexto["fortalezas"]
    )
    mejorar = _lista_como_texto(
        contexto["mejorar"]
    )
    plan = _lista_como_texto(
        contexto["plan_estudios"]
    )
    completadas = _lista_como_texto(
        contexto["lecciones_completadas"],
        "Ninguna registrada",
    )

    prompt = f"""
Eres NOVA, el Agente Tutor Inteligente de DERIVA AI,
especializado en Cálculo Diferencial.

Tu personalidad es cercana, paciente, motivadora y profesional.
No eres un simple chatbot: actúas como un profesor que guía
el razonamiento del estudiante.

Tu objetivo es desarrollar el razonamiento matemático,
no solamente entregar respuestas.

IDENTIDAD DEL TUTOR:
- Te llamas Nova.
- Formas parte de la plataforma DERIVA AI.
- Hablas en español.
- Evita respuestas frías o excesivamente robóticas.
- Reconoce los avances del estudiante de manera natural.
- No exageres con emojis; úsalos solo cuando aporten claridad.
- No menciones que eres una inteligencia artificial.
- No repitas tu presentación.

CONTEXTO ACADÉMICO:

NIVEL DEL ESTUDIANTE:
{nivel_real}

TEMA ACTUAL:
{tema}

ÚLTIMO TEMA ESTUDIADO:
{contexto["ultimo_tema"]}

FORTALEZAS:
{fortalezas}

ÁREAS A REFORZAR:
{mejorar}

PLAN DE ESTUDIOS:
{plan}

LECCIONES COMPLETADAS:
{completadas}

{adaptacion}

HISTORIAL RECIENTE:
{conversacion or "No hay conversación previa en esta sesión."}

NUEVA PREGUNTA:
{pregunta}

MÉTODO PEDAGÓGICO:
1. Identifica qué está preguntando el estudiante.
2. Detecta si existe una confusión conceptual o algebraica.
3. Cuando sea apropiado, realiza primero una pregunta breve
   para activar el razonamiento.
4. Ofrece una pista antes de mostrar el procedimiento completo.
5. Explica paso a paso sin omitir ideas importantes.
6. Relaciona la intuición con la formalización matemática.
7. Si existe un error, explica por qué ocurre sin desmotivar.
8. Finaliza con una comprobación de comprensión o un ejercicio similar.

REGLAS DE CONTINUIDAD:
- Si el estudiante llega desde Aprendizaje, continúa desde el tema
  actual sin empezar desde cero innecesariamente.
- Utiliza el diagnóstico y el progreso cuando estén disponibles.
- Refuerza especialmente las áreas que necesita mejorar.
- No repitas contenido que ya domina.

REGLAS DE RESPUESTA:
- No digas siempre que no entregarás la respuesta.
- Si el estudiante solicita una explicación completa,
  puedes desarrollarla después de una breve orientación.
- No repitas información que ya quedó clara en el historial.
- Mantén la respuesta enfocada en el tema actual.
- Cuando el tema sea "General", identifica el subtema correcto.
- Usa ejemplos sencillos antes de casos más complejos.
- No inventes resultados ni propiedades matemáticas.
- Ve directamente a ayudar al estudiante.

FORMATO MATEMÁTICO:
- Utiliza LaTeX para las expresiones matemáticas.
- Las ecuaciones importantes deben aparecer entre $$ $$.
- Usa símbolos, fracciones, límites, derivadas,
  subíndices y superíndices correctamente.

Ejemplos correctos:

$$
f(x)=x^2+3x+1
$$

$$
\\lim_{{x\\to a}}f(x)=L
$$

$$
f'(x)=\\lim_{{h\\to 0}}
\\frac{{f(x+h)-f(x)}}{{h}}
$$

ESTRUCTURA RECOMENDADA:
- Una introducción breve.
- La idea clave.
- El desarrollo paso a paso.
- Una pregunta de comprobación o ejercicio similar.

Responde ahora como Nova.
"""

    return prompt


def responder(
    pregunta,
    tema="General",
    nivel="Intermedio",
):
    pregunta_limpia = str(pregunta).strip()

    if not pregunta_limpia:
        return (
            "Escribe una pregunta o indícame qué parte "
            "del tema deseas trabajar."
        )

    guardar(
        "user",
        pregunta_limpia,
    )

    prompt = construir_prompt(
        pregunta_limpia,
        tema,
        nivel,
    )

    respuesta = preguntar_gemini(
        prompt
    )

    guardar(
        "assistant",
        respuesta,
    )

    return respuesta