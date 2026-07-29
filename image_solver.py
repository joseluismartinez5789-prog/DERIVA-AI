import streamlit as st

from utils.math_renderer import renderizar_matematicas

from utils.theme import aplicar_tema
from services.diagnostic_service import obtener_nivel
from services.image_service import (
    analizar_ejercicio_imagen,
    extraer_estado_imagen,
    extraer_tema_detectado,
    limpiar_metadatos_analisis,
)
from services.progress_service import registrar_pregunta


st.set_page_config(
    page_title="Resolver por imagen | DERIVA AI",
    page_icon="📷",
    layout="wide",
)

aplicar_tema()


def inicializar_estado():
    valores = {
        "imagen_uploader_key": 0,
        "analisis_imagen": None,
        "estado_imagen": None,
        "tema_imagen": "Pendiente",
        "nombre_imagen_analizada": None,
    }

    for clave, valor in valores.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor


def limpiar_analisis():
    st.session_state["analisis_imagen"] = None
    st.session_state["estado_imagen"] = None
    st.session_state["tema_imagen"] = "Pendiente"
    st.session_state["nombre_imagen_analizada"] = None


def preparar_nueva_imagen():
    limpiar_analisis()
    st.session_state["imagen_uploader_key"] += 1


inicializar_estado()
nivel = obtener_nivel()


