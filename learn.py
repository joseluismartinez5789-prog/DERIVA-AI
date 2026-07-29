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

st.set_page_config(page_title="Aprender", page_icon="📚", layout="wide")
aplicar_tema()

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
        st.switch_page("pages/diagnostic.py")
    st.stop()

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
    temas_validos = {
        tema
        for lista_temas in TEMAS.values()
        for tema in lista_temas
    }

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


ruta_personalizada = construir_ruta_personalizada()
siguiente_tema = obtener_siguiente_tema(ruta_personalizada)
total_ruta = len(ruta_personalizada)
completadas_ruta = sum(
    1 for tema in ruta_personalizada if tema in lecciones_completadas
)
porcentaje_ruta = completadas_ruta / total_ruta if total_ruta else 0

if "unidad_abierta" not in st.session_state:
    st.session_state.unidad_abierta = None

if "tema_actual" not in st.session_state and siguiente_tema:
    st.session_state.tema_actual = siguiente_tema

st.markdown(
    """
    <style>
    .learn-hero {
        background: linear-gradient(135deg, rgba(255,255,255,.80), rgba(220,245,255,.70), rgba(241,224,255,.68));
        border: 1px solid rgba(255,255,255,.90);
        border-radius: 32px;
        padding: 36px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,.76), 0 20px 50px rgba(74,105,190,.12);
        backdrop-filter: blur(22px);
        margin-bottom: 26px;
    }
    .hero-kicker {color:#5D79E6;font-size:14px;font-weight:900;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px;}
    .hero-title {color:#233755;font-size:40px;font-weight:900;line-height:1.2;margin-bottom:10px;}
    .hero-subtitle {color:#60758D;font-size:17px;line-height:1.65;max-width:900px;}
    .hero-metrics {display:flex;flex-wrap:wrap;gap:12px;margin-top:24px;}
    .metric-pill {background:rgba(255,255,255,.64);border:1px solid rgba(255,255,255,.88);border-radius:999px;padding:10px 16px;color:#4B6280;font-size:14px;font-weight:800;box-shadow:0 8px 18px rgba(74,105,190,.07);}
    .section-title {color:#253A58;font-size:28px;font-weight:900;margin:12px 0 18px 0;}
    .next-card {background:linear-gradient(135deg,rgba(198,235,255,.90),rgba(255,211,232,.78),rgba(222,205,255,.80));border:1px solid rgba(255,255,255,.92);border-radius:30px;padding:30px;box-shadow:inset 0 1px 0 rgba(255,255,255,.82),0 18px 42px rgba(79,111,232,.14);margin:22px 0 28px 0;}
    .next-label {color:#556FE0;font-size:14px;font-weight:900;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;}
    .next-title {color:#223755;font-size:27px;font-weight:900;line-height:1.35;margin-bottom:8px;}
    .next-subtitle {color:#5C718A;font-size:15px;}
    .selected-topic {background:linear-gradient(135deg,rgba(220,246,240,.92),rgba(221,240,255,.92));border:1px solid rgba(255,255,255,.92);border-radius:22px;padding:18px 22px;color:#526B86;font-size:17px;font-weight:800;margin:18px 0;box-shadow:0 10px 24px rgba(74,105,190,.08);}
    .lesson-panel {background:rgba(255,255,255,.72);border:1px solid rgba(255,255,255,.90);border-radius:28px;padding:28px;box-shadow:0 18px 40px rgba(74,105,190,.10);margin-top:24px;}
    div.stButton > button {border-radius:22px !important;min-height:62px !important;font-size:17px !important;font-weight:900 !important;border:1px solid rgba(255,255,255,.94) !important;background:linear-gradient(135deg,rgba(207,239,255,.97),rgba(235,213,255,.96)) !important;color:#334FB7 !important;box-shadow:inset 0 1px 0 rgba(255,255,255,.88),0 12px 26px rgba(67,111,218,.15) !important;transition:transform .20s ease,box-shadow .20s ease,filter .20s ease !important;}
    div.stButton > button:hover {transform:translateY(-3px) scale(1.01) !important;box-shadow:inset 0 1px 0 rgba(255,255,255,.94),0 17px 32px rgba(67,111,218,.23) !important;filter:brightness(1.03);}
    div.stButton > button p, div.stButton > button span {font-size:17px !important;font-weight:900 !important;}
    div.stButton > button[kind="primary"], div.stButton > button[data-testid="stBaseButton-primary"] {min-height:76px !important;border-radius:24px !important;background:linear-gradient(135deg,#6D8CFF,#9A5CF6) !important;color:white !important;font-size:23px !important;font-weight:950 !important;letter-spacing:.3px !important;box-shadow:0 16px 34px rgba(91,83,192,.28) !important;}
    div.stButton > button[kind="primary"] *, div.stButton > button[data-testid="stBaseButton-primary"] * {color:white !important;font-size:23px !important;font-weight:950 !important;}
    @media (max-width:800px){.hero-title{font-size:31px}.learn-hero{padding:25px}div.stButton > button[kind="primary"],div.stButton > button[data-testid="stBaseButton-primary"]{font-size:19px !important}}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="learn-hero">
        <div class="hero-kicker">Ruta personalizada</div>
        <div class="hero-title">📚 Aprende con un plan hecho para ti</div>
        <div class="hero-subtitle">
            DERIVA AI organizó esta ruta utilizando tu evaluación diagnóstica.
            Selecciona una unidad, elige un tema y genera una lección personalizada
            directamente en esta página.
        </div>
        <div class="hero-metrics">
            <div class="metric-pill">🎯 Nivel: {nivel}</div>
            <div class="metric-pill">🧭 {len(ruta_personalizada)} temas recomendados</div>
            <div class="metric-pill">✅ {completadas_ruta} lecciones completadas</div>
            <div class="metric-pill">💪 {len(fortalezas)} fortalezas detectadas</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.success(f"🎯 Nivel detectado:\n\n{nivel}")
st.markdown(f"**Progreso de la ruta: {completadas_ruta} de {total_ruta} lecciones**")
st.progress(porcentaje_ruta)

if siguiente_tema:
    st.markdown(
        f"""
        <div class="next-card">
            <div class="next-label">Siguiente paso recomendado</div>
            <div class="next-title">✨ {siguiente_tema}</div>
            <div class="next-subtitle">
                Esta lección coincide directamente con las áreas detectadas
                en tu evaluación diagnóstica.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.success("🎉 Completaste todos los temas de tu ruta recomendada.")

st.markdown('<div class="section-title">📖 Explorar todas las unidades</div>', unsafe_allow_html=True)

columnas = st.columns(3)
for indice, (unidad, lista_temas) in enumerate(TEMAS.items()):
    with columnas[indice % 3]:
        if st.button(
            f"📘 {unidad}",
            use_container_width=True,
            key=f"abrir_unidad_{indice}",
        ):
            st.session_state.unidad_abierta = (
                None if st.session_state.unidad_abierta == unidad else unidad
            )
            st.session_state.pop("teoria", None)
            st.rerun()

unidad_abierta = st.session_state.get("unidad_abierta")
if unidad_abierta:
    st.markdown(f'<div class="section-title">📚 {unidad_abierta}</div>', unsafe_allow_html=True)
    for indice, tema_unidad in enumerate(TEMAS.get(unidad_abierta, [])):
        completada = tema_unidad in lecciones_completadas
        icono = "✅" if completada else "📄"
        if st.button(
            f"{icono} {tema_unidad}",
            use_container_width=True,
            key=f"seleccionar_tema_{indice}_{tema_unidad}",
        ):
            st.session_state.tema_actual = tema_unidad
            st.session_state.pop("teoria", None)
            registrar_leccion_iniciada(tema_unidad)
            st.rerun()

tema = st.session_state.get("tema_actual")
if tema:
    st.markdown(
        f'<div class="selected-topic">✅ Tema seleccionado: {tema}</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "🚀 INICIAR LECCIÓN PERSONALIZADA",
        use_container_width=True,
        type="primary",
        key=f"generar_leccion_{tema}",
    ):
        registrar_leccion_iniciada(tema)
        with st.spinner("DERIVA AI está preparando tu lección personalizada..."):
            st.session_state.teoria = generar_teoria(tema, nivel)
        st.rerun()

if tema and "teoria" in st.session_state:
    st.markdown('<div class="lesson-panel">', unsafe_allow_html=True)
    st.markdown(st.session_state.teoria)
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    if tema in lecciones_completadas:
        st.success("✅ Esta lección ya está marcada como completada.")
    elif st.button(
        "✅ Marcar lección como completada",
        use_container_width=True,
        key="completar_leccion",
    ):
        marcar_leccion_completada(tema)
        st.session_state.pop("teoria", None)
        st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🤖 Ir al Tutor", use_container_width=True, key="ir_tutor"):
            st.session_state.desde_ruta_aprendizaje = True
            st.session_state.tema_actual = tema
            st.switch_page("pages/chat.py")

    with col2:
        if st.button("📝 Practicar este tema", use_container_width=True, key="practicar_tema"):
            st.session_state.tema_actual = tema
            st.switch_page("pages/practice.py")

    siguiente_despues = None
    if tema in ruta_personalizada:
        posicion = ruta_personalizada.index(tema)
        for candidato in ruta_personalizada[posicion + 1:]:
            if candidato not in lecciones_completadas:
                siguiente_despues = candidato
                break

    if siguiente_despues and st.button(
        f"➡️ Continuar con: {siguiente_despues}",
        use_container_width=True,
        key="siguiente_leccion",
    ):
        st.session_state.tema_actual = siguiente_despues
        st.session_state.pop("teoria", None)
        registrar_leccion_iniciada(siguiente_despues)
        st.rerun()