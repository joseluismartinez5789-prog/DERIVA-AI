import json
import os
from datetime import datetime

import streamlit as st

from services.database_service import conexion_db


RUTA = "data/progreso.json"


def _estructura_inicial():
    return {
        "sesiones": 0,
        "preguntas": 0,
        "temas_estudiados": [],
        "lecciones_iniciadas": [],
        "lecciones_completadas": [],
        "ultimo_tema": "Ninguno",
        "ejercicios_generados": 0,
        "ejercicios_revisados": 0,
        "respuestas_correctas": 0,
        "respuestas_parciales": 0,
        "respuestas_incorrectas": 0,
        "historial_practica": [],
        "progreso_por_tema": {},
    }


def _obtener_estudiante_id():
    return st.session_state.get("estudiante_id")


def _normalizar_lista(valor):
    if not isinstance(valor, list):
        return []
    salida = []
    for elemento in valor:
        elemento = str(elemento).strip()
        if elemento and elemento not in salida:
            salida.append(elemento)
    return salida


def _normalizar_progreso(progreso):
    base = _estructura_inicial()
    if not isinstance(progreso, dict):
        return base

    for clave, valor in base.items():
        progreso.setdefault(clave, valor)

    progreso["temas_estudiados"] = _normalizar_lista(
        progreso.get("temas_estudiados")
    )
    progreso["lecciones_iniciadas"] = _normalizar_lista(
        progreso.get("lecciones_iniciadas")
    )
    progreso["lecciones_completadas"] = _normalizar_lista(
        progreso.get("lecciones_completadas")
    )

    if not isinstance(progreso.get("historial_practica"), list):
        progreso["historial_practica"] = []
    if not isinstance(progreso.get("progreso_por_tema"), dict):
        progreso["progreso_por_tema"] = {}

    return progreso


def _cargar_progreso_json():
    if not os.path.exists(RUTA):
        return _estructura_inicial()
    try:
        with open(RUTA, "r", encoding="utf-8") as archivo:
            return _normalizar_progreso(json.load(archivo))
    except (OSError, json.JSONDecodeError):
        return _estructura_inicial()


def _guardar_progreso_json(progreso):
    carpeta = os.path.dirname(RUTA)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with open(RUTA, "w", encoding="utf-8") as archivo:
        json.dump(
            _normalizar_progreso(progreso),
            archivo,
            indent=4,
            ensure_ascii=False,
        )


def _asegurar_progreso_estudiante(estudiante_id):
    with conexion_db() as conexion:
        conexion.execute(
            """
            INSERT OR IGNORE INTO progreso_estudiantes (estudiante_id)
            VALUES (?)
            """,
            (estudiante_id,),
        )


def _cargar_progreso_db(estudiante_id):
    _asegurar_progreso_estudiante(estudiante_id)

    with conexion_db() as conexion:
        fila = conexion.execute(
            """
            SELECT sesiones, preguntas, temas_estudiados, ultimo_tema,
                   ejercicios_generados, ejercicios_revisados,
                   respuestas_correctas, respuestas_parciales,
                   respuestas_incorrectas, progreso_por_tema
            FROM progreso_estudiantes
            WHERE estudiante_id = ?
            """,
            (estudiante_id,),
        ).fetchone()

        historial = conexion.execute(
            """
            SELECT fecha, tema, nivel, resultado, ejercicio, respuesta
            FROM historial_practica
            WHERE estudiante_id = ?
            ORDER BY fecha DESC
            LIMIT 100
            """,
            (estudiante_id,),
        ).fetchall()

    if not fila:
        return _estructura_inicial()

    progreso = dict(fila)

    try:
        progreso["temas_estudiados"] = json.loads(
            progreso.get("temas_estudiados") or "[]"
        )
    except json.JSONDecodeError:
        progreso["temas_estudiados"] = []

    try:
        progreso_por_tema = json.loads(
            progreso.get("progreso_por_tema") or "{}"
        )
    except json.JSONDecodeError:
        progreso_por_tema = {}

    meta = progreso_por_tema.pop("__aprendizaje__", {})
    progreso["progreso_por_tema"] = progreso_por_tema
    progreso["lecciones_iniciadas"] = meta.get("iniciadas", [])
    progreso["lecciones_completadas"] = meta.get("completadas", [])
    progreso["historial_practica"] = [
        dict(registro) for registro in reversed(historial)
    ]

    return _normalizar_progreso(progreso)


