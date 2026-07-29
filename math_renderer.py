"""
Motor central de renderizado matemático de DERIVA AI.

Objetivos:
- Mantener el texto explicativo en Markdown.
- Renderizar fórmulas en línea y en bloque con LaTeX.
- Corregir delimitadores frecuentes producidos por modelos de IA.
- Proteger bloques de código para no modificar ejemplos de programación.
- Evitar conversiones agresivas que puedan alterar el significado.
"""

from __future__ import annotations

import re
from typing import Final

import streamlit as st


_BLOQUE_CODIGO: Final = re.compile(
    r"(```[\s\S]*?```|~~~[\s\S]*?~~~)",
    flags=re.MULTILINE,
)

_SUPERINDICES: Final = str.maketrans(
    {
        "⁰": "0",
        "¹": "1",
        "²": "2",
        "³": "3",
        "⁴": "4",
        "⁵": "5",
        "⁶": "6",
        "⁷": "7",
        "⁸": "8",
        "⁹": "9",
        "⁺": "+",
        "⁻": "-",
        "ⁿ": "n",
    }
)

_SUBINDICES: Final = str.maketrans(
    {
        "₀": "0",
        "₁": "1",
        "₂": "2",
        "₃": "3",
        "₄": "4",
        "₅": "5",
        "₆": "6",
        "₇": "7",
        "₈": "8",
        "₉": "9",
        "₊": "+",
        "₋": "-",
    }
)


def _proteger_codigo(texto: str) -> tuple[str, list[str]]:
    bloques: list[str] = []

    def reemplazar(coincidencia: re.Match[str]) -> str:
        indice = len(bloques)
        bloques.append(coincidencia.group(0))
        return f"@@DERIVA_CODIGO_{indice}@@"

    return _BLOQUE_CODIGO.sub(reemplazar, texto), bloques


def _restaurar_codigo(
    texto: str,
    bloques: list[str],
) -> str:
    for indice, bloque in enumerate(bloques):
        texto = texto.replace(
            f"@@DERIVA_CODIGO_{indice}@@",
            bloque,
        )

    return texto


def _convertir_unicode_matematico(texto: str) -> str:
    """
    Convierte notación Unicode frecuente solo cuando está unida
    a una variable o a un paréntesis matemático.

    Ejemplos:
    x²  -> x^{2}
    x₁  -> x_{1}
    """
    patron_super = re.compile(
        r"(?P<base>[A-Za-z0-9\)\]])"
        r"(?P<exp>[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻ⁿ]+)"
    )

    patron_sub = re.compile(
        r"(?P<base>[A-Za-z0-9\)\]])"
        r"(?P<sub>[₀₁₂₃₄₅₆₇₈₉₊₋]+)"
    )

    def super_reemplazo(coincidencia: re.Match[str]) -> str:
        exponente = coincidencia.group("exp").translate(
            _SUPERINDICES
        )
        return (
            f"{coincidencia.group('base')}"
            f"^{{{exponente}}}"
        )

    def sub_reemplazo(coincidencia: re.Match[str]) -> str:
        subindice = coincidencia.group("sub").translate(
            _SUBINDICES
        )
        return (
            f"{coincidencia.group('base')}"
            f"_{{{subindice}}}"
        )

    texto = patron_super.sub(super_reemplazo, texto)
    texto = patron_sub.sub(sub_reemplazo, texto)

    return texto


def _normalizar_delimitadores(texto: str) -> str:
    # Delimitadores LaTeX compatibles con Markdown/KaTeX de Streamlit.
    texto = re.sub(
        r"\\\[\s*([\s\S]*?)\s*\\\]",
        lambda m: f"\n\n$$\n{m.group(1).strip()}\n$$\n\n",
        texto,
    )

    texto = re.sub(
        r"\\\(\s*([\s\S]*?)\s*\\\)",
        lambda m: f"${m.group(1).strip()}$",
        texto,
    )

    # Gemini a veces devuelve delimitadores escapados doblemente.
    texto = texto.replace(r"\$\$", "$$")
    texto = texto.replace(r"\$", "$")

    # Evita bloques pegados al texto, que pueden impedir el renderizado.
    texto = re.sub(
        r"(?<!\n)\$\$",
        "\n\n$$",
        texto,
    )
    texto = re.sub(
        r"\$\$(?!\n)",
        "$$\n\n",
        texto,
    )

    return texto


def _normalizar_comandos_comunes(texto: str) -> str:
    reemplazos = {
        "Δ": r"\Delta ",
        "∞": r"\infty ",
        "→": r"\to ",
        "≤": r"\le ",
        "≥": r"\ge ",
        "≠": r"\ne ",
        "±": r"\pm ",
        "√": r"\sqrt",
        "·": r"\cdot ",
    }

    # Solo aplicamos estas sustituciones dentro de fórmulas delimitadas.
    patron_formula = re.compile(
        r"(\$\$[\s\S]*?\$\$|\$(?!\$).*?\$)",
        flags=re.MULTILINE,
    )

    def corregir_formula(
        coincidencia: re.Match[str],
    ) -> str:
        formula = coincidencia.group(0)

        for origen, destino in reemplazos.items():
            formula = formula.replace(
                origen,
                destino,
            )

        return formula

    return patron_formula.sub(
        corregir_formula,
        texto,
    )


def normalizar_latex(
    contenido: object,
) -> str:
    """
    Normaliza una respuesta mixta de Markdown + LaTeX sin modificar
    bloques de código.

    No intenta adivinar fórmulas completas sin delimitadores porque
    hacerlo podría cambiar frases normales o resultados del estudiante.
    """
    if contenido is None:
        return ""

    texto = str(contenido).replace(
        "\r\n",
        "\n",
    ).replace(
        "\r",
        "\n",
    )

    texto_protegido, bloques = _proteger_codigo(
        texto
    )

    texto_protegido = _normalizar_delimitadores(
        texto_protegido
    )

    texto_protegido = _convertir_unicode_matematico(
        texto_protegido
    )

    texto_protegido = _normalizar_comandos_comunes(
        texto_protegido
    )

    # Reduce espacios excesivos sin compactar el contenido.
    texto_protegido = re.sub(
        r"\n{4,}",
        "\n\n\n",
        texto_protegido,
    )

    return _restaurar_codigo(
        texto_protegido.strip(),
        bloques,
    )


def renderizar_matematicas(
    contenido: object,
) -> None:
    """
    Muestra texto, Markdown y LaTeX en Streamlit.

    Esta debe ser la función habitual para respuestas de Nova,
    teorías, ejercicios, correcciones y análisis por imagen.
    """
    texto = normalizar_latex(
        contenido
    )

    if not texto:
        return

    st.markdown(
        texto,
        unsafe_allow_html=False,
    )


def mostrar_formula(
    formula: object,
) -> None:
    """
    Muestra una fórmula aislada con st.latex.
    Úsala solo cuando el contenido sea exclusivamente matemático.
    """
    texto = str(
        formula or ""
    ).strip()

    if texto.startswith("$$") and texto.endswith("$$"):
        texto = texto[2:-2].strip()

    if texto.startswith(r"\[") and texto.endswith(r"\]"):
        texto = texto[2:-2].strip()

    st.latex(
        texto
    )
