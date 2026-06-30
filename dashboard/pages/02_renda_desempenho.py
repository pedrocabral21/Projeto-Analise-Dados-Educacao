import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests

st.set_page_config(
    page_title="Renda e Desempenho | Desigualdade Educacional",
    page_icon="📊",
    layout="wide"
)

# =============================================================================
# CSS — padrão do dashboard
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
    "A": 0.0,   "B": 1320.0,  "C": 1650.0,  "D": 2310.0,
    "E": 2970.0, "F": 3630.0,  "G": 4620.0,  "H": 5940.0,
    "I": 7260.0, "J": 8580.0,  "K": 9900.0,  "L": 11220.0,
    "M": 12540.0,"N": 14520.0, "O": 17820.0, "P": 23100.0, "Q": 26400.0
}

REGIOES = {"1": "Norte", "2": "Nordeste", "3": "Sudeste", "4": "Sul", "5": "Centro-Oeste"}

IDH_UF = {
    "RO": 0.725, "AC": 0.706, "AM": 0.708, "RR": 0.750, "PA": 0.698,
    "AP": 0.708, "TO": 0.740, "MA": 0.676, "PI": 0.697, "CE": 0.715,
    "RN": 0.731, "PB": 0.718, "PE": 0.727, "AL": 0.683, "SE": 0.720,
    "BA": 0.714, "MG": 0.774, "ES": 0.776, "RJ": 0.771, "SP": 0.826,
    "PR": 0.796, "SC": 0.808, "RS": 0.806, "MS": 0.778, "MT": 0.771,
    "GO": 0.764, "DF": 0.844
}

IDH_REGIAO = {
    "Norte": 0.690, "Nordeste": 0.683, "Sudeste": 0.766,
    "Sul": 0.774, "Centro-Oeste": 0.757
}

CORES_REGIAO = {
    "Norte": "#4DA3FF", "Nordeste": "#FF9F1C",
    "Sudeste": "#39D98A", "Sul": "#FF6B6B", "Centro-Oeste": "#C77DFF"
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

LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#16213E",
    font=dict(family="Montserrat", size=13, color="white"),
    hoverlabel=dict(bgcolor="#1B263B", font_size=13, font_color="white"),
    margin=dict(l=60, r=30, t=70, b=70),
    height=500
)


# =============================================================================
# CARREGAMENTO DE DADOS
# =============================================================================

@st.cache_data
def carregar_dados():
    df23 = pd.read_csv("ENEM_Tratado_2023.csv", sep=";", encoding="latin-1")
    df21 = pd.read_csv("ENEM_Tratado_2021.csv", sep=";", encoding="latin-1")
    return df21, df23

@st.cache_data
def carregar_geojson():
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    return requests.get(url).json()


# =============================================================================
# FUNÇÕES DE GRÁFICO
# =============================================================================

def fig_renda(df, ano):
    ordem  = list(RENDA_LABEL.keys())
    media  = df.groupby("Q006")["NOTA_GERAL"].mean().reindex(ordem)
    labels = [str(int(v)) if v > 0 else "Sem renda" for v in RENDA_LABEL.values()]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=media,
        mode="lines+markers+text",
        text=[f"{v:.0f}" for v in media],
        textposition="top center",
        line=dict(color="#4DA3FF", width=4),
        marker=dict(size=9, color="#7CC7FF", line=dict(color="white", width=1.5)),
        fill="tozeroy", fillcolor="rgba(77,163,255,0.12)",
        hovertemplate="<b>%{x}</b><br>Nota média: <b>%{y:.1f}</b><extra></extra>"
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"Desempenho no ENEM {ano} por Faixa de Renda Familiar", x=0.5,
                   font=dict(size=20, color="white")),
        xaxis_title="Faixa de Renda Familiar",
        yaxis_title="Nota Média Geral",
    )
    fig.update_xaxes(tickangle=35, tickfont=dict(color="white", size=11),
                     showgrid=False, zeroline=False)
    fig.update_yaxes(range=[media.min()*0.95, media.max()*1.05],
                     gridcolor="rgba(255,255,255,0.08)", griddash="dot",
                     zeroline=False, tickfont=dict(color="white"))
    return fig


