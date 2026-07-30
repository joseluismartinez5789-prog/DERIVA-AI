"""Estado y navegación centralizados para DERIVA AI.

Este módulo no contiene elementos visuales. Su función es mantener un estado
consistente entre las páginas registradas con ``st.navigation``.
"""

from __future__ import annotations

from typing import Any, Iterable

import streamlit as st


ESTADO_INICIAL: dict[str, Any] = {
    # Sesión y perfil
    "rol": None,
    "nivel": "Sin diagnosticar",
    "diagnostico_completo": False,

    # Aprendizaje
    "tema_actual": "General",
    "teoria": None,
    "unidad_abierta": None,
    "desde_ruta_aprendizaje": False,

    # Nova
    "messages": [],
    "clave_bienvenida_nova": None,

    # Diagnóstico
    "evaluacion_iniciada": False,
    "pregunta_actual": 0,
    "respuesta_actual": None,
    "respuestas_diag": [],
    "resultado": None,
    "plan_estudios": [],
    "permitir_repetir_diagnostico": False,

    # Práctica
    "ejercicio_actual": None,
    "respuesta_estudiante": "",
}


CLAVES_SESION_USUARIO = {
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
}


def inicializar_estado() -> None:
    """Crea únicamente las claves ausentes sin sobrescribir datos existentes."""
    for clave, valor in ESTADO_INICIAL.items():
        if clave not in st.session_state:
            # Evita compartir listas o diccionarios mutables.
            if isinstance(valor, list):
                st.session_state[clave] = list(valor)
            elif isinstance(valor, dict):
                st.session_state[clave] = dict(valor)
            else:
                st.session_state[clave] = valor


def obtener(clave: str, predeterminado: Any = None) -> Any:
    return st.session_state.get(clave, predeterminado)


def establecer(clave: str, valor: Any) -> Any:
    st.session_state[clave] = valor
    return valor


def eliminar(*claves: str) -> None:
    for clave in claves:
        st.session_state.pop(clave, None)


def establecer_tema(tema: str, *, desde_ruta: bool | None = None) -> str:
    """Guarda un tema válido antes de cambiar de página."""
    tema_limpio = str(tema or "").strip() or "General"
    st.session_state["tema_actual"] = tema_limpio

    if desde_ruta is not None:
        st.session_state["desde_ruta_aprendizaje"] = bool(desde_ruta)

    return tema_limpio


def guardar_leccion(tema: str, teoria: str) -> None:
    establecer_tema(tema)
    st.session_state["teoria"] = teoria


def limpiar_leccion() -> None:
    eliminar("teoria")


def preparar_nova(tema: str, *, desde_ruta: bool = True) -> None:
    establecer_tema(tema, desde_ruta=desde_ruta)


def preparar_practica(tema: str) -> None:
    establecer_tema(tema)
    eliminar(
        "ejercicio_actual",
        "respuesta_estudiante",
        "retroalimentacion_actual",
    )


def navegar_a(
    pagina: str,
    *,
    tema: str | None = None,
    desde_ruta: bool | None = None,
) -> None:
    """Actualiza el estado y navega mediante el sistema oficial de Streamlit.

    La ruta debe corresponder a una página registrada en ``st.navigation``.
    ``st.switch_page`` detiene la ejecución actual, por lo que no debe
    colocarse ``st.rerun`` después de esta función.
    """
    if tema is not None:
        establecer_tema(tema, desde_ruta=desde_ruta)
    elif desde_ruta is not None:
        st.session_state["desde_ruta_aprendizaje"] = bool(desde_ruta)

    st.switch_page(pagina)


def limpiar_claves(claves: Iterable[str]) -> None:
    for clave in claves:
        st.session_state.pop(clave, None)


def cerrar_sesion_interna() -> None:
    """Elimina datos del usuario y estados temporales de la aplicación."""
    limpiar_claves(CLAVES_SESION_USUARIO)

    for clave in (
        "tema_actual",
        "teoria",
        "unidad_abierta",
        "desde_ruta_aprendizaje",
        "messages",
        "clave_bienvenida_nova",
        "ejercicio_actual",
        "respuesta_estudiante",
        "retroalimentacion_actual",
        "evaluacion_iniciada",
        "pregunta_actual",
        "respuesta_actual",
        "respuestas_diag",
        "resultado",
        "plan_estudios",
        "permitir_repetir_diagnostico",
    ):
        st.session_state.pop(clave, None)

    inicializar_estado()
