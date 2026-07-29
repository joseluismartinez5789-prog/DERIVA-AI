import streamlit as st


def card(
    icon,
    title,
    description,
    button_text="Entrar →",
    color="#DFF3FF"
):
    st.markdown(
        f"""
<style>
.card-container {{
    position: relative;
    overflow: hidden;
    min-height: 330px;
    padding: 36px;
    border-radius: 30px;
    background: linear-gradient(
        160deg,
        rgba(255,255,255,.55),
        {color}
    );
    backdrop-filter: blur(25px);
    border: 1px solid rgba(255,255,255,.75);
    box-shadow: 0 15px 40px rgba(81,125,255,.10);
    transition: transform .35s ease, box-shadow .35s ease;
}}

.card-container:hover {{
    transform: translateY(-8px) scale(1.015);
    box-shadow: 0 25px 60px rgba(110,150,255,.20);
}}

.card-container::before {{
    content: "";
    position: absolute;
    width: 180px;
    height: 180px;
    top: -70px;
    right: -70px;
    border-radius: 50%;
    background: rgba(255,255,255,.30);
    filter: blur(8px);
}}

.card-container::after {{
    content: "";
    position: absolute;
    width: 120px;
    height: 120px;
    left: -30px;
    bottom: -45px;
    border-radius: 50%;
    background: rgba(255,255,255,.18);
}}

.card-icon {{
    position: relative;
    z-index: 2;
    width: 82px;
    height: 82px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 48px;
    line-height: 1;
    border-radius: 24px;
    background: rgba(255,255,255,.48);
    backdrop-filter: blur(15px);
    margin-bottom: 26px;
}}

.card-title {{
    position: relative;
    z-index: 2;
    font-size: 28px;
    font-weight: 700;
    color: #22304A;
    margin-bottom: 14px;
}}

.card-description {{
    position: relative;
    z-index: 2;
    font-size: 16px;
    line-height: 1.65;
    color: #566A83;
    max-width: 92%;
    padding-bottom: 82px;
}}

.card-footer {{
    position: absolute;
    z-index: 3;
    left: 36px;
    right: 36px;
    bottom: 28px;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 14px;
}}

.card-button {{
    padding: 12px 22px;
    border-radius: 18px;
    background: {color};
    color: #3E5FD6;
    font-weight: 700;
    font-size: 15px;
    border: 1px solid rgba(255,255,255,.82);
    box-shadow: 0 8px 20px rgba(81,125,255,.08);
    transition: transform .25s ease, filter .25s ease;
}}

.card-button:hover {{
    transform: translateY(-2px);
    filter: brightness(1.03);
}}

.arrow {{
    font-size: 24px;
    color: #7C8CFF;
}}
</style>

<div class="card-container">
<div class="card-icon">{icon}</div>
<div class="card-title">{title}</div>
<div class="card-description">{description}</div>
<div class="card-footer">
<div class="card-button">{button_text}</div>
<div class="arrow">✦</div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )