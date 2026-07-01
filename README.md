# 📊 Dashboard — Desigualdade Educacional no Brasil

Projeto extensionista de análise de dados públicos educacionais, cruzando indicadores socioeconômicos e desempenho escolar a partir de bases oficiais do INEP.

---

## Estrutura do projeto

```
dashboard/
├── dashboard.py               # Entrada principal
├── pages/
│   ├── 01_visao_geral.py
│   ├── 02_renda_desempenho.py
│   ├── 03_raca_genero.py
│   ├── 04_publico_privado.py
│   ├── 05_saeb.py
│   └── 06_cruzamento.py
└── data/
    ├── ENEM_Tratado_2023.csv
    ├── ENEM_Tratado_2021.csv
    ├── SAEB_Tratado_2023.csv
    ├── SAEB_Tratado_2021.csv
    └── taxa_rendimento.csv
```

---

## Pré-requisitos

- Python **3.9** ou superior
- pip atualizado

---

## Instalação

**1. Clone o repositório ou extraia os arquivos do projeto**

```bash
cd dashboard
```

**2. (Recomendado) Crie um ambiente virtual**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Instale as dependências**

```bash
pip install -r requirements.txt
```

---

## Dependências (`requirements.txt`)

```
streamlit>=1.35.0
pandas>=2.0.0
numpy>=1.25.0
plotly>=5.18.0
requests>=2.31.0
scikit-learn>=1.3.0
scipy>=1.11.0
missingno>=0.5.2
matplotlib>=3.7.0
seaborn>=0.12.0
```

---

## Bases de dados

Coloque os arquivos CSV processados na pasta `dashboard` antes de executar.

| Arquivo | Origem | Descrição |
|---|---|---|
| `ENEM_Tratado_2023.csv` | INEP | Microdados ENEM 2023 com colunas selecionadas e colunas derivadas (`NOTA_GERAL`, `NO_REGIAO`, `SG_UF`, `RENDA_PERCAPITA`) |
| `ENEM_Tratado_2021.csv` | INEP | Microdados ENEM 2021 — mesma estrutura |
| `SAEB_Tratado_2023.csv` | INEP | Microdados SAEB 2023 com `QTDE_ACERTOS` calculada |
| `SAEB_Tratado_2021.csv` | INEP | Microdados SAEB 2021 — mesma estrutura |
| `taxa_rendimento.csv` | INEP | Taxa de Rendimento Escolar 2021 e 2023 |

> Os arquivos CSV devem usar **separador `;`** e **encoding `latin-1`**, que é o padrão dos microdados do INEP.

---

## Execução

```bash
streamlit run dashboard.py
```

O dashboard abrirá automaticamente no navegador em `http://localhost:8501`.

**Para rodar em tela cheia (recomendado para apresentação em projetor):**
- Pressione `F11` no navegador após abrir

**Para forçar recarregamento após alterações no código:**
- Pressione `R` com a página do dashboard em foco, ou
- Clique em **Rerun** no aviso que aparece no canto superior direito

---

## Observações

- O mapa coroplético (Página 2) requer **conexão com a internet** para baixar o GeoJSON dos estados brasileiros.
- Os dados são carregados com `@st.cache_data` — a primeira execução pode ser mais lenta dependendo do tamanho dos arquivos.
- Em caso de erro de encoding ao carregar os CSVs, tente substituir `latin-1` por `iso-8859-1` no parâmetro `encoding` das funções de carregamento.
