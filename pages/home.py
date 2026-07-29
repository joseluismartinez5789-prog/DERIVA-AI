from datetime import datetime

import streamlit as st

from services.diagnostic_service import diagnostico_completado


def obtener_saludo():
    hora = datetime.now().hour

    if 5 <= hora < 12:
        return "Buenos días", "🧠"

    if 12 <= hora < 18:
        return "Buenas tardes", "🧠"

    return "Buenas noches", "🧠"


def mostrar_acceso(
    icono,
    titulo,
    descripcion,
    pagina,
    texto_boton,
    clase,
    habilitado=True,
    mensaje_bloqueo=None,
):
    st.markdown(
        f"""
<div class="deriva-home-card {clase}">
    <div class="deriva-home-card-icon">{icono}</div>
    <div class="deriva-home-card-copy">
        <h3>{titulo}</h3>
        <p>{descripcion}</p>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    if habilitado:
        st.page_link(
            pagina,
            label=texto_boton,
            icon=":material/arrow_forward:",
            use_container_width=True,
        )

    else:
        st.button(
            "Completa el diagnóstico para desbloquear",
            disabled=True,
            use_container_width=True,
            key=f"bloqueado_{titulo}",
        )

        if mensaje_bloqueo:
            st.caption(
                mensaje_bloqueo
            )


nombre = st.session_state.get(
    "estudiante_nombre",
    "Estudiante",
)
curso = st.session_state.get(
    "curso_nombre",
    "Cálculo Diferencial",
)
seccion = st.session_state.get(
    "curso_seccion",
    "",
)
diagnostico_listo = diagnostico_completado()
saludo, icono_saludo = obtener_saludo()


st.markdown(
    """
<style>
.home-shell {
    position: relative;
    overflow: hidden;
    padding: 38px;
    margin-bottom: 28px;
    border-radius: 34px;
    background:
        radial-gradient(
            circle at 87% 15%,
            rgba(255,255,255,.24),
            transparent 22%
        ),
        linear-gradient(
            135deg,
            #78c8f5 0%,
            #9bd7f6 52%,
            #d6c7f3 100%
        );
    box-shadow: 0 28px 62px rgba(76,79,175,.25);
    color: white;
    animation: derivaFadeUp .7s ease both;
}

.home-shell::before,
.home-shell::after {
    content: "";
    position: absolute;
    border-radius: 999px;
    pointer-events: none;
}

.home-shell::before {
    width: 250px;
    height: 250px;
    top: -125px;
    right: -60px;
    background: rgba(255,255,255,.13);
}

.home-shell::after {
    width: 180px;
    height: 180px;
    bottom: -105px;
    right: 23%;
    background: rgba(203,226,255,.15);
}

.home-hero-layout {
    position: relative;
    z-index: 1;
    display: grid;
    grid-template-columns: minmax(0, 1.35fr) minmax(250px, .65fr);
    align-items: center;
    gap: 34px;
}

.home-hero-copy {
    min-width: 0;
}

.home-visual {
    position: relative;
    display: grid;
    place-items: center;
    min-height: 330px;
    isolation: isolate;
}

.home-visual::before,
.home-visual::after {
    content: "";
    position: absolute;
    border-radius: 999px;
    filter: blur(1px);
    pointer-events: none;
}

.home-visual::before {
    width: 270px;
    height: 270px;
    background:
        radial-gradient(
            circle at 35% 30%,
            rgba(255,255,255,.90),
            rgba(210,238,255,.72) 35%,
            rgba(188,210,255,.30) 67%,
            rgba(255,255,255,.06) 100%
        );
    box-shadow:
        inset -20px -24px 44px rgba(122,154,232,.18),
        inset 18px 16px 32px rgba(255,255,255,.50),
        0 26px 50px rgba(63,111,170,.18);
    animation: derivaFloat 4.4s ease-in-out infinite;
}

.home-visual::after {
    width: 210px;
    height: 56px;
    bottom: 30px;
    background: rgba(72,114,163,.16);
    filter: blur(18px);
    transform: scaleX(.92);
    animation: derivaShadowPulse 4.4s ease-in-out infinite;
}

.home-brain-orb {
    position: relative;
    z-index: 2;
    display: grid;
    place-items: center;
    width: 210px;
    height: 210px;
    border: 1px solid rgba(255,255,255,.65);
    border-radius: 50%;
    background:
        radial-gradient(
            circle at 32% 26%,
            rgba(255,255,255,.96),
            rgba(228,244,255,.72) 32%,
            rgba(204,212,255,.52) 63%,
            rgba(211,192,246,.48) 100%
        );
    box-shadow:
        inset 18px 18px 34px rgba(255,255,255,.62),
        inset -20px -24px 42px rgba(123,132,220,.20),
        0 26px 48px rgba(72,103,171,.24);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    animation: derivaFloat 4.4s ease-in-out infinite;
}

.home-brain-orb::before {
    content: "";
    position: absolute;
    inset: 18px;
    border: 1px solid rgba(255,255,255,.48);
    border-radius: inherit;
}

.home-brain-orb::after {
    content: "";
    position: absolute;
    width: 72px;
    height: 34px;
    top: 22px;
    left: 34px;
    border-radius: 50%;
    background: rgba(255,255,255,.68);
    filter: blur(4px);
    transform: rotate(-18deg);
}

.home-brain-icon {
    position: relative;
    z-index: 3;
    font-size: 92px;
    line-height: 1;
    filter: drop-shadow(0 16px 16px rgba(64,83,150,.20));
    transform: rotate(-4deg);
}

.home-orbit {
    position: absolute;
    z-index: 1;
    width: 250px;
    height: 250px;
    border: 2px solid rgba(255,255,255,.38);
    border-radius: 50%;
    animation: derivaOrbit 9s linear infinite;
}

.home-orbit::before,
.home-orbit::after {
    content: "";
    position: absolute;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: linear-gradient(145deg, #ffffff, #cbbcf5);
    box-shadow: 0 8px 18px rgba(76,103,163,.20);
}

.home-orbit::before {
    top: 18px;
    left: 42px;
}

.home-orbit::after {
    right: 18px;
    bottom: 52px;
}

@keyframes derivaOrbit {
    to {
        transform: rotate(360deg);
    }
}

@keyframes derivaShadowPulse {
    0%,
    100% {
        opacity: .72;
        transform: scaleX(.92);
    }

    50% {
        opacity: .48;
        transform: scaleX(.78);
    }
}

.home-eyebrow,
.home-title,
.home-description,
.home-course,
.home-nova {
    position: relative;
    z-index: 1;
}

.home-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 9px 14px;
    border: 1px solid rgba(255,255,255,.23);
    border-radius: 999px;
    background: rgba(255,255,255,.13);
    font-size: 13px;
    font-weight: 800;
    letter-spacing: .8px;
    text-transform: uppercase;
}

.home-title {
    max-width: 760px;
    margin-top: 22px;
    font-size: clamp(38px, 5vw, 62px);
    line-height: 1.04;
    font-weight: 900;
    letter-spacing: -1.8px;
}

.home-title span {
    color: #dff5ff;
}

.home-description {
    max-width: 720px;
    margin-top: 18px;
    color: rgba(255,255,255,.88);
    font-size: 18px;
    line-height: 1.65;
}

.home-course {
    display: inline-flex;
    gap: 9px;
    margin-top: 25px;
    padding: 11px 15px;
    border-radius: 15px;
    background: rgba(255,255,255,.14);
    color: rgba(255,255,255,.92);
    font-size: 14px;
    font-weight: 750;
}

.home-nova {
    display: flex;
    align-items: center;
    gap: 14px;
    max-width: 620px;
    margin-top: 24px;
    padding: 16px 18px;
    border: 1px solid rgba(255,255,255,.20);
    border-radius: 21px;
    background: rgba(255,255,255,.32);
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,.36),
        0 14px 30px rgba(67,110,160,.10);
    backdrop-filter: blur(12px);
}

