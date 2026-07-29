import streamlit as st

from utils.math_renderer import renderizar_matematicas
import pandas as pd
from datetime import datetime, timedelta

from services.progress_service import cargar_progreso
from utils.theme import aplicar_tema


st.set_page_config(
    page_title="Mi progreso | DERIVA AI",
    page_icon="📈",
    layout="wide",
)


aplicar_tema()


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def obtener_valor(
    datos,
    clave,
    valor_predeterminado,
):
    return datos.get(
        clave,
        valor_predeterminado,
    )


def calcular_porcentaje(
    parte,
    total,
):
    if total <= 0:
        return 0

    return round(
        parte / total * 100
    )


def calcular_racha(
    historial,
):
    fechas = set()

    for registro in historial:
        fecha_texto = registro.get(
            "fecha"
        )

        if not fecha_texto:
            continue

        try:
            fecha = datetime.fromisoformat(
                fecha_texto
            ).date()

            fechas.add(
                fecha
            )

        except ValueError:
            continue

    if not fechas:
        return 0

    hoy = datetime.now().date()

    if hoy not in fechas:
        ayer = hoy - timedelta(
            days=1
        )

        if ayer not in fechas:
            return 0

        fecha_actual = ayer

    else:
        fecha_actual = hoy

    racha = 0

    while fecha_actual in fechas:
        racha += 1

        fecha_actual -= timedelta(
            days=1
        )

    return racha


def calcular_dominio_tema(
    datos_tema,
):
    revisados = datos_tema.get(
        "revisados",
        0,
    )

    correctas = datos_tema.get(
        "correctas",
        0,
    )

    parciales = datos_tema.get(
        "parciales",
        0,
    )

    if revisados <= 0:
        return 0

    puntuacion = (
        correctas
        + parciales * 0.5
    )

    return min(
        100,
        round(
            puntuacion / revisados * 100
        ),
    )


def clasificar_dominio(
    porcentaje,
):
    if porcentaje >= 80:
        return "Dominado"

    if porcentaje >= 50:
        return "En progreso"

    if porcentaje > 0:
        return "Por reforzar"

    return "Sin evaluar"


def crear_recomendacion(
    progreso_por_tema,
    revisados,
    porcentaje_global,
):
    if revisados == 0:
        return (
            "Comienza generando tu primer ejercicio en la sección "
            "Practicar. DERIVA AI adaptará la dificultad a tu nivel."
        )

    if not progreso_por_tema:
        return (
            "Continúa practicando para que DERIVA AI pueda identificar "
            "qué temas dominas y cuáles debes reforzar."
        )

    dominios = []

    for tema, datos in progreso_por_tema.items():
        dominios.append(
            (
                tema,
                calcular_dominio_tema(
                    datos
                ),
                datos.get(
                    "revisados",
                    0,
                ),
            )
        )

    temas_evaluados = [
        elemento
        for elemento in dominios
        if elemento[2] > 0
    ]

    if temas_evaluados:
        tema_refuerzo = min(
            temas_evaluados,
            key=lambda elemento: elemento[1],
        )

        if tema_refuerzo[1] < 80:
            return (
                f"Te recomiendo reforzar **{tema_refuerzo[0]}**. "
                f"Tu nivel de dominio estimado es de "
                f"**{tema_refuerzo[1]}%**."
            )

    if porcentaje_global >= 80:
        return (
            "Tu rendimiento general es muy bueno. Intenta practicar "
            "ejercicios de mayor dificultad para seguir avanzando."
        )

    return (
        "Sigue practicando los temas actuales y explica siempre tu "
        "procedimiento completo para recibir una mejor retroalimentación."
    )


def tarjeta_metrica(
    icono,
    titulo,
    valor,
    descripcion,
):
    return (
        '<div class="metric-card">'
        f'<div class="metric-icon">{icono}</div>'
        f'<div class="metric-title">{titulo}</div>'
        f'<div class="metric-value">{valor}</div>'
        f'<div class="metric-description">{descripcion}</div>'
        '</div>'
    )


