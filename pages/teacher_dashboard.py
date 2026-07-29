from io import BytesIO

import pandas as pd
import streamlit as st

from services.course_service import (
    crear_curso,
    listar_cursos_profesor,
)
from services.database_service import conexion_db


st.set_page_config(
    page_title="Panel del profesor | DERIVA AI",
    page_icon="👨‍🏫",
    layout="wide",
)


def obtener_reporte_curso(
    curso_id,
):
    with conexion_db() as conexion:
        filas = conexion.execute(
            """
            SELECT
                estudiantes.nombre,
                estudiantes.nivel,
                estudiantes.diagnostico_realizado,
                COALESCE(progreso_estudiantes.sesiones, 0) AS sesiones,
                COALESCE(progreso_estudiantes.preguntas, 0) AS preguntas_ia,
                COALESCE(progreso_estudiantes.ejercicios_generados, 0)
                    AS ejercicios_generados,
                COALESCE(progreso_estudiantes.ejercicios_revisados, 0)
                    AS ejercicios_revisados,
                COALESCE(progreso_estudiantes.respuestas_correctas, 0)
                    AS correctas,
                COALESCE(progreso_estudiantes.respuestas_parciales, 0)
                    AS parciales,
                COALESCE(progreso_estudiantes.respuestas_incorrectas, 0)
                    AS incorrectas,
                COALESCE(progreso_estudiantes.ultimo_tema, 'Ninguno')
                    AS ultimo_tema,
                estudiantes.ultima_actividad
            FROM estudiantes
            INNER JOIN inscripciones
                ON inscripciones.estudiante_id = estudiantes.id
            LEFT JOIN progreso_estudiantes
                ON progreso_estudiantes.estudiante_id = estudiantes.id
            WHERE inscripciones.curso_id = ?
              AND inscripciones.activo = 1
            ORDER BY estudiantes.nombre
            """,
            (curso_id,),
        ).fetchall()

    registros = []

    for fila in filas:
        dato = dict(
            fila
        )
        revisados = dato[
            "ejercicios_revisados"
        ]
        aciertos = (
            round(
                dato["correctas"]
                / revisados
                * 100
            )
            if revisados
            else 0
        )

        registros.append(
            {
                "Estudiante": dato["nombre"],
                "Nivel": dato["nivel"],
                "Diagnóstico": (
                    "Completado"
                    if dato["diagnostico_realizado"]
                    else "Pendiente"
                ),
                "Sesiones": dato["sesiones"],
                "Preguntas a Nova": dato["preguntas_ia"],
                "Ejercicios generados": dato["ejercicios_generados"],
                "Ejercicios revisados": revisados,
                "Correctas": dato["correctas"],
                "Parciales": dato["parciales"],
                "Incorrectas": dato["incorrectas"],
                "Aciertos (%)": aciertos,
                "Último tema": dato["ultimo_tema"],
                "Última actividad": dato["ultima_actividad"],
            }
        )

    return registros


def crear_excel(
    registros,
    curso,
    profesor_nombre,
):
    salida = BytesIO()

    columnas = [
        "Estudiante",
        "Nivel",
        "Diagnóstico",
        "Sesiones",
        "Preguntas a Nova",
        "Ejercicios generados",
        "Ejercicios revisados",
        "Correctas",
        "Parciales",
        "Incorrectas",
        "Aciertos (%)",
        "Último tema",
        "Última actividad",
    ]

    dataframe = pd.DataFrame(
        registros,
        columns=columnas,
    )

    resumen = pd.DataFrame(
        [
            {
                "Profesor": profesor_nombre,
                "Curso": curso["nombre"],
                "Sección": curso["seccion"],
                "Código": curso["codigo"],
                "Total de estudiantes": len(registros),
                "Preguntas a Nova": sum(
                    registro["Preguntas a Nova"]
                    for registro in registros
                ),
                "Ejercicios revisados": sum(
                    registro["Ejercicios revisados"]
                    for registro in registros
                ),
            }
        ]
    )

    with pd.ExcelWriter(
        salida,
        engine="openpyxl",
    ) as escritor:
        resumen.to_excel(
            escritor,
            sheet_name="Resumen",
            index=False,
        )

        dataframe.to_excel(
            escritor,
            sheet_name="Estudiantes",
            index=False,
        )

        libro = escritor.book

        for nombre_hoja in [
            "Resumen",
            "Estudiantes",
        ]:
            hoja = libro[
                nombre_hoja
            ]
            hoja.freeze_panes = "A2"

            for celda in hoja[1]:
                celda.font = celda.font.copy(
                    bold=True,
                    color="FFFFFF",
                )
                celda.fill = celda.fill.copy(
                    fill_type="solid",
                    fgColor="6879DF",
                )

            for columna in hoja.columns:
                ancho = max(
                    len(
                        str(
                            celda.value
                            if celda.value is not None
                            else ""
                        )
                    )
                    for celda in columna
                )

                hoja.column_dimensions[
                    columna[0].column_letter
                ].width = min(
                    ancho + 3,
                    32,
                )

    salida.seek(
        0
    )

    return salida.getvalue()