.home-nova-avatar {
    display: grid;
    place-items: center;
    flex: 0 0 48px;
    width: 48px;
    height: 48px;
    border-radius: 16px;
    background: rgba(255,255,255,.20);
    font-size: 25px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.25);
}

.home-nova strong {
    display: block;
    color: #24445f;
    font-size: 16px;
    font-weight: 900;
    letter-spacing: -.1px;
}

.home-nova span {
    display: block;
    margin-top: 4px;
    color: #44647d;
    font-size: 14px;
    font-weight: 700;
    line-height: 1.5;
}

.home-section-heading {
    margin: 34px 0 7px;
    color: #243b59;
    font-size: 31px;
    font-weight: 900;
    letter-spacing: -.6px;
}

.home-section-copy {
    margin-bottom: 22px;
    color: #73839a;
    font-size: 16px;
}

.deriva-home-card {
    min-height: 216px;
    padding: 25px;
    margin-bottom: 10px;
    border-radius: 27px;
    border: 1px solid rgba(255,255,255,.96);
    box-shadow: 0 17px 38px rgba(63,83,151,.10);
    transition:
        transform .25s ease,
        box-shadow .25s ease,
        border-color .25s ease;
    animation: derivaFadeUp .65s ease both;
}

.deriva-home-card:hover {
    transform: translateY(-7px);
    box-shadow: 0 25px 48px rgba(63,83,151,.16);
    border-color: rgba(124,106,225,.25);
}

