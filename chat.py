import base64
import json
import random
from pathlib import Path
from textwrap import dedent

import streamlit as st

from utils.math_renderer import renderizar_matematicas

from services.brain_service import responder
from services.progress_service import registrar_pregunta
from services.diagnostic_service import obtener_nivel
from services.memory_service import limpiar


st.set_page_config(
    page_title="Nova | DERIVA AI",
    page_icon="🤖",
    layout="wide",
)


TEMAS_DISPONIBLES = [
    "General",
    "1.1 Una mirada previa al cálculo",
    "1.2 Cálculo de límites de manera gráfica y numérica",
    "1.3 Cálculo analítico de límites",
    "1.4 Continuidad y límites laterales",
    "1.5 Límites infinitos",
    "2.1 La derivada y el problema de la recta tangente",
    "2.2 La derivada como función",
    "2.3 Reglas básicas de derivación",
    "2.4 Regla del producto y cociente",
    "2.5 Derivadas de orden superior",
    "3.1 Regla de la cadena",
    "3.2 Derivación implícita",
    "3.3 Razones relacionadas",
    "3.4 Aproximaciones lineales",
    "3.5 Diferenciales",
]


def cargar_json(ruta_archivo):
    ruta = Path(ruta_archivo)

    if not ruta.exists():
        return {}

    try:
        return json.loads(
            ruta.read_text(
                encoding="utf-8",
            )
        )
    except (OSError, json.JSONDecodeError):
        return {}


def imagen_base64(ruta_archivo):
    ruta = Path(ruta_archivo)

    if not ruta.exists():
        return ""

    return base64.b64encode(
        ruta.read_bytes()
    ).decode("utf-8")


def mensaje_por_nivel(nivel):
    texto = str(nivel).lower()

    if "básico" in texto or "basico" in texto:
        return (
            "Iremos con calma, usando ejemplos sencillos y "
            "comprobando cada paso antes de avanzar."
        )

    if "avanzado" in texto:
        return (
            "Profundizaremos en el razonamiento, la formalización "
            "y las conexiones entre conceptos."
        )

    return (
        "Combinaremos intuición, procedimientos y práctica guiada "
        "para consolidar el tema."
    )


def construir_bienvenida(
    tema,
    nivel,
    desde_ruta,
    areas_refuerzo,
):
    adaptacion = mensaje_por_nivel(
        nivel
    )

    if desde_ruta:
        introduccion = (
            "Me alegra que hayas decidido continuar con la ruta "
            "personalizada que DERIVA AI preparó para ti."
        )
    else:
        introduccion = (
            "Estoy aquí para ayudarte a comprender Cálculo "
            "Diferencial mediante preguntas, pistas y explicaciones."
        )

    refuerzo = ""

    if areas_refuerzo:
        lista = ", ".join(
            str(area)
            for area in areas_refuerzo[:3]
        )

        refuerzo = (
            f"\n\n🎯 **Áreas a reforzar:** {lista}"
        )

    return f"""
### ¡Hola! Soy Nova 👋

{introduccion}

📚 **Tema actual:** {tema}  
🎯 **Nivel detectado:** {nivel}

{adaptacion}{refuerzo}

Puedes comenzar de una de estas formas:

- **Explícame el tema desde cero.**
- **Ayúdame a resolver un ejercicio.**
- **Quiero aclarar una duda puntual.**
"""


diagnostico = cargar_json(
    "data/diagnostico.json"
)

areas_refuerzo = diagnostico.get(
    "mejorar",
    [],
)

nivel = obtener_nivel()

tema_guardado = st.session_state.get(
    "tema_actual",
    "General",
)

desde_ruta = st.session_state.get(
    "desde_ruta_aprendizaje",
    False,
)

if tema_guardado in TEMAS_DISPONIBLES:
    indice_tema = TEMAS_DISPONIBLES.index(
        tema_guardado
    )
else:
    indice_tema = 0


st.sidebar.markdown(
    "## 🤖 Sesión con Nova"
)

