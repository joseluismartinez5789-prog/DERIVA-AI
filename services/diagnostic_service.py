import json
import streamlit as st

from services.database_service import conexion_db


NIVELES_VALIDOS = {
    "Básico",
    "Intermedio",
    "Avanzado",
}


def _cargar_json(valor, valor_por_defecto):
    if valor is None or valor == "":
        return valor_por_defecto

    try:
        return json.loads(valor)
    except (TypeError, json.JSONDecodeError):
        return valor_por_defecto


def obtener_nivel():
    estudiante_id = st.session_state.get(
        "estudiante_id"
    )

    if not estudiante_id:
        return "Sin diagnosticar"

    with conexion_db() as conexion:
        fila = conexion.execute(
            """
            SELECT nivel
            FROM estudiantes
            WHERE id = ?
            """,
            (estudiante_id,),
        ).fetchone()

    if not fila:
        return "Sin diagnosticar"

    return fila["nivel"]


def diagnostico_completado():
    estudiante_id = st.session_state.get(
        "estudiante_id"
    )

    if not estudiante_id:
        return False

    with conexion_db() as conexion:
        fila = conexion.execute(
            """
            SELECT diagnostico_realizado
            FROM estudiantes
            WHERE id = ?
            """,
            (estudiante_id,),
        ).fetchone()

    return bool(
        fila
        and fila["diagnostico_realizado"]
    )


def guardar_resultado_diagnostico(
    estudiante_id,
    nivel,
    puntaje,
    total,
    respuestas,
    fortalezas,
    mejorar,
    plan_estudios,
    siguiente_area=None,
    siguiente_leccion=None,
    detalle_respuestas=None,
):
    if not estudiante_id:
        raise ValueError(
            "No se encontró el estudiante en la sesión."
        )

    nivel = str(nivel).strip()

    if nivel not in NIVELES_VALIDOS:
        raise ValueError(
            "El nivel del diagnóstico no es válido."
        )

    try:
        puntaje = int(puntaje)
        total = int(total)
    except (TypeError, ValueError) as error:
        raise ValueError(
            "El puntaje o el total del diagnóstico no es válido."
        ) from error

    if total <= 0:
        raise ValueError(
            "El total de preguntas debe ser mayor que cero."
        )

    if puntaje < 0 or puntaje > total:
        raise ValueError(
            "El puntaje está fuera del rango permitido."
        )

    respuestas_json = json.dumps(
        respuestas or {},
        ensure_ascii=False,
    )
    detalle_json = json.dumps(
        detalle_respuestas or [],
        ensure_ascii=False,
    )
    fortalezas_json = json.dumps(
        fortalezas or [],
        ensure_ascii=False,
    )
    mejorar_json = json.dumps(
        mejorar or [],
        ensure_ascii=False,
    )
    plan_json = json.dumps(
        plan_estudios or [],
        ensure_ascii=False,
    )

    with conexion_db() as conexion:
        estudiante = conexion.execute(
            """
            SELECT id
            FROM estudiantes
            WHERE id = ?
            LIMIT 1
            """,
            (estudiante_id,),
        ).fetchone()

        if not estudiante:
            raise ValueError(
                "No se encontró el estudiante en la base de datos."
            )

        conexion.execute(
            """
            INSERT INTO diagnosticos (
                estudiante_id,
                puntaje,
                total,
                nivel,
                respuestas,
                detalle_respuestas,
                fortalezas,
                mejorar,
                plan_estudios,
                siguiente_area,
                siguiente_leccion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(estudiante_id)
            DO UPDATE SET
                puntaje = excluded.puntaje,
                total = excluded.total,
                nivel = excluded.nivel,
                respuestas = excluded.respuestas,
                detalle_respuestas = excluded.detalle_respuestas,
                fortalezas = excluded.fortalezas,
                mejorar = excluded.mejorar,
                plan_estudios = excluded.plan_estudios,
                siguiente_area = excluded.siguiente_area,
                siguiente_leccion = excluded.siguiente_leccion,
                actualizado_en = CURRENT_TIMESTAMP
            """,
            (
                estudiante_id,
                puntaje,
                total,
                nivel,
                respuestas_json,
                detalle_json,
                fortalezas_json,
                mejorar_json,
                plan_json,
                siguiente_area,
                siguiente_leccion,
            ),
        )

        conexion.execute(
            """
            UPDATE estudiantes
            SET
                nivel = ?,
                diagnostico_realizado = 1,
                ultima_actividad = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                nivel,
                estudiante_id,
            ),
        )

    return obtener_ultimo_diagnostico(
        estudiante_id
    )


def obtener_ultimo_diagnostico(
    estudiante_id=None,
):
    if estudiante_id is None:
        estudiante_id = st.session_state.get(
            "estudiante_id"
        )

    if not estudiante_id:
        return None

    with conexion_db() as conexion:
        fila = conexion.execute(
            """
            SELECT
                id,
                estudiante_id,
                puntaje,
                total,
                nivel,
                respuestas,
                detalle_respuestas,
                fortalezas,
                mejorar,
                plan_estudios,
                siguiente_area,
                siguiente_leccion,
                realizado_en,
                actualizado_en
            FROM diagnosticos
            WHERE estudiante_id = ?
            LIMIT 1
            """,
            (estudiante_id,),
        ).fetchone()

    if not fila:
        return None

    datos = dict(fila)

    datos["respuestas"] = _cargar_json(
        datos.get("respuestas"),
        {},
    )
    datos["detalle_respuestas"] = _cargar_json(
        datos.get("detalle_respuestas"),
        [],
    )
    datos["fortalezas"] = _cargar_json(
        datos.get("fortalezas"),
        [],
    )
    datos["mejorar"] = _cargar_json(
        datos.get("mejorar"),
        [],
    )
    datos["plan_estudios"] = _cargar_json(
        datos.get("plan_estudios"),
        [],
    )

    return datos