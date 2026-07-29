import re
import sqlite3
import uuid

from services.course_service import (
    obtener_curso_por_codigo,
)
from services.database_service import conexion_db


PATRON_CORREO = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


def _normalizar_nombre(
    nombre,
):
    return " ".join(
        str(nombre).strip().split()
    )


def _normalizar_correo(
    correo,
):
    return str(
        correo
    ).strip().lower()


def _validar_nombre(
    nombre,
):
    nombre = _normalizar_nombre(
        nombre
    )

    if len(nombre) < 3:
        raise ValueError(
            "No se pudo obtener un nombre válido del estudiante."
        )

    return nombre


def _validar_correo(
    correo,
):
    correo = _normalizar_correo(
        correo
    )

    if not correo:
        raise ValueError(
            "No se pudo obtener el correo de la cuenta de Google."
        )

    if not PATRON_CORREO.match(
        correo
    ):
        raise ValueError(
            "El correo obtenido no es válido."
        )

    return correo


def _crear_progreso_si_falta(
    conexion,
    estudiante_id,
):
    conexion.execute(
        """
        INSERT OR IGNORE INTO progreso_estudiantes (
            estudiante_id
        )
        VALUES (?)
        """,
        (estudiante_id,),
    )


def _actualizar_ultima_actividad(
    conexion,
    estudiante_id,
):
    conexion.execute(
        """
        UPDATE estudiantes
        SET ultima_actividad = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (estudiante_id,),
    )


def obtener_estudiante_por_correo(
    correo,
):
    correo = _validar_correo(
        correo
    )

    with conexion_db() as conexion:
        fila = conexion.execute(
            """
            SELECT
                id,
                identificador,
                nombre,
                correo,
                tipo,
                nivel,
                diagnostico_realizado,
                creado_en,
                ultima_actividad
            FROM estudiantes
            WHERE LOWER(TRIM(correo)) = ?
            LIMIT 1
            """,
            (correo,),
        ).fetchone()

    return dict(
        fila
    ) if fila else None


def obtener_inscripcion_activa_estudiante(
    estudiante_id,
):
    with conexion_db() as conexion:
        fila = conexion.execute(
            """
            SELECT
                cursos.id,
                cursos.nombre,
                cursos.seccion,
                cursos.codigo,
                cursos.activo,
                cursos.creado_en,
                profesores.id AS profesor_id,
                profesores.nombre AS profesor_nombre,
                profesores.correo AS profesor_correo
            FROM inscripciones
            INNER JOIN cursos
                ON cursos.id = inscripciones.curso_id
            INNER JOIN profesores
                ON profesores.id = cursos.profesor_id
            WHERE inscripciones.estudiante_id = ?
              AND inscripciones.activo = 1
              AND cursos.activo = 1
            ORDER BY inscripciones.inscrito_en DESC
            LIMIT 1
            """,
            (estudiante_id,),
        ).fetchone()

    return dict(
        fila
    ) if fila else None


def registrar_o_ingresar_estudiante_google(
    nombre,
    correo,
):
    nombre = _validar_nombre(
        nombre
    )

    correo = _validar_correo(
        correo
    )

    es_nuevo = False

    with conexion_db() as conexion:
        estudiante = conexion.execute(
            """
            SELECT
                id,
                identificador,
                nombre,
                correo,
                tipo,
                nivel,
                diagnostico_realizado,
                creado_en,
                ultima_actividad
            FROM estudiantes
            WHERE LOWER(TRIM(correo)) = ?
            LIMIT 1
            """,
            (correo,),
        ).fetchone()

        if estudiante:
            estudiante_id = estudiante["id"]

            conexion.execute(
                """
                UPDATE estudiantes
                SET
                    nombre = ?,
                    ultima_actividad = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    nombre,
                    estudiante_id,
                ),
            )

            _crear_progreso_si_falta(
                conexion,
                estudiante_id,
            )

            fila_actualizada = conexion.execute(
                """
                SELECT
                    id,
                    identificador,
                    nombre,
                    correo,
                    tipo,
                    nivel,
                    diagnostico_realizado,
                    creado_en,
                    ultima_actividad
                FROM estudiantes
                WHERE id = ?
                """,
                (estudiante_id,),
            ).fetchone()

            datos_estudiante = dict(
                fila_actualizada
            )

        else:
            es_nuevo = True

            identificador = str(
                uuid.uuid4()
            )

            try:
                cursor = conexion.execute(
                    """
                    INSERT INTO estudiantes (
                        identificador,
                        nombre,
                        correo,
                        tipo
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        identificador,
                        nombre,
                        correo,
                        "independiente",
                    ),
                )

            except sqlite3.IntegrityError as error:
                raise ValueError(
                    "Ya existe una cuenta estudiantil con este correo."
                ) from error

            estudiante_id = cursor.lastrowid

            _crear_progreso_si_falta(
                conexion,
                estudiante_id,
            )

            fila_nueva = conexion.execute(
                """
                SELECT
                    id,
                    identificador,
                    nombre,
                    correo,
                    tipo,
                    nivel,
                    diagnostico_realizado,
                    creado_en,
                    ultima_actividad
                FROM estudiantes
                WHERE id = ?
                """,
                (estudiante_id,),
            ).fetchone()

            datos_estudiante = dict(
                fila_nueva
            )

    curso = obtener_inscripcion_activa_estudiante(
        datos_estudiante["id"]
    )

    return {
        "estudiante": datos_estudiante,
        "curso": curso,
        "es_nuevo": es_nuevo,
    }


def vincular_estudiante_a_curso(
    estudiante_id,
    codigo_curso,
):
    codigo_curso = str(
        codigo_curso
    ).strip().upper()

    curso = obtener_curso_por_codigo(
        codigo_curso
    )

    if not curso:
        raise ValueError(
            "El código del curso no existe o está desactivado."
        )

    with conexion_db() as conexion:
        estudiante = conexion.execute(
            """
            SELECT
                id,
                nombre,
                correo
            FROM estudiantes
            WHERE id = ?
            LIMIT 1
            """,
            (estudiante_id,),
        ).fetchone()

        if not estudiante:
            raise ValueError(
                "No se encontró el estudiante."
            )

        conexion.execute(
            """
            INSERT INTO inscripciones (
                estudiante_id,
                curso_id,
                activo
            )
            VALUES (?, ?, 1)
            ON CONFLICT (
                estudiante_id,
                curso_id
            )
            DO UPDATE SET
                activo = 1
            """,
            (
                estudiante_id,
                curso["id"],
            ),
        )

        conexion.execute(
            """
            UPDATE estudiantes
            SET
                tipo = 'curso',
                ultima_actividad = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (estudiante_id,),
        )

        _crear_progreso_si_falta(
            conexion,
            estudiante_id,
        )

    estudiante = obtener_estudiante(
        estudiante_id
    )

    return {
        "estudiante": estudiante,
        "curso": curso,
    }