def fig_regiao(df, ano):
    regioes = list(REGIOES.values())
    media   = df.groupby("NO_REGIAO")["NOTA_GERAL"].mean().reindex(regioes)
    cores   = ["#4DA3FF", "#52C7EA", "#39D98A", "#F9C74F", "#FF6B6B"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=regioes, y=media,
        text=[f"{v:.1f}" for v in media], textposition="outside",
        textfont=dict(size=16, color="white"),
        marker=dict(color=cores, line=dict(color="white", width=1)),
        hovertemplate="<b>%{x}</b><br>Nota média: <b>%{y:.1f}</b><extra></extra>"
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"Desempenho Geral no ENEM {ano} por Região", x=0.5,
                   font=dict(size=20, color="white")),
        xaxis_title="Região", yaxis_title="Nota Média Geral",
    )
    fig.update_xaxes(tickfont=dict(color="white", size=15), showgrid=False, zeroline=False)
    fig.update_yaxes(range=[media.min()*0.95, media.max()*1.05],
                     gridcolor="rgba(255,255,255,0.08)", griddash="dot",
                     zeroline=False, tickfont=dict(color="white"))
    return fig


def fig_publico_privado(df, ano):
    regioes   = list(REGIOES.values())
    publica   = df[df["TP_ESCOLA"] == 2]
    privada   = df[df["TP_ESCOLA"] == 3]
    med_pub   = publica.groupby("NO_REGIAO")["NOTA_GERAL"].mean().reindex(regioes)
    med_pri   = privada.groupby("NO_REGIAO")["NOTA_GERAL"].mean().reindex(regioes)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=regioes, y=med_pub, name="Pública",
        marker=dict(color="#4DA3FF", line=dict(color="white", width=1)),
        text=[f"{v:.1f}" for v in med_pub], textposition="outside",
        textfont=dict(size=14, color="white"),
        hovertemplate="<b>%{x}</b><br>Pública: <b>%{y:.1f}</b><extra></extra>"
    ))
    fig.add_trace(go.Bar(
        x=regioes, y=med_pri, name="Privada",
        marker=dict(color="#FF9F1C", line=dict(color="white", width=1)),
        text=[f"{v:.1f}" for v in med_pri], textposition="outside",
        textfont=dict(size=14, color="white"),
        hovertemplate="<b>%{x}</b><br>Privada: <b>%{y:.1f}</b><extra></extra>"
    ))
    fig.update_layout(
        **LAYOUT_BASE, barmode="group",
        title=dict(text=f"ENEM {ano} — Escola Pública × Privada por Região", x=0.5,
                   font=dict(size=20, color="white")),
        xaxis_title="Região", yaxis_title="Nota Média Geral",
        legend=dict(title=dict(text="Tipo de escola", font=dict(size=14)),
                    font=dict(size=13), bgcolor="rgba(0,0,0,0)")
    )
    fig.update_xaxes(tickfont=dict(size=15, color="white"), showgrid=False, zeroline=False)
    fig.update_yaxes(range=[400, 700], gridcolor="rgba(255,255,255,0.08)",
                     griddash="dot", zeroline=False, tickfont=dict(color="white"))
    return fig


