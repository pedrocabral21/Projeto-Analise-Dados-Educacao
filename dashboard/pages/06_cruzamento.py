import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Cruzamento das Bases | Desigualdade Educacional",
    page_icon="🔗",
    layout="wide"
)

# =============================================================================
# CSS — padrão do dashboard (idêntico às demais páginas)
# =============================================================================

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

    .insight-box {
        background-color: #16304d;
        border-left: 4px solid #e08a4f;
        border-radius: 6px;
        padding: 1rem 1.2rem;
        margin: 1rem 0 1.6rem 0;
        color: #dce6ef;
        font-size: 0.98rem;
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


# =============================================================================
# CONSTANTES
# =============================================================================

REGIOES = {"1": "Norte", "2": "Nordeste", "3": "Sudeste", "4": "Sul", "5": "Centro-Oeste"}

ID_UF_MAP = {
    11: "RO", 12: "AC", 13: "AM", 14: "RR", 15: "PA", 16: "AP", 17: "TO",
    21: "MA", 22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE",
    27: "AL", 28: "SE", 29: "BA",
    31: "MG", 32: "ES", 33: "RJ", 35: "SP",
    41: "PR", 42: "SC", 43: "RS",
    50: "MS", 51: "MT", 52: "GO", 53: "DF"
}

UF_REGIAO = {
    "RO": "Norte",    "AC": "Norte",    "AM": "Norte",    "RR": "Norte",
    "PA": "Norte",    "AP": "Norte",    "TO": "Norte",
    "MA": "Nordeste", "PI": "Nordeste", "CE": "Nordeste", "RN": "Nordeste",
    "PB": "Nordeste", "PE": "Nordeste", "AL": "Nordeste", "SE": "Nordeste",
    "BA": "Nordeste",
    "MG": "Sudeste",  "ES": "Sudeste",  "RJ": "Sudeste",  "SP": "Sudeste",
    "PR": "Sul",      "SC": "Sul",      "RS": "Sul",
    "MS": "Centro-Oeste", "MT": "Centro-Oeste",
    "GO": "Centro-Oeste", "DF": "Centro-Oeste"
}

NOME_UF = {
    "RO": "Rondônia",            "AC": "Acre",                "AM": "Amazonas",
    "RR": "Roraima",             "PA": "Pará",                "AP": "Amapá",
    "TO": "Tocantins",           "MA": "Maranhão",            "PI": "Piauí",
    "CE": "Ceará",               "RN": "Rio Grande do Norte", "PB": "Paraíba",
    "PE": "Pernambuco",          "AL": "Alagoas",             "SE": "Sergipe",
    "BA": "Bahia",               "MG": "Minas Gerais",        "ES": "Espírito Santo",
    "RJ": "Rio de Janeiro",      "SP": "São Paulo",           "PR": "Paraná",
    "SC": "Santa Catarina",      "RS": "Rio Grande do Sul",   "MS": "Mato Grosso do Sul",
    "MT": "Mato Grosso",         "GO": "Goiás",               "DF": "Distrito Federal"
}

# Mapa reverso: nome do estado (como aparece na planilha do INEP) -> sigla
UF_POR_NOME = {v: k for k, v in NOME_UF.items()}

CORES_REGIAO = {
    "Norte": "#4DA3FF", "Nordeste": "#FF9F1C",
    "Sudeste": "#39D98A", "Sul": "#FF6B6B", "Centro-Oeste": "#C77DFF"
}

CORES_ANO = {"2021": "#7CC7FF", "2023": "#FF9F1C"}

LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#16213E",
    font=dict(family="Montserrat", size=13, color="white"),
    hoverlabel=dict(bgcolor="#1B263B", font_size=13, font_color="white"),
    margin=dict(l=60, r=30, t=70, b=70),
    height=520
)


# =============================================================================
# CARREGAMENTO E PREPARAÇÃO DOS DADOS
# =============================================================================

@st.cache_data
def carregar_enem():
    df23 = pd.read_csv("ENEM_Tratado_2023.csv", sep=";", encoding="latin-1")
    df21 = pd.read_csv("ENEM_Tratado_2021.csv", sep=";", encoding="latin-1")
    return df21, df23


@st.cache_data
def carregar_saeb():
    df23 = pd.read_csv("SAEB_Tratado_2023.csv")
    df21 = pd.read_csv("SAEB_Tratado_2021.csv")
    for df in (df23, df21):
        df["SG_UF"] = df["ID_UF"].map(ID_UF_MAP)
    return df21, df23


@st.cache_data
def carregar_abandono():
    df23 = pd.read_csv("Taxa_Abandono_ESTADO_2023.csv", sep=";")
    df21 = pd.read_csv("Taxa_Abandono_ESTADO_2021.csv", sep=";")
    for df in (df23, df21):
        df["SG_UF"] = df["UNIDGEO"].map(UF_POR_NOME)
        df["3_CAT_MED"] = pd.to_numeric(df["3_CAT_MED"], errors="coerce")
    return df21, df23

@st.cache_data
def montar_base_cruzada(df_enem, df_saeb, df_abandono):
    """Agrega as três bases por UF em um único dataframe."""
    nota_uf = df_enem.groupby("SG_UF")["NOTA_GERAL"].mean().rename("NOTA_ENEM")
    inse_uf = df_saeb.groupby("SG_UF")["INSE_ALUNO"].mean().rename("INSE_MEDIO")

    aband = df_abandono[df_abandono["NO_DEPENDENCIA"] == "Total"]
    aband_uf = aband.groupby("SG_UF")["3_CAT_MED"].mean().rename("TAXA_ABANDONO")

    base = pd.concat([nota_uf, inse_uf, aband_uf], axis=1).dropna().reset_index()
    base = base.rename(columns={"index": "SG_UF"})
    base["Regiao"] = base["SG_UF"].map(UF_REGIAO)
    base["Estado"] = base["SG_UF"].map(NOME_UF)
    return base


# =============================================================================
# FUNÇÕES DE GRÁFICO
# =============================================================================

