import streamlit as st

from services.course_service import (
    crear_curso,
    crear_profesor,
    iniciar_sesion_profesor,
)
from services.student_service import (
    establecer_estudiante_independiente,
    registrar_o_ingresar_estudiante_google,
    vincular_estudiante_a_curso,
)


st.set_page_config(
    page_title="Acceso | DERIVA AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def guardar_sesion_estudiante(
    datos,
):
    estudiante = datos["estudiante"]
    curso = datos.get("curso")

    st.session_state["rol"] = "estudiante"
    st.session_state["estudiante_id"] = estudiante["id"]
    st.session_state["estudiante_nombre"] = estudiante["nombre"]
    st.session_state["estudiante_correo"] = estudiante["correo"]
    st.session_state["estudiante_tipo"] = estudiante["tipo"]

    st.session_state["nivel"] = estudiante.get(
        "nivel",
        "Sin diagnosticar",
    )

    st.session_state["diagnostico_completo"] = bool(
        estudiante.get(
            "diagnostico_realizado",
            0,
        )
    )

    if curso:
        st.session_state["curso_id"] = curso["id"]
        st.session_state["curso_nombre"] = curso["nombre"]
        st.session_state["curso_seccion"] = curso["seccion"]
        st.session_state["profesor_nombre"] = curso[
            "profesor_nombre"
        ]

    else:
        st.session_state["curso_id"] = None
        st.session_state["curso_nombre"] = None
        st.session_state["curso_seccion"] = None
        st.session_state["profesor_nombre"] = None


def guardar_sesion_profesor(
    profesor,
):
    st.session_state["rol"] = "profesor"
    st.session_state["profesor_id"] = profesor["id"]
    st.session_state["profesor_nombre"] = profesor["nombre"]
    st.session_state["profesor_correo"] = profesor["correo"]


