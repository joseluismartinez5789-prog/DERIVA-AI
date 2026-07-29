import streamlit as st

from utils.theme import aplicar_tema
from data.temas import TEMAS
from services.learn_service import generar_teoria
from services.diagnostic_service import (
    obtener_nivel,
    diagnostico_completado,
    obtener_ultimo_diagnostico,
)

from services.progress_service import (
    cargar_progreso,
    marcar_leccion_completada,
    registrar_leccion_iniciada,
)


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

st.set_page_config(
    page_title="Aprender",
    page_icon="📚",
    layout="wide"
)

aplicar_tema()


# ==========================================================
# PROTECCIÓN DE ACCESO
# ==========================================================

if not diagnostico_completado():

    st.warning(
        "🔒 Debes completar la evaluación diagnóstica antes de acceder "
        "a tu ruta de aprendizaje."
    )

    if st.button(
        "📝 Ir a la evaluación diagnóstica",
        use_container_width=True,
        key="ir_diagnostico_desde_aprender"
    ):

        st.switch_page(
            "pages/diagnostic.py"
        )

    st.stop()


# ==========================================================
# CARGAR DIAGNÓSTICO Y PROGRESO PERSISTENTE
# ==========================================================

estudiante_id = st.session_state.get("estudiante_id")
datos_diagnostico = obtener_ultimo_diagnostico(estudiante_id)

if not datos_diagnostico:
    st.warning(
        "Tu cuenta indica que completaste el diagnóstico, "
        "pero todavía no existe un resultado permanente."
    )
    st.info(
        "Realiza nuevamente la evaluación para crear tu ruta "
        "personalizada y conservarla después de cerrar sesión."
    )
    if st.button(
        "📝 Ir al diagnóstico",
        use_container_width=True,
        key="repetir_diagnostico_desde_aprender",
    ):
        st.session_state.permitir_repetir_diagnostico = True
        st.session_state.evaluacion_iniciada = False
        st.switch_page("pages/diagnostic.py")
    st.stop()

nivel = datos_diagnostico.get("nivel", obtener_nivel())
areas_a_reforzar = datos_diagnostico.get("mejorar", [])
fortalezas = datos_diagnostico.get("fortalezas", [])
plan_diagnostico = datos_diagnostico.get("plan_estudios", [])

progreso = cargar_progreso()
lecciones_completadas = progreso.get("lecciones_completadas", [])


# ==========================================================
# MAPA ENTRE DIAGNÓSTICO Y TEMAS REALES
# ==========================================================

MAPA_RECOMENDACIONES = {
    "Límites": "1.1 Una mirada previa al cálculo",
    "Interpretación gráfica": "1.2 Cálculo de límites de manera gráfica y numérica",
    "Continuidad": "1.4 Continuidad y límites laterales",
    "Continuidad gráfica": "1.4 Continuidad y límites laterales",
    "Definición de derivada": "2.2 Definición de derivada",
    "Derivadas": "2.3 Reglas básicas de derivación",
    "Aplicaciones": "3.1 Razones relacionadas"
}


def construir_ruta_personalizada():
    ruta = []
    temas_validos = {tema for lista in TEMAS.values() for tema in lista}

    for modulo in plan_diagnostico:
        if not isinstance(modulo, dict):
            continue
        for leccion in modulo.get("lecciones", []):
            if leccion in temas_validos and leccion not in ruta:
                ruta.append(leccion)

    for area in areas_a_reforzar:
        tema = MAPA_RECOMENDACIONES.get(area)
        if tema and tema not in ruta:
            ruta.append(tema)

    if not ruta:
        ruta = [
            "2.3 Reglas básicas de derivación",
            "3.1 Razones relacionadas",
        ]

    return ruta


def obtener_siguiente_tema():
    for tema in ruta_personalizada:
        if tema not in lecciones_completadas:
            return tema
    return None


ruta_personalizada = construir_ruta_personalizada()
siguiente_tema = obtener_siguiente_tema()
total_ruta = len(ruta_personalizada)
completadas_ruta = sum(
    1 for tema in ruta_personalizada if tema in lecciones_completadas
)
porcentaje_ruta = completadas_ruta / total_ruta if total_ruta else 0


