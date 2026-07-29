import streamlit as st

from utils.theme import aplicar_tema
from services.exercise_service import (
    generar_ejercicio,
    corregir_ejercicio,
    identificar_resultado,
)
from services.diagnostic_service import obtener_nivel
from services.progress_service import (
    registrar_ejercicio_generado,
    registrar_resultado_ejercicio,
    obtener_resumen_practica,
)


st.set_page_config(
    page_title="Practicar | DERIVA AI",
    page_icon="📝",
    layout="wide",
)


aplicar_tema()


def limpiar_ejercicio():
    claves = [
        "ejercicio_actual",
        "respuesta_practica",
        "retroalimentacion_practica",
        "resultado_practica",
        "revision_registrada",
    ]

    for clave in claves:
        st.session_state.pop(
            clave,
            None,
        )


def clase_resultado(
    resultado,
):
    clases = {
        "correcta": "resultado-correcto",
        "parcial": "resultado-parcial",
        "incorrecta": "resultado-incorrecto",
    }

    return clases.get(
        resultado,
        "resultado-neutro",
    )


def titulo_resultado(
    resultado,
):
    titulos = {
        "correcta": "✅ Respuesta correcta",
        "parcial": "⚠️ Respuesta parcialmente correcta",
        "incorrecta": "❌ Respuesta incorrecta",
    }

    return titulos.get(
        resultado,
        "📌 Retroalimentación",
    )


nivel = obtener_nivel()

tema = st.session_state.get(
    "tema_actual",
    "General",
)

resumen = obtener_resumen_practica()


st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at 84% 8%,
                rgba(232, 211, 255, .58),
                transparent 24%
            ),
            radial-gradient(
                circle at 54% 2%,
                rgba(195, 236, 255, .58),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #fbfdff 0%,
                #eef7ff 50%,
                #faf2ff 100%
            );
    }

    .block-container {
        max-width: 1260px;
        padding-top: 2rem;
        padding-bottom: 7rem;
    }

    .practice-hero {
        position: relative;
        overflow: hidden;
        padding: 34px 36px;
        margin-bottom: 24px;
        border-radius: 32px;
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, .82),
            rgba(218, 241, 255, .72),
            rgba(242, 221, 255, .70)
        );
        border: 1px solid rgba(255, 255, 255, .92);
        box-shadow:
            inset 0 1px 0 rgba(255, 255, 255, .90),
            0 22px 52px rgba(69, 87, 157, .13);
        backdrop-filter: blur(22px);
    }

    .practice-hero::after {
        content: "";
        position: absolute;
        width: 240px;
        height: 240px;
        right: -70px;
        top: -95px;
        border-radius: 50%;
        background: rgba(255, 255, 255, .25);
    }

    .practice-kicker {
        color: #6879df;
        font-size: 14px;
        font-weight: 850;
        letter-spacing: 1.1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .practice-title {
        position: relative;
        z-index: 2;
        color: #213754;
        font-size: 43px;
        font-weight: 850;
        line-height: 1.12;
        margin-bottom: 9px;
    }

    .practice-subtitle {
        position: relative;
        z-index: 2;
        max-width: 730px;
        color: #687b94;
        font-size: 16px;
        line-height: 1.65;
    }

    .practice-badges {
        position: relative;
        z-index: 2;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 20px;
    }

    .practice-badge {
        padding: 9px 14px;
        border-radius: 999px;
        color: #526885;
        background: rgba(255, 255, 255, .65);
        border: 1px solid rgba(255, 255, 255, .92);
        box-shadow: 0 8px 18px rgba(74, 94, 163, .07);
        font-size: 13px;
        font-weight: 750;
    }

    .metric-card {
        min-height: 105px;
        padding: 19px;
        border-radius: 22px;
        background: rgba(255, 255, 255, .69);
        border: 1px solid rgba(255, 255, 255, .92);
        box-shadow: 0 12px 26px rgba(68, 88, 155, .08);
        backdrop-filter: blur(16px);
    }

    .metric-card span {
        display: block;
        color: #7889a0;
        font-size: 13px;
        margin-bottom: 8px;
    }

    .metric-card strong {
        color: #30496d;
        font-size: 27px;
    }

    .section-card {
        margin-top: 18px;
        padding: 26px;
        border-radius: 27px;
        background: rgba(255, 255, 255, .72);
        border: 1px solid rgba(255, 255, 255, .92);
        box-shadow: 0 16px 38px rgba(66, 86, 154, .09);
        backdrop-filter: blur(18px);
    }

    .section-label {
        color: #6375d8;
        font-size: 13px;
        font-weight: 850;
        letter-spacing: .9px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .section-title {
        color: #29415f;
        font-size: 25px;
        font-weight: 820;
        margin-bottom: 12px;
    }

    .resultado-correcto,
    .resultado-parcial,
    .resultado-incorrecto,
    .resultado-neutro {
        padding: 20px 22px;
        margin: 18px 0;
        border-radius: 23px;
        border: 1px solid rgba(255, 255, 255, .92);
        box-shadow: 0 13px 28px rgba(68, 88, 155, .08);
    }

    .resultado-correcto {
        background: linear-gradient(
            135deg,
            rgba(224, 249, 235, .90),
            rgba(237, 255, 247, .88)
        );
        color: #28664b;
    }

    .resultado-parcial {
        background: linear-gradient(
            135deg,
            rgba(255, 245, 211, .94),
            rgba(255, 250, 232, .90)
        );
        color: #80651d;
    }

    .resultado-incorrecto {
        background: linear-gradient(
            135deg,
            rgba(255, 229, 235, .92),
            rgba(255, 241, 245, .90)
        );
        color: #8b4055;
    }

    .resultado-neutro {
        background: rgba(237, 241, 255, .88);
        color: #50617e;
    }

    div.stButton > button {
        min-height: 49px !important;
        border-radius: 999px !important;
        border: 1px solid rgba(255, 255, 255, .94) !important;
        background: linear-gradient(
            135deg,
            rgba(195, 235, 255, .98),
            rgba(235, 207, 255, .98)
        ) !important;
        color: #455fca !important;
        font-weight: 800 !important;
        box-shadow:
            0 10px 23px rgba(72, 101, 183, .15) !important;
        transition:
            transform .2s ease,
            box-shadow .2s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow:
            0 15px 29px rgba(72, 101, 183, .21) !important;
    }

    div[data-testid="stTextArea"] textarea {
        min-height: 210px;
        border-radius: 20px;
        background: rgba(255, 255, 255, .84);
        border: 1px solid rgba(173, 190, 220, .43);
    }

    @media (max-width: 700px) {
        .practice-hero {
            padding: 27px 24px;
        }

        .practice-title {
            font-size: 34px;
        }

        .section-card {
            padding: 21px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


hero_html = (
    '<section class="practice-hero">'
    '<div class="practice-kicker">Práctica adaptativa</div>'
    '<div class="practice-title">📝 Entrena con DERIVA AI</div>'
    '<div class="practice-subtitle">'
    'Resuelve ejercicios ajustados a tu nivel, recibe retroalimentación '
    'personalizada y fortalece tu razonamiento paso a paso.'
    '</div>'
    '<div class="practice-badges">'
    f'<div class="practice-badge">📚 {tema}</div>'
    f'<div class="practice-badge">🎯 Nivel {nivel}</div>'
    '<div class="practice-badge">🤖 Corrección inteligente</div>'
    '</div>'
    '</section>'
)

st.markdown(
    hero_html,
    unsafe_allow_html=True,
)


col1, col2, col3, col4 = st.columns(
    4
)

with col1:
    st.markdown(
        (
            '<div class="metric-card">'
            '<span>Ejercicios generados</span>'
            f'<strong>{resumen["generados"]}</strong>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        (
            '<div class="metric-card">'
            '<span>Ejercicios revisados</span>'
            f'<strong>{resumen["revisados"]}</strong>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        (
            '<div class="metric-card">'
            '<span>Respuestas correctas</span>'
            f'<strong>{resumen["correctas"]}</strong>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        (
            '<div class="metric-card">'
            '<span>Porcentaje de aciertos</span>'
            f'<strong>{resumen["porcentaje_aciertos"]}%</strong>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


st.sidebar.markdown(
    "## 📝 Sesión de práctica"
)

st.sidebar.info(
    f"""
📖 **Tema**

{tema}

🎯 **Nivel**

{nivel}
"""
)

if st.sidebar.button(
    "✨ Nuevo ejercicio",
    use_container_width=True,
):
    limpiar_ejercicio()
    st.rerun()


st.markdown(
    (
        '<div class="section-card">'
        '<div class="section-label">Paso 1</div>'
        '<div class="section-title">Genera un ejercicio adaptado</div>'
        '<div style="color:#71839a; line-height:1.65;">'
        'DERIVA AI utilizará el tema actual, tu nivel y el enfoque de Larson '
        'para preparar una práctica adecuada.'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

if st.button(
    "🚀 Generar ejercicio",
    use_container_width=True,
):
    limpiar_ejercicio()

    with st.spinner(
        "DERIVA AI está creando un ejercicio..."
    ):
        ejercicio = generar_ejercicio(
            tema,
            nivel,
        )

    st.session_state[
        "ejercicio_actual"
    ] = ejercicio

    st.session_state[
        "revision_registrada"
    ] = False

    registrar_ejercicio_generado(
        tema,
        nivel,
    )

    st.rerun()


if "ejercicio_actual" in st.session_state:
    st.markdown(
        (
            '<div class="section-card">'
            '<div class="section-label">Paso 2</div>'
            '<div class="section-title">Tu ejercicio</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        st.session_state[
            "ejercicio_actual"
        ]
    )

    st.markdown(
        (
            '<div class="section-card">'
            '<div class="section-label">Paso 3</div>'
            '<div class="section-title">Escribe tu procedimiento</div>'
            '<div style="color:#71839a; line-height:1.65;">'
            'Incluye tus operaciones y explica cómo llegaste a la respuesta. '
            'Nova podrá ayudarte mejor si muestras tu razonamiento.'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    respuesta = st.text_area(
        "Tu respuesta",
        key="respuesta_practica",
        height=220,
        placeholder=(
            "Escribe aquí el procedimiento completo..."
        ),
        label_visibility="collapsed",
    )

    col_revisar, col_otro = st.columns(
        [2, 1]
    )

    with col_revisar:
        revisar = st.button(
            "🤖 Revisar mi respuesta",
            use_container_width=True,
        )

    with col_otro:
        otro = st.button(
            "🔄 Cambiar ejercicio",
            use_container_width=True,
        )

    if otro:
        limpiar_ejercicio()
        st.rerun()

    if revisar:
        if respuesta.strip() == "":
            st.warning(
                "Escribe una respuesta antes de revisarla."
            )

        else:
            with st.spinner(
                "Nova está analizando tu procedimiento..."
            ):
                retroalimentacion = corregir_ejercicio(
                    tema,
                    st.session_state[
                        "ejercicio_actual"
                    ],
                    respuesta,
                    nivel,
                )

            resultado = identificar_resultado(
                retroalimentacion
            )

            st.session_state[
                "retroalimentacion_practica"
            ] = retroalimentacion

            st.session_state[
                "resultado_practica"
            ] = resultado

            if not st.session_state.get(
                "revision_registrada",
                False,
            ):
                registrar_resultado_ejercicio(
                    tema=tema,
                    nivel=nivel,
                    resultado=resultado,
                    ejercicio=st.session_state[
                        "ejercicio_actual"
                    ],
                    respuesta=respuesta,
                )

                st.session_state[
                    "revision_registrada"
                ] = True

            st.rerun()


if "retroalimentacion_practica" in st.session_state:
    resultado = st.session_state.get(
        "resultado_practica",
        "sin_clasificar",
    )

    clase = clase_resultado(
        resultado
    )

    titulo = titulo_resultado(
        resultado
    )

    st.markdown(
        (
            f'<div class="{clase}">'
            f'<strong style="font-size:19px;">{titulo}</strong>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    retroalimentacion = st.session_state[
        "retroalimentacion_practica"
    ]

    lineas = retroalimentacion.splitlines()

    if (
        lineas
        and lineas[0].strip().upper().startswith(
            "RESULTADO:"
        )
    ):
        retroalimentacion = chr(10).join(
            lineas[1:]
        ).strip()

    st.markdown(
        retroalimentacion
    )

    col_reintentar, col_siguiente = st.columns(
        2
    )

    with col_reintentar:
        if st.button(
            "✏️ Mejorar mi respuesta",
            use_container_width=True,
        ):
            st.session_state.pop(
                "retroalimentacion_practica",
                None,
            )

            st.session_state.pop(
                "resultado_practica",
                None,
            )

            st.session_state[
                "revision_registrada"
            ] = False

            st.rerun()

    with col_siguiente:
        if st.button(
            "🚀 Practicar otro ejercicio",
            use_container_width=True,
        ):
            limpiar_ejercicio()
            st.rerun()