# =========================================================
# DATOS
# =========================================================

progreso = cargar_progreso()

preguntas = obtener_valor(
    progreso,
    "preguntas",
    0,
)

temas_estudiados = obtener_valor(
    progreso,
    "temas_estudiados",
    [],
)

ultimo_tema = obtener_valor(
    progreso,
    "ultimo_tema",
    "Ninguno",
)

ejercicios_generados = obtener_valor(
    progreso,
    "ejercicios_generados",
    0,
)

ejercicios_revisados = obtener_valor(
    progreso,
    "ejercicios_revisados",
    0,
)

respuestas_correctas = obtener_valor(
    progreso,
    "respuestas_correctas",
    0,
)

respuestas_parciales = obtener_valor(
    progreso,
    "respuestas_parciales",
    0,
)

respuestas_incorrectas = obtener_valor(
    progreso,
    "respuestas_incorrectas",
    0,
)

historial = obtener_valor(
    progreso,
    "historial_practica",
    [],
)

progreso_por_tema = obtener_valor(
    progreso,
    "progreso_por_tema",
    {},
)

porcentaje_aciertos = calcular_porcentaje(
    respuestas_correctas,
    ejercicios_revisados,
)

racha = calcular_racha(
    historial
)

recomendacion = crear_recomendacion(
    progreso_por_tema,
    ejercicios_revisados,
    porcentaje_aciertos,
)


