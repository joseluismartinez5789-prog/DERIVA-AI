from pathlib import Path

import streamlit as st

from services.database_service import inicializar_base_datos
from services.diagnostic_service import diagnostico_completado


st.set_page_config(
    page_title="DERIVA AI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)


def cargar_css():
    """Carga el sistema visual global de DERIVA AI."""
    carpeta = Path("assets/styles")

    archivos = [
        "variables.css",
        "main.css",
        "sidebar.css",
        "header.css",
        "cards.css",
        "buttons.css",
        "chat.css",
        "animations.css",
        "responsive.css",
    ]

    bloques_css = []

    for archivo in archivos:
        ruta = carpeta / archivo

        if ruta.exists():
            bloques_css.append(
                ruta.read_text(
                    encoding="utf-8",
                )
            )

    if bloques_css:
        st.markdown(
            "<style>"
            + "\n".join(bloques_css)
            + "</style>",
            unsafe_allow_html=True,
        )


def cerrar_sesion():
    """Cierra la sesión interna y también la sesión de Google."""
    claves = [
        "rol",
        "estudiante_id",
        "estudiante_nombre",
        "estudiante_correo",
        "estudiante_tipo",
        "nivel",
        "diagnostico_completo",
        "curso_id",
        "curso_nombre",
        "curso_seccion",
        "profesor_nombre",
        "profesor_id",
        "profesor_correo",
        "ultimo_curso_creado",
    ]

    for clave in claves:
        st.session_state.pop(
            clave,
            None,
        )

    usuario_google_activo = bool(
        getattr(
            st.user,
            "email",
            None,
        )
    )

    if usuario_google_activo:
        st.logout()
    else:
        st.rerun()


def mostrar_marca_sidebar():
    st.sidebar.markdown(
        """
<div class="deriva-sidebar-brand">
    <div class="deriva-sidebar-logo">∂</div>
    <div class="deriva-sidebar-brand-copy">
        <strong>DERIVA AI</strong>
        <span>Aprende. Practica. Avanza.</span>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def mostrar_perfil_estudiante():
    nombre = st.session_state.get(
        "estudiante_nombre",
        "Estudiante",
    )
    tipo = st.session_state.get(
        "estudiante_tipo",
        "independiente",
    )
    curso = st.session_state.get(
        "curso_nombre"
    )
    seccion = st.session_state.get(
        "curso_seccion",
        "",
    )

    inicial = (
        nombre.strip()[:1].upper()
        if nombre.strip()
        else "E"
    )

    if tipo == "curso" and curso:
        detalle = curso

        if seccion:
            detalle += f" · Sección {seccion}"
    else:
        detalle = "Aprendizaje independiente"

    st.sidebar.markdown(
        f"""
<div class="deriva-sidebar-profile">
    <div class="deriva-profile-avatar">{inicial}</div>
    <div class="deriva-profile-copy">
        <span class="deriva-profile-role">ESTUDIANTE</span>
        <strong>{nombre}</strong>
        <small>{detalle}</small>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def mostrar_perfil_profesor():
    nombre = st.session_state.get(
        "profesor_nombre",
        "Profesor",
    )
    correo = st.session_state.get(
        "profesor_correo",
        "",
    )

    inicial = (
        nombre.strip()[:1].upper()
        if nombre.strip()
        else "P"
    )

    st.sidebar.markdown(
        f"""
<div class="deriva-sidebar-profile">
    <div class="deriva-profile-avatar">{inicial}</div>
    <div class="deriva-profile-copy">
        <span class="deriva-profile-role">PROFESOR</span>
        <strong>{nombre}</strong>
        <small>{correo}</small>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def mostrar_pie_sidebar():
    st.sidebar.markdown(
        """
<div class="deriva-sidebar-divider"></div>
<div class="deriva-sidebar-footer-copy">
    <span>Plataforma educativa inteligente</span>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.button(
        "↪ Cerrar sesión",
        on_click=cerrar_sesion,
        use_container_width=True,
        key="boton_cerrar_sesion_global",
    )


inicializar_base_datos()
cargar_css()

rol = st.session_state.get(
    "rol"
)

paginas = {
    "Acceso": [
        st.Page(
            "pages/access.py",
            title="Entrar",
            icon=":material/login:",
            default=True,
        )
    ]
}


if rol == "estudiante":
    diagnostico_realizado = diagnostico_completado()

    paginas = {
        "Principal": [
            st.Page(
                "pages/home.py",
                title="Inicio",
                icon=":material/home:",
                default=True,
            ),
            st.Page(
                "pages/diagnostic.py",
                title="Diagnóstico",
                icon=":material/assignment:",
            ),
            st.Page(
                "pages/learn.py",
                title="Aprender",
                icon=":material/menu_book:",
            ),
        ]
    }

    if diagnostico_realizado:
        paginas["Entrenamiento"] = [
            st.Page(
                "pages/chat.py",
                title="Nova",
                icon=":material/smart_toy:",
            ),
            st.Page(
                "pages/practice.py",
                title="Practicar",
                icon=":material/edit_note:",
            ),
            st.Page(
                "pages/image_solver.py",
                title="Resolver por imagen",
                icon=":material/photo_camera:",
            ),
            st.Page(
                "pages/progress.py",
                title="Mi progreso",
                icon=":material/monitoring:",
            ),
        ]

    mostrar_marca_sidebar()
    mostrar_perfil_estudiante()


elif rol == "profesor":
    paginas = {
        "Profesor": [
            st.Page(
                "pages/teacher_dashboard.py",
                title="Panel y reportes",
                icon=":material/dashboard:",
                default=True,
            ),
        ]
    }

    mostrar_marca_sidebar()
    mostrar_perfil_profesor()


if rol:
    mostrar_pie_sidebar()


navegacion = st.navigation(
    paginas,
    position="sidebar",
)

navegacion.run()