if st.session_state.get(
    "rol"
) != "profesor":
    st.warning(
        "Debes iniciar sesión como profesor."
    )
    st.stop()


profesor_id = st.session_state.get(
    "profesor_id"
)
profesor_nombre = st.session_state.get(
    "profesor_nombre",
    "Profesor",
)
profesor_correo = st.session_state.get(
    "profesor_correo",
    "",
)


st.markdown(
    """
<style>
.stApp {
    background:
        radial-gradient(circle at 90% 7%, rgba(235,213,255,.55), transparent 25%),
        radial-gradient(circle at 35% 0%, rgba(195,237,255,.56), transparent 31%),
        linear-gradient(135deg, #fbfdff 0%, #eef8ff 52%, #faf3ff 100%);
}

.block-container {
    max-width: 1280px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

.teacher-hero {
    padding: 32px 34px;
    margin-bottom: 24px;
    border-radius: 32px;
    background: linear-gradient(
        135deg,
        rgba(255,255,255,.90),
        rgba(216,242,255,.82),
        rgba(241,220,255,.80)
    );
    border: 1px solid rgba(255,255,255,.96);
    box-shadow: 0 20px 48px rgba(69,87,157,.12);
}

.teacher-kicker {
    color: #6879df;
    font-size: 13px;
    font-weight: 850;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.teacher-title {
    margin-top: 7px;
    color: #263c59;
    font-size: 40px;
    font-weight: 900;
}

.teacher-text {
    margin-top: 9px;
    color: #71839a;
    font-size: 16px;
    line-height: 1.65;
}

.course-code {
    padding: 20px 24px;
    border-radius: 24px;
    background: linear-gradient(
        135deg,
        rgba(218,243,255,.94),
        rgba(239,219,255,.94)
    );
    border: 1px solid rgba(255,255,255,.98);
    box-shadow: 0 14px 30px rgba(68,88,155,.10);
}

.course-code strong {
    color: #435bc7;
    font-size: 23px;
    letter-spacing: 1px;
}

div[data-testid="stMetric"] {
    padding: 19px;
    border-radius: 23px;
    background: rgba(255,255,255,.80);
    border: 1px solid rgba(255,255,255,.97);
    box-shadow: 0 12px 27px rgba(68,88,155,.09);
}

div[data-testid="stTabs"] {
    padding: 16px 18px 24px;
    border-radius: 28px;
    background: rgba(255,255,255,.72);
    border: 1px solid rgba(255,255,255,.96);
    box-shadow: 0 18px 42px rgba(68,88,155,.09);
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #5f6fda;
    font-weight: 850;
}

div.stDownloadButton > button,
div[data-testid="stFormSubmitButton"] > button {
    min-height: 49px;
    border-radius: 16px;
    border: 0;
    background: linear-gradient(135deg, #6f8bf7, #8f63ef);
    color: white;
    font-weight: 850;
}

.empty-report {
    padding: 30px;
    border-radius: 25px;
    text-align: center;
    background: linear-gradient(
        135deg,
        rgba(235,247,255,.90),
        rgba(248,237,255,.90)
    );
    border: 1px dashed rgba(110,126,218,.35);
    color: #66758e;
}
</style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""<section class="teacher-hero">
<div class="teacher-kicker">Panel docente y seguimiento académico</div>
<div class="teacher-title">👨‍🏫 Bienvenido, {profesor_nombre}</div>
<div class="teacher-text">Cuenta: {profesor_correo}<br>Consulta tus cursos, estudiantes, uso de Nova y reportes de progreso.</div>
</section>""",
    unsafe_allow_html=True,
)

ultimo_curso = st.session_state.get(
    "ultimo_curso_creado"
)

if ultimo_curso:
    st.success(
        "Curso creado correctamente."
    )

    st.markdown(
        f"""<div class="course-code">
Comparte este código con tus estudiantes:<br>
<strong>{ultimo_curso["codigo"]}</strong>
</div>""",
        unsafe_allow_html=True,
    )

    if st.button(
        "Entendido, continuar",
        use_container_width=True,
    ):
        st.session_state.pop(
            "ultimo_curso_creado",
            None,
        )
        st.rerun()

cursos = listar_cursos_profesor(
    profesor_id
)

if not cursos:
    st.info(
        "Tu cuenta todavía no tiene cursos."
    )

    with st.form(
        "primer_curso_profesor"
    ):
        nombre = st.text_input(
            "Nombre del curso",
            value="Cálculo Diferencial",
        )
        seccion = st.text_input(
            "Sección",
            placeholder="Ejemplo: A",
        )
        crear = st.form_submit_button(
            "Crear primer curso",
            use_container_width=True,
        )

    if crear:
        try:
            curso = crear_curso(
                profesor_id=profesor_id,
                nombre=nombre,
                seccion=seccion,
            )
            st.session_state[
                "ultimo_curso_creado"
            ] = curso
            st.rerun()

        except ValueError as error:
            st.error(
                str(error)
            )

    st.stop()

