import streamlit as st
import os



def aplicar_tema():

    ruta_css = os.path.join(
        "assets",
        "styles",
        "style.css"
    )


    if os.path.exists(ruta_css):

        with open(
            ruta_css,
            "r",
            encoding="utf-8"
        ) as archivo:

            css = archivo.read()


        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )



def cargar_css():

    aplicar_tema()