# =========================================================
# ESTILOS
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at 87% 7%,
                rgba(238, 214, 255, .62),
                transparent 24%
            ),
            radial-gradient(
                circle at 45% 0%,
                rgba(199, 238, 255, .62),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #fbfdff 0%,
                #eef8ff 50%,
                #faf3ff 100%
            );
    }

    .block-container {
        max-width: 1280px;
        padding-top: 2rem;
        padding-bottom: 6rem;
    }

    .progress-hero {
        position: relative;
        overflow: hidden;
        padding: 35px 37px;
        margin-bottom: 24px;
        border-radius: 32px;
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, .84),
            rgba(218, 242, 255, .74),
            rgba(242, 221, 255, .72)
        );
        border: 1px solid rgba(255, 255, 255, .94);
        box-shadow:
            inset 0 1px 0 rgba(255, 255, 255, .94),
            0 22px 52px rgba(69, 87, 157, .13);
        backdrop-filter: blur(22px);
    }

    .progress-hero::after {
        content: "";
        position: absolute;
        width: 255px;
        height: 255px;
        right: -75px;
        top: -100px;
        border-radius: 50%;
        background: rgba(255, 255, 255, .27);
    }

    .hero-kicker {
        position: relative;
        z-index: 2;
        color: #6879df;
        font-size: 14px;
        font-weight: 850;
        letter-spacing: 1.1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .hero-title {
        position: relative;
        z-index: 2;
        color: #213754;
        font-size: 43px;
        font-weight: 850;
        line-height: 1.13;
        margin-bottom: 10px;
    }

    .hero-subtitle {
        position: relative;
        z-index: 2;
        max-width: 770px;
        color: #687b94;
        font-size: 16px;
        line-height: 1.65;
    }

    .hero-badges {
        position: relative;
        z-index: 2;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 20px;
    }

    .hero-badge {
        padding: 9px 14px;
        border-radius: 999px;
        color: #526885;
        background: rgba(255, 255, 255, .66);
        border: 1px solid rgba(255, 255, 255, .94);
        box-shadow: 0 8px 18px rgba(74, 94, 163, .07);
        font-size: 13px;
        font-weight: 750;
    }

    .metric-card {
        min-height: 155px;
        padding: 21px;
        border-radius: 24px;
        background: rgba(255, 255, 255, .72);
        border: 1px solid rgba(255, 255, 255, .94);
        box-shadow: 0 13px 30px rgba(68, 88, 155, .09);
        backdrop-filter: blur(17px);
    }

    .metric-icon {
        font-size: 25px;
        margin-bottom: 9px;
    }

    .metric-title {
        color: #7889a0;
        font-size: 13px;
        font-weight: 720;
        margin-bottom: 5px;
    }

    .metric-value {
        color: #30496d;
        font-size: 29px;
        font-weight: 850;
        line-height: 1.2;
    }

    .metric-description {
        color: #8b9aaf;
        font-size: 12px;
        line-height: 1.45;
        margin-top: 7px;
    }

    .section-card {
        margin-top: 20px;
        padding: 27px;
        border-radius: 27px;
        background: rgba(255, 255, 255, .74);
        border: 1px solid rgba(255, 255, 255, .94);
        box-shadow: 0 16px 38px rgba(66, 86, 154, .09);
        backdrop-filter: blur(18px);
    }

    .section-kicker {
        color: #6577d9;
        font-size: 13px;
        font-weight: 850;
        letter-spacing: .9px;
        text-transform: uppercase;
        margin-bottom: 7px;
    }

    .section-title {
        color: #29415f;
        font-size: 25px;
        font-weight: 830;
        margin-bottom: 8px;
    }

    .section-text {
        color: #71839a;
        font-size: 14px;
        line-height: 1.65;
    }

    .recommendation-card {
        padding: 24px;
        border-radius: 25px;
        background: linear-gradient(
            135deg,
            rgba(232, 244, 255, .92),
            rgba(245, 231, 255, .92)
        );
        border: 1px solid rgba(255, 255, 255, .94);
        box-shadow: 0 14px 31px rgba(68, 88, 155, .09);
    }

    .achievement-card {
        min-height: 125px;
        padding: 20px;
        border-radius: 22px;
        background: rgba(255, 255, 255, .70);
        border: 1px solid rgba(255, 255, 255, .94);
        box-shadow: 0 12px 26px rgba(68, 88, 155, .08);
    }

    .achievement-locked {
        opacity: .48;
        filter: grayscale(.35);
    }

    .achievement-icon {
        font-size: 28px;
        margin-bottom: 8px;
    }

    .achievement-title {
        color: #324b6d;
        font-size: 15px;
        font-weight: 820;
        margin-bottom: 5px;
    }

    .achievement-text {
        color: #7c8ca2;
        font-size: 12px;
        line-height: 1.45;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 20px;
        overflow: hidden;
    }

    @media (max-width: 700px) {
        .progress-hero {
            padding: 27px 24px;
        }

        .hero-title {
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


# =========================================================
# ENCABEZADO
# =========================================================

hero_html = (
    '<section class="progress-hero">'
    '<div class="hero-kicker">Tu evolución académica</div>'
    '<div class="hero-title">📈 Mi progreso</div>'
    '<div class="hero-subtitle">'
    'Observa cómo avanzas, identifica los temas que ya dominas y descubre '
    'qué debes reforzar para continuar mejorando en Cálculo Diferencial.'
    '</div>'
    '<div class="hero-badges">'
    f'<div class="hero-badge">📚 {len(temas_estudiados)} temas explorados</div>'
    f'<div class="hero-badge">🔥 Racha de {racha} días</div>'
    f'<div class="hero-badge">🎯 {porcentaje_aciertos}% de aciertos</div>'
    '</div>'
    '</section>'
)

st.markdown(
    hero_html,
    unsafe_allow_html=True,
)


# =========================================================
# MÉTRICAS PRINCIPALES
# =========================================================

col1, col2, col3, col4 = st.columns(
    4
)

with col1:
    st.markdown(
        tarjeta_metrica(
            "💬",
            "Preguntas realizadas",
            preguntas,
            "Consultas hechas a Nova durante tu aprendizaje.",
        ),
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        tarjeta_metrica(
            "📝",
            "Ejercicios revisados",
            ejercicios_revisados,
            "Prácticas que recibieron retroalimentación.",
        ),
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        tarjeta_metrica(
            "✅",
            "Respuestas correctas",
            respuestas_correctas,
            "Ejercicios resueltos correctamente.",
        ),
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        tarjeta_metrica(
            "🔥",
            "Racha actual",
            f"{racha} días",
            "Días consecutivos con actividad de práctica.",
        ),
        unsafe_allow_html=True,
    )


# =========================================================
# RENDIMIENTO GENERAL
# =========================================================

st.markdown(
    (
        '<div class="section-card">'
        '<div class="section-kicker">Resumen general</div>'
        '<div class="section-title">Tu rendimiento</div>'
        '<div class="section-text">'
        'Este indicador considera tus respuestas correctas, parciales '
        'e incorrectas registradas en la sección Practicar.'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

col_rendimiento, col_resultados = st.columns(
    [1.05, 1]
)

with col_rendimiento:
    st.markdown(
        "#### 🎯 Porcentaje de aciertos"
    )

    st.progress(
        porcentaje_aciertos / 100
        if porcentaje_aciertos > 0
        else 0
    )

    st.caption(
        f"{porcentaje_aciertos}% de respuestas completamente correctas."
    )

    st.markdown(
        "#### 📖 Último tema trabajado"
    )

    st.info(
        ultimo_tema
    )

with col_resultados:
    datos_resultados = pd.DataFrame(
        {
            "Resultado": [
                "Correctas",
                "Parciales",
                "Incorrectas",
            ],
            "Cantidad": [
                respuestas_correctas,
                respuestas_parciales,
                respuestas_incorrectas,
            ],
        }
    )

    if ejercicios_revisados > 0:
        st.bar_chart(
            datos_resultados,
            x="Resultado",
            y="Cantidad",
            use_container_width=True,
        )

    else:
        st.info(
            "Todavía no hay ejercicios revisados para mostrar."
        )


# =========================================================
# PROGRESO POR TEMA
# =========================================================

st.markdown(
    (
        '<div class="section-card">'
        '<div class="section-kicker">Mapa de aprendizaje</div>'
        '<div class="section-title">Dominio por tema</div>'
        '<div class="section-text">'
        'El dominio se estima usando tus respuestas correctas y parciales '
        'en cada tema.'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

filas_temas = []

for tema, datos in progreso_por_tema.items():
    dominio = calcular_dominio_tema(
        datos
    )

    filas_temas.append(
        {
            "Tema": tema,
            "Nivel": datos.get(
                "ultimo_nivel",
                "No registrado",
            ),
            "Generados": datos.get(
                "generados",
                0,
            ),
            "Revisados": datos.get(
                "revisados",
                0,
            ),
            "Dominio": dominio,
            "Estado": clasificar_dominio(
                dominio
            ),
        }
    )

if filas_temas:
    filas_temas.sort(
        key=lambda fila: fila["Dominio"],
        reverse=True,
    )

    for fila in filas_temas:
        col_tema, col_barra, col_estado = st.columns(
            [1.4, 2.1, 1]
        )

        with col_tema:
            st.markdown(
                f"**{fila['Tema']}**"
            )

            st.caption(
                f"Nivel: {fila['Nivel']} · "
                f"{fila['Revisados']} revisados"
            )

        with col_barra:
            st.progress(
                fila["Dominio"] / 100
            )

            st.caption(
                f"{fila['Dominio']}% de dominio estimado"
            )

        with col_estado:
            estado = fila[
                "Estado"
            ]

            if estado == "Dominado":
                st.success(
                    "🏆 Dominado"
                )

            elif estado == "En progreso":
                st.info(
                    "📘 En progreso"
                )

            elif estado == "Por reforzar":
                st.warning(
                    "🧠 Por reforzar"
                )

            else:
                st.caption(
                    "Sin evaluar"
                )

else:
    st.info(
        "Aún no hay suficiente información para calcular tu dominio por tema."
    )


# =========================================================
# RECOMENDACIÓN DE NOVA
# =========================================================

st.markdown(
    (
        '<div class="recommendation-card">'
        '<div class="section-kicker">Recomendación personalizada</div>'
        '<div class="section-title">💡 Nova te recomienda</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

renderizar_matematicas(
    recomendacion
)


# =========================================================
# LOGROS
# =========================================================

st.markdown(
    (
        '<div class="section-card">'
        '<div class="section-kicker">Motivación</div>'
        '<div class="section-title">🏆 Tus logros</div>'
        '<div class="section-text">'
        'Los logros se desbloquean automáticamente mientras estudias.'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

logros = [
    {
        "icono": "🌱",
        "titulo": "Primer paso",
        "texto": "Completa tu primer ejercicio.",
        "desbloqueado": ejercicios_revisados >= 1,
    },
    {
        "icono": "📚",
        "titulo": "Explorador",
        "texto": "Estudia al menos 3 temas.",
        "desbloqueado": len(
            temas_estudiados
        ) >= 3,
    },
    {
        "icono": "🎯",
        "titulo": "Precisión matemática",
        "texto": "Consigue 5 respuestas correctas.",
        "desbloqueado": respuestas_correctas >= 5,
    },
    {
        "icono": "🔥",
        "titulo": "Constancia",
        "texto": "Mantén una racha de 3 días.",
        "desbloqueado": racha >= 3,
    },
]

columnas_logros = st.columns(
    4
)

for columna, logro in zip(
    columnas_logros,
    logros,
):
    clase = (
        ""
        if logro["desbloqueado"]
        else " achievement-locked"
    )

    estado = (
        "Desbloqueado"
        if logro["desbloqueado"]
        else "Bloqueado"
    )

    with columna:
        st.markdown(
            (
                f'<div class="achievement-card{clase}">'
                f'<div class="achievement-icon">{logro["icono"]}</div>'
                f'<div class="achievement-title">{logro["titulo"]}</div>'
                f'<div class="achievement-text">{logro["texto"]}</div>'
                f'<div class="achievement-text"><strong>{estado}</strong></div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )


# =========================================================
# HISTORIAL RECIENTE
# =========================================================

st.markdown(
    (
        '<div class="section-card">'
        '<div class="section-kicker">Actividad reciente</div>'
        '<div class="section-title">🕒 Historial de práctica</div>'
        '<div class="section-text">'
        'Aquí aparecen tus ejercicios revisados más recientes.'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

if historial:
    filas_historial = []

    for registro in reversed(
        historial[-10:]
    ):
        fecha_texto = registro.get(
            "fecha",
            "",
        )

        fecha_mostrada = fecha_texto

        try:
            fecha_mostrada = datetime.fromisoformat(
                fecha_texto
            ).strftime(
                "%d/%m/%Y %I:%M %p"
            )

        except ValueError:
            pass

        resultado = registro.get(
            "resultado",
            "sin clasificar",
        ).capitalize()

        filas_historial.append(
            {
                "Fecha": fecha_mostrada,
                "Tema": registro.get(
                    "tema",
                    "General",
                ),
                "Nivel": registro.get(
                    "nivel",
                    "No registrado",
                ),
                "Resultado": resultado,
            }
        )

    dataframe_historial = pd.DataFrame(
        filas_historial
    )

    st.dataframe(
        dataframe_historial,
        use_container_width=True,
        hide_index=True,
    )

else:
    st.info(
        "Tu historial aparecerá después de revisar ejercicios en Practicar."
    )


# =========================================================
# TEMAS EXPLORADOS
# =========================================================

with st.expander(
    "📚 Ver todos los temas explorados"
):
    if temas_estudiados:
        for tema in temas_estudiados:
            st.markdown(
                f"✅ {tema}"
            )

    else:
        st.write(
            "Aún no tienes temas registrados."
        )