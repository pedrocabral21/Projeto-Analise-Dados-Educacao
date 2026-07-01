import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="SAEB | Desigualdade Educacional",
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



DB_BG      = "rgba(0,0,0,0)"       
DB_CARD    = "#16213E"
DB_GRID    = "#1E3448"
DB_TEXT    = "#eef2f6"
DB_SUBTEXT = "#b8c4d0"
DB_ORANGE  = "#e08a4f"
COR_2021   = "#818CF8"           
COR_2023   = "#EAB308"            
CORES_TIPO = {"Pública": COR_2021, "Privada": COR_2023}

LAYOUT_BASE = dict(
    paper_bgcolor=DB_BG,
    plot_bgcolor=DB_CARD,
    font=dict(family="Montserrat", size=13, color=DB_TEXT),
    hoverlabel=dict(bgcolor="#1B263B", font_size=13, font_color="white"),
    margin=dict(l=60, r=30, t=80, b=80),
    height=520,
)

REGIOES_ORDEM = ["Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]



@st.cache_data
def carregar_dados():
    df21 = pd.read_csv("SAEB_Tratado_2021.csv")
    df21["ANO"] = 2021
    df23 = pd.read_csv("SAEB_Tratado_2023.csv")
    df23["ANO"] = 2023
    df = pd.concat([df21, df23], ignore_index=True)

    REGIOES = {1: "Norte", 2: "Nordeste", 3: "Sudeste", 4: "Sul", 5: "Centro-Oeste"}
    ESCOLA  = {1: "Pública", 0: "Privada"}

    df["REGIAO_NOME"] = df["ID_REGIAO"].map(REGIOES)
    df["ESCOLA_TIPO"] = df["IN_PUBLICA"].map(ESCOLA)
    return df


#funções


def fig_scatter(df, ano):
    SAMPLE = 15_000
    dados = (
        df[df["ANO"] == ano]
        .dropna(subset=["INSE_ALUNO", "ACERTOS_TOTAIS"])
        .sample(min(SAMPLE, len(df[df["ANO"] == ano])), random_state=42)
        .copy()
    )
    cor = COR_2021 if ano == 2021 else COR_2023

    np.random.seed(42)
    y_jitter = dados["ACERTOS_TOTAIS"] + np.random.uniform(-0.45, 0.45, len(dados))

    dados["INSE_BIN"] = pd.cut(dados["INSE_ALUNO"], bins=60)
    media_bin = (
        dados.groupby("INSE_BIN", observed=True)
             .agg(INSE_MED=("INSE_ALUNO", "mean"),
                  ACERTOS_MED=("ACERTOS_TOTAIS", "mean"),
                  N=("ACERTOS_TOTAIS", "count"))
             .dropna().reset_index()
    )

    coef   = np.polyfit(dados["INSE_ALUNO"], dados["ACERTOS_TOTAIS"], 1)
    x_line = np.linspace(dados["INSE_ALUNO"].min(), dados["INSE_ALUNO"].max(), 100)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dados["INSE_ALUNO"], y=y_jitter, mode="markers",
        name="Alunos (amostra)",
        marker=dict(color=cor, size=3, opacity=0.20),
        hovertemplate="INSE: %{x:.2f}<br>Acertos: %{customdata}<extra></extra>",
        customdata=dados["ACERTOS_TOTAIS"].values,
    ))
    fig.add_trace(go.Scatter(
        x=media_bin["INSE_MED"], y=media_bin["ACERTOS_MED"], mode="lines",
        name="Média por faixa",
        line=dict(color=DB_ORANGE, width=3),
        hovertemplate="Faixa INSE ≈ %{x:.2f}<br>Média: %{y:.1f}<br>N: %{customdata}<extra></extra>",
        customdata=media_bin["N"].values,
    ))
    fig.add_trace(go.Scatter(
        x=x_line, y=np.polyval(coef, x_line), mode="lines",
        name="Regressão linear",
        line=dict(color="#FFFFFF", width=1.5, dash="dot"),
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(
            text=(f"<b>Nível Socioeconômico × Desempenho — {ano}</b><br>"
                  f"<span style='color:{DB_SUBTEXT};font-size:12px'>"
                  f"INSE vs. Acertos Totais · amostra de {SAMPLE:,} alunos</span>"),
            x=0.03, font=dict(color=DB_TEXT, family="Montserrat"),
        ),
        xaxis=dict(title=dict(text="INSE do Aluno", font=dict(color=DB_SUBTEXT, size=12)),
                   tickfont=dict(color=DB_SUBTEXT), gridcolor=DB_GRID,
                   zeroline=False, range=[2, 7.8], linecolor=DB_GRID),
        yaxis=dict(title=dict(text="Acertos Totais (LP + MT)", font=dict(color=DB_SUBTEXT, size=12)),
                   tickfont=dict(color=DB_SUBTEXT), gridcolor=DB_GRID,
                   zeroline=False, range=[-1, 53], linecolor=DB_GRID),
        legend=dict(orientation="h", y=-0.16, x=0,
                    font=dict(color=DB_TEXT, size=12), bgcolor="rgba(0,0,0,0)"),
        annotations=[dict(
            x=0.98, y=0.06, xref="paper", yref="paper",
            text=f"<b>β = {coef[0]:.2f}</b>  acertos / ponto INSE",
            showarrow=False,
            font=dict(color=DB_ORANGE, size=12, family="Montserrat"),
            bgcolor="#0d1b2a", bordercolor=DB_ORANGE, borderwidth=1, borderpad=6,
        )],
    )
    return fig


def fig_histograma(df, ano):
    cor = COR_2021 if ano == 2021 else COR_2023
    BINS = list(range(0, 53, 1))

    fig = make_subplots(
        rows=5, cols=1,
        subplot_titles=[f"<b>{r}</b>" for r in REGIOES_ORDEM],
        shared_xaxes=True,
        vertical_spacing=0.06,
    )

    for row_idx, regiao in enumerate(REGIOES_ORDEM, start=1):
        dados = (
            df[(df["REGIAO_NOME"] == regiao) & (df["ANO"] == ano)]
            ["ACERTOS_TOTAIS"].dropna()
        )
        if dados.empty:
            continue

        counts, edges = np.histogram(dados, bins=BINS)
        pct = counts / counts.sum() * 100
        x_centers = (edges[:-1] + edges[1:]) / 2
        media = dados.mean()

        fig.add_trace(go.Bar(
            x=x_centers, y=pct,
            name=regiao, marker_color=cor, opacity=0.75, width=0.8,
            showlegend=False,
            hovertemplate=(f"<b>{regiao}</b><br>Acertos: %{{x}}<br>"
                           "% alunos: %{y:.2f}%<extra></extra>"),
        ), row=row_idx, col=1)

        fig.add_vline(x=media, line_dash="dot", line_color=DB_ORANGE,
                      line_width=1.5, row=row_idx, col=1)

        fig.add_annotation(
            x=0.98, y=0.82,
            xref="x domain" if row_idx == 1 else f"x{row_idx} domain",
            yref="y domain" if row_idx == 1 else f"y{row_idx} domain",
            text=f"<b>μ = {media:.1f}</b>",
            showarrow=False,
            font=dict(color=DB_ORANGE, size=11, family="Montserrat"),
            bgcolor="#0d1b2a", bordercolor=DB_ORANGE, borderwidth=1, borderpad=4,
        )

    for i in range(1, 6):
        fig.update_yaxes(
            title_text="% alunos" if i == 3 else "",
            gridcolor=DB_GRID, ticksuffix="%",
            tickfont=dict(color=DB_SUBTEXT, size=11),
            title_font=dict(color=DB_SUBTEXT, size=12),
            linecolor=DB_GRID, row=i, col=1,
        )
    fig.update_xaxes(
        title_text="Total de Acertos (LP + MT)",
        gridcolor=DB_GRID, range=[-0.5, 51.5],
        tickfont=dict(color=DB_SUBTEXT, size=11),
        title_font=dict(color=DB_SUBTEXT, size=12),
        linecolor=DB_GRID, row=5, col=1,
    )
    for ann in fig.layout.annotations:
        ann.font = dict(color=DB_TEXT, size=13, family="Montserrat")

    fig.update_layout(
        paper_bgcolor=DB_BG, plot_bgcolor=DB_CARD,
        title=dict(
            text=(f"<b>Distribuição de Acertos por Região — {ano}</b><br>"
                  f"<span style='color:{DB_SUBTEXT};font-size:12px'>"
                  "Cada painel = uma região · linha laranja = média</span>"),
            x=0.03, y=0.97, font=dict(color=DB_TEXT, family="Montserrat"),
        ),
        barmode="overlay",
        font=dict(family="Montserrat", size=13, color=DB_TEXT),
        height=1100,
        margin=dict(l=60, r=40, t=120, b=60),
    )
    return fig


def fig_barras_inse(df, ano):
    inse_reg = (
        df[df["ANO"] == ano]
        .groupby(["REGIAO_NOME", "ESCOLA_TIPO"])["INSE_ALUNO"]
        .mean().reset_index()
        .rename(columns={"INSE_ALUNO": "INSE_MEDIO"})
    )
    y_max = inse_reg["INSE_MEDIO"].max()

    fig = go.Figure()
    for tipo in ["Pública", "Privada"]:
        d = inse_reg[inse_reg["ESCOLA_TIPO"] == tipo].sort_values("REGIAO_NOME")
        fig.add_trace(go.Bar(
            x=d["REGIAO_NOME"], y=d["INSE_MEDIO"],
            name=tipo, marker_color=CORES_TIPO[tipo], opacity=0.85,
            text=d["INSE_MEDIO"].round(2), textposition="outside",
            textfont=dict(color=DB_TEXT, size=11),
            hovertemplate=f"<b>%{{x}} · {tipo}</b><br>INSE Médio: %{{y:.2f}}<extra></extra>",
        ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(
            text=(f"<b>INSE Médio por Região — {ano}</b><br>"
                  f"<span style='color:{DB_SUBTEXT};font-size:12px'>"
                  "Pública vs. Privada</span>"),
            x=0.03, font=dict(color=DB_TEXT, family="Montserrat"),
        ),
        barmode="group",
        xaxis=dict(tickfont=dict(color=DB_SUBTEXT, size=12),
                   gridcolor=DB_GRID, linecolor=DB_GRID,
                   categoryorder="array", categoryarray=REGIOES_ORDEM),
        yaxis=dict(title=dict(text="INSE Médio", font=dict(color=DB_SUBTEXT, size=12)),
                   tickfont=dict(color=DB_SUBTEXT), gridcolor=DB_GRID,
                   linecolor=DB_GRID, zeroline=False, range=[0, y_max * 1.18]),
        legend=dict(title=dict(text="Escola", font=dict(color=DB_TEXT)),
                    orientation="h", x=0, y=-0.15,
                    font=dict(color=DB_TEXT, size=12), bgcolor="rgba(0,0,0,0)",
                    bordercolor=DB_ORANGE, borderwidth=1),
    )
    return fig


def fig_comparativo(df):
    acertos_comp = (
        df.groupby(["ANO", "REGIAO_NOME", "ESCOLA_TIPO"])
          .agg(ACERTOS_TOTAIS=("ACERTOS_TOTAIS", "mean"))
          .reset_index()
    )
    y_max = acertos_comp["ACERTOS_TOTAIS"].max()

    fig = go.Figure()
    for tipo, pattern in [("Pública", ""), ("Privada", "/")]:
        for ano, cor in [(2021, COR_2021), (2023, COR_2023)]:
            d = (acertos_comp[
                    (acertos_comp["ESCOLA_TIPO"] == tipo) &
                    (acertos_comp["ANO"] == ano)
                 ].sort_values("REGIAO_NOME"))
            fig.add_trace(go.Bar(
                x=d["REGIAO_NOME"], y=d["ACERTOS_TOTAIS"],
                name=f"{ano} · {tipo}",
                marker_color=cor,
                marker_pattern_shape=pattern,
                opacity=0.85, legendgroup=f"{ano}-{tipo}",
                text=d["ACERTOS_TOTAIS"].round(1), textposition="outside",
                textfont=dict(color=DB_TEXT, size=10),
                hovertemplate=(f"<b>%{{x}} · {tipo} · {ano}</b><br>"
                               "Acertos médios: %{y:.1f}<extra></extra>"),
            ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(
            text=("<b>Comparativo 2021 × 2023 — Acertos Médios</b><br>"
                  f"<span style='color:{DB_SUBTEXT};font-size:12px'>"
                  "Por região e tipo de escola · barras hachuradas = Privada</span>"),
            x=0.03, font=dict(color=DB_TEXT, family="Montserrat"),
        ),
        barmode="group",
        xaxis=dict(title=dict(text="Região", font=dict(color=DB_SUBTEXT, size=12)),
                   tickfont=dict(color=DB_SUBTEXT, size=12),
                   gridcolor=DB_GRID, linecolor=DB_GRID,
                   categoryorder="array", categoryarray=REGIOES_ORDEM),
        yaxis=dict(title=dict(text="Acertos Médios (LP + MT)", font=dict(color=DB_SUBTEXT, size=12)),
                   tickfont=dict(color=DB_SUBTEXT), gridcolor=DB_GRID,
                   linecolor=DB_GRID, zeroline=False, range=[0, y_max * 1.18]),
        legend=dict(title=dict(text="Ano · Escola", font=dict(color=DB_TEXT)),
                    orientation="h", x=0, y=-0.15,
                    font=dict(color=DB_TEXT, size=12), bgcolor="rgba(0,0,0,0)",
                    bordercolor=DB_ORANGE, borderwidth=1),
        height=520,
        margin=dict(l=60, r=40, t=100, b=100),
    )
    return fig


# =============================================================================
# LAYOUT DA PÁGINA
# =============================================================================
st.markdown('<div class="page-title">SAEB — Ensino Básico</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">SAEB 2021 e 2023 — relação entre nível socioeconômico e desempenho '
    'dos alunos por região e tipo de escola.</div>',
    unsafe_allow_html=True
)

try:
    df = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

# --------------------------------------------------
# gráfico 1 — Scatter INSE × Acertos
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 1</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Nível Socioeconômico × Desempenho</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📅 2021", "📅 2023"])
with tab1:
    st.plotly_chart(fig_scatter(df, 2021), use_container_width=True)
with tab2:
    st.plotly_chart(fig_scatter(df, 2023), use_container_width=True)

# --------------------------------------------------
# gráfico 2 — Histograma por Região
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 2</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Distribuição de Acertos por Região</div>', unsafe_allow_html=True)

tab3, tab4 = st.tabs(["📅 2021", "📅 2023"])
with tab3:
    st.plotly_chart(fig_histograma(df, 2021), use_container_width=True)
with tab4:
    st.plotly_chart(fig_histograma(df, 2023), use_container_width=True)

# --------------------------------------------------
# gráfico 3 — INSE médio por região
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 3</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">INSE Médio por Região e Tipo de Escola</div>', unsafe_allow_html=True)

tab5, tab6 = st.tabs(["📅 2021", "📅 2023"])
with tab5:
    st.plotly_chart(fig_barras_inse(df, 2021), use_container_width=True)
with tab6:
    st.plotly_chart(fig_barras_inse(df, 2023), use_container_width=True)

# --------------------------------------------------
# gráfico 4 — Comparativo 2021 × 2023
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 4</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Comparativo 2021 × 2023</div>', unsafe_allow_html=True)

st.plotly_chart(fig_comparativo(df), use_container_width=True)
