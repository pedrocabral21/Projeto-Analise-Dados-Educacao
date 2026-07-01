import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="Raça e Gênero | Desigualdade Educacional",
    page_icon="👥",
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


# =============================================================================
# CONSTANTES
# =============================================================================

RENDA_LABEL = {
    "A": "Sem renda",
    "B": "até R$1.320",
    "C": "R$1.320–1.650",
    "D": "R$1.650–2.310",
    "E": "R$2.310–2.970",
    "F": "R$2.970–3.630",
    "G": "R$3.630–4.620",
    "H": "R$4.620–5.940",
    "I": "R$5.940–7.260",
    "J": "R$7.260–8.580",
    "K": "R$8.580–9.900",
    "L": "R$9.900–11.220",
    "M": "R$11.220–12.540",
    "N": "R$12.540–14.520",
    "O": "R$14.520–17.820",
    "P": "R$17.820–23.100",
    "Q": "acima de R$23.100"
}
RENDA_ORDEM = list(RENDA_LABEL.keys())
RENDA_TEXTO = list(RENDA_LABEL.values())

COR_RACA_MAP = {
    0: "Não declarado",
    1: "Branca",
    2: "Preta",
    3: "Parda",
    4: "Amarela",
    5: "Indígena",
    6: "Código 6",   # poucos participantes — filtrado depois
}
SEXO_MAP = {"M": "Masculino", "F": "Feminino"}
ESCOLA_MAP = {1: "Não respondeu", 2: "Pública", 3: "Privada", 4: "Exterior"}

RACE_COLORS = {
    "Branca": "#4DA3FF",
    "Parda": "#52C7EA",
    "Preta": "#39D98A",
    "Amarela": "#F9C74F",
    "Indígena": "#FF6B6B",
}
GENDER_COLORS = {
    "Feminino": "#FF6B6B",
    "Masculino": "#F9C74F",
}
CHART_COLORS = ["#4DA3FF", "#52C7EA", "#39D98A", "#F9C74F", "#FF6B6B"]

LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#16213E",
    font=dict(family="Montserrat", size=13, color="white"),
    hoverlabel=dict(bgcolor="#1B263B", font_size=13, font_color="white"),
    margin=dict(l=60, r=30, t=70, b=70),
    height=500
)


# =============================================================================
# CARREGAMENTO E PREPARAÇÃO DOS DADOS
# =============================================================================

def preparar_df(df, ano):
    """Padroniza um dos CSVs tratados gerados pelo notebook de limpeza."""
    df = df.copy()

    if "NOTA_GERAL" not in df.columns:
        cols_notas = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
        cols_notas = [c for c in cols_notas if c in df.columns]
        df["NOTA_GERAL"] = df[cols_notas].mean(axis=1)

    df["Raça/Cor"] = df["TP_COR_RACA"].map(COR_RACA_MAP)
    df["Gênero"] = df["TP_SEXO"].map(SEXO_MAP).fillna(df["TP_SEXO"])
    df["Tipo de Escola"] = df["TP_ESCOLA"].map(ESCOLA_MAP)
    df["NU_ANO"] = ano

    # remove grupos residuais (ex.: "Código 6", com pouquíssimos registros)
    contagem = df["Raça/Cor"].value_counts()
    grupos_residuais = contagem[contagem < 30].index.tolist()
    df = df[~df["Raça/Cor"].isin(grupos_residuais)]

    return df.dropna(subset=["NOTA_GERAL"])


@st.cache_data
def carregar_dados():
    df23 = pd.read_csv("ENEM_Tratado_2023.csv", sep=";", encoding="latin-1")
    df21 = pd.read_csv("ENEM_Tratado_2021.csv", sep=";", encoding="latin-1")
    return preparar_df(df21, 2021), preparar_df(df23, 2023)


def calcular_gaps(df21, df23):
    """Calcula gap racial (cada raça vs Branca) e gap de gênero (M - F), 2021 e 2023."""
    linhas = []
    for ano, df in [(2021, df21), (2023, df23)]:
        if df is None or df.empty:
            continue

        medias_raca = df.groupby("Raça/Cor")["NOTA_GERAL"].mean()
        if "Branca" in medias_raca.index:
            base_branca = medias_raca["Branca"]
            for raca, media in medias_raca.items():
                if raca == "Branca":
                    continue
                linhas.append({
                    "Ano": ano, "Tipo": "Racial",
                    "Comparação": raca,
                    "Gap (pontos)": base_branca - media,
                })

        medias_sexo = df.groupby("Gênero")["NOTA_GERAL"].mean()
        if "Masculino" in medias_sexo.index and "Feminino" in medias_sexo.index:
            linhas.append({
                "Ano": ano, "Tipo": "Gênero",
                "Comparação": "Masculino vs Feminino",
                "Gap (pontos)": medias_sexo["Masculino"] - medias_sexo["Feminino"],
            })

    return pd.DataFrame(linhas)