def _scatter_base(base, x_col, y_col, x_title, y_title, titulo, ano, altura=520):
    fig = go.Figure()

    for regiao, cor in CORES_REGIAO.items():
        sub = base[base["Regiao"] == regiao]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub[x_col], y=sub[y_col],
            mode="markers",
            name=regiao,
            customdata=np.stack([sub["Estado"], sub["SG_UF"]], axis=-1),
            marker=dict(size=14, color=cor, line=dict(color="white", width=1.5)),
            hovertemplate="<b>%{customdata[0]} (%{customdata[1]})</b><br>"
                          f"{x_title}: " + "%{x:.2f}<br>"
                          f"{y_title}: " + "%{y:.1f}<extra></extra>"
        ))

    if base[x_col].nunique() > 1:
        z = np.polyfit(base[x_col], base[y_col], 1)
        x_line = np.linspace(base[x_col].min(), base[x_col].max(), 100)
        fig.add_trace(go.Scatter(
            x=x_line, y=np.poly1d(z)(x_line),
            mode="lines", name="Tendência",
            line=dict(color="white", dash="dash", width=2),
            hoverinfo="skip"
        ))

    fig.update_layout(
        **{**LAYOUT_BASE, "height": altura, "plot_bgcolor": "#22304A"},
        title=dict(text=f"{titulo} — {ano}", x=0.5, font=dict(size=19, color="white")),
        xaxis_title=x_title, yaxis_title=y_title,
        legend=dict(title="Região", bgcolor="rgba(0,0,0,0)", font=dict(size=13))
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", griddash="dot", tickfont=dict(size=12))
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", griddash="dot", tickfont=dict(size=12))
    return fig


def fig_inse_enem(base, ano):
    return _scatter_base(
        base, "INSE_MEDIO", "NOTA_ENEM",
        "INSE Médio (SAEB)", "Nota Média ENEM",
        "INSE Médio (SAEB) × Nota Média ENEM por UF", ano
    )


def fig_abandono_inse(base, ano):
    return _scatter_base(
        base, "INSE_MEDIO", "TAXA_ABANDONO",
        "INSE Médio (SAEB)", "Taxa de Abandono — Ens. Médio (%)",
        "Taxa de Abandono × INSE Médio por UF", ano
    )


def fig_abandono_enem(base, ano):
    return _scatter_base(
        base, "TAXA_ABANDONO", "NOTA_ENEM",
        "Taxa de Abandono — Ens. Médio (%)", "Nota Média ENEM",
        "Taxa de Abandono × Nota Média ENEM por UF", ano
    )


def fig_painel_comparativo(base21, base23):
    """Painel 2x3 comparando as três relações entre 2021 e 2023."""
    especificacoes = [
        ("INSE_MEDIO", "NOTA_ENEM", "INSE × Nota ENEM"),
        ("INSE_MEDIO", "TAXA_ABANDONO", "INSE × Abandono"),
        ("TAXA_ABANDONO", "NOTA_ENEM", "Abandono × Nota ENEM"),
    ]

    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[f"{t} — 2021" for _, _, t in especificacoes] +
                        [f"{t} — 2023" for _, _, t in especificacoes],
        horizontal_spacing=0.07, vertical_spacing=0.18
    )

    for col, (x_col, y_col, _) in enumerate(especificacoes, start=1):
        for row, (base, ano) in enumerate([(base21, "2021"), (base23, "2023")], start=1):
            z = np.polyfit(base[x_col], base[y_col], 1) if base[x_col].nunique() > 1 else None

            fig.add_trace(
                go.Scatter(
                    x=base[x_col], y=base[y_col],
                    mode="markers",
                    marker=dict(size=10, color=CORES_ANO[ano], line=dict(color="white", width=1)),
                    customdata=np.stack([base["Estado"], base["SG_UF"]], axis=-1),
                    hovertemplate="<b>%{customdata[0]} (%{customdata[1]})</b><br>"
                                  "X: %{x:.2f}<br>Y: %{y:.1f}<extra></extra>",
                    showlegend=False,
                    name=ano
                ),
                row=row, col=col
            )

            if z is not None:
                x_line = np.linspace(base[x_col].min(), base[x_col].max(), 50)
                fig.add_trace(
                    go.Scatter(
                        x=x_line, y=np.poly1d(z)(x_line),
                        mode="lines",
                        line=dict(color="white", dash="dash", width=1.5),
                        hoverinfo="skip", showlegend=False
                    ),
                    row=row, col=col
                )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#22304A",
        font=dict(family="Montserrat", size=12, color="white"),
        hoverlabel=dict(bgcolor="#1B263B", font_size=12, font_color="white"),
        margin=dict(l=40, r=30, t=80, b=40),
        height=680,
        title=dict(text="Painel Comparativo 2021 × 2023 — As Três Relações da Desigualdade Educacional",
                   x=0.5, font=dict(size=20, color="white"))
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", griddash="dot", tickfont=dict(size=10))
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", griddash="dot", tickfont=dict(size=10))
    fig.update_annotations(font=dict(size=13, color="#e08a4f"))
    return fig


def calcular_correlacoes(base):
    return {
        "inse_enem": base["INSE_MEDIO"].corr(base["NOTA_ENEM"]),
        "abandono_inse": base["INSE_MEDIO"].corr(base["TAXA_ABANDONO"]),
        "abandono_enem": base["TAXA_ABANDONO"].corr(base["NOTA_ENEM"]),
    }


# =============================================================================
# LAYOUT DA PÁGINA
# =============================================================================

st.markdown('<div class="page-title">Cruzamento das Bases</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">SAEB × ENEM × Taxa de Abandono — a resposta direta à questão de pesquisa: '
    'nível socioeconômico, evasão e desempenho caminham juntos entre os estados brasileiros?</div>',
    unsafe_allow_html=True
)

try:
    df21_enem, df23_enem = carregar_enem()
    df21_saeb, df23_saeb = carregar_saeb()
    df21_aband, df23_aband = carregar_abandono()

    base21 = montar_base_cruzada(df21_enem, df21_saeb, df21_aband)
    base23 = montar_base_cruzada(df23_enem, df23_saeb, df23_aband)
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

