import streamlit as st


MAX_MENSAJES = 40


def inicializar_memoria():
    if "historial" not in st.session_state:
        st.session_state.historial = []


def guardar(role, contenido):
    inicializar_memoria()

    role_limpio = str(role).strip()
    contenido_limpio = str(contenido).strip()

    if not contenido_limpio:
        return

    st.session_state.historial.append(
        {
            "role": role_limpio,
            "content": contenido_limpio,
        }
    )

    st.session_state.historial = (
        st.session_state.historial[-MAX_MENSAJES:]
    )


def obtener():
    inicializar_memoria()

    return list(
        st.session_state.historial
    )


def limpiar():
    st.session_state.historial = []