# =============================================================================
# FUNÇÕES DE GRÁFICO
# =============================================================================

def fig_boxplot_raca(df, ano, escola_label):
    df_plot = df[df["Raça/Cor"] != "Não declarado"].copy()
    if escola_label != "Todas":
        df_plot = df_plot[df_plot["Tipo de Escola"] == escola_label]

    race_order = (
        df_plot.groupby("Raça/Cor")["NOTA_GERAL"].median()
        .sort_values(ascending=False).index.tolist()
    )

    fig = go.Figure()
    for race in race_order:
        df_race = df_plot[df_plot["Raça/Cor"] == race]
        fig.add_trace(go.Box(
            y=df_race["NOTA_GERAL"], name=race,
            marker_color=RACE_COLORS.get(race, "#6b7280"),
            line=dict(color=RACE_COLORS.get(race, "#6b7280"))
        ))

    fig.update_layout(
        **LAYOUT_BASE, showlegend=False,
        title=dict(text=f"Distribuição de Notas por Raça/Cor — ENEM {ano}", x=0.5,
                   font=dict(size=20, color="white")),
        xaxis_title="Raça/Cor", yaxis_title="Nota Geral",
    )
    fig.update_xaxes(tickfont=dict(color="white", size=13), showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", griddash="dot",
                     zeroline=False, tickfont=dict(color="white"))
    return fig


def fig_genero_escola(df, ano):
    df_agg = df[df["Tipo de Escola"] != "Exterior"].groupby(
        ["Gênero", "Tipo de Escola"]
    )["NOTA_GERAL"].mean().reset_index()

    fig = go.Figure()
    for genero in ["Feminino", "Masculino"]:
        df_genero = df_agg[df_agg["Gênero"] == genero]
        fig.add_trace(go.Bar(
            name=genero, x=df_genero["Tipo de Escola"], y=df_genero["NOTA_GERAL"],
            marker=dict(color=GENDER_COLORS[genero], line=dict(color="white", width=1)),
            text=[f"{v:.1f}" for v in df_genero["NOTA_GERAL"]], textposition="outside",
            textfont=dict(size=14, color="white"),
            hovertemplate="<b>%{x}</b><br>Nota média: <b>%{y:.1f}</b><extra></extra>"
        ))

    fig.update_layout(
        **LAYOUT_BASE, barmode="group",
        title=dict(text=f"Nota Média por Gênero e Tipo de Escola — ENEM {ano}", x=0.5,
                   font=dict(size=20, color="white")),
        xaxis_title="Tipo de Escola", yaxis_title="Nota Média",
        legend=dict(title=dict(text="Gênero", font=dict(size=14)),
                    font=dict(size=13), bgcolor="rgba(0,0,0,0)")
    )
    fig.update_xaxes(tickfont=dict(size=14, color="white"), showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", griddash="dot",
                     zeroline=False, tickfont=dict(color="white"))
    return fig


def fig_raca_renda(df, ano):
    agg = df.groupby(["Raça/Cor", "Q006"], as_index=False)["NOTA_GERAL"].mean()
    agg["Q006"] = pd.Categorical(agg["Q006"], categories=RENDA_ORDEM, ordered=True)
    agg = agg.sort_values(["Raça/Cor", "Q006"])
    agg["Q006_num"] = agg["Q006"].cat.codes

    fig = go.Figure()
    for race in ["Branca", "Parda", "Preta", "Amarela", "Indígena"]:
        df_race = agg[agg["Raça/Cor"] == race]
        if df_race.empty:
            continue
        fig.add_trace(go.Scatter(
            x=df_race["Q006_num"], y=df_race["NOTA_GERAL"], name=race,
            mode="lines+markers",
            line=dict(color=RACE_COLORS[race], width=3),
            marker=dict(size=8, color=RACE_COLORS[race], line=dict(color="white", width=1)),
            hovertemplate="<b>" + race + "</b><br>Nota média: <b>%{y:.1f}</b><extra></extra>"
        ))

    fig.update_layout(
        **{**LAYOUT_BASE, "plot_bgcolor": "#22304A"},
        title=dict(text=f"Nota Média por Raça/Cor e Faixa de Renda — ENEM {ano}", x=0.5,
                   font=dict(size=20, color="white")),
        xaxis_title="Faixa de Renda Familiar", yaxis_title="Nota Média",
        legend=dict(title=dict(text="Raça/Cor", font=dict(size=14)),
                    font=dict(size=13), bgcolor="rgba(0,0,0,0)")
    )
    fig.update_xaxes(tickmode="array", tickvals=list(range(len(RENDA_ORDEM))),
                     ticktext=RENDA_TEXTO, tickangle=-45,
                     tickfont=dict(color="white", size=11), showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", griddash="dot",
                     zeroline=False, tickfont=dict(color="white"))
    return fig


