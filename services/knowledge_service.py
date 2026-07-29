import os


KNOWLEDGE_FILE = "knowledge/larson_texto.txt"



def leer_larson():

    if not os.path.exists(KNOWLEDGE_FILE):

        return ""


    with open(
        KNOWLEDGE_FILE,
        "r",
        encoding="utf-8"
    ) as archivo:

        contenido = archivo.read()


    return contenido




def dividir_fragmentos(texto):

    fragmentos = texto.split(
        "--- Página"
    )


    fragmentos_limpios = []


    for fragmento in fragmentos:

        if len(fragmento.strip()) > 100:

            fragmentos_limpios.append(
                fragmento.strip()
            )


    return fragmentos_limpios




def obtener_palabras_clave(tema, pregunta=""):

    texto = (
        tema + " " + pregunta
    ).lower()


    palabras = []


    if (
        "límite" in texto
        or "limite" in texto
    ):

        palabras.extend([
            "límite",
            "limite",
            "aproximación",
            "función",
            "valor"
        ])


    if "continu" in texto:

        palabras.extend([
            "continuidad",
            "continua",
            "discontinuidad"
        ])


    if (
        "infinito" in texto
        or "infinita" in texto
    ):

        palabras.extend([
            "infinito",
            "asíntota",
            "vertical"
        ])


    if "deriv" in texto:

        palabras.extend([
            "derivada",
            "pendiente",
            "tangente",
            "razón de cambio"
        ])


    if "regla de la cadena" in texto:

        palabras.extend([
            "cadena",
            "composición",
            "derivada"
        ])


    if not palabras:

        palabras.extend([
            "cálculo",
            "calculo"
        ])


    return palabras




def buscar_tema(tema, pregunta=""):

    contenido = leer_larson()


    if not contenido:

        return ""



    fragmentos = dividir_fragmentos(
        contenido
    )


    palabras = obtener_palabras_clave(
        tema,
        pregunta
    )


    resultados = []


    for fragmento in fragmentos:

        puntuacion = 0


        fragmento_lower = fragmento.lower()


        for palabra in palabras:

            if palabra in fragmento_lower:

                puntuacion += 1



        if puntuacion > 0:

            resultados.append(
                (
                    puntuacion,
                    fragmento
                )
            )



    resultados.sort(
        reverse=True,
        key=lambda x: x[0]
    )


    mejores = []


    for puntuacion, fragmento in resultados[:5]:

        mejores.append(
            fragmento
        )


    return "\n\n".join(
        mejores
    )