def fig_idh_scatter(df, ano):
    media_uf   = df.groupby("SG_UF")["NOTA_GERAL"].mean()
    ufs        = [uf for uf in IDH_UF if uf in media_uf.index]
    idh_vals   = [IDH_UF[uf] for uf in ufs]
    notas_vals = [media_uf[uf] for uf in ufs]
    regs       = [UF_REGIAO[uf] for uf in ufs]

    fig = go.Figure()
    for regiao, cor in CORES_REGIAO.items():
        idx = [i for i, r in enumerate(regs) if r == regiao]
        fig.add_trace(go.Scatter(
            x=[idh_vals[i] for i in idx],
            y=[notas_vals[i] for i in idx],
            mode="markers",
            customdata=[ufs[i] for i in idx],
            name=regiao,
            marker=dict(size=12, color=cor, line=dict(color="white", width=1)),
            hovertemplate="<b>%{customdata}</b><br>IDH: %{x:.3f}<br>Nota: %{y:.1f}<extra></extra>"
        ))

    z      = np.polyfit(idh_vals, notas_vals, 1)
    x_line = np.linspace(min(idh_vals), max(idh_vals), 100)
    fig.add_trace(go.Scatter(
        x=x_line, y=np.poly1d(z)(x_line),
        mode="lines", name="Tendência",
        line=dict(color="white", dash="dash", width=2),
        hoverinfo="skip"
    ))

    fig.update_layout(
        **{**LAYOUT_BASE, "height": 580, "plot_bgcolor": "#22304A"},
        title=dict(text=f"Correlação IDH Estadual × Desempenho no ENEM {ano}", x=0.5,
                   font=dict(size=20, color="white")),
        xaxis_title="IDH Estadual (PNUD 2021)", yaxis_title="Nota Média Geral",
        legend=dict(title="Região", bgcolor="rgba(0,0,0,0)", font=dict(size=14))
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", griddash="dot",
                     tickfont=dict(size=13))
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", griddash="dot",
                     tickfont=dict(size=13))
    return fig


def fig_idh_barras(df):
    regioes   = list(REGIOES.values())
    media_reg = df.groupby("NO_REGIAO")["NOTA_GERAL"].mean().reindex(regioes)
    idh_vals  = [IDH_REGIAO[r] for r in regioes]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=regioes, y=media_reg, name="Nota Média",
        marker=dict(color="#4DA3FF", line=dict(color="white", width=1)),
        text=[f"{v:.1f}" for v in media_reg], textposition="outside",
        textfont=dict(size=15, color="white"),
        hovertemplate="<b>%{x}</b><br>Nota média: <b>%{y:.1f}</b><extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=regioes, y=idh_vals, name="IDH",
        mode="lines+markers+text",
        text=[f"{v:.3f}" for v in idh_vals], textposition="top center",
        textfont=dict(size=14, color="#FFB347"),
        line=dict(color="#FF9F1C", width=4),
        marker=dict(size=10, color="#FF9F1C", line=dict(color="white", width=1)),
        yaxis="y2",
        hovertemplate="<b>%{x}</b><br>IDH: <b>%{y:.3f}</b><extra></extra>"
    ))
    fig.update_layout(
        **{**LAYOUT_BASE, "plot_bgcolor": "#22304A"},
        title=dict(text="Desempenho no ENEM 2023 e IDH por Região", x=0.5,
                   font=dict(size=20, color="white")),
        yaxis=dict(title="Nota Média Geral", titlefont=dict(color="#4DA3FF"),
                   tickfont=dict(color="#4DA3FF"),
                   range=[media_reg.min()*0.95, media_reg.max()*1.05],
                   gridcolor="rgba(255,255,255,0.08)", griddash="dot"),
        yaxis2=dict(title="IDH", titlefont=dict(color="#FF9F1C"),
                    tickfont=dict(color="#FF9F1C"),
                    overlaying="y", side="right", range=[0.65, 0.80]),
        legend=dict(font=dict(size=14), bgcolor="rgba(0,0,0,0)")
    )
    fig.update_xaxes(tickfont=dict(size=15, color="white"), showgrid=False, zeroline=False)
    return fig