def fig_scatter_renda_genero(df, ano):
    df_scatter = df[df["Q006"].notna()].groupby(
        ["Q006", "Gênero"]
    )["NOTA_GERAL"].mean().reset_index()
    df_scatter["Q006"] = pd.Categorical(df_scatter["Q006"], categories=RENDA_ORDEM, ordered=True)
    df_scatter = df_scatter.sort_values("Q006")
    df_scatter["Q006_num"] = df_scatter["Q006"].cat.codes

    fig = go.Figure()
    for genero in ["Feminino", "Masculino"]:
        df_genero = df_scatter[df_scatter["Gênero"] == genero]
        if df_genero.empty:
            continue
        fig.add_trace(go.Scatter(
            x=df_genero["Q006_num"], y=df_genero["NOTA_GERAL"], name=genero,
            mode="markers", marker=dict(size=10, color=GENDER_COLORS[genero],
                                        line=dict(color="white", width=1)),
            hovertemplate="<b>" + genero + "</b><br>Nota média: <b>%{y:.1f}</b><extra></extra>"
        ))

        x = df_genero["Q006_num"].values.astype(float)
        y = df_genero["NOTA_GERAL"].values.astype(float)
        if len(x) >= 2:
            slope, intercept = np.polyfit(x, y, 1)
            line_x = np.array([x.min(), x.max()])
            line_y = slope * line_x + intercept
            fig.add_trace(go.Scatter(
                x=line_x, y=line_y, mode="lines",
                line=dict(color=GENDER_COLORS[genero], width=2, dash="dash"),
                showlegend=False, hoverinfo="skip"
            ))

    fig.update_layout(
        **{**LAYOUT_BASE, "plot_bgcolor": "#22304A"},
        title=dict(text=f"Renda Familiar × Nota Média por Gênero — ENEM {ano}", x=0.5,
                   font=dict(size=20, color="white")),
        xaxis_title="Faixa de Renda Familiar", yaxis_title="Nota Média",
        legend=dict(title=dict(text="Gênero", font=dict(size=14)),
                    font=dict(size=13), bgcolor="rgba(0,0,0,0)")
    )
    fig.update_xaxes(tickmode="array", tickvals=list(range(len(RENDA_ORDEM))),
                     ticktext=RENDA_TEXTO, tickangle=-45,
                     tickfont=dict(color="white", size=11), showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", griddash="dot",
                     zeroline=False, tickfont=dict(color="white"))
    return fig


def fig_gap_racial(gaps_df):
    df_racial = gaps_df[gaps_df["Tipo"] == "Racial"]

    fig = go.Figure()
    for i, ano in enumerate([2021, 2023]):
        df_ano = df_racial[df_racial["Ano"] == ano]
        fig.add_trace(go.Bar(
            name=str(ano), x=df_ano["Comparação"], y=df_ano["Gap (pontos)"],
            text=[f"{v:.1f}" for v in df_ano["Gap (pontos)"]], textposition="outside",
            textfont=dict(size=13, color="white"),
            marker=dict(color=CHART_COLORS[i], line=dict(color="white", width=1)),
            hovertemplate="<b>%{x}</b><br>Gap: <b>%{y:.1f}</b> pts<extra></extra>"
        ))

    fig.update_layout(
        **{**LAYOUT_BASE, "height": 460, "margin": dict(l=60, r=30, t=100, b=70)},
        title=dict(text="Gaps Raciais vs Branca — 2021 e 2023", 
                   x=0.03,  # alinha à esquerda
                   font=dict(size=18, color="white")),
        legend=dict(title=dict(text="Ano", font=dict(size=14)),
                    font=dict(size=13), bgcolor="rgba(0,0,0,0)")
    )
    fig.update_xaxes(tickfont=dict(size=13, color="white"), showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", griddash="dot",
                     zeroline=True, zerolinecolor="rgba(255,255,255,0.25)",
                     tickfont=dict(color="white"))
    return fig


