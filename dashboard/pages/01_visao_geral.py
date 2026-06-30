import streamlit as st

st.set_page_config(
    page_title="Visão Geral | Desigualdade Educacional",
    page_icon="📊",
    layout="wide"
)

# =============================================================================
# CSS — tema escuro, fonte Montserrat, otimizado para projeção
# =============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

    .stApp {
        background-color: #0d1b2a;
    }

    html, body, [class*="css"]  {
        font-family: 'Montserrat', sans-serif;
        color: #eef2f6;
        font-size: 120%;
    }

    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        font-size: 2.6rem;
        font-weight: 400;
        color: #b8c4d0;
        max-width: 900px;
        line-height: 1.4;
        margin-bottom: 0.8rem;
    }

    .hero-question {
        font-size: 1.35rem;
        font-weight: 500;
        font-style: italic;
        color: #ffffff;
        border-left: 4px solid #e08a4f;
        padding-left: 1.2rem;
        margin: 1.2rem 0 1.4rem 0;
        max-width: 950px;
        line-height: 1.45;
    }

    .stat-row {
        display: flex;
        gap: 3rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }

    .stat-number {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.6rem;
        font-weight: 600;
        color: #e08a4f;
        line-height: 1.1;
    }

    .stat-label {
        font-size: 1rem;
        font-weight: 500;
        color: #8fa0b3;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .section-title {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin-top: 2.2rem;
        margin-bottom: 1rem;
    }

    .base-card {
        border-radius: 10px;
        padding: 1.4rem 1.7rem;
        margin-bottom: 1.2rem;
        background-color: #1b3a5c;
        border-left: 6px solid var(--accent);
    }

    .base-card-header {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin-bottom: 1rem;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .base-name {
        font-size: 1.65rem;
        font-weight: 700;
        color: #ffffff;
    }

    .base-years {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem;
        font-weight: 500;
        color: #d8e1ea;
        background-color: rgba(255,255,255,0.12);
        padding: 0.25rem 0.8rem;
        border-radius: 5px;
    }

    .spec-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
        gap: 0.7rem 1.6rem;
    }

    .spec-item {
        line-height: 1.3;
    }

    .spec-label {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: var(--accent);
        margin-bottom: 0.1rem;
    }

    .spec-value {
        font-size: 1.05rem;
        font-weight: 400;
        color: #eef2f6;
        line-height: 1.3;
    }

    .relevance-box {
        margin-top: 0.9rem;
        padding-top: 0.7rem;
        border-top: 1px solid rgba(255,255,255,0.12);
    }

    .relevance-label {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: var(--accent);
        margin-bottom: 0.2rem;
    }

    .relevance-text {
        font-size: 1.05rem;
        font-weight: 400;
        color: #d8e1ea;
        line-height: 1.35;
    }

    .simple-card {
        border-radius: 10px;
        padding: 1.3rem 1.7rem;
        background-color: #16314d;
        border-left: 6px solid #5c7691;
        font-size: 1.05rem;
        font-weight: 400;
        color: #d8e1ea;
        line-height: 1.45;
    }

    .simple-card strong {
        font-size: 1.25rem;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# HERO
# =============================================================================

st.markdown('<div class="hero-title">Desigualdade Educacional no Brasil</div>', unsafe_allow_html=True)
st.markdown("""
<ul class="hero-subtitle" style="margin: 0; padding-left: 1.3rem; list-style-type: disc;">
    <li>Análise de dados públicos educacionais cruzando indicadores socioeconômicos e desempenho escolar</li>
    <li>Metodologia CRISP-DM</li>
</ul>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero-question">"Em que medida o nível socioeconômico se relaciona com a desigualdade '
    'de desempenho entre alunos — e como isso varia por raça, gênero e território?"</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="stat-row">
    <div>
        <div class="stat-number">3</div>
        <div class="stat-label">Bases de dados</div>
    </div>
    <div>
        <div class="stat-number">2021/2023</div>
        <div class="stat-label">Período analisado</div>
    </div>
    <div>
        <div class="stat-number">27</div>
        <div class="stat-label">UFs cobertas</div>
    </div>
    <div>
        <div class="stat-number">5</div>
        <div class="stat-label">Regiões do Brasil</div>
    </div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# BASES DE DADOS
# =============================================================================

st.markdown('<div class="section-title">Bases utilizadas</div>', unsafe_allow_html=True)

# --- ENEM ---
st.markdown("""
<div class="base-card" style="--accent:#e08a4f;">
    <div class="base-card-header">
        <div class="base-name">ENEM</div>
        <div class="base-years">2021 · 2023</div>
    </div>
    <div class="spec-grid">
        <div class="spec-item">
            <div class="spec-label">Análise</div>
            <div class="spec-value">Região e UF</div>
        </div>
        <div class="spec-item">
            <div class="spec-label">Participantes</div>
            <div class="spec-value">~4,9 mi válidos</div>
        </div>
        <div class="spec-item">
            <div class="spec-label">Medida socioeconômica</div>
            <div class="spec-value">Questionário enem</div>
        </div>
        <div class="spec-item">
            <div class="spec-label">Fonte</div>
            <div class="spec-value">INEP — Microdados ENEM</div>
        </div>
    </div>
    <div class="relevance-box">
        <div class="relevance-label">Relevância</div>
        <div class="relevance-text">Base principal de desempenho — sustenta os recortes de renda, raça, gênero e tipo de escola.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SAEB ---
st.markdown("""
<div class="base-card" style="--accent:#4fb3bf;">
    <div class="base-card-header">
        <div class="base-name">SAEB</div>
        <div class="base-years">2021 · 2023</div>
    </div>
    <div class="spec-grid">
        <div class="spec-item">
            <div class="spec-label">Análise</div>
            <div class="spec-value">Região, UF e zona urbana/rural</div>
        </div>
        <div class="spec-item">
            <div class="spec-label">Participantes</div>
            <div class="spec-value">~2,9 mi válidos</div>
        </div>
        <div class="spec-item">
            <div class="spec-label">Medida socioeconômica</div>
            <div class="spec-value">INSE do aluno</div>
        </div>
        <div class="spec-item">
            <div class="spec-label">Fonte</div>
            <div class="spec-value">INEP — Microdados SAEB</div>
        </div>
    </div>
    <div class="relevance-box">
        <div class="relevance-label">Relevância</div>
        <div class="relevance-text">Valida a relação INSE-desempenho ainda na educação básica, antes do ENEM.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Taxa de Rendimento ---
st.markdown("""
<div class="simple-card">
    <strong>Taxa de Rendimento Escolar</strong> · 2021 · 2023<br>
    Usada apenas para extrair a <strong>taxa de abandono</strong> por região/UF — complementa a análise
    cruzando desigualdade socioeconômica com evasão escolar.
</div>
""", unsafe_allow_html=True)