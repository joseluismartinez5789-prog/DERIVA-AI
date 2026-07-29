import streamlit as st

from utils.math_renderer import renderizar_matematicas
import matplotlib.pyplot as plt
import numpy as np

from services.diagnostic_service import (
    guardar_resultado_diagnostico,
)

from utils.theme import aplicar_tema

# ==========================
# CONFIGURACIÓN
# ==========================

st.set_page_config(
    page_title="Evaluación Diagnóstica",
    page_icon="📝",
    layout="wide"
)

aplicar_tema()

st.markdown(
    """
    <style>
    div.stButton > button {
        border-radius: 999px !important;
        min-height: 54px !important;
        font-weight: 800 !important;
        border: 1px solid rgba(255,255,255,.92) !important;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.82),
            0 10px 24px rgba(67,111,218,.16) !important;
        transition:
            transform .20s ease,
            box-shadow .20s ease,
            filter .20s ease !important;
    }

    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.01) !important;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.9),
            0 15px 30px rgba(67,111,218,.22) !important;
        filter: brightness(1.03);
    }

    div.stButton > button:active {
        transform: translateY(0) scale(.99) !important;
    }

    .study-plan-card {
        background: rgba(255,255,255,.68);
        border: 1px solid rgba(255,255,255,.86);
        border-radius: 24px;
        padding: 22px 24px;
        box-shadow: 0 12px 28px rgba(77,118,210,.08);
        margin-bottom: 14px;
    }

    .study-plan-number {
        display: inline-flex;
        width: 38px;
        height: 38px;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: #E8F1FF;
        color: #4F6FE8;
        font-weight: 800;
        margin-right: 10px;
    }

    .study-plan-area {
        color: #263B59;
        font-size: 21px;
        font-weight: 800;
    }

    .study-plan-lesson {
        color: #61748A;
        font-size: 15px;
        margin: 7px 0 0 49px;
    }

    .next-step-card {
        background: linear-gradient(
            135deg,
            rgba(205,236,255,.90),
            rgba(224,217,255,.80)
        );
        border: 1px solid rgba(255,255,255,.88);
        border-radius: 26px;
        padding: 25px;
        box-shadow: 0 14px 34px rgba(79,111,232,.12);
        margin: 20px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================
# PREGUNTAS
# ==========================

preguntas = [

    {
        "tipo": "texto",
        "pregunta": "¿Qué representa el límite de una función cuando x se aproxima a un valor determinado?",
        "opciones": [
            "El valor al que se aproxima la función",
            "La derivada de la función",
            "El área bajo la curva",
            "Una operación algebraica"
        ],
        "respuesta": "El valor al que se aproxima la función",
        "categoria": "Límites"
    },

    {
        "tipo": "texto",
        "pregunta": "Si una función es continua en un punto, significa que:",
        "opciones": [
            "La gráfica no presenta interrupciones en ese punto",
            "La función siempre aumenta",
            "La derivada siempre es cero",
            "La función tiene forma lineal"
        ],
        "respuesta": "La gráfica no presenta interrupciones en ese punto",
        "categoria": "Continuidad"
    },

    {
        "tipo": "texto",
        "pregunta": "La derivada de una función representa principalmente:",
        "opciones": [
            "Una razón de cambio o pendiente",
            "Un área acumulada",
            "Un número fijo",
            "Una ecuación cuadrática"
        ],
        "respuesta": "Una razón de cambio o pendiente",
        "categoria": "Derivadas"
    },


    {
        "tipo": "texto",
        "pregunta": "Calcula la derivada de $f(x)=x^2$.",
        "opciones": [
            "x",
            "$2x$",
            "$x^2$",
            "2"
        ],
        "respuesta": "$2x$",
        "categoria": "Derivadas"
    },


    {
        "tipo": "grafica",
        "pregunta": "Observa la gráfica. ¿Qué ocurre con el límite cuando $x$ se acerca a $2$?",
        "opciones": [
            "El límite existe y vale 3",
            "El límite no existe",
            "La función vale 2",
            "La función es continua"
        ],
        "respuesta": "El límite existe y vale 3",
        "categoria": "Interpretación gráfica"
    },


    {
        "tipo": "grafica_continuidad",
        "pregunta": "Observa la gráfica. ¿La función es continua en $x=0$?",
        "opciones": [
            "Sí, porque no hay interrupción",
            "No, porque existe un salto",
            "No existe función",
            "La derivada es cero"
        ],
        "respuesta": "Sí, porque no hay interrupción",
        "categoria": "Continuidad gráfica"
    },


    {
        "tipo": "texto",
        "pregunta": "Para resolver algunos límites indeterminados suele utilizarse:",
        "opciones": [
            "Factorización",
            "Dividir entre cero",
            "Sumar términos sin cambiar nada",
            "Eliminar variables"
        ],
        "respuesta": "Factorización",
        "categoria": "Límites"
    },


    {
        "tipo": "texto",
        "pregunta": "La regla de la cadena se utiliza principalmente para:",
        "opciones": [
            "Derivar funciones compuestas",
            "Resolver sistemas",
            "Calcular áreas",
            "Graficar rectas"
        ],
        "respuesta": "Derivar funciones compuestas",
        "categoria": "Derivadas"
    },


    {
        "tipo": "texto",
        "pregunta": "Si la velocidad cambia con el tiempo, la derivada representa:",
        "opciones": [
            "La aceleración",
            "La distancia total",
            "El tiempo",
            "El punto inicial"
        ],
        "respuesta": "La aceleración",
        "categoria": "Aplicaciones"
    },


    {
        "tipo": "texto",
        "pregunta": "La definición de derivada utiliza principalmente:",
        "opciones": [
            "Un límite cuando $\\Delta x$ se aproxima a cero",
            "Una suma de funciones",
            "Una multiplicación directa",
            "Una ecuación cuadrática"
        ],
        "respuesta": "Un límite cuando $\\Delta x$ se aproxima a cero",
        "categoria": "Definición de derivada"
    }

]


# ==========================
# VARIABLES DE SESIÓN
# ==========================

if "evaluacion_iniciada" not in st.session_state:
    st.session_state.evaluacion_iniciada = False


if "pregunta_actual" not in st.session_state:
    st.session_state.pregunta_actual = 0


if "diagnostico_nuevo" not in st.session_state:
    st.session_state.diagnostico_nuevo = True


if "respuestas_diag" not in st.session_state:
    st.session_state.respuestas_diag = {}


if "respuesta_actual" not in st.session_state:
    st.session_state.respuesta_actual = None



# ==========================
# PANTALLA INICIAL
# ==========================

if not st.session_state.evaluacion_iniciada:

    st.markdown(
        """
        <style>

        .diag-card{

            background:rgba(255,255,255,.60);

            backdrop-filter:blur(18px);

            border:1px solid rgba(255,255,255,.70);

            border-radius:30px;

            padding:45px;

            box-shadow:0 20px 45px rgba(80,120,255,.10);

            margin-top:15px;

            margin-bottom:25px;

        }

        .diag-title{

            font-size:42px;

            font-weight:700;

            color:#17324D;

            margin-bottom:10px;

        }

        .diag-sub{

            color:#5D738A;

            font-size:18px;

            line-height:1.7;

            margin-bottom:35px;

        }

        .metric-box{

            background:linear-gradient(
                135deg,
                rgba(114,200,248,.18),
                rgba(255,255,255,.55)
            );

            border-radius:22px;

            padding:22px;

            text-align:center;

            border:1px solid rgba(255,255,255,.70);

            box-shadow:0 8px 18px rgba(90,120,255,.06);

        }

        .metric-number{

            font-size:26px;

            font-weight:700;

            color:#3F66D6;

            margin-top:8px;

        }

        .metric-label{

            color:#6D7F92;

            font-size:15px;

        }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="diag-card">

        <div class="diag-title">
        📝 Evaluación Diagnóstica
        </div>

        <div class="diag-sub">
        Antes de comenzar responderás una breve evaluación para que
        <b>DERIVA AI</b> conozca tu nivel y construya una ruta de aprendizaje
        personalizada.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown("""
        <div class="metric-box">
        <div style="font-size:34px;">⏱</div>
        <div class="metric-number">5 min</div>
        <div class="metric-label">Duración</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:

        st.markdown("""
        <div class="metric-box">
        <div style="font-size:34px;">📝</div>
        <div class="metric-number">10</div>
        <div class="metric-label">Preguntas</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:

        st.markdown("""
        <div class="metric-box">
        <div style="font-size:34px;">🎯</div>
        <div class="metric-number">1</div>
        <div class="metric-label">Intento</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "🚀 Comenzar evaluación",
        use_container_width=True
    ):

        st.session_state.pregunta_actual = 0
        st.session_state.respuestas_diag = {}
        st.session_state.evaluacion_iniciada = True

        st.rerun()

    st.stop()


# ==========================
# INTERFAZ DE EVALUACIÓN
# ==========================

indice = st.session_state.pregunta_actual

pregunta = preguntas[indice]


st.title(
    "📝 Evaluación Diagnóstica DERIVA AI"
)


progreso = (indice + 1) / len(preguntas)

st.progress(progreso)


st.caption(
    f"{int(progreso*100)} % completado"
)


st.markdown(
    """
    <style>
    .diagnostic-question-card {
        background: linear-gradient(
            135deg,
            rgba(255,255,255,.78),
            rgba(240,248,255,.70)
        );
        border-radius: 28px;
        padding: 35px;
        border: 1px solid rgba(255,255,255,.85);
        box-shadow: 0 15px 35px rgba(91,156,255,.10);
        margin-top: 20px;
        margin-bottom: 25px;
    }

    .diagnostic-question-step {
        color: #4F7DF7;
        font-size: 15px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }

    .diagnostic-question-category {
        display: inline-block;
        margin-bottom: 18px;
        padding: 8px 18px;
        border-radius: 20px;
        background: #EAF6FF;
        color: #3182CE;
        font-weight: 600;
        font-size: 15px;
    }

    .diagnostic-question-text {
        color: #17324D;
        font-size: 30px;
        font-weight: 700;
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""<div class="diagnostic-question-card">
    <div class="diagnostic-question-step">
        Pregunta {indice + 1} de {len(preguntas)}
    </div>
    <div class="diagnostic-question-category">
        📘 {pregunta["categoria"]}
    </div>
    </div>""",
    unsafe_allow_html=True,
)

renderizar_matematicas(
    f"### {pregunta['pregunta']}"
)


# CONTINÚA PARTE 2

# ==========================
# GRÁFICAS
# ==========================

if pregunta["tipo"] == "grafica":

    # La función se dibuja en dos tramos para mostrar claramente
    # el hueco en x=2 sin cambiar la respuesta correcta del límite.
    x_izquierda = np.linspace(0, 1.96, 120)
    x_derecha = np.linspace(2.04, 4, 120)

    y_izquierda = 3 + (x_izquierda - 2)**2
    y_derecha = 3 + (x_derecha - 2)**2

    fig, ax = plt.subplots()

    ax.plot(x_izquierda, y_izquierda)
    ax.plot(x_derecha, y_derecha)

    ax.scatter(
        [2],
        [3],
        facecolors="white",
        edgecolors="#1f77b4",
        linewidths=2.5,
        s=170,
        zorder=10
    )

    ax.axvline(
        2,
        color="gray",
        linestyle="--",
        linewidth=1,
        alpha=0.45
    )

    ax.annotate(
        "Hueco en x = 2",
        xy=(2, 3),
        xytext=(2.35, 3.35),
        arrowprops=dict(
            arrowstyle="->",
            linewidth=1.2
        ),
        fontsize=11
    )

    ax.grid(alpha=0.45)
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_title(
        "La función tiene un hueco, pero el límite existe"
    )

    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


if pregunta["tipo"] == "grafica_continuidad":

    x = np.linspace(-3, 3, 200)

    y = x**2


    fig, ax = plt.subplots()

    ax.plot(x, y)

    ax.grid()

    ax.set_xlabel("x")

    ax.set_ylabel("f(x)")


    st.pyplot(fig)



# ==========================
# RESPUESTA
# ==========================

st.markdown(
    """
    <style>
    div[data-testid="stRadio"] > label {
        font-size: 17px !important;
        font-weight: 700 !important;
        color: #29415D !important;
        margin-bottom: 12px !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 12px;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: rgba(255,255,255,.62);
        border: 1px solid rgba(255,255,255,.82);
        border-radius: 18px;
        padding: 14px 18px;
        min-height: 54px;
        box-shadow: 0 8px 20px rgba(80,120,255,.06);
        transition: transform .20s ease, box-shadow .20s ease, background .20s ease;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        transform: translateY(-2px);
        background: rgba(255,255,255,.82);
        box-shadow: 0 12px 26px rgba(80,120,255,.10);
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 18px !important;
        line-height: 1.45 !important;
        color: #405873 !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
        background: rgba(224,238,255,.92);
        border-color: rgba(79,125,247,.55);
        box-shadow: 0 10px 24px rgba(79,125,247,.13);
    }
    </style>
    """,
    unsafe_allow_html=True
)
respuesta = st.radio(

    "Selecciona tu respuesta:",

    pregunta["opciones"],

    index=None,

    key=f"respuesta_{indice}"

)


# ==========================
# NAVEGACIÓN
# ==========================

st.divider()



if indice < len(preguntas)-1:


    if st.button(
        "➡️ Siguiente",
        use_container_width=True,
        key=f"siguiente_{indice}"
    ):


        if respuesta is None:

            st.error(
                "⚠️ Debes seleccionar una respuesta antes de continuar."
            )


        else:

    
            st.session_state.respuestas_diag[indice] = respuesta


            st.session_state.pregunta_actual = indice + 1


            st.rerun()



# ==========================
# FINALIZAR
# ==========================

else:


    if st.button(
        "🎯 Finalizar evaluación",
        use_container_width=True,
        key="finalizar_evaluacion"
    ):


        if respuesta is None:

            st.error(
                "⚠️ Debes seleccionar una respuesta antes de finalizar."
            )


        else:


            st.session_state.respuestas_diag[indice] = respuesta


            puntos = 0

            fortalezas = []

            mejorar = []



            for i, p in enumerate(preguntas):


                respuesta_usuario = (
                    st.session_state.respuestas_diag.get(i)
                )


                if respuesta_usuario == p["respuesta"]:

                    puntos += 1

                    fortalezas.append(
                        p["categoria"]
                    )


                else:

                    mejorar.append(
                        p["categoria"]
                    )



            # ==========================
            # NIVEL
            # ==========================

            if puntos <= 4:

                nivel = "Básico"


            elif puntos <= 7:

                nivel = "Intermedio"


            else:

                nivel = "Avanzado"



            # ==========================
            # PLAN PERSONALIZADO
            # ==========================

            catalogo_lecciones = {
                "Límites": [
                    "Concepto intuitivo de límite",
                    "Límites laterales",
                    "Resolución de límites por factorización"
                ],
                "Continuidad": [
                    "Condiciones de continuidad",
                    "Reconocimiento de discontinuidades",
                    "Relación entre límite y continuidad"
                ],
                "Derivadas": [
                    "Derivada como razón de cambio",
                    "Reglas básicas de derivación",
                    "Regla de la cadena"
                ],
                "Interpretación gráfica": [
                    "Lectura de límites en gráficas",
                    "Huecos, saltos y asíntotas",
                    "Límites laterales desde una gráfica"
                ],
                "Continuidad gráfica": [
                    "Continuidad en una gráfica",
                    "Detección de saltos y huecos",
                    "Análisis de continuidad por tramos"
                ],
                "Aplicaciones": [
                    "Velocidad y aceleración",
                    "Razones de cambio",
                    "Problemas aplicados con derivadas"
                ],
                "Definición de derivada": [
                    "Cociente incremental",
                    "Límite cuando Δx tiende a cero",
                    "Interpretación geométrica de la derivada"
                ]
            }

            areas_prioritarias = list(dict.fromkeys(mejorar))

            if not areas_prioritarias:
                areas_prioritarias = [
                    "Aplicaciones",
                    "Derivadas"
                ]

            plan_estudios = []

            for orden, area in enumerate(areas_prioritarias, start=1):

                lecciones = catalogo_lecciones.get(
                    area,
                    [
                        f"Repaso guiado de {area}",
                        f"Ejercicios básicos de {area}",
                        f"Práctica aplicada de {area}"
                    ]
                )

                plan_estudios.append(
                    {
                        "orden": orden,
                        "area": area,
                        "lecciones": lecciones,
                        "estado": "Pendiente"
                    }
                )

            siguiente_area = plan_estudios[0]["area"]
            siguiente_leccion = plan_estudios[0]["lecciones"][0]

            datos = {

                "realizado": True,

                "nivel": nivel,

                "puntaje": puntos,

                "total": len(preguntas),

                "fortalezas": list(dict.fromkeys(fortalezas)),

                "mejorar": list(dict.fromkeys(mejorar)),

                "plan_estudios": plan_estudios,

                "siguiente_area": siguiente_area,

                "siguiente_leccion": siguiente_leccion

            }



            # ==========================
            # GUARDAR RESULTADO
            # ==========================

            estudiante_id = st.session_state.get(
                "estudiante_id"
            )

            if not estudiante_id:
                st.error(
                    "No se encontró el usuario autenticado. "
                    "Cierra la sesión e inicia sesión nuevamente."
                )
                st.stop()

            detalle_respuestas = []

            for i, pregunta_item in enumerate(preguntas):
                respuesta_usuario = (
                    st.session_state.respuestas_diag.get(i)
                )

                detalle_respuestas.append(
                    {
                        "numero": i + 1,
                        "pregunta": pregunta_item["pregunta"],
                        "categoria": pregunta_item["categoria"],
                        "respuesta_usuario": respuesta_usuario,
                        "respuesta_correcta": pregunta_item["respuesta"],
                        "correcta": (
                            respuesta_usuario
                            == pregunta_item["respuesta"]
                        ),
                    }
                )

            guardar_resultado_diagnostico(
                estudiante_id=estudiante_id,
                nivel=nivel,
                puntaje=puntos,
                total=len(preguntas),
                respuestas=st.session_state.respuestas_diag,
                fortalezas=list(dict.fromkeys(fortalezas)),
                mejorar=list(dict.fromkeys(mejorar)),
                plan_estudios=plan_estudios,
                siguiente_area=siguiente_area,
                siguiente_leccion=siguiente_leccion,
                detalle_respuestas=detalle_respuestas,
            )


            st.session_state.resultado = datos

            st.session_state.plan_estudios = plan_estudios

            st.session_state.diagnostico_completo = True



            st.success(
                "🎉 Evaluación completada correctamente."
            )


            st.balloons()



            # ==========================
            # RESULTADO VISUAL
            # ==========================

            st.divider()


            st.header(
                "📊 Resultado"
            )


            if nivel == "Avanzado":

                icono = "🟢"


            elif nivel == "Intermedio":

                icono = "🟡"


            else:

                icono = "🔴"



            st.subheader(
                f"{icono} Nivel {nivel}"
            )


            st.metric(
                "Puntuación",
                f"{puntos} / {len(preguntas)}"
            )



            st.divider()


            col1, col2 = st.columns(2)



            with col1:

                st.subheader(
                    "💪 Fortalezas"
                )


                if fortalezas:

                    for f in set(fortalezas):

                        st.write(
                            f"✅ {f}"
                        )

                else:

                    st.write(
                        "Sin fortalezas identificadas aún."
                    )



            with col2:

                st.subheader(
                    "📌 Aspectos por reforzar"
                )


                if mejorar:

                    for m in set(mejorar):

                        st.write(
                            f"📌 {m}"
                        )

                else:

                    st.write(
                        "Excelente dominio del contenido."
                    )



            st.divider()


            # ==========================
            # RUTA PERSONALIZADA
            # ==========================

            st.header(
                "🧭 Tu plan de estudios personalizado"
            )

            st.write(
                "DERIVA AI organizó tu siguiente ruta según las áreas "
                "que debes reforzar."
            )

            for modulo in plan_estudios:

                lecciones_html = "".join(
                    f'<div class="study-plan-lesson">• {leccion}</div>'
                    for leccion in modulo["lecciones"]
                )

                st.markdown(
                    f"""<div class="study-plan-card">
                    <span class="study-plan-number">{modulo["orden"]}</span>
                    <span class="study-plan-area">{modulo["area"]}</span>
                    {lecciones_html}
                    </div>""",
                    unsafe_allow_html=True
                )

            st.markdown(
                f"""<div class="next-step-card">
                <div style="font-size:14px;font-weight:800;color:#4F6FE8;
                            text-transform:uppercase;letter-spacing:1px;">
                    Siguiente paso recomendado
                </div>
                <div style="font-size:24px;font-weight:800;color:#20324D;
                            margin-top:8px;">
                    📘 {siguiente_leccion}
                </div>
                <div style="font-size:15px;color:#60748B;margin-top:6px;">
                    Área: {siguiente_area} · Nivel de partida: {nivel}
                </div>
                </div>""",
                unsafe_allow_html=True
            )

            st.caption(
                f"{len(plan_estudios)} módulos recomendados"
            )

            st.page_link(
                "pages/learn.py",
                label="🚀 Comenzar mi ruta de aprendizaje",
                icon="📚",
                use_container_width=True
            )