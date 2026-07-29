import re
import secrets
import sqlite3
import string

from services.database_service import conexion_db


ALFABETO_CODIGO = string.ascii_uppercase + string.digits
PATRON_CORREO = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


def _normalizar_texto(
    valor,
):
    return " ".join(
        str(valor).strip().split()
    )


def _normalizar_correo(
    correo,
):
    return str(
        correo
    ).strip().lower()


def _validar_correo(
    correo,
):
    correo = _normalizar_correo(
        correo
    )

    if not correo:
        raise ValueError(
            "El correo electrónico es obligatorio."
        )

    if not PATRON_CORREO.match(
        correo
    ):
        raise ValueError(
            "Escribe un correo electrónico válido."
        )

    return correo


def _generar_codigo():
    bloque = "".join(
        secrets.choice(
            ALFABETO_CODIGO
        )
        for _ in range(6)
    )

    return f"DERIVA-{bloque}"


def obtener_profesor_por_correo(
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
                nombre,
                correo,
                creado_en
            FROM profesores
            WHERE LOWER(TRIM(correo)) = ?
            LIMIT 1
            """,
            (correo,),
        ).fetchone()

    return dict(
        fila
    ) if fila else None


def iniciar_sesion_profesor(
    correo,
):
    profesor = obtener_profesor_por_correo(
        correo
    )

    if not profesor:
        raise ValueError(
            "No existe una cuenta de profesor con ese correo."
        )

    return profesor


def crear_profesor(
    nombre,
    correo,
):
    nombre = _normalizar_texto(
        nombre
    )
    correo = _validar_correo(
        correo
    )

    if len(nombre) < 3:
        raise ValueError(
            "El nombre del profesor es obligatorio."
        )

    existente = obtener_profesor_por_correo(
        correo
    )

    if existente:
        raise ValueError(
            "Ya existe un profesor con ese correo. "
            "Utiliza la opción Iniciar sesión."
        )

    try:
        with conexion_db() as conexion:
            cursor = conexion.execute(
                """
                INSERT INTO profesores (
                    nombre,
                    correo
                )
                VALUES (?, ?)
                """,
                (
                    nombre,
                    correo,
                ),
            )

            profesor_id = cursor.lastrowid

    except sqlite3.IntegrityError as error:
        if "idx_profesores_correo_unico" in str(
            error
        ) or "UNIQUE" in str(
            error
        ).upper():
            raise ValueError(
                "Ya existe un profesor con ese correo. "
                "Utiliza la opción Iniciar sesión."
            ) from error

        raise

    return obtener_profesor(
        profesor_id
    )


def obtener_profesor(
    profesor_id,
):
    with conexion_db() as conexion:
        fila = conexion.execute(
            """
            SELECT
                id,
                nombre,
                correo,
                creado_en
            FROM profesores
            WHERE id = ?
            """,
            (profesor_id,),
        ).fetchone()

    return dict(
        fila
    ) if fila else None


def crear_curso(
    profesor_id,
    nombre,
    seccion,
):
    nombre = _normalizar_texto(
        nombre
    )
    seccion = _normalizar_texto(
        seccion
    )

    if not nombre:
        raise ValueError(
            "El nombre del curso es obligatorio."
        )

    if not seccion:
        raise ValueError(
            "La sección es obligatoria."
        )

    for _ in range(20):
        codigo = _generar_codigo()

        try:
            with conexion_db() as conexion:
                cursor = conexion.execute(
                    """
                    INSERT INTO cursos (
                        profesor_id,
                        nombre,
                        seccion,
                        codigo
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        profesor_id,
                        nombre,
                        seccion,
                        codigo,
                    ),
                )

                curso_id = cursor.lastrowid

            return obtener_curso_por_id(
                curso_id
            )

        except sqlite3.IntegrityError as error:
            if (
                "cursos.codigo"
                not in str(error)
            ):
                raise

    raise RuntimeError(
        "No se pudo generar un código único para el curso."
    )


def obtener_curso_por_codigo(
    codigo,
):
    codigo = str(
        codigo
    ).strip().upper()

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
            FROM cursos
            INNER JOIN profesores
                ON profesores.id = cursos.profesor_id
            WHERE cursos.codigo = ?
              AND cursos.activo = 1
            """,
            (codigo,),
        ).fetchone()

    return dict(
        fila
    ) if fila else None


def obtener_curso_por_id(
    curso_id,
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
            FROM cursos
            INNER JOIN profesores
                ON profesores.id = cursos.profesor_id
            WHERE cursos.id = ?
            """,
            (curso_id,),
        ).fetchone()

    return dict(
        fila
    ) if fila else None


def listar_cursos_profesor(
    profesor_id,
):
    with conexion_db() as conexion:
        filas = conexion.execute(
            """
            SELECT
                cursos.id,
                cursos.nombre,
                cursos.seccion,
                cursos.codigo,
                cursos.activo,
                cursos.creado_en,
                COUNT(
                    DISTINCT inscripciones.estudiante_id
                ) AS total_estudiantes
            FROM cursos
            LEFT JOIN inscripciones
                ON inscripciones.curso_id = cursos.id
               AND inscripciones.activo = 1
            WHERE cursos.profesor_id = ?
            GROUP BY cursos.id
            ORDER BY cursos.creado_en DESC
            """,
            (profesor_id,),
        ).fetchall()

    return [
        dict(fila)
        for fila in filas
    ]