.card-diagnostic {
    background: linear-gradient(145deg, #ecf8ff, #f8fcff);
}

.card-learn {
    background: linear-gradient(145deg, #effcf5, #fbfffd);
}

.card-nova {
    background: linear-gradient(145deg, #fff0fb, #fff9fe);
}

.card-practice {
    background: linear-gradient(145deg, #fff8e8, #fffdf8);
}

.card-image {
    background: linear-gradient(145deg, #eef5ff, #fbfdff);
}

.card-progress {
    background: linear-gradient(145deg, #f1edff, #fbfaff);
}

.deriva-home-card-icon {
    position: relative;
    display: grid;
    place-items: center;
    width: 82px;
    height: 82px;
    margin-bottom: 24px;
    border: 1px solid rgba(255,255,255,.92);
    border-radius: 50%;
    background:
        radial-gradient(
            circle at 30% 24%,
            rgba(255,255,255,.98),
            rgba(255,255,255,.72) 38%,
            rgba(219,232,255,.56) 72%,
            rgba(202,186,245,.40) 100%
        );
    box-shadow:
        inset 10px 10px 18px rgba(255,255,255,.74),
        inset -12px -14px 22px rgba(103,126,214,.12),
        0 18px 30px rgba(68,88,155,.16);
    font-size: 40px;
    filter: saturate(1.05);
    animation: derivaIconFloat 3.8s ease-in-out infinite;
}

.deriva-home-card-icon::after {
    content: "";
    position: absolute;
    width: 42px;
    height: 16px;
    bottom: -18px;
    border-radius: 50%;
    background: rgba(69,91,146,.14);
    filter: blur(8px);
    animation: derivaIconShadow 3.8s ease-in-out infinite;
}

@keyframes derivaIconFloat {
    0%,
    100% {
        transform: translateY(0) rotate(-1deg);
    }

    50% {
        transform: translateY(-10px) rotate(1deg);
    }
}

@keyframes derivaIconShadow {
    0%,
    100% {
        opacity: .62;
        transform: scaleX(1);
    }

    50% {
        opacity: .36;
        transform: scaleX(.78);
    }
}

.deriva-home-card h3 {
    margin: 0;
    color: #243b59;
    font-size: 23px;
    font-weight: 900;
}

.deriva-home-card p {
    min-height: 72px;
    margin: 11px 0 0;
    color: #718097;
    font-size: 15px;
    line-height: 1.62;
}

div[data-testid="stPageLink"] a {
    min-height: 50px;
    margin-bottom: 19px;
    border: 0 !important;
    border-radius: 16px !important;
    background: linear-gradient(
        135deg,
        #6685f4,
        #8b62e9
    ) !important;
    color: white !important;
    font-weight: 850 !important;
    box-shadow:
        0 14px 0 rgba(70,106,168,.10),
        0 20px 34px rgba(87,109,187,.22),
        inset 0 1px 0 rgba(255,255,255,.24);
    transform: translateY(-2px);
    transition:
        transform .22s ease,
        box-shadow .22s ease,
        filter .22s ease;
}

div[data-testid="stPageLink"] a:hover {
    transform: translateY(-7px);
    filter: brightness(1.04);
    box-shadow:
        0 18px 0 rgba(70,106,168,.08),
        0 28px 42px rgba(87,109,187,.28),
        inset 0 1px 0 rgba(255,255,255,.32);
}

div[data-testid="stPageLink"] a:active {
    transform: translateY(-1px);
    box-shadow:
        0 8px 0 rgba(70,106,168,.08),
        0 14px 24px rgba(87,109,187,.20);
}

div[data-testid="stPageLink"] a p,
div[data-testid="stPageLink"] a span {
    color: white !important;
    font-weight: 850 !important;
}

div[data-testid="stButton"] > button:disabled {
    min-height: 50px;
    margin-bottom: 8px;
    border-radius: 16px;
    background: rgba(231,236,246,.86);
    color: #8a96a9;
    border: 1px solid rgba(210,219,233,.94);
    opacity: 1;
}

.home-status {
    display: flex;
    align-items: flex-start;
    gap: 15px;
    padding: 22px;
    margin-top: 18px;
    border-radius: 24px;
    background: rgba(255,255,255,.76);
    border: 1px solid rgba(255,255,255,.97);
    box-shadow: 0 15px 34px rgba(68,88,155,.08);
}

.home-status-icon {
    display: grid;
    place-items: center;
    flex: 0 0 46px;
    width: 46px;
    height: 46px;
    border-radius: 15px;
    background: linear-gradient(135deg, #e0f4ff, #eee4ff);
    font-size: 23px;
}

.home-status strong {
    color: #2c405d;
    font-size: 16px;
}

.home-status p {
    margin: 5px 0 0;
    color: #75849a;
    font-size: 14px;
    line-height: 1.55;
}

.home-footer {
    margin-top: 40px;
    padding-top: 22px;
    border-top: 1px solid rgba(120,139,166,.16);
    color: #8592a5;
    text-align: center;
    font-size: 14px;
}

@keyframes derivaFadeUp {
    from {
        opacity: 0;
        transform: translateY(14px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 980px) {
    .home-hero-layout {
        grid-template-columns: 1fr;
    }

    .home-visual {
        min-height: 260px;
        margin-top: 8px;
    }
}

@media (max-width: 780px) {
    .home-shell {
        padding: 27px 23px;
        border-radius: 26px;
    }

    .home-title {
        font-size: 39px;
    }

    .home-description {
        font-size: 16px;
    }

    .home-visual {
        min-height: 220px;
    }

    .home-brain-orb {
        width: 170px;
        height: 170px;
    }

    .home-brain-icon {
        font-size: 74px;
    }

    .home-orbit {
        width: 205px;
        height: 205px;
    }

    .deriva-home-card {
        min-height: auto;
    }

    .deriva-home-card p {
        min-height: auto;
    }
}
</style>
    """,
    unsafe_allow_html=True,
)


mensaje_nova = (
    "Tu diagnóstico está completado. Ya puedes conversar, "
    "practicar y revisar tu progreso."
    if diagnostico_listo
    else
    "Primero completa tu diagnóstico para que pueda "
    "personalizar tu experiencia de aprendizaje."
)

hero_html = (
    '<section class="home-shell">'
    '<div class="home-hero-layout">'
    '<div class="home-hero-copy">'
    f'<div class="home-eyebrow">{icono_saludo} Experiencia de aprendizaje personalizada</div>'
    f'<div class="home-title">{saludo}, <span>{nombre}</span> 👋</div>'
    '<div class="home-description">'
    'Hoy es una nueva oportunidad para comprender el cálculo, '
    'avanzar a tu ritmo y convertir cada ejercicio en progreso.'
    '</div>'
    f'<div class="home-course">📘 {curso} · Sección {seccion}</div>'
    '<div class="home-nova">'
    '<div class="home-nova-avatar">✨</div>'
    '<div>'
    '<strong>Nova está contigo</strong>'
    f'<span>{mensaje_nova}</span>'
    '</div>'
    '</div>'
    '</div>'
    '<div class="home-visual" aria-hidden="true">'
    '<div class="home-orbit"></div>'
    '<div class="home-brain-orb">'
    '<div class="home-brain-icon">🧠</div>'
    '</div>'
    '</div>'
    '</div>'
    '</section>'
)

st.markdown(
    hero_html,
    unsafe_allow_html=True,
)


st.markdown(
    """
<div class="home-section-heading">
    Explora tu aprendizaje
</div>
<div class="home-section-copy">
    Accede directamente a cada herramienta de DERIVA AI.
</div>
    """,
    unsafe_allow_html=True,
)


fila_uno = st.columns(
    3,
    gap="large",
)

with fila_uno[0]:
    mostrar_acceso(
        icono="📝",
        titulo="Diagnóstico",
        descripcion=(
            "Descubre tu nivel actual y permite que Nova "
            "prepare una ruta adaptada a tus necesidades."
        ),
        pagina="pages/diagnostic.py",
        texto_boton=(
            "Revisar diagnóstico"
            if diagnostico_listo
            else "Comenzar diagnóstico"
        ),
        clase="card-diagnostic",
    )

with fila_uno[1]:
    mostrar_acceso(
        icono="📚",
        titulo="Aprender",
        descripcion=(
            "Explora conceptos de cálculo diferencial con "
            "explicaciones claras y organizadas paso a paso."
        ),
        pagina="pages/learn.py",
        texto_boton="Explorar contenidos",
        clase="card-learn",
    )

with fila_uno[2]:
    mostrar_acceso(
        icono="🤖",
        titulo="Nova",
        descripcion=(
            "Pregunta, razona y recibe acompañamiento de tu "
            "tutora inteligente durante todo el curso."
        ),
        pagina="pages/chat.py",
        texto_boton="Conversar con Nova",
        clase="card-nova",
        habilitado=diagnostico_listo,
        mensaje_bloqueo=(
            "Nova se habilita al completar el diagnóstico."
        ),
    )


fila_dos = st.columns(
    3,
    gap="large",
)

with fila_dos[0]:
    mostrar_acceso(
        icono="🧮",
        titulo="Práctica",
        descripcion=(
            "Resuelve ejercicios adaptativos y recibe "
            "retroalimentación inmediata sobre tus respuestas."
        ),
        pagina="pages/practice.py",
        texto_boton="Comenzar práctica",
        clase="card-practice",
        habilitado=diagnostico_listo,
        mensaje_bloqueo=(
            "La práctica se personaliza después del diagnóstico."
        ),
    )

with fila_dos[1]:
    mostrar_acceso(
        icono="📷",
        titulo="Resolver por imagen",
        descripcion=(
            "Sube una fotografía de un ejercicio y permite que "
            "Nova lo analice y explique paso a paso."
        ),
        pagina="pages/image_solver.py",
        texto_boton="Analizar una imagen",
        clase="card-image",
        habilitado=diagnostico_listo,
        mensaje_bloqueo=(
            "Esta herramienta se habilita después del diagnóstico."
        ),
    )

with fila_dos[2]:
    mostrar_acceso(
        icono="📈",
        titulo="Mi progreso",
        descripcion=(
            "Consulta tus avances, resultados, temas estudiados "
            "y evolución dentro de DERIVA AI."
        ),
        pagina="pages/progress.py",
        texto_boton="Ver mi progreso",
        clase="card-progress",
        habilitado=diagnostico_listo,
        mensaje_bloqueo=(
            "Tu progreso aparecerá después de completar el diagnóstico."
        ),
    )


estado_titulo = (
    "Tu experiencia completa está desbloqueada"
    if diagnostico_listo
    else
    "Tu siguiente paso es el diagnóstico"
)

estado_texto = (
    "Puedes utilizar Nova, practicar, resolver ejercicios por imagen "
    "y consultar tu progreso desde esta página."
    if diagnostico_listo
    else
    "Al completarlo, DERIVA AI conocerá tu nivel y habilitará las "
    "herramientas personalizadas de aprendizaje."
)

st.markdown(
    f"""
<div class="home-status">
    <div class="home-status-icon">
        {"✅" if diagnostico_listo else "🧭"}
    </div>
    <div>
        <strong>{estado_titulo}</strong>
        <p>{estado_texto}</p>
    </div>
</div>

<div class="home-footer">
    ✦ DERIVA AI · Aprende cálculo de forma inteligente
</div>
    """,
    unsafe_allow_html=True,
)