def fig_gap_genero(gaps_df):
    df_genero = gaps_df[gaps_df["Tipo"] == "Gênero"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_genero["Ano"].astype(str), y=df_genero["Gap (pontos)"],
        text=[f"{v:.2f}" for v in df_genero["Gap (pontos)"]], textposition="outside",
        textfont=dict(size=14, color="white"),
        marker=dict(color="#e08a4f", line=dict(color="white", width=1)),
        hovertemplate="<b>%{x}</b><br>Gap (M-F): <b>%{y:.2f}</b> pts<extra></extra>"
    ))

    fig.update_layout(
        **{**LAYOUT_BASE, "height": 460, "margin": dict(l=60, r=30, t=100, b=70)},
        title=dict(text="Gap de Gênero (Masculino − Feminino)",
                   x=0.03, 
                   font=dict(size=18, color="white")),
        xaxis_title="Ano", yaxis_title="Gap (pontos)", showlegend=False
    )
    fig.update_xaxes(tickfont=dict(size=14, color="white"), showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", griddash="dot",
                     zeroline=True, zerolinecolor="rgba(255,255,255,0.25)",
                     tickfont=dict(color="white"))
    return fig


# =============================================================================
# LAYOUT DA PÁGINA
# =============================================================================

st.markdown('<div class="page-title">Raça e Gênero</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">ENEM 2021 e 2023 — desigualdade de desempenho por raça/cor, '
    'gênero e sua relação com renda familiar e tipo de escola.</div>',
    unsafe_allow_html=True
)

try:
    df21, df23 = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

gaps_df = calcular_gaps(df21, df23)
tem_2021 = not df21.empty

# --------------------------------------------------
# SEÇÃO 1 — Distribuição de notas por raça/cor
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 1</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Distribuição de Notas por Raça/Cor</div>', unsafe_allow_html=True)

opcoes_escola = ["Todas"] + sorted(
    set(df23["Tipo de Escola"].dropna().unique()) | set(df21["Tipo de Escola"].dropna().unique())
)
escola_filtro = st.selectbox("Filtrar por Tipo de Escola:", opcoes_escola, index=0)

tab1, tab2 = st.tabs(["📅 2023", "📅 2021"])
with tab1:
    st.plotly_chart(fig_boxplot_raca(df23, 2023, escola_filtro), use_container_width=True)
with tab2:
    if tem_2021:
        st.plotly_chart(fig_boxplot_raca(df21, 2021, escola_filtro), use_container_width=True)
    else:
        st.info("ENEM_Tratado_2021.csv não encontrado — gráfico indisponível.")

# --------------------------------------------------
# SEÇÃO 2 — Nota média por gênero e tipo de escola
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 2</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Gênero e Tipo de Escola</div>', unsafe_allow_html=True)

tab3, tab4 = st.tabs(["📅 2023", "📅 2021"])
with tab3:
    st.plotly_chart(fig_genero_escola(df23, 2023), use_container_width=True)
with tab4:
    if tem_2021:
        st.plotly_chart(fig_genero_escola(df21, 2021), use_container_width=True)
    else:
        st.info("ENEM_Tratado_2021.csv não encontrado — gráfico indisponível.")

# --------------------------------------------------
# SEÇÃO 3 — Raça/Cor x Faixa de Renda
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 3</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Raça/Cor por Faixa de Renda</div>', unsafe_allow_html=True)

tab5, tab6 = st.tabs(["📅 2023", "📅 2021"])
with tab5:
    st.plotly_chart(fig_raca_renda(df23, 2023), use_container_width=True)
with tab6:
    if tem_2021:
        st.plotly_chart(fig_raca_renda(df21, 2021), use_container_width=True)
    else:
        st.info("ENEM_Tratado_2021.csv não encontrado — gráfico indisponível.")

# --------------------------------------------------
# SEÇÃO 4 — Renda x Gênero
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 4</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Renda Familiar × Gênero</div>', unsafe_allow_html=True)

tab7, tab8 = st.tabs(["🔵 2023", "🔵 2021"])
with tab7:
    st.plotly_chart(fig_scatter_renda_genero(df23, 2023), use_container_width=True)
with tab8:
    if tem_2021:
        st.plotly_chart(fig_scatter_renda_genero(df21, 2021), use_container_width=True)
    else:
        st.info("ENEM_Tratado_2021.csv não encontrado — gráfico indisponível.")

# --------------------------------------------------
# SEÇÃO 5 — Evolução dos gaps 2021 → 2023
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 5</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Evolução dos Gaps (2021 → 2023)</div>', unsafe_allow_html=True)

if tem_2021 and not gaps_df.empty:
    col_racial, col_genero = st.columns(2)
    with col_racial:
        st.plotly_chart(fig_gap_racial(gaps_df), use_container_width=True)
    with col_genero:
        st.plotly_chart(fig_gap_genero(gaps_df), use_container_width=True)
else:
    st.info("ENEM_Tratado_2021.csv não encontrado — comparativo indisponível.")