import streamlit as st


def hero():

    st.markdown(
        """
<style>

.hero{

    position:relative;

    overflow:hidden;

    border-radius:32px;

    padding:60px;

    min-height:330px;

    display:flex;

    justify-content:space-between;

    align-items:center;

    background:
        linear-gradient(
        135deg,
        rgba(117,198,255,.95),
        rgba(162,175,255,.90),
        rgba(228,184,255,.88)
        );

    backdrop-filter:blur(25px);

    box-shadow:
        0 25px 60px rgba(74,118,255,.18);

}


.hero::before{

    content:"";

    position:absolute;

    width:320px;

    height:320px;

    border-radius:50%;

    right:-90px;

    top:-100px;

    background:rgba(255,255,255,.20);

    filter:blur(15px);

}


.hero::after{

    content:"";

    position:absolute;

    width:180px;

    height:180px;

    border-radius:50%;

    left:-50px;

    bottom:-70px;

    background:rgba(255,255,255,.15);

}


.hero-grid{

    display:grid;

    grid-template-columns:2fr 1fr;

    gap:50px;

    align-items:center;

}


.hero-title{

    color:white;

    font-size:56px;

    font-weight:700;

    margin-bottom:10px;

}


.hero-sub{

    color:white;

    font-size:22px;

    opacity:.96;

    margin-bottom:25px;

}


.hero-text{

    color:white;

    font-size:18px;

    line-height:1.8;

    max-width:650px;

    opacity:.92;

}


.hero-buttons{

    margin-top:35px;

    display:flex;

    gap:18px;

}


.hero-btn{

    background:white;

    color:#3657C8;

    padding:14px 28px;

    border-radius:16px;

    font-weight:600;

    text-decoration:none;

}


.hero-btn-secondary{

    background:rgba(255,255,255,.20);

    color:white;

    padding:14px 28px;

    border-radius:16px;

    border:1px solid rgba(255,255,255,.35);

}


.hero-stats{

    display:flex;

    gap:18px;

    margin-top:35px;

}


.stat{

    background:rgba(255,255,255,.18);

    backdrop-filter:blur(15px);

    padding:16px 22px;

    border-radius:18px;

    border:1px solid rgba(255,255,255,.25);

    text-align:center;

    min-width:110px;

}


.stat h2{

    color:white;

    margin:0;

    font-size:28px;

}


.stat span{

    color:white;

    opacity:.85;

    font-size:14px;

}


.hero-robot{

    display:flex;

    justify-content:center;

    align-items:center;

    font-size:120px;

}

</style>

<div class="hero">

<div class="hero-grid">

<div>

<div class="hero-title">
🤖 DERIVA AI
</div>

<div class="hero-sub">
Tu tutor inteligente de Cálculo Diferencial
</div>

<div class="hero-text">
Aprende con explicaciones paso a paso, resuelve ejercicios,
analiza imágenes matemáticas y recibe una ruta personalizada
para mejorar continuamente.
</div>

<div class="hero-buttons">

<div class="hero-btn">
Comenzar
</div>

<div class="hero-btn-secondary">
Ver progreso
</div>

</div>

<div class="hero-stats">

<div class="stat">

<h2>24</h2>

<span>Lecciones</span>

</div>

<div class="stat">

<h2>120+</h2>

<span>Ejercicios</span>

</div>

<div class="stat">

<h2>IA</h2>

<span>Tutor 24/7</span>

</div>

</div>

</div>

<div class="hero-robot">

🧠

</div>

</div>

</div>

""",
        unsafe_allow_html=True,
    )