tema = st.sidebar.selectbox(
    "Tema actual",
    TEMAS_DISPONIBLES,
    index=indice_tema,
)

st.session_state["tema_actual"] = tema

st.sidebar.markdown(
    dedent(
        f"""
        <div class="nova-side-card">
            <span>🎯 Nivel detectado</span>
            <strong>{nivel}</strong>
        </div>
        """
    ),
    unsafe_allow_html=True,
)

if desde_ruta:
    st.sidebar.success(
        "✨ Estás siguiendo tu ruta personalizada."
    )


robot = imagen_base64(
    "assets/images/robot_deriva.png"
)

st.markdown(
    dedent(
        """
        <style>
        .stApp {
            background:
                radial-gradient(
                    circle at 78% 12%,
                    rgba(235, 210, 255, .65),
                    transparent 25%
                ),
                radial-gradient(
                    circle at 57% 4%,
                    rgba(196, 237, 255, .62),
                    transparent 28%
                ),
                linear-gradient(
                    135deg,
                    #fbfdff 0%,
                    #eef7ff 48%,
                    #faf1ff 100%
                );
        }

        .block-container {
            max-width: 1280px;
            padding-top: 2rem;
            padding-bottom: 8rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,
                rgba(248, 250, 255, .97),
                rgba(239, 244, 253, .96)
            );
            border-right: 1px solid rgba(169, 190, 220, .28);
        }

        .nova-side-card {
            margin-top: 16px;
            padding: 17px;
            border-radius: 19px;
            background: linear-gradient(
                135deg,
                rgba(210, 238, 255, .92),
                rgba(234, 219, 255, .90)
            );
            border: 1px solid rgba(255, 255, 255, .88);
            box-shadow: 0 10px 24px rgba(76, 96, 170, .10);
        }

        .nova-side-card span {
            display: block;
            color: #66758d;
            font-size: 14px;
            margin-bottom: 7px;
        }

        .nova-side-card strong {
            color: #30476c;
            font-size: 19px;
        }

        .nova-hero {
            position: relative;
            overflow: hidden;
            min-height: 370px;
            padding: 38px;
            margin-bottom: 24px;
            border-radius: 34px;
            border: 1px solid rgba(255, 255, 255, .92);
            background: linear-gradient(
                135deg,
                rgba(255, 255, 255, .80),
                rgba(218, 242, 255, .70),
                rgba(243, 220, 255, .68)
            );
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, .86),
                0 24px 58px rgba(70, 88, 158, .14);
            backdrop-filter: blur(24px);
        }

        .nova-hero::before {
            content: "";
            position: absolute;
            width: 270px;
            height: 270px;
            right: -80px;
            top: -95px;
            border-radius: 50%;
            background: rgba(255, 255, 255, .24);
            filter: blur(8px);
        }

        .nova-copy {
            position: relative;
            z-index: 3;
            width: 62%;
        }

        .nova-kicker {
            color: #6879df;
            font-size: 14px;
            font-weight: 850;
            letter-spacing: 1.15px;
            text-transform: uppercase;
            margin-bottom: 9px;
        }

        .nova-title {
            color: #213754;
            font-size: 46px;
            font-weight: 850;
            line-height: 1.1;
            margin-bottom: 9px;
        }

        .nova-subtitle {
            color: #687b94;
            font-size: 16px;
            line-height: 1.65;
            max-width: 610px;
        }

        .nova-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 21px;
        }

        .nova-pill {
            padding: 9px 14px;
            border-radius: 999px;
            color: #506786;
            background: rgba(255, 255, 255, .62);
            border: 1px solid rgba(255, 255, 255, .90);
            box-shadow: 0 8px 18px rgba(75, 95, 165, .07);
            font-size: 13px;
            font-weight: 750;
        }

        .route-note {
            margin-top: 18px;
            padding: 15px 17px;
            border-radius: 20px;
            color: #526884;
            background: linear-gradient(
                135deg,
                rgba(203, 238, 255, .76),
                rgba(241, 218, 255, .74)
            );
            border: 1px solid rgba(255, 255, 255, .90);
            box-shadow: 0 10px 23px rgba(70, 92, 163, .09);
            font-weight: 650;
        }

        .robot-glow {
            position: absolute;
            z-index: 1;
            right: 38px;
            bottom: 12px;
            width: 285px;
            height: 205px;
            border-radius: 50%;
            background: radial-gradient(
                ellipse,
                rgba(120, 207, 255, .42),
                rgba(198, 161, 255, .22),
                transparent 70%
            );
            filter: blur(18px);
            animation: glow 3.4s ease-in-out infinite;
            pointer-events: none;
        }

        .robot-box {
            position: absolute;
            z-index: 2;
            right: 34px;
            bottom: 10px;
            width: 300px;
            animation: floatRobot 4.6s ease-in-out infinite;
            filter: drop-shadow(
                0 23px 25px rgba(71, 79, 155, .19)
            );
            pointer-events: none;
        }

        .robot-box img {
            display: block;
            width: 100%;
            height: auto;
            border-radius: 0;
            mix-blend-mode: normal;
            background: transparent;
        }

        @keyframes floatRobot {
            0%,
            100% {
                transform: translateY(0) rotate(0deg);
            }

            50% {
                transform: translateY(-13px) rotate(.6deg);
            }
        }

        @keyframes glow {
            0%,
            100% {
                transform: scale(1);
                opacity: .72;
            }

            50% {
                transform: scale(1.08);
                opacity: 1;
            }
        }

        div[data-testid="stChatMessage"] {
            border-radius: 24px;
            padding: 12px 16px;
            margin-bottom: 13px;
            background: rgba(255, 255, 255, .67);
            border: 1px solid rgba(255, 255, 255, .90);
            box-shadow: 0 12px 28px rgba(70, 90, 158, .08);
            backdrop-filter: blur(16px);
        }

        div[data-testid="stChatMessage"]:has(
            [data-testid="chatAvatarIcon-user"]
        ) {
            background: linear-gradient(
                135deg,
                rgba(209, 238, 255, .82),
                rgba(232, 221, 255, .78)
            );
        }

        div.stButton > button {
            min-height: 49px !important;
            border-radius: 999px !important;
            border: 1px solid rgba(255, 255, 255, .92) !important;
            background: linear-gradient(
                135deg,
                rgba(197, 235, 255, .97),
                rgba(235, 208, 255, .97)
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

        @media (max-width: 900px) {
            .nova-hero {
                min-height: 410px;
                padding: 30px;
            }

            .nova-copy {
                width: 100%;
            }

            .nova-title {
                font-size: 36px;
            }

            .robot-box {
                width: 235px;
                right: -34px;
                bottom: -4px;
                opacity: .32;
            }

            .robot-glow {
                right: -30px;
                bottom: 0;
                opacity: .45;
            }
        }

        @media (max-width: 600px) {
            .nova-hero {
                min-height: 430px;
                padding: 25px;
            }

            .nova-title {
                font-size: 32px;
            }

            .nova-subtitle {
                font-size: 15px;
            }

            .robot-box {
                width: 205px;
                right: -45px;
                bottom: -8px;
                opacity: .22;
            }
        }
        </style>
        """
    ),
    unsafe_allow_html=True,
)