def fig_mapa(df, geojson):
    media_uf = df.groupby("SG_UF")["NOTA_GERAL"].mean().reset_index()
    media_uf.columns = ["UF", "Nota"]
    media_uf["Região"] = media_uf["UF"].map(UF_REGIAO)

    fig = px.choropleth(
        media_uf, geojson=geojson, locations="UF",
        featureidkey="properties.sigla", color="Nota",
        color_continuous_scale="Viridis",
        hover_data={"Nota": ":.1f", "Região": True}
    )
    fig.update_traces(
        hovertemplate="<b>%{location}</b><br>Nota Média: %{z:.1f}<br>Região: %{customdata[1]}<extra></extra>"
    )
    fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(
        title=dict(text="Desempenho Médio no ENEM 2023 por UF", x=0.5,
                   font=dict(size=20, color="white")),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white", size=13),
        margin=dict(l=0, r=0, t=60, b=0), height=500,
        coloraxis_colorbar=dict(title="Nota Média",
                                tickfont=dict(color="white"),
                                title_font=dict(color="white"))
    )
    return fig


def fig_top5(df, ano):
    media_uf = df.groupby("SG_UF")["NOTA_GERAL"].mean().reset_index()
    media_uf.columns = ["UF", "Nota"]
    media_uf["IDH"] = media_uf["UF"].map(IDH_UF)
    top5 = media_uf.sort_values("Nota", ascending=False).head(5)

    fig = go.Figure(data=[go.Table(
        header=dict(values=["<b>UF</b>", "<b>Nota Média</b>", "<b>IDH</b>"],
                    fill_color="#1B263B", font=dict(color="white", size=16),
                    align="center", height=40),
        cells=dict(values=[top5["UF"], top5["Nota"].round(1), top5["IDH"].round(3)],
                   fill_color="#22304A", font=dict(color="white", size=15),
                   align="center", height=35)
    )])
    fig.update_layout(
        title=dict(text=f"Top 5 Estados — {ano}", x=0.5,
                   font=dict(color="white", size=20)),
        paper_bgcolor="rgba(0,0,0,0)", height=380,
        margin=dict(l=10, r=10, t=60, b=10)
    )
    return fig


def fig_comparativo(df21, df23):
    regioes  = list(REGIOES.values())
    med_2021 = df21.groupby("NO_REGIAO")["NOTA_GERAL"].mean().reindex(regioes)
    med_2023 = df23.groupby("NO_REGIAO")["NOTA_GERAL"].mean().reindex(regioes)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=regioes, y=med_2021, name="2021",
        marker=dict(color="#7CC7FF", line=dict(color="white", width=1)),
        text=[f"{v:.1f}" for v in med_2021], textposition="outside",
        textfont=dict(size=14, color="white")
    ))
    fig.add_trace(go.Bar(
        x=regioes, y=med_2023, name="2023",
        marker=dict(color="#FF9F1C", line=dict(color="white", width=1)),
        text=[f"{v:.1f}" for v in med_2023], textposition="outside",
        textfont=dict(size=14, color="white")
    ))
    fig.update_layout(
        **{**LAYOUT_BASE, "plot_bgcolor": "#22304A"}, barmode="group",
        title=dict(text="Evolução do ENEM — 2021 vs 2023 por Região", x=0.5,
                   font=dict(size=20, color="white")),
        xaxis_title="Região", yaxis_title="Nota Média Geral",
        legend=dict(title=dict(text="Ano", font=dict(size=14)),
                    font=dict(size=13), bgcolor="rgba(0,0,0,0)")
    )
    fig.update_xaxes(tickfont=dict(size=14, color="white"), showgrid=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", griddash="dot",
                     tickfont=dict(size=13, color="white"))
    return fig


