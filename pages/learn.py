import streamlit as st
from utils.theme import aplicar_tema
from data.temas import TEMAS
from services.learn_service import generar_teoria
from services.session_service import (
    establecer,
    establecer_tema,
    guardar_leccion,
    inicializar_estado,
    limpiar_leccion,
    navegar_a,
    preparar_nova,
    preparar_practica,
)
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
    layout="wide",
)

aplicar_tema()
inicializar_estado()


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
        key="ir_diagnostico_desde_aprender",
    ):
        navegar_a("pages/diagnostic.py")

    st.stop()


# ==========================================================
# CARGAR DIAGNÓSTICO Y PROGRESO
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
        establecer("permitir_repetir_diagnostico", True)
        establecer("evaluacion_iniciada", False)
        navegar_a("pages/diagnostic.py")

    st.stop()


nivel = datos_diagnostico.get("nivel", obtener_nivel())
areas_a_reforzar = datos_diagnostico.get("mejorar", [])
fortalezas = datos_diagnostico.get("fortalezas", [])
plan_diagnostico = datos_diagnostico.get("plan_estudios", [])

progreso = cargar_progreso()
lecciones_completadas = progreso.get("lecciones_completadas", [])

TEMAS_VALIDOS = {
    tema
    for lista_temas in TEMAS.values()
    for tema in lista_temas
}


# ==========================================================
# MAPA ENTRE DIAGNÓSTICO Y TEMAS
# ==========================================================

MAPA_RECOMENDACIONES = {
    "Límites": "1.1 Una mirada previa al cálculo",
    "Interpretación gráfica": "1.2 Cálculo de límites de manera gráfica y numérica",
    "Continuidad": "1.4 Continuidad y límites laterales",
    "Continuidad gráfica": "1.4 Continuidad y límites laterales",
    "Definición de derivada": "2.2 Definición de derivada",
    "Derivadas": "2.3 Reglas básicas de derivación",
    "Aplicaciones": "3.1 Razones relacionadas",
}


def construir_ruta_personalizada():
    ruta = []
    temas_validos = TEMAS_VALIDOS

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


def obtener_siguiente_tema(ruta):
    for tema in ruta:
        if tema not in lecciones_completadas:
            return tema
    return None


def generar_leccion(tema):
    """Genera una lección y conserva el estado antes de redibujar."""
    tema = establecer_tema(tema)
    limpiar_leccion()
    registrar_leccion_iniciada(tema)

    try:
        with st.spinner(
            "DERIVA AI está preparando tu lección personalizada..."
        ):
            teoria_generada = generar_teoria(
                tema,
                nivel,
            )

        if not teoria_generada:
            raise RuntimeError(
                "El servicio no devolvió contenido para la lección."
            )

        teoria_limpia = str(teoria_generada).strip()

        if not teoria_limpia or teoria_limpia.lower() == "none":
            raise RuntimeError(
                "El servicio devolvió una lección vacía."
            )

        guardar_leccion(
            tema,
            teoria_limpia,
        )
        return True

    except Exception as error:
        limpiar_leccion()
        st.error(
            "No fue posible generar la lección en este momento. "
            "Tu tema y tu progreso permanecen guardados."
        )
        with st.expander("Ver detalle técnico"):
            st.code(
                f"{type(error).__name__}: {error}"
            )
        return False


ruta_personalizada = construir_ruta_personalizada()
siguiente_tema = obtener_siguiente_tema(ruta_personalizada)

total_ruta = len(ruta_personalizada)
completadas_ruta = sum(
    1 for tema in ruta_personalizada
    if tema in lecciones_completadas
)
porcentaje_ruta = (
    completadas_ruta / total_ruta
    if total_ruta
    else 0
)


# ==========================================================
# ESTADO DE LA INTERFAZ
# ==========================================================

if "unidad_abierta" not in st.session_state:
    st.session_state["unidad_abierta"] = None


# ==========================================================
# ESTILOS
# ==========================================================