robot_html = ""

if robot:
    robot_html = (
        '<div class="robot-glow"></div>'
        '<div class="robot-box">'
        f'<img src="data:image/png;base64,{robot}" '
        'alt="Nova, agente tutor de DERIVA AI">'
        '</div>'
    )

route_html = ""

if desde_ruta:
    route_html = (
        '<div class="route-note">'
        '✨ Elegiste seguir tu ruta personalizada. '
        'Nova adaptará esta sesión al nivel '
        f'<strong>{nivel}</strong> y al tema '
        f'<strong>{tema}</strong>.'
        '</div>'
    )

hero_html = (
    '<section class="nova-hero">'
    '<div class="nova-copy">'
    '<div class="nova-kicker">'
    'Agente tutor inteligente'
    '</div>'
    '<div class="nova-title">'
    'Conoce a Nova 🤖'
    '</div>'
    '<div class="nova-subtitle">'
    'Tu acompañante de DERIVA AI para comprender '
    'Cálculo Diferencial mediante preguntas, '
    'pistas y explicaciones adaptadas a ti.'
    '</div>'
    '<div class="nova-pills">'
    f'<div class="nova-pill">📚 {tema}</div>'
    f'<div class="nova-pill">🎯 Nivel {nivel}</div>'
    '<div class="nova-pill">💡 Método socrático</div>'
    '</div>'
    f'{route_html}'
    '</div>'
    f'{robot_html}'
    '</section>'
)