st.markdown(
    """
<style>
:root {
    --deriva-blue: #5f7cf4;
    --deriva-violet: #8b5cf6;
    --deriva-dark: #24324a;
    --deriva-muted: #718096;
}

.stApp {
    background:
        radial-gradient(circle at 10% 8%, rgba(125,211,252,.34), transparent 29%),
        radial-gradient(circle at 88% 10%, rgba(196,181,253,.38), transparent 30%),
        linear-gradient(135deg, #f8fcff 0%, #eef7ff 46%, #f8f1ff 100%);
}

header[data-testid="stHeader"] {
    background: transparent;
}

section[data-testid="stSidebar"] {
    display: none;
}

.block-container {
    max-width: 1180px;
    padding-top: 2.7rem;
    padding-bottom: 4rem;
}

.deriva-shell {
    display: grid;
    grid-template-columns: 1.05fr .95fr;
    gap: 26px;
    align-items: stretch;
    margin-bottom: 26px;
}

.deriva-hero {
    min-height: 280px;
    padding: 36px;
    border-radius: 34px;
    background: linear-gradient(
        135deg,
        rgba(255,255,255,.94),
        rgba(224,242,254,.88) 46%,
        rgba(237,233,254,.90)
    );
    border: 1px solid rgba(255,255,255,.98);
    box-shadow: 0 26px 60px rgba(65,81,145,.14);
}

.deriva-brand {
    display: inline-flex;
    padding: 9px 15px;
    border-radius: 999px;
    background: rgba(255,255,255,.78);
    color: var(--deriva-blue);
    font-size: 14px;
    font-weight: 850;
    letter-spacing: .7px;
    text-transform: uppercase;
}

.deriva-title {
    margin-top: 22px;
    color: var(--deriva-dark);
    font-size: 50px;
    line-height: 1.05;
    font-weight: 900;
    letter-spacing: -1.6px;
}

.deriva-title span {
    background: linear-gradient(90deg, var(--deriva-blue), var(--deriva-violet));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.deriva-subtitle {
    margin-top: 17px;
    color: #65758d;
    font-size: 18px;
    line-height: 1.72;
}

.deriva-feature-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0,1fr));
    gap: 14px;
    margin-top: 28px;
}

.deriva-feature {
    padding: 17px 18px;
    border-radius: 20px;
    background: rgba(255,255,255,.80);
    border: 1px solid rgba(255,255,255,.96);
    color: #4e5f7a;
    font-size: 15px;
    font-weight: 800;
    box-shadow: 0 10px 22px rgba(72,90,150,.07);
}

.nova-card {
    min-height: 280px;
    padding: 34px;
    border-radius: 34px;
    background: linear-gradient(145deg, #5f7cf4, #8b5cf6);
    color: white;
    box-shadow: 0 26px 60px rgba(97,77,180,.25);
    position: relative;
    overflow: hidden;
}

.nova-card:before {
    content: "";
    position: absolute;
    width: 190px;
    height: 190px;
    top: -70px;
    right: -45px;
    border-radius: 50%;
    background: rgba(255,255,255,.15);
}

.nova-icon,
.nova-title,
.nova-text,
.nova-chip {
    position: relative;
    z-index: 1;
}

.nova-icon {
    font-size: 54px;
}

.nova-title {
    margin-top: 16px;
    font-size: 34px;
    font-weight: 900;
}

.nova-text {
    margin-top: 13px;
    color: rgba(255,255,255,.90);
    line-height: 1.68;
    font-size: 17px;
}

.nova-chip {
    display: inline-block;
    margin-top: 24px;
    padding: 11px 15px;
    border-radius: 999px;
    background: rgba(255,255,255,.17);
    border: 1px solid rgba(255,255,255,.26);
    font-weight: 850;
    font-size: 14px;
}

div[data-testid="stTabs"] {
    padding: 18px 20px 28px;
    border-radius: 32px;
    background: rgba(255,255,255,.86);
    border: 1px solid rgba(255,255,255,.98);
    box-shadow: 0 22px 50px rgba(65,81,145,.12);
}

div[data-baseweb="tab-list"] {
    gap: 12px;
    padding: 6px;
    border-radius: 20px;
    background: linear-gradient(
        135deg,
        rgba(225,239,255,.78),
        rgba(241,228,255,.78)
    );
}

button[data-baseweb="tab"] {
    height: 54px;
    border-radius: 16px;
    padding-left: 24px;
    padding-right: 24px;
    font-weight: 850;
    font-size: 15px;
    color: #68758c;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #6f8bf7, #8f63ef);
    color: white !important;
    box-shadow: 0 10px 22px rgba(91,88,184,.22);
}

div[data-testid="stForm"] {
    padding: 26px;
    border-radius: 26px;
    border: 1px solid rgba(220,228,241,.98);
    background: linear-gradient(
        145deg,
        rgba(255,255,255,.94),
        rgba(245,249,255,.90)
    );
    box-shadow: 0 13px 30px rgba(68,88,155,.07);
}

div[data-testid="stTextInput"] label {
    color: #43526b;
    font-weight: 850;
    font-size: 15px;
}

div[data-testid="stTextInput"] input {
    min-height: 52px;
    border-radius: 16px;
    background: rgba(243,247,253,.98);
    border: 1px solid #dfe7f2;
    color: #24324a;
    padding-left: 15px;
    font-size: 15px;
}

div[data-testid="stFormSubmitButton"] button {
    width: 100%;
    min-height: 54px;
    margin-top: 10px;
    border: 0;
    border-radius: 17px;
    background: linear-gradient(135deg, #6f8bf7, #8f63ef);
    color: white;
    font-size: 16px;
    font-weight: 900;
    box-shadow: 0 14px 28px rgba(96,83,190,.24);
}

h3 {
    color: #2f3f59;
    font-size: 31px !important;
    font-weight: 900 !important;
}

[data-testid="stCaptionContainer"] {
    color: #7d899b;
    font-size: 15px;
}



/* Selección inicial del tipo de estudiante */
.deriva-choice-heading {
    margin-top: 8px;
    margin-bottom: 18px;
    color: #2f3f59;
    font-size: 25px;
    font-weight: 900;
    text-align: center;
}

.deriva-choice-card {
    min-height: 220px;
    padding: 25px;
    border-radius: 25px;
    background: linear-gradient(
        145deg,
        rgba(255,255,255,.98),
        rgba(242,247,255,.96)
    );
    border: 1px solid rgba(215,225,241,.98);
    box-shadow: 0 14px 32px rgba(68,88,155,.10);
    margin-bottom: 12px;
}

.deriva-choice-icon {
    font-size: 40px;
    line-height: 1;
}

.deriva-choice-title {
    margin-top: 16px;
    color: #2f3f59;
    font-size: 22px;
    font-weight: 900;
}

.deriva-choice-text {
    margin-top: 10px;
    color: #6d7b91;
    font-size: 15px;
    line-height: 1.65;
}

.deriva-choice-tag {
    display: inline-block;
    margin-top: 17px;
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(111,139,247,.12);
    color: #6078dc;
    font-size: 13px;
    font-weight: 850;
}

/* Botones principales fuera de formularios, incluido Google */
div[data-testid="stButton"] button[kind="primary"],
div[data-testid="stButton"] button[data-testid="stBaseButton-primary"] {
    width: 100%;
    min-height: 64px;
    border: 0 !important;
    border-radius: 18px !important;
    background: linear-gradient(135deg, #6f8bf7, #a855f7) !important;
    color: #ffffff !important;
    font-size: 20px !important;
    font-weight: 900 !important;
    letter-spacing: .2px;
    box-shadow: 0 14px 28px rgba(96,83,190,.28);
    transition: transform .2s ease, box-shadow .2s ease;
}

div[data-testid="stButton"] button[kind="primary"]:hover,
div[data-testid="stButton"] button[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 18px 36px rgba(96,83,190,.36);
    color: #ffffff !important;
}

div[data-testid="stButton"] button[kind="primary"] *,
div[data-testid="stButton"] button[data-testid="stBaseButton-primary"] * {
    color: #ffffff !important;
    font-size: 20px !important;
    font-weight: 900 !important;
}

/* Refuerzo específico para el texto interno del botón */
div[data-testid="stButton"] button[kind="primary"] p,
div[data-testid="stButton"] button[kind="primary"] span,
div[data-testid="stButton"] button[data-testid="stBaseButton-primary"] p,
div[data-testid="stButton"] button[data-testid="stBaseButton-primary"] span {
    color: #ffffff !important;
    opacity: 1 !important;
}

@media (max-width: 900px) {
    .deriva-shell {
        grid-template-columns: 1fr;
    }

    .deriva-title {
        font-size: 40px;
    }

    .deriva-feature-grid {
        grid-template-columns: 1fr;
    }
}
</style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """<div class="deriva-shell">
<section class="deriva-hero">
<div class="deriva-brand">✦ Plataforma educativa inteligente</div>
<div class="deriva-title">Aprende cálculo con <span>DERIVA AI</span></div>
<div class="deriva-subtitle">Una experiencia personalizada para aprender, practicar, resolver ejercicios y recibir acompañamiento de Nova, tu tutora de inteligencia artificial.</div>
<div class="deriva-feature-grid">
<div class="deriva-feature">🧠 Diagnóstico adaptativo</div>
<div class="deriva-feature">🤖 Tutoría con Nova</div>
<div class="deriva-feature">📷 Resolución por imagen</div>
<div class="deriva-feature">📊 Seguimiento del progreso</div>
</div>
</section>
<aside class="nova-card">
<div class="nova-icon">✨</div>
<div class="nova-title">Conoce a Nova</div>
<div class="nova-text">Nova analiza tu nivel, explica paso a paso y adapta cada respuesta para ayudarte a comprender el cálculo diferencial de una forma clara y cercana.</div>
<div class="nova-chip">Impulsada por inteligencia artificial</div>
</aside>
</div>""",
    unsafe_allow_html=True,
)

tab_estudiante, tab_profesor = st.tabs(
    [
        "🎓 Acceso estudiante",
        "👨‍🏫 Acceso profesor",
    ]
)

with tab_estudiante:
    st.subheader(
        "Acceso del estudiante"
    )

    st.caption(
        "Inicia sesión con tu cuenta de Google para conservar "
        "tu diagnóstico, nivel y progreso."
    )

    usuario_google_activo = bool(
        getattr(
            st.user,
            "email",
            None,
        )
    )

    if not usuario_google_activo:
        st.info(
            "Tu correo de Google se utilizará únicamente para "
            "identificar tu cuenta dentro de DERIVA AI."
        )

        if st.button(
            "🔵  CONTINUAR CON GOOGLE",
            use_container_width=True,
            type="primary",
            key="boton_login_google",
        ):
            st.login("google")

    else:
        nombre_google = str(
            getattr(
                st.user,
                "name",
                "",
            )
            or ""
        ).strip()

        correo_google = str(
            getattr(
                st.user,
                "email",
                "",
            )
            or ""
        ).strip().lower()

        if not correo_google:
            st.error(
                "Google no devolvió un correo válido para esta cuenta."
            )

        else:
            if not nombre_google:
                nombre_google = correo_google.split("@")[0]

            st.success(
                f"Cuenta de Google verificada: {correo_google}"
            )

            try:
                datos_google = (
                    registrar_o_ingresar_estudiante_google(
                        nombre=nombre_google,
                        correo=correo_google,
                    )
                )

                estudiante_google = datos_google["estudiante"]
                curso_google = datos_google["curso"]
                es_nuevo_google = bool(datos_google.get("es_nuevo", False))

                st.markdown(
                    f"""
                    **Nombre:** {estudiante_google["nombre"]}  
                    **Correo:** {estudiante_google["correo"]}
                    """
                )

                if curso_google:
                    guardar_sesion_estudiante(
                        datos_google
                    )

                    st.success(
                        "Tu cuenta y tu curso fueron recuperados."
                    )

                    st.rerun()

                elif (
                    estudiante_google.get("tipo") == "independiente"
                    and not es_nuevo_google
                ):
                    guardar_sesion_estudiante(
                        datos_google
                    )

                    st.success(
                        "Tu cuenta independiente fue recuperada."
                    )

                    st.rerun()

                else:
                    modo_nuevo_estudiante = st.session_state.get(
                        "modo_nuevo_estudiante"
                    )

                    if modo_nuevo_estudiante == "curso":
                        st.markdown(
                            '<div class="deriva-choice-heading">'
                            'Entrar a un curso'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                        st.info(
                            "Escribe el código que te proporcionó tu profesor."
                        )

                        with st.form(
                            "formulario_vincular_curso_google"
                        ):
                            codigo_google = st.text_input(
                                "Código del curso",
                                placeholder="DERIVA-ABC123",
                            )

                            vincular = st.form_submit_button(
                                "Vincular mi cuenta al curso",
                                use_container_width=True,
                            )

                        if vincular:
                            try:
                                datos_vinculados = (
                                    vincular_estudiante_a_curso(
                                        estudiante_id=estudiante_google[
                                            "id"
                                        ],
                                        codigo_curso=codigo_google,
                                    )
                                )

                                guardar_sesion_estudiante(
                                    datos_vinculados
                                )

                                st.session_state.pop(
                                    "modo_nuevo_estudiante",
                                    None,
                                )

                                st.success(
                                    "Tu cuenta fue vinculada correctamente."
                                )

                                st.rerun()

                            except ValueError as error:
                                st.error(
                                    str(error)
                                )

                            except Exception as error:
                                st.error(
                                    "No se pudo vincular la cuenta al curso."
                                )

                                with st.expander(
                                    "Ver detalle técnico"
                                ):
                                    st.code(
                                        str(error)
                                    )

                        if st.button(
                            "← Volver a las opciones",
                            use_container_width=True,
                            key="volver_opciones_estudiante",
                        ):
                            st.session_state.pop(
                                "modo_nuevo_estudiante",
                                None,
                            )
                            st.rerun()

                    else:
                        st.markdown(
                            '<div class="deriva-choice-heading">'
                            '¿Cómo deseas aprender?'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                        columna_independiente, columna_curso = st.columns(
                            2,
                            gap="large",
                        )

                        with columna_independiente:
                            st.markdown(
                                """
<div class="deriva-choice-card">
    <div class="deriva-choice-icon">🎓</div>
    <div class="deriva-choice-title">Aprender por mi cuenta</div>
    <div class="deriva-choice-text">
        Estudia Cálculo Diferencial a tu ritmo, realiza el
        diagnóstico y utiliza a Nova como tu tutora personal.
    </div>
    <div class="deriva-choice-tag">Sin código de curso</div>
</div>
                                """,
                                unsafe_allow_html=True,
                            )

                            comenzar_independiente = st.button(
                                "Comenzar mi aprendizaje",
                                use_container_width=True,
                                type="primary",
                                key="entrar_independiente_google",
                            )

                        with columna_curso:
                            st.markdown(
                                """
<div class="deriva-choice-card">
    <div class="deriva-choice-icon">👨‍🏫</div>
    <div class="deriva-choice-title">Entrar a un curso</div>
    <div class="deriva-choice-text">
        Únete al grupo de un profesor mediante un código y
        permite que pueda acompañar tu progreso académico.
    </div>
    <div class="deriva-choice-tag">Necesita código</div>
</div>
                                """,
                                unsafe_allow_html=True,
                            )

                            entrar_curso = st.button(
                                "Tengo un código de curso",
                                use_container_width=True,
                                key="elegir_curso_google",
                            )

                        if comenzar_independiente:
                            try:
                                estudiante_independiente = (
                                    establecer_estudiante_independiente(
                                        estudiante_google["id"]
                                    )
                                )

                                datos_independientes = {
                                    "estudiante": estudiante_independiente,
                                    "curso": None,
                                }

                                guardar_sesion_estudiante(
                                    datos_independientes
                                )

                                st.success(
                                    "Tu cuenta independiente quedó configurada."
                                )

                                st.rerun()

                            except ValueError as error:
                                st.error(
                                    str(error)
                                )

                            except Exception as error:
                                st.error(
                                    "No se pudo configurar la cuenta independiente."
                                )

                                with st.expander(
                                    "Ver detalle técnico"
                                ):
                                    st.code(
                                        str(error)
                                    )

                        if entrar_curso:
                            st.session_state[
                                "modo_nuevo_estudiante"
                            ] = "curso"
                            st.rerun()

            except ValueError as error:
                st.error(
                    str(error)
                )

            except Exception as error:
                st.error(
                    "No se pudo recuperar la cuenta del estudiante."
                )

                with st.expander(
                    "Ver detalle técnico"
                ):
                    st.code(
                        str(error)
                    )

        if st.button(
            "Cerrar sesión de Google",
            use_container_width=True,
            key="cerrar_google_acceso",
        ):
            st.logout()

with tab_profesor:
    modo_profesor = st.radio(
        "Selecciona una opción",
        [
            "Iniciar sesión",
            "Crear cuenta docente",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    if modo_profesor == "Iniciar sesión":
        st.subheader(
            "Volver al panel docente"
        )

        st.caption(
            "Usa el mismo correo con el que registraste tu cuenta."
        )

        with st.form(
            "formulario_login_profesor"
        ):
            correo_login = st.text_input(
                "Correo electrónico",
                placeholder="profesor@correo.com",
            )

            entrar_profesor = st.form_submit_button(
                "Abrir mis cursos y reportes",
                use_container_width=True,
            )

        if entrar_profesor:
            try:
                profesor = iniciar_sesion_profesor(
                    correo_login
                )

                guardar_sesion_profesor(
                    profesor
                )

                st.rerun()

            except ValueError as error:
                st.error(
                    str(error)
                )

            except Exception as error:
                st.error(
                    "No se pudo iniciar la sesión."
                )

                with st.expander(
                    "Ver detalle técnico"
                ):
                    st.code(
                        str(error)
                    )

    else:
        st.subheader(
            "Crear cuenta y primer curso"
        )

        st.caption(
            "El correo será obligatorio y no podrá repetirse."
        )

        with st.form(
            "formulario_nuevo_profesor"
        ):
            nombre_profesor = st.text_input(
                "Nombre del profesor",
                placeholder="Ejemplo: Prof. Carlos Pérez",
            )

            correo_profesor = st.text_input(
                "Correo electrónico",
                placeholder="profesor@correo.com",
            )

            nombre_curso = st.text_input(
                "Nombre del curso",
                value="Cálculo Diferencial",
            )

            seccion_curso = st.text_input(
                "Sección o grupo",
                placeholder="Ejemplo: A",
            )

            crear = st.form_submit_button(
                "Crear cuenta y curso",
                use_container_width=True,
            )

        if crear:
            try:
                profesor = crear_profesor(
                    nombre=nombre_profesor,
                    correo=correo_profesor,
                )

                curso = crear_curso(
                    profesor_id=profesor["id"],
                    nombre=nombre_curso,
                    seccion=seccion_curso,
                )

                guardar_sesion_profesor(
                    profesor
                )

                st.session_state[
                    "ultimo_curso_creado"
                ] = curso

                st.rerun()

            except ValueError as error:
                st.error(
                    str(error)
                )

            except Exception as error:
                st.error(
                    "No se pudo crear la cuenta docente."
                )

                with st.expander(
                    "Ver detalle técnico"
                ):
                    st.code(
                        str(error)
                    )