def fig_tabela_comparativa(df21, df23):
    def resumo(df):
        df = df.copy()
        df["RENDA"] = df["Q006"].map(RENDA_LABEL)
        return {
            "nota":   df["NOTA_GERAL"].mean(),
            "partic": df.shape[0],
            "renda":  df["RENDA"].mean()
        }
    r21, r23 = resumo(df21), resumo(df23)

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b>Ano</b>", "<b>Nota Média</b>",
                    "<b>Participantes</b>", "<b>Renda Média Familiar</b>"],
            fill_color="#1B263B", font=dict(color="white", size=16),
            align="center", height=40
        ),
        cells=dict(
            values=[
                ["2021", "2023"],
                [f"{r21['nota']:.1f}", f"{r23['nota']:.1f}"],
                [f"{r21['partic']:,}", f"{r23['partic']:,}"],
                [f"R$ {r21['renda']:.0f}", f"R$ {r23['renda']:.0f}"]
            ],
            fill_color="#22304A", font=dict(color="white", size=15),
            align="center", height=35
        )
    )])
    fig.update_layout(
        title=dict(text="Comparativo ENEM 2021 vs 2023 — Indicadores Gerais",
                   x=0.5, font=dict(size=20, color="white")),
        paper_bgcolor="rgba(0,0,0,0)", height=300,
        margin=dict(l=10, r=10, t=60, b=10)
    )
    return fig


# =============================================================================
# LAYOUT DA PÁGINA
# =============================================================================

st.markdown('<div class="page-title">Renda e Desempenho</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">ENEM 2021 e 2023 — impacto da renda familiar no desempenho dos alunos '
    'por região, tipo de escola e IDH estadual.</div>',
    unsafe_allow_html=True
)

try:
    df21, df23 = carregar_dados()
    geojson    = carregar_geojson()
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

# --------------------------------------------------
# SEÇÃO 1 — Renda x Desempenho
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 1</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Desempenho por Faixa de Renda</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📅 2023", "📅 2021"])
with tab1:
    st.plotly_chart(fig_renda(df23, 2023), use_container_width=True)
with tab2:
    st.plotly_chart(fig_renda(df21, 2021), use_container_width=True)

# --------------------------------------------------
# SEÇÃO 2 — Desempenho por Região
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 2</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Desempenho por Região</div>', unsafe_allow_html=True)

tab3, tab4 = st.tabs(["📅 2023", "📅 2021"])
with tab3:
    st.plotly_chart(fig_regiao(df23, 2023), use_container_width=True)
with tab4:
    st.plotly_chart(fig_regiao(df21, 2021), use_container_width=True)

# --------------------------------------------------
# SEÇÃO 3 — Público vs Privado
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 3</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Escola Pública × Privada por Região</div>', unsafe_allow_html=True)

tab5, tab6 = st.tabs(["📅 2023", "📅 2021"])
with tab5:
    st.plotly_chart(fig_publico_privado(df23, 2023), use_container_width=True)
with tab6:
    st.plotly_chart(fig_publico_privado(df21, 2021), use_container_width=True)

# --------------------------------------------------
# SEÇÃO 4 — IDH x Desempenho
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 4</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">IDH e Desempenho</div>', unsafe_allow_html=True)

st.plotly_chart(fig_idh_barras(df23), use_container_width=True)

tab7, tab8 = st.tabs(["🔵 Scatter 2023", "🔵 Scatter 2021"])
with tab7:
    st.plotly_chart(fig_idh_scatter(df23, 2023), use_container_width=True)
with tab8:
    st.plotly_chart(fig_idh_scatter(df21, 2021), use_container_width=True)

# --------------------------------------------------
# SEÇÃO 5 — Mapa + Top 5
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 5</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Distribuição Geográfica — 2023</div>', unsafe_allow_html=True)

col_mapa, col_top5 = st.columns([1.6, 1])
with col_mapa:
    st.plotly_chart(fig_mapa(df23, geojson), use_container_width=True)
with col_top5:
    st.plotly_chart(fig_top5(df23, 2023), use_container_width=True)

# --------------------------------------------------
# SEÇÃO 6 — Comparativo 2021 x 2023
# --------------------------------------------------
st.markdown('<div class="section-label">Seção 6</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Evolução 2021 → 2023</div>', unsafe_allow_html=True)

st.plotly_chart(fig_comparativo(df21, df23), use_container_width=True)
st.plotly_chart(fig_tabela_comparativa(df21, df23), use_container_width=True)