def _guardar_progreso_db(estudiante_id, progreso):
    progreso = _normalizar_progreso(progreso)
    progreso_por_tema = dict(progreso["progreso_por_tema"])
    progreso_por_tema["__aprendizaje__"] = {
        "iniciadas": progreso["lecciones_iniciadas"],
        "completadas": progreso["lecciones_completadas"],
    }

    with conexion_db() as conexion:
        conexion.execute(
            """
            INSERT INTO progreso_estudiantes (
                estudiante_id, sesiones, preguntas, temas_estudiados,
                ultimo_tema, ejercicios_generados, ejercicios_revisados,
                respuestas_correctas, respuestas_parciales,
                respuestas_incorrectas, progreso_por_tema, actualizado_en
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(estudiante_id) DO UPDATE SET
                sesiones = excluded.sesiones,
                preguntas = excluded.preguntas,
                temas_estudiados = excluded.temas_estudiados,
                ultimo_tema = excluded.ultimo_tema,
                ejercicios_generados = excluded.ejercicios_generados,
                ejercicios_revisados = excluded.ejercicios_revisados,
                respuestas_correctas = excluded.respuestas_correctas,
                respuestas_parciales = excluded.respuestas_parciales,
                respuestas_incorrectas = excluded.respuestas_incorrectas,
                progreso_por_tema = excluded.progreso_por_tema,
                actualizado_en = CURRENT_TIMESTAMP
            """,
            (
                estudiante_id,
                progreso["sesiones"],
                progreso["preguntas"],
                json.dumps(progreso["temas_estudiados"], ensure_ascii=False),
                progreso["ultimo_tema"],
                progreso["ejercicios_generados"],
                progreso["ejercicios_revisados"],
                progreso["respuestas_correctas"],
                progreso["respuestas_parciales"],
                progreso["respuestas_incorrectas"],
                json.dumps(progreso_por_tema, ensure_ascii=False),
            ),
        )
        conexion.execute(
            """
            UPDATE estudiantes
            SET ultima_actividad = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (estudiante_id,),
        )


def cargar_progreso():
    estudiante_id = _obtener_estudiante_id()
    if estudiante_id:
        return _cargar_progreso_db(estudiante_id)
    return _cargar_progreso_json()


def guardar_progreso(progreso):
    estudiante_id = _obtener_estudiante_id()
    if estudiante_id:
        _guardar_progreso_db(estudiante_id, progreso)
    else:
        _guardar_progreso_json(progreso)


def registrar_sesion():
    progreso = cargar_progreso()
    progreso["sesiones"] += 1
    guardar_progreso(progreso)


def registrar_pregunta(tema):
    tema = str(tema).strip() or "No identificado"
    progreso = cargar_progreso()
    progreso["preguntas"] += 1
    progreso["ultimo_tema"] = tema
    if tema not in progreso["temas_estudiados"]:
        progreso["temas_estudiados"].append(tema)
    guardar_progreso(progreso)


def registrar_leccion_iniciada(tema):
    tema = str(tema).strip()
    if not tema:
        return
    progreso = cargar_progreso()
    progreso["ultimo_tema"] = tema
    if tema not in progreso["lecciones_iniciadas"]:
        progreso["lecciones_iniciadas"].append(tema)
    if tema not in progreso["temas_estudiados"]:
        progreso["temas_estudiados"].append(tema)
    guardar_progreso(progreso)


def marcar_leccion_completada(tema):
    tema = str(tema).strip()
    if not tema:
        return
    progreso = cargar_progreso()
    progreso["ultimo_tema"] = tema
    if tema not in progreso["lecciones_iniciadas"]:
        progreso["lecciones_iniciadas"].append(tema)
    if tema not in progreso["lecciones_completadas"]:
        progreso["lecciones_completadas"].append(tema)
    if tema not in progreso["temas_estudiados"]:
        progreso["temas_estudiados"].append(tema)
    guardar_progreso(progreso)


def registrar_ejercicio_generado(tema, nivel):
    progreso = cargar_progreso()
    progreso["ejercicios_generados"] += 1
    progreso["ultimo_tema"] = tema
    if tema not in progreso["temas_estudiados"]:
        progreso["temas_estudiados"].append(tema)
    datos = progreso["progreso_por_tema"].setdefault(
        tema,
        {
            "generados": 0,
            "revisados": 0,
            "correctas": 0,
            "parciales": 0,
            "incorrectas": 0,
            "ultimo_nivel": nivel,
        },
    )
    datos["generados"] += 1
    datos["ultimo_nivel"] = nivel
    guardar_progreso(progreso)


def registrar_resultado_ejercicio(
    tema,
    nivel,
    resultado,
    ejercicio="",
    respuesta="",
):
    progreso = cargar_progreso()
    resultado_normalizado = str(resultado).lower()
    progreso["ejercicios_revisados"] += 1
    progreso["ultimo_tema"] = tema

    if tema not in progreso["temas_estudiados"]:
        progreso["temas_estudiados"].append(tema)

    datos = progreso["progreso_por_tema"].setdefault(
        tema,
        {
            "generados": 0,
            "revisados": 0,
            "correctas": 0,
            "parciales": 0,
            "incorrectas": 0,
            "ultimo_nivel": nivel,
        },
    )
    datos["revisados"] += 1
    datos["ultimo_nivel"] = nivel

    if resultado_normalizado == "correcta":
        progreso["respuestas_correctas"] += 1
        datos["correctas"] += 1
    elif resultado_normalizado == "parcial":
        progreso["respuestas_parciales"] += 1
        datos["parciales"] += 1
    elif resultado_normalizado == "incorrecta":
        progreso["respuestas_incorrectas"] += 1
        datos["incorrectas"] += 1

    registro = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "tema": tema,
        "nivel": nivel,
        "resultado": resultado_normalizado,
        "ejercicio": ejercicio,
        "respuesta": respuesta,
    }
    progreso["historial_practica"].append(registro)
    progreso["historial_practica"] = progreso["historial_practica"][-100:]

    estudiante_id = _obtener_estudiante_id()
    if estudiante_id:
        with conexion_db() as conexion:
            conexion.execute(
                """
                INSERT INTO historial_practica (
                    estudiante_id, tema, nivel, resultado,
                    ejercicio, respuesta, fecha
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    estudiante_id,
                    tema,
                    nivel,
                    resultado_normalizado,
                    ejercicio,
                    respuesta,
                    registro["fecha"],
                ),
            )

    guardar_progreso(progreso)


def obtener_resumen_practica():
    progreso = cargar_progreso()
    revisados = progreso["ejercicios_revisados"]
    correctas = progreso["respuestas_correctas"]
    porcentaje = round(correctas / revisados * 100) if revisados > 0 else 0
    return {
        "generados": progreso["ejercicios_generados"],
        "revisados": revisados,
        "correctas": correctas,
        "parciales": progreso["respuestas_parciales"],
        "incorrectas": progreso["respuestas_incorrectas"],
        "porcentaje_aciertos": porcentaje,
    }