import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Abandono Escolar | Pública vs. Privada",
    page_icon="📚",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

    .stApp { background-color: #0d1b2a; }

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
        color: #eef2f6;
        font-size: 120%;
    }

    .page-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
        margin-bottom: 0.3rem;
    }

    .page-subtitle {
        font-size: 1.15rem;
        font-weight: 400;
        color: #b8c4d0;
        margin-bottom: 1.2rem;
    }

    .section-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #e08a4f;
        margin-top: 2.2rem;
        margin-bottom: 0.2rem;
    }

    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.8rem;
    }

    div[data-baseweb="tab-list"] {
        background-color: #16304d;
        border-radius: 8px;
        padding: 4px;
    }

    div[data-baseweb="tab"] {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #b8c4d0 !important;
    }

    div[aria-selected="true"] {
        color: #ffffff !important;
        background-color: #e08a4f !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Paleta ────────────────────────────────────────────────────────────────────
DB_BG      = "rgba(0,0,0,0)"
DB_CARD    = "#16213E"
DB_GRID    = "#1E3448"
DB_TEXT    = "#eef2f6"
DB_SUBTEXT = "#b8c4d0"
DB_ORANGE  = "#e08a4f"
COR_2021   = "#818CF8"
COR_2023   = "#EAB308"
COR_PUBLICA  = COR_2021
COR_PRIVADA  = COR_2023
COR_FEDERAL  = "#34D399"

REGIOES_ORDEM = ["Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]

LAYOUT_BASE = dict(
    paper_bgcolor=DB_BG,
    plot_bgcolor=DB_CARD,
    font=dict(family="Montserrat", size=13, color=DB_TEXT),
    hoverlabel=dict(bgcolor="#1B263B", font_size=13, font_color="white"),
    margin=dict(l=60, r=30, t=90, b=90),
    height=520,
)

# ── Dados ─────────────────────────────────────────────────────────────────────
@st.cache_data
def carregar_dados():
    reg21 = pd.read_csv("Taxa_Abandono_REGIAO_2021.csv", sep=";")
    reg23 = pd.read_csv("Taxa_Abandono_REGIAO_2023.csv", sep=";")
    est21 = pd.read_csv("Taxa_Abandono_ESTADO_2021.csv", sep=";")
    est23 = pd.read_csv("Taxa_Abandono_ESTADO_2023.csv", sep=";")

    regioes = pd.concat([reg21, reg23], ignore_index=True)
    estados = pd.concat([est21, est23], ignore_index=True)

    regioes.columns = ["ANO", "UNIDGEO", "DEPENDENCIA", "TX_FUND", "TX_MED"]
    estados.columns = ["ANO", "UNIDGEO", "DEPENDENCIA", "TX_FUND", "TX_MED"]

    return regioes, estados


# ── Gráfico 1 — Barras agrupadas por nível (Fundamental e Médio) ──────────────
def fig_barras_nivel(df_reg, ano):
    """
    Para cada dependência (Pública / Privada / Total):
    barras lado a lado mostrando TX_FUND e TX_MED por região.
    """
    dados = df_reg[
        (df_reg["ANO"] == ano) &
        (df_reg["DEPENDENCIA"].isin(["Pública", "Privada"]))
    ].copy()

    dados["UNIDGEO"] = pd.Categorical(dados["UNIDGEO"], categories=REGIOES_ORDEM, ordered=True)
    dados = dados.sort_values("UNIDGEO")

    y_max = max(dados["TX_FUND"].max(), dados["TX_MED"].max())

    fig = go.Figure()

    cores_dep = {"Pública": COR_PUBLICA, "Privada": COR_PRIVADA}
    patterns   = {"TX_FUND": "", "TX_MED": "/"}
    labels_niv = {"TX_FUND": "Fundamental", "TX_MED": "Médio"}

    for dep in ["Pública", "Privada"]:
        d = dados[dados["DEPENDENCIA"] == dep]
        for col, pattern in patterns.items():
            fig.add_trace(go.Bar(
                x=d["UNIDGEO"],
                y=d[col],
                name=f"{dep} · {labels_niv[col]}",
                marker_color=cores_dep[dep],
                marker_pattern_shape=pattern,
                opacity=0.85,
                legendgroup=f"{dep}-{col}",
                text=d[col].map(lambda v: f"{v:.1f}%"),
                textposition="outside",
                textfont=dict(color=DB_TEXT, size=10),
                hovertemplate=(
                    f"<b>%{{x}} · {dep} · {labels_niv[col]}</b><br>"
                    "Taxa de Abandono: %{y:.1f}%<extra></extra>"
                ),
            ))

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(
            text=(
                f"<b>Taxa de Abandono por Nível e Dependência — {ano}</b><br>"
                f"<span style='color:{DB_SUBTEXT};font-size:12px'>"
                "Barras sólidas = Ens. Fundamental · barras hachuradas = Ens. Médio</span>"
            ),
            x=0.03,
            font=dict(color=DB_TEXT, family="Montserrat"),
        ),
        barmode="group",
        xaxis=dict(
            tickfont=dict(color=DB_SUBTEXT, size=12),
            gridcolor=DB_GRID, linecolor=DB_GRID,
            categoryorder="array", categoryarray=REGIOES_ORDEM,
        ),
        yaxis=dict(
            title=dict(text="Taxa de Abandono (%)", font=dict(color=DB_SUBTEXT, size=12)),
            tickfont=dict(color=DB_SUBTEXT),
            gridcolor=DB_GRID, linecolor=DB_GRID,
            zeroline=False,
            range=[0, y_max * 1.22],
            ticksuffix="%",
        ),
        legend=dict(
            title=dict(text="Dependência · Nível", font=dict(color=DB_TEXT)),
            orientation="h", x=0, y=-0.18,
            font=dict(color=DB_TEXT, size=12),
            bgcolor="rgba(0,0,0,0)",
            bordercolor=DB_ORANGE, borderwidth=1,
        ),
    )
    return fig



def fig_comparativo_anos(df_reg):
    """
    Barras agrupadas: eixo X = regiões, grupos = (Pública 2021, Pública 2023,
    Privada 2021, Privada 2023), dois sub-gráficos: Fundamental e Médio.
    """
    dados = df_reg[df_reg["DEPENDENCIA"].isin(["Pública", "Privada"])].copy()
    dados["UNIDGEO"] = pd.Categorical(dados["UNIDGEO"], categories=REGIOES_ORDEM, ordered=True)
    dados = dados.sort_values("UNIDGEO")

    cores_ano  = {2021: COR_2021,   2023: COR_2023}
    pattern_dep = {"Pública": "",    "Privada": "/"}

    def _traces(col, show_legend):
        traces = []
        for dep in ["Pública", "Privada"]:
            for ano in [2021, 2023]:
                d = dados[(dados["DEPENDENCIA"] == dep) & (dados["ANO"] == ano)]
                traces.append(go.Bar(
                    x=d["UNIDGEO"],
                    y=d[col],
                    name=f"{dep} · {ano}",
                    marker_color=cores_ano[ano],
                    marker_pattern_shape=pattern_dep[dep],
                    opacity=0.85,
                    legendgroup=f"{dep}-{ano}",
                    showlegend=show_legend,
                    text=d[col].map(lambda v: f"{v:.1f}%"),
                    textposition="outside",
                    textfont=dict(color=DB_TEXT, size=10),
                    hovertemplate=(
                        f"<b>%{{x}} · {dep} · {ano}</b><br>"
                        f"Taxa ({'Fundamental' if col == 'TX_FUND' else 'Médio'}): "
                        "%{y:.1f}%<extra></extra>"
                    ),
                ))
        return traces

    y_max_fund = dados["TX_FUND"].max()
    y_max_med  = dados["TX_MED"].max()

    # Ensino Fundamental
    fig_fund = go.Figure(_traces("TX_FUND", show_legend=True))
    fig_fund.update_layout(
        **{**LAYOUT_BASE, "height": 500, "margin": dict(l=60, r=30, t=90, b=110)},
        title=dict(
            text=(
                "<b>Comparativo 2021 × 2023 — Abandono no Ensino Fundamental</b><br>"
                f"<span style='color:{DB_SUBTEXT};font-size:12px'>"
                "Por região e rede · barras hachuradas = Privada</span>"
            ),
            x=0.03, font=dict(color=DB_TEXT, family="Montserrat"),
        ),
        barmode="group",
        xaxis=dict(
            tickfont=dict(color=DB_SUBTEXT, size=12),
            gridcolor=DB_GRID, linecolor=DB_GRID,
            categoryorder="array", categoryarray=REGIOES_ORDEM,
        ),
        yaxis=dict(
            title=dict(text="Taxa de Abandono (%)", font=dict(color=DB_SUBTEXT, size=12)),
            tickfont=dict(color=DB_SUBTEXT),
            gridcolor=DB_GRID, linecolor=DB_GRID,
            zeroline=False, range=[0, y_max_fund * 1.22],
            ticksuffix="%",
        ),
        legend=dict(
            title=dict(text="Rede · Ano", font=dict(color=DB_TEXT)),
            orientation="h", x=0, y=-0.2,
            font=dict(color=DB_TEXT, size=12),
            bgcolor="rgba(0,0,0,0)",
            bordercolor=DB_ORANGE, borderwidth=1,
        ),
    )

  
    fig_med = go.Figure(_traces("TX_MED", show_legend=True))
    fig_med.update_layout(
        **{**LAYOUT_BASE, "height": 500, "margin": dict(l=60, r=30, t=90, b=110)},
        title=dict(
            text=(
                "<b>Comparativo 2021 × 2023 — Abandono no Ensino Médio</b><br>"
                f"<span style='color:{DB_SUBTEXT};font-size:12px'>"
                "Por região e rede · barras hachuradas = Privada</span>"
            ),
            x=0.03, font=dict(color=DB_TEXT, family="Montserrat"),
        ),
        barmode="group",
        xaxis=dict(
            tickfont=dict(color=DB_SUBTEXT, size=12),
            gridcolor=DB_GRID, linecolor=DB_GRID,
            categoryorder="array", categoryarray=REGIOES_ORDEM,
        ),
        yaxis=dict(
            title=dict(text="Taxa de Abandono (%)", font=dict(color=DB_SUBTEXT, size=12)),
            tickfont=dict(color=DB_SUBTEXT),
            gridcolor=DB_GRID, linecolor=DB_GRID,
            zeroline=False, range=[0, y_max_med * 1.22],
            ticksuffix="%",
        ),
        legend=dict(
            title=dict(text="Rede · Ano", font=dict(color=DB_TEXT)),
            orientation="h", x=0, y=-0.2,
            font=dict(color=DB_TEXT, size=12),
            bgcolor="rgba(0,0,0,0)",
            bordercolor=DB_ORANGE, borderwidth=1,
        ),
    )

    return fig_fund, fig_med



st.markdown('<div class="page-title">Abandono Escolar — Escola Pública vs. Privada</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">'
    'Censo Escolar 2021 e 2023 — taxa de abandono por nível de ensino, '
    'rede administrativa e região.'
    '</div>',
    unsafe_allow_html=True
)

try:
    df_reg, df_est = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

# --------------------------------------------------
#Gráfico1 — Barras por nível e dependência

st.markdown('<div class="section-label">Seção 1</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-title">Taxa de Abandono por Nível e Rede — Fundamental vs. Médio</div>',
    unsafe_allow_html=True
)

tab1, tab2 = st.tabs(["📅 2021", "📅 2023"])
with tab1:
    st.plotly_chart(fig_barras_nivel(df_reg, 2021), use_container_width=True)
with tab2:
    st.plotly_chart(fig_barras_nivel(df_reg, 2023), use_container_width=True)

# --------------------------------------------------
#Gráfico 2 — Comparativo 2021 × 2023 por dependência

st.markdown('<div class="section-label">Seção 2</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-title">Comparativo 2021 × 2023 por Dependência Administrativa</div>',
    unsafe_allow_html=True
)

fig_fund, fig_med = fig_comparativo_anos(df_reg)

tab3, tab4 = st.tabs(["📘 Ensino Fundamental", "📗 Ensino Médio"])
with tab3:
    st.plotly_chart(fig_fund, use_container_width=True)
with tab4:
    st.plotly_chart(fig_med, use_container_width=True)