st.markdown(
    hero_html,
    unsafe_allow_html=True,
)


clave_bienvenida = (
    tema,
    nivel,
    desde_ruta,
)

if (
    "messages" not in st.session_state
    or st.session_state.get(
        "clave_bienvenida_nova"
    ) != clave_bienvenida
):
    bienvenida = construir_bienvenida(
        tema,
        nivel,
        desde_ruta,
        areas_refuerzo,
    )

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": bienvenida,
        }
    ]

    st.session_state[
        "clave_bienvenida_nova"
    ] = clave_bienvenida


for mensaje in st.session_state.messages:
    avatar = (
        "🤖"
        if mensaje["role"] == "assistant"
        else "🧑‍🎓"
    )

    with st.chat_message(
        mensaje["role"],
        avatar=avatar,
    ):
        renderizar_matematicas(
            mensaje["content"]
        )


st.markdown(
    "#### ¿Cómo deseas comenzar?"
)

col1, col2, col3 = st.columns(3)

with col1:
    desde_cero = st.button(
        "📘 Explícame desde cero",
        use_container_width=True,
    )

with col2:
    resolver_ejercicio = st.button(
        "🧩 Resolver un ejercicio",
        use_container_width=True,
    )

with col3:
    aclarar_duda = st.button(
        "💬 Aclarar una duda",
        use_container_width=True,
    )


pregunta_rapida = None

if desde_cero:
    pregunta_rapida = (
        f"Explícame desde cero el tema {tema}, "
        f"adaptándolo a mi nivel {nivel}."
    )

elif resolver_ejercicio:
    pregunta_rapida = (
        f"Propón un ejercicio guiado sobre {tema} "
        f"adecuado para mi nivel {nivel}."
    )

elif aclarar_duda:
    pregunta_rapida = (
        f"Antes de comenzar con {tema}, hazme una pregunta "
        "breve para identificar exactamente qué parte no comprendo."
    )


pregunta_chat = st.chat_input(
    "Escribe tu pregunta de cálculo..."
)

pregunta = pregunta_chat or pregunta_rapida

if pregunta:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": pregunta,
        }
    )

    with st.chat_message(
        "user",
        avatar="🧑‍🎓",
    ):
        renderizar_matematicas(
            pregunta
        )

    registrar_pregunta(
        tema
    )

    estados = [
        "🧠 Analizando tu razonamiento...",
        "📚 Preparando una explicación clara...",
        "💡 Adaptando la respuesta a tu nivel...",
        "✍️ Construyendo un ejemplo paso a paso...",
    ]

    with st.chat_message(
        "assistant",
        avatar="🤖",
    ):
        with st.spinner(
            random.choice(estados)
        ):
            respuesta = responder(
                pregunta,
                tema,
                nivel,
            )

            renderizar_matematicas(
                respuesta
            )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": respuesta,
        }
    )

    if pregunta_rapida:
        st.rerun()


st.divider()

col_limpiar, col_info = st.columns(
    [1, 2]
)

with col_limpiar:
    if st.button(
        "🗑 Limpiar conversación",
        use_container_width=True,
    ):
        limpiar()

        st.session_state.messages = []

        st.session_state[
            "clave_bienvenida_nova"
        ] = None

        st.rerun()

with col_info:
    st.caption(
        "Nova utiliza tu tema actual y el nivel detectado "
        "para adaptar cada explicación."
    )