st.markdown(
    """
    <style>
    .learn-hero {
        background: linear-gradient(
            135deg,
            rgba(255,255,255,.82),
            rgba(220,245,255,.72),
            rgba(241,224,255,.70)
        );
        border: 1px solid rgba(255,255,255,.92);
        border-radius: 32px;
        padding: 36px;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.78),
            0 20px 50px rgba(74,105,190,.12);
        backdrop-filter: blur(22px);
        margin-bottom: 26px;
    }

    .hero-kicker {
        color: #5D79E6;
        font-size: 14px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 10px;
    }

    .hero-title {
        color: #233755;
        font-size: 40px;
        font-weight: 900;
        line-height: 1.2;
        margin-bottom: 10px;
    }

    .hero-subtitle {
        color: #60758D;
        font-size: 17px;
        line-height: 1.65;
        max-width: 900px;
    }

    .hero-metrics {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 24px;
    }

    .metric-pill {
        background: rgba(255,255,255,.66);
        border: 1px solid rgba(255,255,255,.90);
        border-radius: 999px;
        padding: 10px 16px;
        color: #4B6280;
        font-size: 14px;
        font-weight: 800;
        box-shadow: 0 8px 18px rgba(74,105,190,.07);
    }

    .section-title {
        color: #253A58;
        font-size: 28px;
        font-weight: 900;
        margin: 18px 0 18px 0;
    }

    .next-card {
        background: linear-gradient(
            135deg,
            rgba(198,235,255,.92),
            rgba(255,211,232,.80),
            rgba(222,205,255,.82)
        );
        border: 1px solid rgba(255,255,255,.94);
        border-radius: 30px;
        padding: 30px;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.84),
            0 18px 42px rgba(79,111,232,.14);
        margin: 22px 0 18px 0;
    }

    .next-label {
        color: #556FE0;
        font-size: 14px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }

    .next-title {
        color: #223755;
        font-size: 27px;
        font-weight: 900;
        line-height: 1.35;
        margin-bottom: 8px;
    }

    .next-subtitle {
        color: #5C718A;
        font-size: 15px;
    }

    .selected-unit {
        background: linear-gradient(
            135deg,
            rgba(220,246,240,.94),
            rgba(221,240,255,.94)
        );
        border: 1px solid rgba(255,255,255,.94);
        border-radius: 22px;
        padding: 18px 22px;
        color: #526B86;
        font-size: 17px;
        font-weight: 800;
        margin: 18px 0;
        box-shadow: 0 10px 24px rgba(74,105,190,.08);
    }

    .lesson-panel {
        background: rgba(255,255,255,.74);
        border: 1px solid rgba(255,255,255,.92);
        border-radius: 28px;
        padding: 28px;
        box-shadow: 0 18px 40px rgba(74,105,190,.10);
        margin-top: 24px;
    }

    div.stButton > button {
        border-radius: 22px !important;
        min-height: 62px !important;
        font-size: 17px !important;
        font-weight: 900 !important;
        border: 1px solid rgba(255,255,255,.94) !important;
        background: linear-gradient(
            135deg,
            rgba(207,239,255,.98),
            rgba(235,213,255,.97)
        ) !important;
        color: #334FB7 !important;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.88),
            0 12px 26px rgba(67,111,218,.15) !important;
        transition:
            transform .20s ease,
            box-shadow .20s ease,
            filter .20s ease !important;
    }

    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.01) !important;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.94),
            0 17px 32px rgba(67,111,218,.23) !important;
        filter: brightness(1.03);
    }

    div.stButton > button[kind="primary"] {
        min-height: 76px !important;
        border-radius: 24px !important;
        background: linear-gradient(
            135deg,
            #6D8CFF,
            #9A5CF6
        ) !important;
        color: white !important;
        font-size: 22px !important;
        box-shadow:
            0 16px 34px rgba(91,83,192,.28) !important;
    }

    div.stButton > button[kind="primary"] * {
        color: white !important;
        font-size: 22px !important;
        font-weight: 950 !important;
    }

    @media (max-width: 800px) {
        .hero-title {
            font-size: 31px;
        }

        .learn-hero {
            padding: 25px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# ENCABEZADO
# ==========================================================

html_encabezado = (
    f'<div class="learn-hero">'
    f'<div class="hero-kicker">RUTA PERSONALIZADA</div>'
    f'<div class="hero-title">📚 Aprende con un plan hecho para ti</div>'
    f'<div class="hero-subtitle">'
    f'DERIVA AI organizó esta ruta utilizando tu evaluación diagnóstica. '
    f'Puedes comenzar por la recomendación principal o explorar las unidades. '
    f'Al elegir un tema, la lección se genera directamente en esta página.'
    f'</div>'
    f'<div class="hero-metrics">'
    f'<div class="metric-pill">🎯 Nivel: {nivel}</div>'
    f'<div class="metric-pill">🧭 {len(ruta_personalizada)} temas recomendados</div>'
    f'<div class="metric-pill">✅ {completadas_ruta} lecciones completadas</div>'
    f'<div class="metric-pill">💪 {len(fortalezas)} fortalezas detectadas</div>'
    f'</div>'
    f'</div>'
)

st.markdown(
    html_encabezado,
    unsafe_allow_html=True,
)


# ==========================================================
# INICIAR LECCIÓN RECOMENDADA
# ==========================================================

if siguiente_tema:
    st.markdown(
        f'<div class="next-card">'
        f'<div class="next-label">Tu siguiente paso recomendado</div>'
        f'<div class="next-title">📘 {siguiente_tema}</div>'
        f'<div class="next-subtitle">'
        f'Esta lección fue seleccionada según tu diagnóstico y progreso.'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.get("teoria"):
        if st.button(
            "🚀 Iniciar lección recomendada",
            use_container_width=True,
            type="primary",
            key="iniciar_leccion_recomendada",
        ):
            if generar_leccion(siguiente_tema):
                st.rerun()
else:
    st.success(
        "🎉 Ya completaste todos los temas de tu ruta personalizada."
    )



# ==========================================================
# EXPLORAR TODAS LAS UNIDADES
# ==========================================================

st.markdown(
    '<div class="section-title">📖 Explorar todas las unidades</div>',
    unsafe_allow_html=True,
)

unidades = list(TEMAS.keys())
iconos_unidades = ["🌱", "⚡", "🚀"]

columnas_unidades = st.columns(len(unidades))

for indice, unidad in enumerate(unidades):
    with columnas_unidades[indice]:
        cantidad_temas = len(TEMAS[unidad])
        unidad_seleccionada = (
            st.session_state["unidad_abierta"] == unidad
        )
        icono = (
            iconos_unidades[indice]
            if indice < len(iconos_unidades)
            else "📘"
        )

        if st.button(
            f"{icono} {unidad}\n\n{cantidad_temas} temas disponibles",
            use_container_width=True,
            key=f"abrir_unidad_{indice}",
            type="primary" if unidad_seleccionada else "secondary",
        ):
            establecer(
                "unidad_abierta",
                None if unidad_seleccionada else unidad,
            )
            st.rerun()


# ==========================================================
# TEMAS DE LA UNIDAD SELECCIONADA
# ==========================================================

unidad_abierta = st.session_state["unidad_abierta"]

if unidad_abierta:
    st.markdown(
        f'<div class="selected-unit">'
        f'📘 Unidad seleccionada: {unidad_abierta}'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Selecciona el tema que deseas estudiar")

    for indice_tema, tema_unidad in enumerate(
        TEMAS.get(unidad_abierta, [])
    ):
        if tema_unidad in lecciones_completadas:
            estado = "✅"
        elif tema_unidad == siguiente_tema:
            estado = "✨"
        else:
            estado = "📖"

        if st.button(
            f"{estado} {tema_unidad}",
            use_container_width=True,
            key=f"seleccionar_tema_{indice_tema}_{unidad_abierta}",
        ):
            if generar_leccion(tema_unidad):
                st.rerun()


# ==========================================================
# MOSTRAR LA LECCIÓN GENERADA
# ==========================================================

teoria_actual = st.session_state.get("teoria")
tema_actual = st.session_state.get("tema_actual")

if (
    tema_actual in TEMAS_VALIDOS
    and teoria_actual
    and str(teoria_actual).strip().lower() != "none"
):
    tema = tema_actual

    st.divider()

    st.markdown(
        f'<div class="lesson-panel">'
        f'<div class="next-label">Lección personalizada</div>'
        f'<div class="next-title">📖 {tema}</div>'
        f'<div class="next-subtitle">'
        f'Contenido adaptado a tu nivel: <strong>{nivel}</strong>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(teoria_actual)
    st.divider()

    if tema in lecciones_completadas:
        st.success(
            "✅ Esta lección ya está marcada como completada."
        )
    else:
        if st.button(
            "✅ Marcar lección como completada",
            use_container_width=True,
            key="completar_leccion",
        ):
            marcar_leccion_completada(tema)
            limpiar_leccion()
            st.rerun()

    st.markdown("### Continúa aprendiendo")
    columna_tutor, columna_practica = st.columns(2)

    with columna_tutor:
        if st.button(
            "🤖 Consultar a Nova",
            use_container_width=True,
            key="ir_tutor",
        ):
            preparar_nova(
                tema,
                desde_ruta=True,
            )
            navegar_a("pages/chat.py")

    with columna_practica:
        if st.button(
            "📝 Practicar este tema",
            use_container_width=True,
            key="practicar_tema",
        ):
            preparar_practica(tema)
            navegar_a("pages/practice.py")

    siguiente_despues = None

    if tema in ruta_personalizada:
        posicion_actual = ruta_personalizada.index(tema)

        for candidato in ruta_personalizada[posicion_actual + 1:]:
            if candidato not in lecciones_completadas:
                siguiente_despues = candidato
                break

    if siguiente_despues:
        st.info(
            f"Tu siguiente tema recomendado es: "
            f"**{siguiente_despues}**"
        )

        if st.button(
            f"➡️ Continuar con: {siguiente_despues}",
            use_container_width=True,
            key="continuar_siguiente_leccion",
        ):
            generar_leccion(siguiente_despues)
            st.rerun()