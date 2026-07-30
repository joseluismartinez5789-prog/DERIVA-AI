import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path


RUTA_BASE_DATOS = Path("data/deriva_ai.db")

# Evita que dos ejecuciones de Streamlit intenten migrar SQLite al mismo tiempo.
_BLOQUEO_INICIALIZACION = threading.Lock()
_BASE_DATOS_INICIALIZADA = False


def _crear_carpeta_datos():
    RUTA_BASE_DATOS.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


def obtener_conexion():
    _crear_carpeta_datos()

    conexion = sqlite3.connect(
        RUTA_BASE_DATOS,
        timeout=30,
    )

    conexion.row_factory = sqlite3.Row

    conexion.execute(
        "PRAGMA foreign_keys = ON"
    )
    conexion.execute(
        "PRAGMA busy_timeout = 60000"
    )

    return conexion


@contextmanager
def conexion_db():
    conexion = obtener_conexion()

    try:
        yield conexion
        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def _columnas_tabla(
    conexion,
    tabla,
):
    filas = conexion.execute(
        f"PRAGMA table_info({tabla})"
    ).fetchall()

    return {
        fila["name"]
        for fila in filas
    }


def _agregar_columna_si_falta(
    conexion,
    tabla,
    columna,
    definicion,
):
    columnas = _columnas_tabla(
        conexion,
        tabla,
    )

    if columna not in columnas:
        conexion.execute(
            f"""
            ALTER TABLE {tabla}
            ADD COLUMN {columna} {definicion}
            """
        )


def _normalizar_correos_profesores(
    conexion,
):
    filas = conexion.execute(
        """
        SELECT
            id,
            correo
        FROM profesores
        WHERE correo IS NOT NULL
          AND TRIM(correo) <> ''
        ORDER BY id
        """
    ).fetchall()

    profesor_principal_por_correo = {}

    for fila in filas:
        profesor_id = fila["id"]

        correo = str(
            fila["correo"]
        ).strip().lower()

        conexion.execute(
            """
            UPDATE profesores
            SET correo = ?
            WHERE id = ?
            """,
            (
                correo,
                profesor_id,
            ),
        )

        if correo not in profesor_principal_por_correo:
            profesor_principal_por_correo[
                correo
            ] = profesor_id

            continue

        profesor_principal = profesor_principal_por_correo[
            correo
        ]

        conexion.execute(
            """
            UPDATE cursos
            SET profesor_id = ?
            WHERE profesor_id = ?
            """,
            (
                profesor_principal,
                profesor_id,
            ),
        )

        conexion.execute(
            """
            DELETE FROM profesores
            WHERE id = ?
            """,
            (profesor_id,),
        )


def _normalizar_correos_estudiantes(
    conexion,
):
    filas = conexion.execute(
        """
        SELECT
            id,
            correo
        FROM estudiantes
        WHERE correo IS NOT NULL
          AND TRIM(correo) <> ''
        """
    ).fetchall()

    for fila in filas:
        correo = str(
            fila["correo"]
        ).strip().lower()

        conexion.execute(
            """
            UPDATE estudiantes
            SET correo = ?
            WHERE id = ?
            """,
            (
                correo,
                fila["id"],
            ),
        )