opciones = {
    f"{curso['nombre']} · Sección {curso['seccion']} · {curso['codigo']}": curso
    for curso in cursos
}

seleccion = st.selectbox(
    "Curso para consultar",
    options=list(
        opciones.keys()
    ),
)

curso = opciones[
    seleccion
]
registros = obtener_reporte_curso(
    curso["id"]
)

total_estudiantes = len(
    registros
)
diagnosticos = sum(
    1
    for registro in registros
    if registro["Diagnóstico"] == "Completado"
)
total_preguntas = sum(
    registro["Preguntas a Nova"]
    for registro in registros
)
total_revisados = sum(
    registro["Ejercicios revisados"]
    for registro in registros
)
total_correctas = sum(
    registro["Correctas"]
    for registro in registros
)
promedio_aciertos = (
    round(
        total_correctas
        / total_revisados
        * 100
    )
    if total_revisados
    else 0
)

st.markdown(
    f"""<div class="course-code">
📘 Código del curso: <strong>{curso["codigo"]}</strong>
</div>""",
    unsafe_allow_html=True,
)

st.write("")

col1, col2, col3, col4, col5 = st.columns(
    5
)
col1.metric(
    "Estudiantes",
    total_estudiantes,
)
col2.metric(
    "Diagnósticos",
    diagnosticos,
)
col3.metric(
    "Preguntas a Nova",
    total_preguntas,
)
col4.metric(
    "Ejercicios",
    total_revisados,
)
col5.metric(
    "Aciertos",
    f"{promedio_aciertos}%",
)

tab_reporte, tab_estudiantes, tab_cursos = st.tabs(
    [
        "📊 Reportes",
        "👥 Estudiantes",
        "📚 Mis cursos",
    ]
)

with tab_reporte:
    st.subheader(
        "Reporte académico del curso"
    )

    if not registros:
        st.markdown(
            """<div class="empty-report">
<h3>📊 El reporte está listo</h3>
<p>Aún no hay estudiantes inscritos. Las métricas comenzarán a actualizarse cuando un estudiante entre con el código del curso y utilice Nova.</p>
</div>""",
            unsafe_allow_html=True,
        )

    else:
        st.dataframe(
            registros,
            use_container_width=True,
            hide_index=True,
        )

    excel = crear_excel(
        registros=registros,
        curso=curso,
        profesor_nombre=profesor_nombre,
    )

    columnas_csv = [
        "Estudiante",
        "Nivel",
        "Diagnóstico",
        "Sesiones",
        "Preguntas a Nova",
        "Ejercicios generados",
        "Ejercicios revisados",
        "Correctas",
        "Parciales",
        "Incorrectas",
        "Aciertos (%)",
        "Último tema",
        "Última actividad",
    ]

    csv = pd.DataFrame(
        registros,
        columns=columnas_csv,
    ).to_csv(
        index=False,
    ).encode(
        "utf-8-sig"
    )

    col_excel, col_csv = st.columns(
        2
    )

    with col_excel:
        st.download_button(
            "📥 Descargar reporte Excel",
            data=excel,
            file_name=(
                f"reporte_{curso['nombre']}_"
                f"{curso['seccion']}.xlsx"
            ),
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            ),
            use_container_width=True,
        )

    with col_csv:
        st.download_button(
            "📄 Descargar reporte CSV",
            data=csv,
            file_name=(
                f"reporte_{curso['nombre']}_"
                f"{curso['seccion']}.csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )

with tab_estudiantes:
    st.subheader(
        "Estudiantes inscritos"
    )

    if registros:
        st.dataframe(
            registros,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(
            "Todavía no hay estudiantes inscritos en este curso."
        )

with tab_cursos:
    st.subheader(
        "Cursos del profesor"
    )

    tabla_cursos = [
        {
            "Curso": dato["nombre"],
            "Sección": dato["seccion"],
            "Código": dato["codigo"],
            "Estudiantes": dato["total_estudiantes"],
            "Estado": (
                "Activo"
                if dato["activo"]
                else "Inactivo"
            ),
        }
        for dato in cursos
    ]

    st.dataframe(
        tabla_cursos,
        use_container_width=True,
        hide_index=True,
    )

    with st.expander(
        "➕ Crear un nuevo curso"
    ):
        with st.form(
            "nuevo_curso_profesor"
        ):
            nuevo_nombre = st.text_input(
                "Nombre del nuevo curso",
                value="Cálculo Diferencial",
            )
            nueva_seccion = st.text_input(
                "Sección o grupo",
                placeholder="Ejemplo: B",
            )
            crear_nuevo = st.form_submit_button(
                "Crear nuevo curso",
                use_container_width=True,
            )

        if crear_nuevo:
            try:
                nuevo_curso = crear_curso(
                    profesor_id=profesor_id,
                    nombre=nuevo_nombre,
                    seccion=nueva_seccion,
                )
                st.session_state[
                    "ultimo_curso_creado"
                ] = nuevo_curso
                st.rerun()

            except ValueError as error:
                st.error(
                    str(error)
                )