# --------------------------------------------------
# SEÇÃO 1 — INSE (SAEB) × Nota ENEM
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 1</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">INSE Médio (SAEB) × Nota Média ENEM por UF</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📅 2023", "📅 2021"])
with tab1:
    st.plotly_chart(fig_inse_enem(base23, 2023), use_container_width=True)
    corr = calcular_correlacoes(base23)["inse_enem"]
    st.markdown(f'<div class="insight-box">Correlação entre INSE médio e nota do ENEM em 2023: '
                f'<b>{corr:.2f}</b>. Quanto mais próximo de 1, mais forte a relação entre nível '
                f'socioeconômico e desempenho.</div>', unsafe_allow_html=True)
with tab2:
    st.plotly_chart(fig_inse_enem(base21, 2021), use_container_width=True)
    corr = calcular_correlacoes(base21)["inse_enem"]
    st.markdown(f'<div class="insight-box">Correlação entre INSE médio e nota do ENEM em 2021: '
                f'<b>{corr:.2f}</b>.</div>', unsafe_allow_html=True)

# --------------------------------------------------
# SEÇÃO 2 — Taxa de Abandono × INSE
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 2</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Taxa de Abandono × INSE Médio por UF</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="insight-box">Quanto maior o nível socioeconômico médio da UF, menor tende a ser '
    'a taxa de abandono no Ensino Médio? Os pontos abaixo respondem essa pergunta.</div>',
    unsafe_allow_html=True
)

tab3, tab4 = st.tabs(["📅 2023", "📅 2021"])
with tab3:
    st.plotly_chart(fig_abandono_inse(base23, 2023), use_container_width=True)
with tab4:
    st.plotly_chart(fig_abandono_inse(base21, 2021), use_container_width=True)

# --------------------------------------------------
# SEÇÃO 3 — Taxa de Abandono × Nota ENEM
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 3</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Taxa de Abandono × Nota Média ENEM por UF</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="insight-box">Evasão escolar e desempenho no ENEM andam juntos? Estados com maior '
    'abandono no Ensino Médio tendem a apresentar notas médias mais baixas.</div>',
    unsafe_allow_html=True
)

tab5, tab6 = st.tabs(["📅 2023", "📅 2021"])
with tab5:
    st.plotly_chart(fig_abandono_enem(base23, 2023), use_container_width=True)
with tab6:
    st.plotly_chart(fig_abandono_enem(base21, 2021), use_container_width=True)

# --------------------------------------------------
# SEÇÃO 4 — Painel Comparativo 2021 × 2023
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 4</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">A Desigualdade Piorou ou Melhorou?</div>', unsafe_allow_html=True)

st.plotly_chart(fig_painel_comparativo(base21, base23), use_container_width=True)

corr21 = calcular_correlacoes(base21)
corr23 = calcular_correlacoes(base23)

col1, col2, col3 = st.columns(3)
with col1:
    delta = corr23["inse_enem"] - corr21["inse_enem"]
    st.metric("Correlação INSE × Nota ENEM", f"{corr23['inse_enem']:.2f}",
              delta=f"{delta:+.2f} vs. 2021")
with col2:
    delta = corr23["abandono_inse"] - corr21["abandono_inse"]
    st.metric("Correlação Abandono × INSE", f"{corr23['abandono_inse']:.2f}",
              delta=f"{delta:+.2f} vs. 2021", delta_color="inverse")
with col3:
    delta = corr23["abandono_enem"] - corr21["abandono_enem"]
    st.metric("Correlação Abandono × Nota ENEM", f"{corr23['abandono_enem']:.2f}",
              delta=f"{delta:+.2f} vs. 2021", delta_color="inverse")

st.markdown(
    '<div class="insight-box">Os coeficientes de correlação de Pearson acima resumem a força de cada '
    'relação nos dois anos. Valores de correlação mais próximos de +1 ou -1 indicam relações mais fortes; '
    'valores próximos de 0 indicam pouca relação. A comparação entre 2021 e 2023 mostra se a associação '
    'entre nível socioeconômico, evasão e desempenho ficou mais forte (desigualdade mais estrutural) ou '
    'mais fraca (maior equalização entre estados) no período.</div>',
    unsafe_allow_html=True
)