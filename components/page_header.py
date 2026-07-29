import streamlit as st


def page_header(
    titulo,
    subtitulo="",
    icono="📘"
):

    st.markdown(
        f"""
        <style>

        .page-header{{
            background:linear-gradient(
                135deg,
                rgba(114,200,248,.95),
                rgba(140,217,255,.92),
                rgba(205,239,255,.90)
            );

            padding:30px;

            border-radius:26px;

            margin-bottom:30px;

            box-shadow:
                0 12px 35px rgba(80,120,255,.10);

            border:1px solid rgba(255,255,255,.55);

        }}

        .page-title{{
            color:white;
            font-size:36px;
            font-weight:700;
            margin-bottom:8px;
        }}

        .page-subtitle{{
            color:white;
            font-size:18px;
            opacity:.95;
        }}

        </style>

        <div class="page-header">

            <div class="page-title">

                {icono} {titulo}

            </div>

            <div class="page-subtitle">

                {subtitulo}

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )