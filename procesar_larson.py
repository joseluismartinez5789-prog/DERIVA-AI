import os
from pypdf import PdfReader


PDF_PATH = "knowledge"

ARCHIVO_SALIDA = "knowledge/larson_texto.txt"



def extraer_pdf():

    texto_completo = ""

    archivos = os.listdir(PDF_PATH)


    for archivo in archivos:

        if archivo.lower().endswith(".pdf"):

            ruta_pdf = os.path.join(
                PDF_PATH,
                archivo
            )

            print(
                f"Leyendo: {archivo}"
            )


            lector = PdfReader(
                ruta_pdf
            )


            total_paginas = len(
                lector.pages
            )


            print(
                f"Páginas encontradas: {total_paginas}"
            )


            for numero, pagina in enumerate(
                lector.pages
            ):

                texto = pagina.extract_text()


                if texto:

                    texto_completo += (
                        f"\n\n--- Página {numero + 1} ---\n\n"
                    )

                    texto_completo += texto


                if numero % 50 == 0:

                    print(
                        f"Procesadas {numero}/{total_paginas} páginas"
                    )


    return texto_completo




def guardar_texto(texto):

    with open(
        ARCHIVO_SALIDA,
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(
            texto
        )


    print(
        "✅ Libro procesado correctamente"
    )

    print(
        f"Guardado en: {ARCHIVO_SALIDA}"
    )




if __name__ == "__main__":


    texto = extraer_pdf()


    guardar_texto(
        texto
    )