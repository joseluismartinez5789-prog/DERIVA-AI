import re

import streamlit as st


_BLOQUE_LATEX = re.compile(
    r"\$\$(.*?)\$\$|\\\[(.*?)\\\]",
    flags=re.DOTALL,
)


def normalizar_latex(texto):
    """
    Normaliza delimitadores matemáticos producidos por la IA.

    Convierte:
    - \\[ ... \\] en $$ ... $$
    - elimina bloques Markdown que envuelven fórmulas
    - conserva matemáticas en línea con $...$ o \\(...\\)
    """
    if texto is None:
        return ""

    resultado = str(texto).replace("\r\n", "\n")

    resultado = re.sub(
        r"```(?:latex|tex|math)?\s*(.*?)```",
        lambda coincidencia: coincidencia.group(1).strip(),
        resultado,
        flags=re.DOTALL | re.IGNORECASE,
    )

    resultado = re.sub(
        r"\\\[(.*?)\\\]",
        lambda coincidencia: "$$\n"
        + coincidencia.group(1).strip()
        + "\n$$",
        resultado,
        flags=re.DOTALL,
    )

    resultado = re.sub(
        r"\\\((.*?)\\\)",
        lambda coincidencia: "$"
        + coincidencia.group(1).strip()
        + "$",
        resultado,
        flags=re.DOTALL,
    )

    resultado = re.sub(
        r"\n{3,}",
        "\n\n",
        resultado,
    )

    return resultado.strip()


def renderizar_matematicas(
    contenido,
):
    """
    Renderiza texto y fórmulas de forma uniforme en Streamlit.

    Úsala en lugar de st.write() para respuestas de Nova,
    ejercicios, retroalimentaciones y soluciones por imagen.
    """
    texto = normalizar_latex(
        contenido
    )

    if not texto:
        return

    posicion = 0

    for coincidencia in _BLOQUE_LATEX.finditer(
        texto
    ):
        texto_anterior = texto[
            posicion:coincidencia.start()
        ].strip()

        if texto_anterior:
            st.markdown(
                texto_anterior
            )

        formula = (
            coincidencia.group(1)
            or coincidencia.group(2)
            or ""
        ).strip()

        if formula:
            st.latex(
                formula
            )

        posicion = coincidencia.end()

    texto_final = texto[
        posicion:
    ].strip()

    if texto_final:
        st.markdown(
            texto_final
        )


def mostrar_formula(
    formula,
):
    """Muestra una fórmula individual sin delimitadores."""
    formula_limpia = str(
        formula
    ).strip()

    formula_limpia = re.sub(
        r"^\$\$|\$\$$",
        "",
        formula_limpia,
    ).strip()

    formula_limpia = re.sub(
        r"^\\\[|\\\]$",
        "",
        formula_limpia,
    ).strip()

    st.latex(
        formula_limpia
    )