# ==========================================================
# ESTILOS
# ==========================================================

st.markdown(
    """
    <style>
    .learn-page-wrap {
        position: relative;
        overflow: hidden;
        padding-bottom: 30px;
    }

    .floating-bubble {
        position: fixed;
        border-radius: 50%;
        filter: blur(2px);
        opacity: .32;
        z-index: 0;
        animation: floatBubble 9s ease-in-out infinite;
        pointer-events: none;
    }

    .bubble-blue {
        width: 190px;
        height: 190px;
        top: 110px;
        right: 40px;
        background: radial-gradient(
            circle at 30% 30%,
            rgba(126,221,255,.85),
            rgba(126,221,255,.08)
        );
    }

    .bubble-pink {
        width: 150px;
        height: 150px;
        bottom: 80px;
        left: 25px;
        background: radial-gradient(
            circle at 30% 30%,
            rgba(255,181,218,.82),
            rgba(255,181,218,.08)
        );
        animation-delay: 1.5s;
    }

    .bubble-lilac {
        width: 135px;
        height: 135px;
        top: 420px;
        right: 180px;
        background: radial-gradient(
            circle at 30% 30%,
            rgba(194,170,255,.82),
            rgba(194,170,255,.08)
        );
        animation-delay: 3s;
    }

    @keyframes floatBubble {
        0%, 100% {
            transform: translateY(0px) translateX(0px);
        }
        50% {
            transform: translateY(-16px) translateX(8px);
        }
    }

    .learn-hero {
        position: relative;
        z-index: 2;
        background: linear-gradient(
            135deg,
            rgba(255,255,255,.78),
            rgba(220,245,255,.68),
            rgba(241,224,255,.64)
        );
        border: 1px solid rgba(255,255,255,.88);
        border-radius: 32px;
        padding: 36px;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.75),
            0 20px 50px rgba(74,105,190,.12);
        backdrop-filter: blur(22px);
        margin-bottom: 26px;
    }

    .hero-kicker {
        color: #5D79E6;
        font-size: 14px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 10px;
    }

    .hero-title {
        color: #233755;
        font-size: 40px;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 10px;
    }

    .hero-subtitle {
        color: #60758D;
        font-size: 17px;
        line-height: 1.65;
        max-width: 850px;
    }

    .hero-metrics {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 24px;
    }

    .metric-pill {
        background: rgba(255,255,255,.60);
        border: 1px solid rgba(255,255,255,.86);
        border-radius: 999px;
        padding: 10px 16px;
        color: #4B6280;
        font-size: 14px;
        font-weight: 700;
        box-shadow: 0 8px 18px rgba(74,105,190,.07);
    }

    .section-title {
        color: #253A58;
        font-size: 26px;
        font-weight: 800;
        margin: 8px 0 16px 0;
    }

    .route-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 18px;
        margin-bottom: 24px;
    }

    .route-card {
        position: relative;
        z-index: 2;
        background: linear-gradient(
            145deg,
            rgba(255,255,255,.72),
            rgba(229,244,255,.58)
        );
        border: 1px solid rgba(255,255,255,.88);
        border-radius: 26px;
        padding: 24px;
        min-height: 210px;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.74),
            0 14px 32px rgba(74,105,190,.10);
        backdrop-filter: blur(18px);
        transition: transform .22s ease, box-shadow .22s ease;
    }

    .route-card:hover {
        transform: translateY(-5px);
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.80),
            0 20px 40px rgba(74,105,190,.15);
    }

    .route-index {
        display: inline-flex;
        width: 42px;
        height: 42px;
        justify-content: center;
        align-items: center;
        border-radius: 50%;
        background: linear-gradient(
            135deg,
            #B8E7FF,
            #E7C9FF
        );
        color: #3E5FD6;
        font-weight: 800;
        margin-bottom: 18px;
        box-shadow: 0 8px 18px rgba(79,111,232,.12);
    }

    .route-topic {
        color: #2B3F5F;
        font-size: 19px;
        line-height: 1.45;
        font-weight: 800;
        margin-bottom: 12px;
    }

    .route-status {
        display: inline-block;
        margin-top: 10px;
        border-radius: 999px;
        padding: 7px 12px;
        background: rgba(232,241,255,.88);
        color: #5871D9;
        font-size: 13px;
        font-weight: 700;
    }

    .next-card {
        position: relative;
        z-index: 2;
        background: linear-gradient(
            135deg,
            rgba(198,235,255,.88),
            rgba(255,211,232,.76),
            rgba(222,205,255,.76)
        );
        border: 1px solid rgba(255,255,255,.90);
        border-radius: 30px;
        padding: 30px;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.80),
            0 18px 42px rgba(79,111,232,.14);
        margin: 22px 0 28px 0;
    }

    .next-label {
        color: #556FE0;
        font-size: 14px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }

    .next-title {
        color: #223755;
        font-size: 27px;
        font-weight: 800;
        line-height: 1.35;
        margin-bottom: 8px;
    }

    .next-subtitle {
        color: #5C718A;
        font-size: 15px;
    }

    div.stButton > button {
        border-radius: 999px !important;
        min-height: 54px !important;
        font-weight: 800 !important;
        border: 1px solid rgba(255,255,255,.92) !important;
        background: linear-gradient(
            135deg,
            rgba(190,233,255,.94),
            rgba(237,207,255,.92)
        ) !important;
        color: #3B57C8 !important;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.85),
            0 10px 24px rgba(67,111,218,.16) !important;
        transition:
            transform .20s ease,
            box-shadow .20s ease,
            filter .20s ease !important;
    }

    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.01) !important;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.92),
            0 16px 30px rgba(67,111,218,.22) !important;
        filter: brightness(1.03);
    }

    div.stButton > button:active {
        transform: translateY(0) scale(.99) !important;
    }

    div[data-testid="stExpander"] {
        border-radius: 22px !important;
        border: 1px solid rgba(255,255,255,.85) !important;
        background: rgba(255,255,255,.54) !important;
        box-shadow: 0 10px 24px rgba(74,105,190,.08) !important;
        overflow: hidden;
        margin-bottom: 12px;
    }

    @media (max-width: 800px) {
        .hero-title {
            font-size: 32px;
        }

        .learn-hero {
            padding: 26px;
        }
    }
    </style>

    <div class="learn-page-wrap">
        <div class="floating-bubble bubble-blue"></div>
        <div class="floating-bubble bubble-pink"></div>
        <div class="floating-bubble bubble-lilac"></div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# ENCABEZADO
# ==========================================================

st.markdown(
    f"""<div class="learn-hero">
    <div class="hero-kicker">Ruta personalizada</div>
    <div class="hero-title">📚 Aprende con un plan hecho para ti</div>
    <div class="hero-subtitle">
        DERIVA AI organizó esta ruta utilizando tu evaluación diagnóstica.
        Puedes comenzar por la recomendación principal o explorar todas las unidades.
    </div>
    <div class="hero-metrics">
        <div class="metric-pill">🎯 Nivel: {nivel}</div>
        <div class="metric-pill">🧭 {len(ruta_personalizada)} temas recomendados</div>
        <div class="metric-pill">✅ {completadas_ruta} lecciones completadas</div>
        <div class="metric-pill">💪 {len(fortalezas)} fortalezas detectadas</div>
    </div>
    </div>""",
    unsafe_allow_html=True
)


st.sidebar.success(
    f"🎯 Nivel detectado:\n\n{nivel}"
)


st.markdown(
    f"**Progreso de la ruta: {completadas_ruta} de {total_ruta} lecciones**"
)
st.progress(porcentaje_ruta)


# ==========================================================
# RUTA PERSONALIZADA
# ==========================================================

st.markdown(
    '<div class="section-title">🧭 Tu ruta recomendada</div>',
    unsafe_allow_html=True
)

tarjetas_ruta = []

for indice, tema in enumerate(ruta_personalizada, start=1):

    if tema in lecciones_completadas:
        estado = "✅ Completada"
    elif tema == siguiente_tema:
        estado = "🚀 Continúa aquí"
    else:
        estado = "Pendiente"

    tarjetas_ruta.append(
        f"""<div class="route-card">
        <div class="route-index">{indice}</div>
        <div class="route-topic">{tema}</div>
        <div class="route-status">{estado}</div>
        </div>"""
    )

st.markdown(
    f'<div class="route-grid">{"".join(tarjetas_ruta)}</div>',
    unsafe_allow_html=True
)


# ==========================================================
# SIGUIENTE PASO
# ==========================================================

if siguiente_tema:

    st.markdown(
        f"""<div class="next-card">
        <div class="next-label">Siguiente paso recomendado</div>
        <div class="next-title">✨ {siguiente_tema}</div>
        <div class="next-subtitle">
            Esta lección coincide directamente con las áreas detectadas
            en tu evaluación diagnóstica.
        </div>
        </div>""",
        unsafe_allow_html=True
    )

    if st.button(
        "🚀 Iniciar lección recomendada",
        use_container_width=True,
        key="iniciar_recomendada"
    ):

        st.session_state["tema_actual"] = siguiente_tema
        st.session_state.pop("teoria", None)
        registrar_leccion_iniciada(siguiente_tema)
        st.rerun()

else:
    st.success("🎉 Completaste todos los temas de tu ruta recomendada.")


# ==========================================================
# EXPLORAR TODAS LAS UNIDADES
# ==========================================================

st.divider()

st.markdown(
    '<div class="section-title">📖 Explorar todas las unidades</div>',
    unsafe_allow_html=True
)

for unidad, lista_temas in TEMAS.items():

    with st.expander(
        f"📘 {unidad}"
    ):

        for tema in lista_temas:

            if st.button(
                tema,
                key=f"tema_{unidad}_{tema}",
                use_container_width=True
            ):

                st.session_state["tema_actual"] = tema
                st.session_state.pop("teoria", None)
                registrar_leccion_iniciada(tema)
                st.rerun()


# ==========================================================
# MOSTRAR TEMA SELECCIONADO
# ==========================================================

if "tema_actual" in st.session_state:

    tema = st.session_state["tema_actual"]

    st.divider()

    st.success(
        f"✅ Tema seleccionado: {tema}"
    )

    st.header(
        f"📖 {tema}"
    )

    if st.button(
        "🚀 Iniciar lección",
        use_container_width=True,
        key="iniciar_leccion"
    ):

        with st.spinner(
            "DERIVA AI está preparando la lección..."
        ):

            teoria = generar_teoria(
                tema,
                nivel
            )

        st.session_state["teoria"] = teoria


# ==========================================================
# MOSTRAR TEORÍA GENERADA
# ==========================================================

if "teoria" in st.session_state:

    st.markdown(
        st.session_state["teoria"]
    )

    st.divider()

    if tema in lecciones_completadas:
        st.success("✅ Esta lección ya está marcada como completada.")
    else:
        if st.button(
            "✅ Marcar lección como completada",
            use_container_width=True,
            key="completar_leccion",
        ):
            marcar_leccion_completada(tema)
            st.session_state.pop("teoria", None)
            st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🤖 Ir al Tutor",
            use_container_width=True,
            key="ir_tutor"
        ):
            st.session_state["desde_ruta_aprendizaje"] = True
            st.session_state["tema_actual"] = tema
            st.switch_page("pages/chat.py")

    with col2:
        if st.button(
            "📝 Practicar este tema",
            use_container_width=True,
            key="practicar_tema"
        ):
            st.session_state["tema_actual"] = tema
            st.switch_page("pages/practice.py")

    siguiente_despues = None
    if tema in ruta_personalizada:
        posicion = ruta_personalizada.index(tema)
        for candidato in ruta_personalizada[posicion + 1:]:
            if candidato not in lecciones_completadas:
                siguiente_despues = candidato
                break

    if siguiente_despues:
        if st.button(
            f"➡️ Continuar con: {siguiente_despues}",
            use_container_width=True,
            key="siguiente_leccion",
        ):
            st.session_state["tema_actual"] = siguiente_despues
            st.session_state.pop("teoria", None)
            registrar_leccion_iniciada(siguiente_despues)
            st.rerun()