st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 88% 8%, rgba(237,214,255,.62), transparent 24%),
            radial-gradient(circle at 46% 0%, rgba(197,238,255,.63), transparent 29%),
            linear-gradient(135deg, #fbfdff 0%, #eef8ff 50%, #faf3ff 100%);
    }

    .block-container {
        max-width: 1260px;
        padding-top: 2rem;
        padding-bottom: 7rem;
    }

    .image-hero {
        position: relative;
        overflow: hidden;
        padding: 35px 37px;
        margin-bottom: 24px;
        border-radius: 32px;
        background: linear-gradient(
            135deg,
            rgba(255,255,255,.84),
            rgba(218,242,255,.74),
            rgba(242,221,255,.72)
        );
        border: 1px solid rgba(255,255,255,.94);
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.94),
            0 22px 52px rgba(69,87,157,.13);
        backdrop-filter: blur(22px);
    }

    .image-hero::after {
        content: "";
        position: absolute;
        width: 255px;
        height: 255px;
        right: -75px;
        top: -100px;
        border-radius: 50%;
        background: rgba(255,255,255,.27);
    }

    .hero-kicker,
    .hero-title,
    .hero-subtitle,
    .hero-badges {
        position: relative;
        z-index: 2;
    }

    .hero-kicker {
        color: #6879df;
        font-size: 14px;
        font-weight: 850;
        letter-spacing: 1.1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .hero-title {
        color: #213754;
        font-size: 43px;
        font-weight: 850;
        line-height: 1.13;
        margin-bottom: 10px;
    }

    .hero-subtitle {
        max-width: 780px;
        color: #687b94;
        font-size: 16px;
        line-height: 1.65;
    }

    .hero-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 20px;
    }

    .hero-badge {
        padding: 9px 14px;
        border-radius: 999px;
        color: #526885;
        background: rgba(255,255,255,.66);
        border: 1px solid rgba(255,255,255,.94);
        box-shadow: 0 8px 18px rgba(74,94,163,.07);
        font-size: 13px;
        font-weight: 750;
    }

    .section-card {
        margin-top: 18px;
        padding: 26px;
        border-radius: 27px;
        background: rgba(255,255,255,.74);
        border: 1px solid rgba(255,255,255,.94);
        box-shadow: 0 16px 38px rgba(66,86,154,.09);
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

    .tip-card {
        min-height: 156px;
        padding: 21px;
        border-radius: 23px;
        background: rgba(255,255,255,.70);
        border: 1px solid rgba(255,255,255,.94);
        box-shadow: 0 13px 28px rgba(68,88,155,.08);
    }

    .tip-icon {
        font-size: 27px;
        margin-bottom: 9px;
    }

    .tip-title {
        color: #344d70;
        font-size: 15px;
        font-weight: 820;
        margin-bottom: 6px;
    }

    .tip-text {
        color: #7d8da3;
        font-size: 13px;
        line-height: 1.55;
    }

    .status-valid,
    .status-blurry,
    .status-invalid,
    .status-neutral {
        padding: 19px 22px;
        margin: 18px 0;
        border-radius: 23px;
        border: 1px solid rgba(255,255,255,.94);
        box-shadow: 0 13px 28px rgba(68,88,155,.08);
        font-size: 15px;
        font-weight: 760;
    }

    .status-valid {
        background: rgba(226,250,237,.92);
        color: #2e6b50;
    }

    .status-blurry {
        background: rgba(255,246,214,.94);
        color: #81671e;
    }

    .status-invalid {
        background: rgba(255,230,236,.93);
        color: #8b4055;
    }

    .status-neutral {
        background: rgba(237,241,255,.90);
        color: #53647e;
    }

    div[data-testid="stFileUploader"] {
        padding: 18px;
        border-radius: 24px;
        background: rgba(255,255,255,.62);
        border: 1px dashed rgba(119,139,207,.48);
    }

    div.stButton > button {
        min-height: 49px !important;
        border-radius: 999px !important;
        border: 1px solid rgba(255,255,255,.94) !important;
        background: linear-gradient(
            135deg,
            rgba(195,235,255,.98),
            rgba(235,207,255,.98)
        ) !important;
        color: #455fca !important;
        font-weight: 800 !important;
        box-shadow: 0 10px 23px rgba(72,101,183,.15) !important;
    }

    @media (max-width: 700px) {
        .image-hero {
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


st.markdown(
    (
        '<section class="image-hero">'
        '<div class="hero-kicker">Visión matemática</div>'
        '<div class="hero-title">📷 Resolver por imagen</div>'
        '<div class="hero-subtitle">'
        'Sube una fotografía de tu ejercicio y Nova analizará el contenido, '
        'identificará el tema y te guiará paso a paso.'
        '</div>'
        '<div class="hero-badges">'
        f'<div class="hero-badge">🎯 Nivel {nivel}</div>'
        '<div class="hero-badge">🔎 Lectura inteligente</div>'
        '<div class="hero-badge">🧠 Explicación pedagógica</div>'
        '</div>'
        '</section>'
    ),
    unsafe_allow_html=True,
)


st.markdown(
    (
        '<div class="section-card">'
        '<div class="section-kicker">Antes de comenzar</div>'
        '<div class="section-title">Obtén un mejor análisis</div>'
        '<div class="section-text">'
        'Una fotografía clara permite que Nova transcriba correctamente '
        'las expresiones y evite interpretar datos que no aparecen.'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

columnas_consejos = st.columns(3)

consejos = [
    (
        "💡",
        "Buena iluminación",
        "Evita sombras fuertes, reflejos y zonas demasiado oscuras.",
    ),
    (
        "📐",
        "Imagen derecha",
        "Toma la fotografía de frente y muestra el ejercicio completo.",
    ),
    (
        "🔍",
        "Texto legible",
        "No cortes fórmulas, exponentes, signos ni datos importantes.",
    ),
]

for columna, consejo in zip(columnas_consejos, consejos):
    with columna:
        st.markdown(
            (
                '<div class="tip-card">'
                f'<div class="tip-icon">{consejo[0]}</div>'
                f'<div class="tip-title">{consejo[1]}</div>'
                f'<div class="tip-text">{consejo[2]}</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )


st.markdown(
    (
        '<div class="section-card">'
        '<div class="section-kicker">Paso 1</div>'
        '<div class="section-title">Sube tu ejercicio</div>'
        '<div class="section-text">'
        'Formatos admitidos: PNG, JPG y JPEG. El tamaño máximo es 10 MB.'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

imagen = st.file_uploader(
    "Selecciona una imagen",
    type=["png", "jpg", "jpeg"],
    label_visibility="collapsed",
    key=f"imagen_uploader_{st.session_state['imagen_uploader_key']}",
)


if imagen is not None:
    imagen_bytes = imagen.getvalue()
    tamano_mb = len(imagen_bytes) / (1024 * 1024)

    nombre_anterior = st.session_state.get(
        "nombre_imagen_analizada"
    )

    if nombre_anterior and nombre_anterior != imagen.name:
        limpiar_analisis()

    if tamano_mb > 10:
        st.error(
            "La imagen supera el límite de 10 MB. "
            "Reduce su tamaño e inténtalo nuevamente."
        )
    else:
        col_imagen, col_datos = st.columns([1.55, 1])

        with col_imagen:
            st.image(
                imagen_bytes,
                caption="Vista previa del ejercicio",
                use_container_width=True,
            )

        with col_datos:
            st.markdown("### ✅ Imagen lista")
            st.write(f"**Archivo:** {imagen.name}")
            st.write(f"**Formato:** {imagen.type}")
            st.write(f"**Tamaño:** {tamano_mb:.2f} MB")
            st.info(
                "Nova analizará el contenido matemático necesario "
                "para ayudarte con el ejercicio."
            )

        if st.button(
            "🤖 Analizar ejercicio con Nova",
            use_container_width=True,
            disabled=not imagen_bytes,
        ):
            try:
                with st.spinner(
                    "Nova está observando y analizando la imagen..."
                ):
                    analisis = analizar_ejercicio_imagen(
                        imagen_bytes=imagen_bytes,
                        mime_type=imagen.type,
                        nivel=nivel,
                    )

                estado = extraer_estado_imagen(analisis)
                tema_detectado = extraer_tema_detectado(analisis)

                st.session_state["analisis_imagen"] = analisis
                st.session_state["estado_imagen"] = estado
                st.session_state["tema_imagen"] = tema_detectado
                st.session_state[
                    "nombre_imagen_analizada"
                ] = imagen.name

                if estado == "valida":
                    st.session_state["tema_actual"] = tema_detectado
                    registrar_pregunta(tema_detectado)

                st.rerun()

            except ValueError as error:
                st.error(
                    f"No se pudo procesar la imagen: {error}"
                )

            except RuntimeError as error:
                st.error(
                    f"No se pudo conectar con Gemini: {error}"
                )

            except Exception as error:
                st.error(
                    "Ocurrió un error inesperado durante el análisis."
                )
                with st.expander("Ver detalle técnico"):
                    st.code(str(error))


if st.session_state.get("analisis_imagen"):
    estado = st.session_state.get(
        "estado_imagen",
        "desconocido",
    )
    tema_detectado = st.session_state.get(
        "tema_imagen",
        "No identificado",
    )

    estados = {
        "valida": (
            "status-valid",
            f"✅ Ejercicio detectado · Tema: {tema_detectado}",
        ),
        "borrosa": (
            "status-blurry",
            "⚠️ La imagen no es suficientemente clara.",
        ),
        "no_matematica": (
            "status-invalid",
            "❌ No se detectó un ejercicio de Cálculo Diferencial.",
        ),
        "desconocido": (
            "status-neutral",
            "📌 Análisis completado.",
        ),
    }

    clase, mensaje = estados.get(
        estado,
        estados["desconocido"],
    )

    st.markdown(
        f'<div class="{clase}">{mensaje}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        (
            '<div class="section-card">'
            '<div class="section-kicker">Análisis de Nova</div>'
            '<div class="section-title">🧠 Explicación del ejercicio</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    analisis_limpio = limpiar_metadatos_analisis(
        st.session_state["analisis_imagen"]
    )

    renderizar_matematicas(analisis_limpio)

    if estado == "valida":
        st.info(
            "El tema detectado quedó guardado como tema actual. "
            "Puedes abrir Practicar para generar un ejercicio relacionado."
        )

    if st.button(
        "📷 Analizar otra imagen",
        use_container_width=True,
    ):
        preparar_nueva_imagen()
        st.rerun()


st.sidebar.markdown("## 📷 Análisis por imagen")
st.sidebar.info(
    f"""
🎯 **Nivel actual**

{nivel}

📚 **Tema detectado**

{st.session_state.get("tema_imagen", "Pendiente")}
"""
)