def _inicializar_base_datos_interna():
    with conexion_db() as conexion:
        conexion.executescript(
            """
            CREATE TABLE IF NOT EXISTS profesores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT,
                creado_en TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS cursos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profesor_id INTEGER NOT NULL,
                nombre TEXT NOT NULL,
                seccion TEXT NOT NULL,
                codigo TEXT NOT NULL UNIQUE,
                activo INTEGER NOT NULL DEFAULT 1,
                creado_en TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profesor_id)
                    REFERENCES profesores(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS estudiantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identificador TEXT NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                correo TEXT,
                tipo TEXT NOT NULL DEFAULT 'curso',
                nivel TEXT NOT NULL
                    DEFAULT 'Sin diagnosticar',
                diagnostico_realizado INTEGER NOT NULL
                    DEFAULT 0,
                creado_en TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,
                ultima_actividad TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS inscripciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudiante_id INTEGER NOT NULL,
                curso_id INTEGER NOT NULL,
                inscrito_en TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,
                activo INTEGER NOT NULL DEFAULT 1,
                UNIQUE (
                    estudiante_id,
                    curso_id
                ),
                FOREIGN KEY (estudiante_id)
                    REFERENCES estudiantes(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (curso_id)
                    REFERENCES cursos(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS progreso_estudiantes (
                estudiante_id INTEGER PRIMARY KEY,
                sesiones INTEGER NOT NULL DEFAULT 0,
                preguntas INTEGER NOT NULL DEFAULT 0,
                ultimo_tema TEXT NOT NULL DEFAULT 'Ninguno',
                ejercicios_generados INTEGER NOT NULL
                    DEFAULT 0,
                ejercicios_revisados INTEGER NOT NULL
                    DEFAULT 0,
                respuestas_correctas INTEGER NOT NULL
                    DEFAULT 0,
                respuestas_parciales INTEGER NOT NULL
                    DEFAULT 0,
                respuestas_incorrectas INTEGER NOT NULL
                    DEFAULT 0,
                temas_estudiados TEXT NOT NULL
                    DEFAULT '[]',
                progreso_por_tema TEXT NOT NULL
                    DEFAULT '{}',
                actualizado_en TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (estudiante_id)
                    REFERENCES estudiantes(id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS diagnosticos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudiante_id INTEGER NOT NULL UNIQUE,
                puntaje INTEGER NOT NULL,
                total INTEGER NOT NULL,
                nivel TEXT NOT NULL,
                respuestas TEXT NOT NULL DEFAULT '{}',
                detalle_respuestas TEXT NOT NULL DEFAULT '[]',
                fortalezas TEXT NOT NULL DEFAULT '[]',
                mejorar TEXT NOT NULL DEFAULT '[]',
                plan_estudios TEXT NOT NULL DEFAULT '[]',
                siguiente_area TEXT,
                siguiente_leccion TEXT,
                realizado_en TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (estudiante_id)
                    REFERENCES estudiantes(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS historial_practica (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudiante_id INTEGER NOT NULL,
                tema TEXT NOT NULL,
                nivel TEXT NOT NULL,
                resultado TEXT NOT NULL,
                ejercicio TEXT,
                respuesta TEXT,
                fecha TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (estudiante_id)
                    REFERENCES estudiantes(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_cursos_codigo
            ON cursos(codigo);

            CREATE INDEX IF NOT EXISTS idx_inscripciones_curso
            ON inscripciones(curso_id);


            CREATE INDEX IF NOT EXISTS idx_diagnosticos_estudiante
            ON diagnosticos(estudiante_id);

            CREATE INDEX IF NOT EXISTS idx_historial_estudiante
            ON historial_practica(estudiante_id);
            """
        )

        # Migración para bases de datos ya existentes.

        _agregar_columna_si_falta(
            conexion,
            "estudiantes",
            "correo",
            "TEXT",
        )

        _agregar_columna_si_falta(
            conexion,
            "estudiantes",
            "tipo",
            "TEXT NOT NULL DEFAULT 'curso'",
        )

        _agregar_columna_si_falta(
            conexion,
            "estudiantes",
            "nivel",
            "TEXT NOT NULL DEFAULT 'Sin diagnosticar'",
        )

        _agregar_columna_si_falta(
            conexion,
            "estudiantes",
            "diagnostico_realizado",
            "INTEGER NOT NULL DEFAULT 0",
        )

        _agregar_columna_si_falta(
            conexion,
            "progreso_estudiantes",
            "temas_estudiados",
            "TEXT NOT NULL DEFAULT '[]'",
        )

        _agregar_columna_si_falta(
            conexion,
            "progreso_estudiantes",
            "progreso_por_tema",
            "TEXT NOT NULL DEFAULT '{}'",
        )

        # Los estudiantes existentes pertenecen a cursos.

        conexion.execute(
            """
            UPDATE estudiantes
            SET tipo = 'curso'
            WHERE tipo IS NULL
               OR TRIM(tipo) = ''
            """
        )

        _normalizar_correos_profesores(
            conexion
        )

        _normalizar_correos_estudiantes(
            conexion
        )

        conexion.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_profesores_correo_unico
            ON profesores(
                LOWER(TRIM(correo))
            )
            WHERE correo IS NOT NULL
              AND TRIM(correo) <> ''
            """
        )

        conexion.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_estudiantes_correo_unico
            ON estudiantes(
                LOWER(TRIM(correo))
            )
            WHERE correo IS NOT NULL
              AND TRIM(correo) <> ''
            """
        )


def inicializar_base_datos():
    """
    Inicializa y migra la base de datos una sola vez por proceso.

    Streamlit puede ejecutar app.py varias veces y también puede recibir
    varias sesiones al mismo tiempo. Este bloqueo evita que dos ejecuciones
    intenten modificar el esquema SQLite simultáneamente.

    Si SQLite está temporalmente bloqueado durante el arranque, se realizan
    varios intentos antes de mostrar el error real.
    """
    global _BASE_DATOS_INICIALIZADA

    if _BASE_DATOS_INICIALIZADA:
        return

    with _BLOQUEO_INICIALIZACION:
        if _BASE_DATOS_INICIALIZADA:
            return

        ultimo_error = None

        for intento in range(5):
            try:
                _inicializar_base_datos_interna()
                _BASE_DATOS_INICIALIZADA = True
                return

            except sqlite3.OperationalError as error:
                ultimo_error = error
                mensaje = str(error).lower()

                if (
                    "locked" not in mensaje
                    and "busy" not in mensaje
                ):
                    raise

                time.sleep(1.5 * (intento + 1))

        if ultimo_error is not None:
            raise ultimo_error