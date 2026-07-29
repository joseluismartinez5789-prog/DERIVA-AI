import streamlit as st


def page_container_start():
    """
    Inicia el contenedor principal de la página.
    """

    st.markdown(
        """
        <style>

        .deriva-container{

            background:rgba(255,255,255,.55);

            backdrop-filter:blur(18px);

            border:1px solid rgba(255,255,255,.65);

            border-radius:30px;

            padding:40px;

            margin-top:20px;

            margin-bottom:40px;

            box-shadow:
                0 20px 45px rgba(90,120,255,.10);

        }

        </style>

        <div class="deriva-container">
        """,
        unsafe_allow_html=True,
    )


def page_container_end():
    """
    Cierra el contenedor principal.
    """

    st.markdown(
        """
        </div>
        """,
        unsafe_allow_html=True,
    )