def establecer_estudiante_independiente(
    estudiante_id,
):
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
                "No se encontró el estudiante."
            )

        conexion.execute(
            """
            UPDATE inscripciones
            SET activo = 0
            WHERE estudiante_id = ?
            """,
            (estudiante_id,),
        )

        conexion.execute(
            """
            UPDATE estudiantes
            SET
                tipo = 'independiente',
                ultima_actividad = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (estudiante_id,),
        )

        _crear_progreso_si_falta(
            conexion,
            estudiante_id,
        )

    return obtener_estudiante(
        estudiante_id
    )


def registrar_o_ingresar_estudiante(
    nombre,
    codigo_curso,
):
    """
    Acceso antiguo por nombre y código.

    Se mantiene temporalmente para no romper pages/access.py
    mientras implementamos el acceso con Google.
    """

    nombre = _validar_nombre(
        nombre
    )

    codigo_curso = str(
        codigo_curso
    ).strip().upper()

    curso = obtener_curso_por_codigo(
        codigo_curso
    )

    if not curso:
        raise ValueError(
            "El código del curso no existe o está desactivado."
        )

    with conexion_db() as conexion:
        estudiante = conexion.execute(
            """
            SELECT
                estudiantes.id,
                estudiantes.identificador,
                estudiantes.nombre,
                estudiantes.correo,
                estudiantes.tipo,
                estudiantes.nivel,
                estudiantes.diagnostico_realizado
            FROM estudiantes
            INNER JOIN inscripciones
                ON inscripciones.estudiante_id = estudiantes.id
            WHERE LOWER(estudiantes.nombre) = LOWER(?)
              AND inscripciones.curso_id = ?
              AND inscripciones.activo = 1
            LIMIT 1
            """,
            (
                nombre,
                curso["id"],
            ),
        ).fetchone()

        if estudiante:
            estudiante_id = estudiante["id"]

            _actualizar_ultima_actividad(
                conexion,
                estudiante_id,
            )

            _crear_progreso_si_falta(
                conexion,
                estudiante_id,
            )

            datos_estudiante = dict(
                estudiante
            )

        else:
            identificador = str(
                uuid.uuid4()
            )

            cursor = conexion.execute(
                """
                INSERT INTO estudiantes (
                    identificador,
                    nombre,
                    tipo
                )
                VALUES (?, ?, ?)
                """,
                (
                    identificador,
                    nombre,
                    "curso",
                ),
            )

            estudiante_id = cursor.lastrowid

            conexion.execute(
                """
                INSERT INTO inscripciones (
                    estudiante_id,
                    curso_id
                )
                VALUES (?, ?)
                """,
                (
                    estudiante_id,
                    curso["id"],
                ),
            )

            _crear_progreso_si_falta(
                conexion,
                estudiante_id,
            )

            datos_estudiante = {
                "id": estudiante_id,
                "identificador": identificador,
                "nombre": nombre,
                "correo": None,
                "tipo": "curso",
                "nivel": "Sin diagnosticar",
                "diagnostico_realizado": 0,
            }

    return {
        "estudiante": datos_estudiante,
        "curso": curso,
    }


def obtener_estudiante(
    estudiante_id,
):
    with conexion_db() as conexion:
        fila = conexion.execute(
            """
            SELECT
                id,
                identificador,
                nombre,
                correo,
                tipo,
                nivel,
                diagnostico_realizado,
                creado_en,
                ultima_actividad
            FROM estudiantes
            WHERE id = ?
            """,
            (estudiante_id,),
        ).fetchone()

    return dict(
        fila
    ) if fila else None


def listar_estudiantes_curso(
    curso_id,
):
    with conexion_db() as conexion:
        filas = conexion.execute(
            """
            SELECT
                estudiantes.id,
                estudiantes.nombre,
                estudiantes.correo,
                estudiantes.tipo,
                estudiantes.nivel,
                estudiantes.diagnostico_realizado,
                estudiantes.creado_en,
                estudiantes.ultima_actividad,
                progreso_estudiantes.sesiones,
                progreso_estudiantes.preguntas,
                progreso_estudiantes.ultimo_tema,
                progreso_estudiantes.ejercicios_generados,
                progreso_estudiantes.ejercicios_revisados,
                progreso_estudiantes.respuestas_correctas,
                progreso_estudiantes.respuestas_parciales,
                progreso_estudiantes.respuestas_incorrectas
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

    return [
        dict(fila)
        for fila in filas
    ]