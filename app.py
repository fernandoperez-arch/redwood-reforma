import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import json
import io
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from fpdf import FPDF

# ── Configuração da página ───────────────────────────────────────────────────
_FAVICON = os.path.join(os.path.dirname(__file__), "assets", "logo_redwood_vertical.png")
st.set_page_config(
    page_title="Projeção da Reforma Tributária | RedWood",
    page_icon=_FAVICON if os.path.exists(_FAVICON) else "🌲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Cores RedWood ────────────────────────────────────────────────────────────
RW = {
    "dark_red":   "#6B2D2D",
    "navy":       "#1B1F3B",
    "beige":      "#D5C4A1",
    "light_beige":"#E8DCC8",
    "bg":         "#F5F0EB",
    "white":      "#FFFFFF",
    "green":      "#2E7D32",
    "amber":      "#F57F17",
    "text":       "#333333",
}

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700;800&display=swap');

  /* ── Esconde TODA a chrome do Streamlit Cloud ─────────────────────────────
     Inclui: menu hambúrguer, avatar/perfil, status widget, "Manage app",
     "Deploy" button, viewer badge ("Made with Streamlit"), decoração superior. */
  #MainMenu, footer,
  header, .stApp > header,
  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stStatusWidget"],
  [data-testid="stDecoration"],
  [data-testid="stAppDeployButton"],
  [data-testid="stAppViewBlockContainer"] > div:first-child > [data-testid="stToolbar"],
  .stDeployButton,
  .stAppDeployButton,
  div[class*="viewerBadge"],
  div[class*="_profileContainer_"],
  div[class*="profileContainer"],
  a[href*="streamlit.io/cloud"],
  button[title*="View profile"],
  button[title*="Manage"],
  button[kind="header"],
  iframe[title*="manage"] {{
    display:none !important;
    visibility:hidden !important;
    height:0 !important;
    width:0 !important;
    pointer-events:none !important;
  }}
  .block-container {{ padding-top:1.2rem !important; padding-bottom:2rem !important; }}

  .stApp {{ background-color:{RW['bg']}; }}

  /* ── Tipografia Figtree em toda a aplicação ─────────────────────────────── */
  /* IMPORTANTE: NÃO incluir span/div universalmente — quebra os ícones do
     Material Symbols (setinhas dos expanders viram texto "arrow_drop_down"). */
  html, body, .stApp, .stMarkdown, .stMarkdown p, .stMarkdown li,
  .stTextInput input, .stNumberInput input, .stTextArea textarea,
  .stSelectbox label, .stSlider label, button,
  h1, h2, h3, h4, h5, h6, label, p {{
    font-family:'Figtree','Inter','Segoe UI',-apple-system,sans-serif !important;
  }}
  /* Inputs e botões herdam Figtree */
  input, textarea, select {{
    font-family:'Figtree','Inter','Segoe UI',-apple-system,sans-serif !important;
  }}
  /* PRESERVA fontes de ícones — Material Symbols (NÃO incluir svg/* aqui:
     isso quebra os textos dos gráficos Plotly) */
  span[class*="material-symbols"],
  span[class*="MaterialSymbols"],
  span[class*="material-icons"],
  span.material-symbols-outlined,
  span.material-symbols-rounded,
  span.material-icons,
  span.material-icons-outlined,
  i.material-icons,
  i[class*="material"] {{
    font-family:'Material Symbols Outlined','Material Symbols Rounded',
                'Material Icons','Material Icons Outlined' !important;
  }}
  /* Plotly: força Figtree em todos os textos SVG dos gráficos */
  .js-plotly-plot text, .js-plotly-plot tspan,
  .plot-container text, .plot-container tspan,
  .main-svg text, .main-svg tspan {{
    font-family:'Figtree','Inter','Segoe UI',sans-serif !important;
    text-transform:none !important;
    letter-spacing:normal !important;
  }}
  h1,h2,h3,h4 {{ letter-spacing:-.3px; }}

  /* ── Sidebar — força fundo navy escuro (multi-selector p/ versões novas Streamlit) ── */
  section[data-testid="stSidebar"],
  div[data-testid="stSidebar"],
  [data-testid="stSidebar"],
  [data-testid="stSidebar"] > div,
  [data-testid="stSidebarContent"],
  [data-testid="stSidebarUserContent"] {{
    background: linear-gradient(180deg,#0F1228 0%,{RW['navy']} 50%,#2A2F52 100%) !important;
  }}
  /* Garante que blocos internos não cubram o gradiente */
  [data-testid="stSidebar"] [data-testid="stVerticalBlock"],
  [data-testid="stSidebar"] [data-testid="block-container"] {{
    background:transparent !important;
  }}
  /* Cor de texto branca/bege em todos os labels e markdowns da sidebar */
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] .stMarkdown,
  [data-testid="stSidebar"] .stMarkdown p,
  [data-testid="stSidebar"] .stMarkdown h1,
  [data-testid="stSidebar"] .stMarkdown h2,
  [data-testid="stSidebar"] .stMarkdown h3,
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stTextInput label,
  [data-testid="stSidebar"] .stTextArea label,
  [data-testid="stSidebar"] .stNumberInput label,
  [data-testid="stSidebar"] .stSlider label,
  [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
  [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
    color:{RW['white']} !important;
  }}
  /* Inputs da sidebar — fundo claro + texto navy escuro (legível) */
  [data-testid="stSidebar"] .stTextInput input,
  [data-testid="stSidebar"] .stNumberInput input,
  [data-testid="stSidebar"] .stTextArea textarea,
  [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {{
    background:#FFFFFF !important;
    color:{RW['navy']} !important;
    font-weight:500 !important;
  }}
  /* Slider track na sidebar */
  [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] {{ color:{RW['beige']}; }}
  /* Caixa de dica/ajuda no sidebar — bem legível sobre navy */
  .hint-box {{
    background:rgba(255,255,255,.08);
    border:1px solid rgba(213,196,161,.35);
    border-radius:10px;
    padding:.75rem .85rem;
    color:#F5EBD9 !important;
    font-size:.82rem !important;
    line-height:1.7;
    margin:.2rem 0 .9rem 0;
  }}
  .hint-box b {{ color:#FFFFFF !important; }}
  .hint-box code {{
    background:#FFFFFF !important;
    color:{RW['dark_red']} !important;
    padding:.1rem .4rem !important;
    border-radius:4px !important;
    font-size:.78rem !important;
    font-weight:700 !important;
    font-family:'JetBrains Mono','Courier New',monospace !important;
    box-shadow:0 1px 3px rgba(0,0,0,.2);
  }}
  /* Caixa de exemplo (CMV) — visualmente distinta e legível */
  .example-box {{
    background:rgba(255,255,255,.10);
    border-left:3px solid {RW['beige']};
    border-radius:6px;
    padding:.7rem .85rem;
    color:#FFFFFF !important;
    font-size:.8rem !important;
    line-height:1.65;
    margin:-.2rem 0 .9rem 0;
  }}
  .example-box b {{ color:{RW['beige']} !important; font-weight:700; }}

  /* ── Cards de métrica ───────────────────────────────────────────────────── */
  .metric-card {{
    background:{RW['white']};border-radius:12px;padding:1.2rem;
    border-left:4px solid {RW['dark_red']};
    box-shadow:0 4px 12px rgba(27,31,59,.08);
    transition:transform .2s,box-shadow .2s;
  }}
  .metric-card:hover {{
    transform:translateY(-2px);
    box-shadow:0 6px 18px rgba(27,31,59,.12);
  }}
  .metric-card h3 {{color:{RW['text']};font-size:.82rem;margin:0 0 .3rem 0;font-weight:500;}}
  .metric-card .value {{font-size:1.6rem;font-weight:700;margin:0;letter-spacing:-.5px;}}
  .metric-card .sub {{font-size:.72rem;color:#888;margin:.25rem 0 0 0;}}
  .metric-green .value {{color:{RW['green']};}}
  .metric-red   .value {{color:#C62828;}}
  .metric-navy  .value {{color:{RW['navy']};}}
  .metric-amber .value {{color:{RW['amber']};}}

  /* ── Títulos de seção ───────────────────────────────────────────────────── */
  .section-title {{
    color:{RW['navy']};font-size:1.25rem;font-weight:700;
    border-bottom:3px solid {RW['dark_red']};padding-bottom:.4rem;
    margin:1.4rem 0 .9rem 0;letter-spacing:-.3px;
  }}

  /* ── Caixas de alerta ───────────────────────────────────────────────────── */
  .alert-box {{
    background:linear-gradient(135deg,#FFF3E0,#FFE0B2);
    border:1px solid #FFB74D;border-radius:12px;padding:1rem 1.2rem;margin:.9rem 0;
    box-shadow:0 2px 8px rgba(245,124,0,.08);
  }}
  .alert-box h4 {{color:#E65100;margin:0 0 .4rem 0;}}
  .alert-box p {{color:#BF360C;margin:0;font-size:.88rem;line-height:1.55;}}

  /* ── CTA ────────────────────────────────────────────────────────────────── */
  .cta-box {{
    background:linear-gradient(135deg,{RW['navy']} 0%,#2A2F52 50%,{RW['dark_red']} 100%);
    border-radius:14px;padding:1.6rem 2rem;margin:1.2rem 0;text-align:center;
    box-shadow:0 8px 20px rgba(27,31,59,.20);
  }}
  .cta-box h3 {{color:{RW['white']};margin:0 0 .4rem 0;}}
  .cta-box p  {{color:{RW['beige']};margin:0;font-size:.92rem;line-height:1.5;}}

  .esg-example-item {{
    background:{RW['light_beige']};border-radius:6px;
    padding:.45rem .85rem;margin:.3rem 0;font-size:.85rem;color:{RW['text']};
  }}
  .footer-bar {{
    background:{RW['navy']};color:{RW['beige']};
    text-align:center;padding:.85rem;border-radius:10px;font-size:.8rem;margin-top:1.5rem;
  }}

  /* ── Tabs estilizadas ───────────────────────────────────────────────────── */
  .stTabs [data-baseweb="tab-list"] {{
    gap:.5rem;
    background:transparent;
    border-bottom:2px solid rgba(107,45,45,.15);
    padding-bottom:0;
  }}
  .stTabs [data-baseweb="tab"] {{
    background:{RW['white']} !important;
    border-radius:10px 10px 0 0 !important;
    border:1px solid rgba(27,31,59,.08) !important;
    border-bottom:none !important;
    padding:.7rem 1.2rem !important;
    font-weight:500 !important;
    color:{RW['navy']} !important;
    transition:all .25s ease !important;
    box-shadow:0 -2px 6px rgba(0,0,0,.03);
  }}
  .stTabs [data-baseweb="tab"]:hover {{
    background:{RW['light_beige']} !important;
    transform:translateY(-1px);
  }}
  .stTabs [aria-selected="true"] {{
    background:linear-gradient(135deg,{RW['dark_red']} 0%, #8B3A3A 100%) !important;
    color:#FFFFFF !important;
    font-weight:600 !important;
    box-shadow:0 -4px 12px rgba(107,45,45,.25) !important;
    border:1px solid {RW['dark_red']} !important;
    border-bottom:none !important;
  }}
  .stTabs [data-baseweb="tab-highlight"] {{ background:transparent !important; }}

  /* ── Inputs polidos ─────────────────────────────────────────────────────── */
  .stTextInput input, .stNumberInput input {{
    border-radius:8px !important;
    border:1px solid rgba(27,31,59,.15) !important;
    transition:border-color .2s,box-shadow .2s !important;
  }}
  .stTextInput input:focus, .stNumberInput input:focus {{
    border-color:{RW['dark_red']} !important;
    box-shadow:0 0 0 3px rgba(107,45,45,.12) !important;
  }}

  /* ── Botões ─────────────────────────────────────────────────────────────── */
  .stButton button {{
    border-radius:10px !important;
    font-weight:600 !important;
    letter-spacing:.2px !important;
    transition:transform .15s, box-shadow .2s !important;
  }}
  .stButton button:hover {{
    transform:translateY(-1px);
    box-shadow:0 6px 16px rgba(107,45,45,.25) !important;
  }}
</style>
""", unsafe_allow_html=True)

# ── Constantes tributárias ───────────────────────────────────────────────────
CURRENT_TAX_RATES = {"ICMS":0.17,"PIS":0.0165,"COFINS":0.076,"IPI":0.0}

REFORM_RATES_2033 = {
    "CBS":0.095,"IBS_ESTADUAL":0.13,"IBS_MUNICIPAL":0.055,"IVA_TOTAL":0.28,"IS":0.0
}

TRANSITION_RATES = {
    2026:{"cbs":.009,"ibs":.001,"icms":.17,"pis":.0165,"cofins":.076},
    2027:{"cbs":.095,"ibs":.001,"icms":.17,"pis":.0,"cofins":.0},
    2028:{"cbs":.095,"ibs":.001,"icms":.17,"pis":.0,"cofins":.0},
    2029:{"cbs":.095,"ibs":.050,"icms":.1275,"pis":.0,"cofins":.0},
    2030:{"cbs":.095,"ibs":.100,"icms":.085,"pis":.0,"cofins":.0},
    2031:{"cbs":.095,"ibs":.140,"icms":.0425,"pis":.0,"cofins":.0},
    2032:{"cbs":.095,"ibs":.175,"icms":.02125,"pis":.0,"cofins":.0},
    2033:{"cbs":.095,"ibs":.185,"icms":.0,"pis":.0,"cofins":.0},
}

SIMPLES_FAIXAS = [
    {"faixa":"1ª Faixa","min":0,"max":180_000,"aliquota":.04,"deduzir":0},
    {"faixa":"2ª Faixa","min":180_000.01,"max":360_000,"aliquota":.073,"deduzir":5_940},
    {"faixa":"3ª Faixa","min":360_000.01,"max":720_000,"aliquota":.095,"deduzir":13_860},
    {"faixa":"4ª Faixa","min":720_000.01,"max":1_800_000,"aliquota":.107,"deduzir":22_500},
    {"faixa":"5ª Faixa","min":1_800_000.01,"max":3_600_000,"aliquota":.143,"deduzir":87_300},
    {"faixa":"6ª Faixa","min":3_600_000.01,"max":4_800_000,"aliquota":.19,"deduzir":378_000},
]

ESTADOS_BR = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS",
              "MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC",
              "SP","SE","TO"]

# ICMS por estado (simplificado)
ICMS_POR_ESTADO = {
    "AC":.17,"AL":.17,"AP":.17,"AM":.18,"BA":.185,"CE":.18,"DF":.18,
    "ES":.17,"GO":.17,"MA":.18,"MT":.17,"MS":.17,"MG":.18,"PA":.17,
    "PB":.18,"PR":.175,"PE":.185,"PI":.18,"RJ":.20,"RN":.18,"RS":.17,
    "RO":.175,"RR":.17,"SC":.17,"SP":.18,"SE":.18,"TO":.18,
}

# ── GRI Indicators com exemplos ──────────────────────────────────────────────
GRI_INDICATORS = {
    "🌿 Ambiental": {
        "GRI 302 — Energia": {
            "desc": "Gestão de consumo energético e uso de fontes renováveis",
            "taxa": 0.10,
            "exemplos": [
                "☀️ Instalação de painéis fotovoltaicos (energia solar)",
                "💡 Troca de toda iluminação para LED (redução ≥30% consumo)",
                "📋 Certificação PROCEL de eficiência energética",
                "🌬️ Contrato de energia 100% renovável (I-REC / GO)",
                "🔋 Programa de monitoramento e gestão de energia em tempo real",
                "🏭 Substituição de equipamentos por versões A ou A+ de eficiência",
            ],
        },
        "GRI 303 — Água e Efluentes": {
            "desc": "Gestão responsável de recursos hídricos",
            "taxa": 0.05,
            "exemplos": [
                "🌧️ Sistema de captação e reúso de água da chuva",
                "♻️ Tratamento e reaproveitamento de efluentes industriais",
                "📊 Medidores inteligentes de consumo de água por setor",
                "🚰 Programa de redução de desperdício hídrico certificado",
                "🌊 Parceria com programas de conservação de bacias hidrográficas",
            ],
        },
        "GRI 305 — Emissões de GEE": {
            "desc": "Redução e compensação de emissões de carbono",
            "taxa": 0.15,
            "exemplos": [
                "📊 Inventário de emissões GHG Protocol (Escopos 1, 2 e 3)",
                "🌳 Compensação de carbono via créditos REDD+ ou refl orestamento",
                "🚗 Eletrificação ou hibridização da frota de veículos",
                "✈️ Programa de neutralização de viagens corporativas",
                "🏗️ Construção/reforma com materiais de baixo carbono incorporado",
                "💨 Redução de HFCs em sistemas de refrigeração/ar-condicionado",
            ],
        },
        "GRI 306 — Resíduos": {
            "desc": "Gestão e redução de resíduos sólidos",
            "taxa": 0.08,
            "exemplos": [
                "♻️ Programa formal de logística reversa (Lei 12.305/2010 +)",
                "🤝 Parceria com cooperativas de catadores para coleta seletiva",
                "🏭 Certificação ISO 14001 (sistema de gestão ambiental)",
                "🚫 Programa de eliminação de plástico de uso único",
                "🌱 Compostagem de resíduos orgânicos operacionais",
                "📦 Redesenho de embalagens para economia circular",
            ],
        },
    },
    "👥 Social": {
        "GRI 401 — Emprego e Benefícios": {
            "desc": "Condições de trabalho e benefícios além da legislação",
            "taxa": 0.12,
            "exemplos": [
                "💰 PLR (Participação nos Lucros) com parcela extra acima do mínimo legal",
                "🏥 Plano de saúde e odontológico extensivo a dependentes",
                "🍽️ Vale-Refeição/Alimentação acima do piso da categoria",
                "👶 Auxílio-creche e licença maternidade/paternidade estendida",
                "🏠 Auxílio home-office e ergonomia para trabalho remoto",
                "📚 Programa de bolsas de estudo para funcionários e dependentes",
            ],
        },
        "GRI 403 — Saúde e Segurança no Trabalho": {
            "desc": "Programas de saúde ocupacional e segurança",
            "taxa": 0.10,
            "exemplos": [
                "🧠 Programa de saúde mental (psicólogo, mindfulness, apoio emocional)",
                "🏋️ Academia ou subsídio de atividade física para colaboradores",
                "🦺 SIPAT ampliada com atividades além das exigências da NR-5",
                "🩺 Check-up médico anual custeado pela empresa",
                "🪑 Programa de ergonomia e ginástica laboral",
                "💊 Campanha de vacinação corporativa (além da obrigatória)",
            ],
        },
        "GRI 404 — Treinamento e Desenvolvimento": {
            "desc": "Investimento em capacitação e desenvolvimento profissional",
            "taxa": 0.15,
            "exemplos": [
                "🎓 Plataforma de EAD corporativa (cursos ilimitados para todos)",
                "📜 Subsídio de 100% para certificações profissionais relevantes",
                "🤝 Programa de mentoria interna e coaching executivo",
                "🌍 Intercâmbio profissional ou treinamento no exterior",
                "📊 Programa de desenvolvimento de lideranças (trilha gerencial)",
                "🤖 Capacitação em transformação digital e novas tecnologias",
            ],
        },
        "GRI 405 — Diversidade e Igualdade de Oportunidades": {
            "desc": "Programas de inclusão, equidade e diversidade",
            "taxa": 0.08,
            "exemplos": [
                "♿ Cotas voluntárias para PcD acima do exigido pela Lei de Cotas",
                "👩 Programa de equidade salarial de gênero com auditoria externa",
                "🌈 Comitê de Diversidade, Equidade e Inclusão (DEI) ativo",
                "📊 Metas de diversidade com indicadores mensuráveis e publicados",
                "🎯 Programa Jovem Aprendiz expandido para grupos vulneráveis",
                "🏫 Parceria com escolas públicas para estágios e primeiro emprego",
            ],
        },
    },
    "🏛️ Governança": {
        "GRI 205 — Anticorrupção e Compliance": {
            "desc": "Programas de integridade, ética e compliance",
            "taxa": 0.05,
            "exemplos": [
                "📢 Canal de denúncias anônimo (0800 ou plataforma digital)",
                "📋 Código de Conduta atualizado e assinado por todos os colaboradores",
                "🎓 Treinamento anual obrigatório de compliance e ética empresarial",
                "🔍 Due diligence de fornecedores e parceiros (análise de integridade)",
                "📊 Certificação ISO 37001 (Sistema de Gestão Antissuborno)",
                "⚖️ Política de Conflito de Interesses formalizada e auditada",
            ],
        },
        "GRI 206 — Concorrência Leal": {
            "desc": "Conformidade com legislação antitruste e concorrência",
            "taxa": 0.03,
            "exemplos": [
                "📜 Política formal de compliance concorrencial documentada",
                "🎓 Treinamento anual sobre Lei de Defesa da Concorrência (Lei 12.529)",
                "🔍 Auditoria independente de práticas comerciais e precificação",
                "📋 Procedimentos de controle para participação em associações setoriais",
            ],
        },
    },
}

# ── Funções utilitárias ──────────────────────────────────────────────────────
def fmt(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def parse_brl(s: str) -> float:
    """
    Parser inteligente de valores em R$ no padrão brasileiro.

    Aceita qualquer um destes formatos:
        '5300300'                  → 5.300.300,00
        '5300300.50'               → 5.300.300,50
        '5.300.300,00'             → 5.300.300,00
        '5300300,50'               → 5.300.300,50
        '5,3 mi' / '5.3 milhoes'   → 5.300.000,00
        '2 bi' / '2 bilhoes'       → 2.000.000.000,00
        '500 mil'                  → 500.000,00
        'R$ 5.300.300,00'          → 5.300.300,00
    """
    if s is None:
        return 0.0
    s = str(s).strip().lower()
    if not s:
        return 0.0

    # Detecta sufixo de unidade
    mult = 1.0
    sufixos = [
        ("bilhões", 1e9), ("bilhoes", 1e9), ("bilhão", 1e9), ("bilhao", 1e9), ("bi", 1e9),
        ("milhões", 1e6), ("milhoes", 1e6), ("milhão", 1e6), ("milhao", 1e6), ("mi", 1e6), ("mm", 1e6),
        ("mil", 1e3), ("k", 1e3),
    ]
    for suf, m in sufixos:
        if s.endswith(suf):
            s = s[:-len(suf)].strip()
            mult = m
            break

    # Remove prefixos / símbolos
    s = s.replace("r$", "").replace("$", "").replace(" ", "").strip()
    if not s:
        return 0.0

    # Converte separadores: padrão brasileiro "1.234.567,89" → "1234567.89"
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    # se só houver ".", mantém (ex.: "5300300.50" formato US)

    try:
        return float(s) * mult
    except ValueError:
        return 0.0

def fmt_latex(v: float) -> str:
    r"""Formata moeda escapando o $ para uso em st.latex (R\$)."""
    return f"R\\$\\,{v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def fmt_resumo(v: float) -> str:
    """Formata valor em milhões/bilhões para exibição compacta."""
    if v >= 1_000_000_000:
        return f"R$ {v/1_000_000_000:,.2f} bi".replace(",","X").replace(".",",").replace("X",".")
    if v >= 1_000_000:
        return f"R$ {v/1_000_000:,.2f} mi".replace(",","X").replace(".",",").replace("X",".")
    if v >= 1_000:
        return f"R$ {v/1_000:,.1f} mil".replace(",","X").replace(".",",").replace("X",".")
    return fmt(v)

def pct(v: float) -> str:
    return f"{v*100:.2f}%"

# ── Tema RedWood para Plotly ─────────────────────────────────────────────────
PLOT_FONT = dict(family="Figtree, Inter, sans-serif", size=13, color="#1B1F3B")

# Paleta tributária consistente com a marca (sem amarelos clashing)
TRIB_COLORS = {
    "ICMS":   "#C76B5E",   # terracota suave (alaranjado avermelhado)
    "PIS":    "#E0B080",   # bege quente
    "COFINS": "#D5C4A1",   # bege RedWood
    "CBS":    "#6B2D2D",   # dark_red RedWood
    "IBS":    "#1B1F3B",   # navy RedWood
}

def style_fig(fig, title=None, h=400, legend_top=True):
    """Aplica o tema RedWood (Figtree + cores + grid suave) a uma figura Plotly."""
    fig.update_layout(
        title=dict(
            text=title or "",
            font=dict(family="Figtree", size=16, color="#1B1F3B", weight=700),
            x=0.02, xanchor="left", y=0.96,
        ),
        font=PLOT_FONT,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=h,
        margin=dict(l=50, r=20, t=60, b=50),
        legend=dict(
            orientation="h" if legend_top else "v",
            y=1.08 if legend_top else 1, x=1, xanchor="right",
            bgcolor="rgba(255,255,255,.6)", bordercolor="rgba(27,31,59,.1)",
            borderwidth=1, font=dict(family="Figtree", size=12),
        ),
        hoverlabel=dict(
            bgcolor="#1B1F3B", font=dict(family="Figtree", color="white", size=13),
            bordercolor="#6B2D2D",
        ),
        xaxis=dict(
            showgrid=False, showline=True, linecolor="rgba(27,31,59,.2)",
            tickfont=dict(family="Figtree", size=12, color="#555"),
            title_font=dict(family="Figtree", size=13, color="#1B1F3B"),
        ),
        yaxis=dict(
            showgrid=True, gridcolor="rgba(27,31,59,.07)", zerolinecolor="rgba(27,31,59,.15)",
            tickfont=dict(family="Figtree", size=12, color="#555"),
            title_font=dict(family="Figtree", size=13, color="#1B1F3B"),
        ),
    )
    return fig

def _ascii(s: str) -> str:
    """Remove/replace non-latin1 chars for FPDF"""
    r = {"—":"-","–":"-","'":"'","'":"'",""":'"',""":'"',"…":"...",
         "☀️":"","💡":"","📋":"","🌬️":"","🔋":"","🏭":"","🌧️":"",
         "♻️":"","📊":"","🚰":"","🌊":"","🚗":"","✈️":"","🏗️":"",
         "💨":"","🤝":"","🚫":"","🌱":"","📦":"","💰":"","🏥":"",
         "🍽️":"","👶":"","🏠":"","📚":"","🧠":"","🏋️":"","🦺":"",
         "🩺":"","🪑":"","💊":"","🎓":"","📜":"","🤝":"","🌍":"",
         "🤖":"","♿":"","👩":"","🌈":"","🎯":"","🏫":"","📢":"",
         "⚖️":"","🔍":"","📢":"","🎓":"","🌿":"","👥":"","🏛️":"",
         "ç":"c","ã":"a","á":"a","é":"e","í":"i","ó":"o","ú":"u",
         "ô":"o","ê":"e","â":"a","Ç":"C","Ã":"A","Á":"A","É":"E",
         "Í":"I","Ó":"O","Ú":"U","Ô":"O","Ê":"E","Â":"A",
         "ü":"u","ö":"o","ä":"a","õ":"o",
    }
    for k,v in r.items():
        s = s.replace(k,v)
    return s.encode("latin-1","replace").decode("latin-1")

# ── Geolocalização & Email ───────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def obter_localizacao_ip(ip: str) -> str:
    try:
        resp = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        if resp.status_code == 200:
            d = resp.json()
            return f"{d.get('city','')}, {d.get('region','')} ({d.get('country','BR')})"
    except Exception:
        pass
    return "Localização não identificada"

def get_client_ip() -> str:
    try:
        hdrs = st.context.headers
        ip = hdrs.get("x-forwarded-for","") or hdrs.get("x-real-ip","")
        if ip:
            return ip.split(",")[0].strip()
    except Exception:
        pass
    return ""

def enviar_notificacao_email(empresa: str, regime: str, localizacao: str, total: int = 0):
    """Notificação silenciosa para fernando@redwood.report"""
    try:
        eu = st.secrets.get("EMAIL_USER","")
        ep = st.secrets.get("EMAIL_PASS","")
        if not eu or not ep:
            return
        agora = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
        msg = MIMEMultipart()
        msg["From"]    = eu
        msg["To"]      = "fernando@redwood.report"
        msg["Subject"] = f"🌲 Novo Relatório #{total} — {localizacao}"
        body = (
            f"Novo relatório gerado na Plataforma RedWood!\n\n"
            f"📍 Localização : {localizacao}\n"
            f"📅 Data/Hora   : {agora}\n"
            f"🏢 Regime       : {regime}\n"
            f"🏭 Empresa      : {empresa or 'Não informado'}\n"
            f"📊 Total acumulado: {total} projeções\n\n"
            f"---\nRedWood — Projeção Reforma Tributária"
        )
        msg.attach(MIMEText(body,"plain","utf-8"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=6) as s:
            s.login(eu, ep)
            s.send_message(msg)
    except Exception:
        pass  # silencioso

def enviar_notificacao_sms(empresa: str, regime: str, localizacao: str, total: int = 0):
    """
    SMS silencioso via Twilio para +5541985151622.

    Configuração necessária no Streamlit Cloud → Settings → Secrets:
        TWILIO_SID   = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        TWILIO_TOKEN = "your_auth_token_here"
        TWILIO_FROM  = "+1xxxxxxxxxx"      # número Twilio (formato E.164)
        SMS_TO       = "+5541985151622"    # destinatário (RedWood)

    Se algum secret não estiver configurado, a função sai silenciosamente
    sem lançar erro. O e-mail continua sendo enviado de qualquer forma.
    """
    try:
        sid   = st.secrets.get("TWILIO_SID", "")
        token = st.secrets.get("TWILIO_TOKEN", "")
        frm   = st.secrets.get("TWILIO_FROM", "")
        to    = st.secrets.get("SMS_TO", "+5541985151622")
        if not (sid and token and frm and to):
            return
        agora = datetime.datetime.now().strftime("%d/%m %H:%M")
        body = (
            f"RedWood #{total} | {localizacao} | {agora} | "
            f"{regime} | {(empresa or 'N/I')[:30]}"
        )
        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
        requests.post(
            url,
            data={"From": frm, "To": to, "Body": body},
            auth=(sid, token),
            timeout=6,
        )
    except Exception:
        pass  # silencioso

def notificar_relatorio(empresa: str, regime: str, localizacao: str, total: int = 0):
    """Dispara e-mail e (se configurado) SMS para a RedWood."""
    enviar_notificacao_email(empresa, regime, localizacao, total)
    enviar_notificacao_sms(empresa, regime, localizacao, total)

# ── Contador de relatórios ───────────────────────────────────────────────────
_COUNT_FILE = os.path.join(os.path.dirname(__file__), "data", "report_count.json")

def _ler_contador() -> int:
    try:
        os.makedirs(os.path.dirname(_COUNT_FILE), exist_ok=True)
        if os.path.exists(_COUNT_FILE):
            with open(_COUNT_FILE, "r") as f:
                return int(json.load(f).get("total", 0))
    except Exception:
        pass
    return 0

def _incrementar_contador() -> int:
    try:
        os.makedirs(os.path.dirname(_COUNT_FILE), exist_ok=True)
        total = _ler_contador() + 1
        with open(_COUNT_FILE, "w") as f:
            json.dump({"total": total}, f)
        return total
    except Exception:
        pass
    return 0

# ── CNPJ Lookup ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def buscar_cnpj(cnpj: str) -> dict | None:
    c = "".join(x for x in cnpj if x.isdigit())
    if len(c) != 14:
        return None
    for url in [
        f"https://brasilapi.com.br/api/cnpj/v1/{c}",
        f"https://receitaws.com.br/v1/cnpj/{c}",
    ]:
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            continue
    return None

# ── Cálculos ─────────────────────────────────────────────────────────────────
def faixa_simples(rec: float):
    for f in SIMPLES_FAIXAS:
        if rec <= f["max"]:
            return f
    return SIMPLES_FAIXAS[-1]

def calc_atual(cmv, regime, receita, margem, estado):
    icms_r = ICMS_POR_ESTADO.get(estado, 0.17)
    if regime == "Simples Nacional":
        fx = faixa_simples(receita)
        alq = (receita * fx["aliquota"] - fx["deduzir"]) / receita if receita else fx["aliquota"]
        mk = 1 - (alq + margem)
        if mk <= 0: mk = 0.01
        pv = cmv / mk
        lb = pv * margem
        tt = pv * alq
        return dict(regime=regime, faixa=fx["faixa"], preco_venda=pv, lucro_bruto=lb,
                    icms=0, pis=0, cofins=0, simples=tt, total_tributos=tt,
                    carga_tributaria=tt/(cmv+lb) if (cmv+lb)>0 else 0,
                    markup=mk, aliquota_efetiva=alq)
    elif regime == "Lucro Presumido":
        pr, cr, ir, cs = 0.0065, 0.03, 0.048, 0.0288
    else:  # Lucro Real
        pr, cr, ir, cs = 0.0165, 0.076, 0.0, 0.0
    taxa = icms_r + pr + cr + ir + cs
    mk = 1 - (taxa + margem)
    if mk <= 0: mk = 0.01
    pv = cmv / mk
    lb = pv * margem
    return dict(regime=regime, faixa="-", preco_venda=pv, lucro_bruto=lb,
                icms=pv*icms_r, pis=pv*pr, cofins=pv*cr, simples=0,
                total_tributos=pv*taxa,
                carga_tributaria=(pv*taxa)/(cmv+lb) if (cmv+lb)>0 else 0,
                markup=mk, aliquota_efetiva=taxa)

def calc_reforma(cmv, margem):
    mk = 1 - margem
    base = cmv / mk
    lb   = base * margem
    cbs  = base * REFORM_RATES_2033["CBS"]
    ibe  = base * REFORM_RATES_2033["IBS_ESTADUAL"]
    ibm  = base * REFORM_RATES_2033["IBS_MUNICIPAL"]
    iva  = cbs + ibe + ibm
    comp = base * 0.025      # compliance
    spl  = base * 0.012      # split payment
    ada  = comp + spl
    pf   = base + iva + ada
    ct   = (iva + ada) / (cmv + lb) if (cmv + lb) > 0 else 0
    return dict(preco_venda=base, preco_final_nfe=pf, lucro_bruto=lb,
                cbs=cbs, ibs_estadual=ibe, ibs_municipal=ibm, total_iva=iva,
                custo_compliance=comp, custo_split_payment=spl, custo_adaptacao=ada,
                carga_tributaria=ct, markup=mk)

def calc_transicao(cmv, margem):
    rows = []
    for ano, tx in TRANSITION_RATES.items():
        taxa = tx["cbs"]+tx["ibs"]+tx["icms"]+tx["pis"]+tx["cofins"]
        if ano >= 2029:
            mk = 1 - margem; base = cmv/mk
            tt = base*(tx["icms"]+tx["pis"]+tx["cofins"]+tx["cbs"]+tx["ibs"])
            pv = base + base*(tx["cbs"]+tx["ibs"]) + base*(tx["icms"])
        else:
            mk = 1-(taxa+margem)
            if mk <= 0: mk = 0.01
            base = cmv/mk; tt = base*taxa; pv = base
        lb = base*margem
        rows.append(dict(ano=ano,cbs=tx["cbs"],ibs=tx["ibs"],
                         icms=tx["icms"],pis=tx["pis"],cofins=tx["cofins"],
                         total_taxa=taxa, preco_venda=pv, total_tributos=tt,
                         carga_tributaria=tt/(cmv+lb) if (cmv+lb)>0 else 0))
    return rows

def calc_esg(base, acoes):
    td = sum(a["taxa"] for a in acoes)
    vd = base * td
    ec = vd * REFORM_RATES_2033["IVA_TOTAL"]
    return dict(taxa_total=td, valor_deducao=vd, economia_fiscal=ec, base_reduzida=base-vd)

# ── PDF ──────────────────────────────────────────────────────────────────────
class RedWoodPDF(FPDF):
    _logo = os.path.join(os.path.dirname(__file__), "assets", "logo_redwood_vertical.png")

    def header(self):
        self.set_fill_color(27,31,59); self.rect(0,0,210,34,"F")
        self.set_fill_color(107,45,45); self.rect(0,34,210,3,"F")
        if os.path.exists(self._logo):
            self.image(self._logo, 8, 3, 26)
        self.set_text_color(255,255,255); self.set_font("Helvetica","B",15)
        self.set_xy(38,7); self.cell(0,8,"Projecao da Reforma Tributaria",ln=True)
        self.set_font("Helvetica","",8); self.set_text_color(213,196,161)
        self.set_xy(38,17); self.cell(0,6,"RedWood Estrategia & Impacto | CBS/IBS/ESG",ln=True)
        self.ln(20)

    def footer(self):
        self.set_y(-14); self.set_font("Helvetica","I",7)
        self.set_text_color(160,160,160)
        self.cell(0,10,f"RedWood Estrategia & Impacto | redwood.report | Pg {self.page_no()}/{{nb}}",align="C")

    def sec(self, t):
        self.set_font("Helvetica","B",12); self.set_text_color(27,31,59)
        self.cell(0,9,_ascii(t),ln=True)
        self.set_draw_color(107,45,45); self.set_line_width(.7)
        self.line(10,self.get_y(),200,self.get_y()); self.ln(3)

    def tbl(self, hdrs, rows, ws=None):
        ws = ws or [95,95]
        self.set_font("Helvetica","B",9)
        self.set_fill_color(27,31,59); self.set_text_color(255,255,255)
        for i,h in enumerate(hdrs):
            self.cell(ws[i],8,_ascii(str(h)),border=1,fill=True,align="C")
        self.ln(); fl=False
        for row in rows:
            self.set_fill_color(245,240,235 if fl else 255)
            self.set_text_color(51,51,51); self.set_font("Helvetica","",9)
            for i,c in enumerate(row):
                self.cell(ws[i],7,_ascii(str(c)),border=1,fill=True,align="L" if i==0 else "R")
            self.ln(); fl=not fl

def gerar_pdf(nome,regime,estado,cmv,margem,atual,reforma,trans,diff,diff_r):
    pdf = RedWoodPDF(); pdf.alias_nb_pages(); pdf.add_page()
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    pdf.set_font("Helvetica","",10); pdf.set_text_color(60,60,60)
    pdf.cell(0,6,_ascii(f"Empresa: {nome} | Regime: {regime} | UF: {estado} | Data: {hoje}"),ln=True)
    pdf.ln(4)

    pdf.sec("Cenario Atual")
    pdf.tbl(["Indicador","Valor"],[
        ["CMV",fmt(cmv)],["Preco de Venda",fmt(atual["preco_venda"])],
        ["Total Tributos",fmt(atual["total_tributos"])],
        ["Carga Tributaria",pct(atual["carga_tributaria"])],
    ])
    pdf.ln(5)

    pdf.sec("Reforma Tributaria 2033")
    pdf.tbl(["Indicador","Valor"],[
        ["Base de Calculo",fmt(reforma["preco_venda"])],
        ["CBS Federal (9,5%)",fmt(reforma["cbs"])],
        ["IBS Estadual (13%)",fmt(reforma["ibs_estadual"])],
        ["IBS Municipal (5,5%)",fmt(reforma["ibs_municipal"])],
        ["Total IVA (28%)",fmt(reforma["total_iva"])],
        ["Compliance + Obrig.",fmt(reforma["custo_compliance"])],
        ["Split Payment",fmt(reforma["custo_split_payment"])],
        ["Preco Final NF-e",fmt(reforma["preco_final_nfe"])],
        ["Carga Total",pct(reforma["carga_tributaria"])],
    ])
    pdf.ln(5)

    pdf.sec("Impacto")
    pdf.set_font("Helvetica","",10); pdf.set_text_color(60,60,60)
    pdf.cell(0,7,_ascii(f"Variacao da carga: {'+'if diff>0 else ''}{pct(diff)}"),ln=True)
    pdf.cell(0,7,_ascii(f"Impacto por operacao: {'+'if diff_r>0 else ''}{fmt(diff_r)}"),ln=True)
    pdf.ln(5)

    pdf.sec("Cronograma de Transicao (2026-2033)")
    pdf.tbl(["Ano","CBS","IBS","ICMS","Carga"],
            [[str(t["ano"]),f"{t['cbs']*100:.1f}%",f"{t['ibs']*100:.1f}%",
              f"{t['icms']*100:.1f}%",pct(t["carga_tributaria"])] for t in trans],
            ws=[28,36,36,46,44])

    pdf.add_page()
    pdf.sec("Acoes ESG / GRI — Deducoes Fiscais na Reforma")
    pdf.set_font("Helvetica","",8); pdf.set_text_color(60,60,60)
    pdf.multi_cell(0,5,_ascii(
        "ESG engloba tudo que a empresa faz alem das obrigacoes legais. "
        "Com a Reforma Tributaria, acoes ESG alinhadas ao GRI podem gerar deducoes na base de calculo."
    ))
    pdf.ln(3)
    for cat, inds in GRI_INDICATORS.items():
        pdf.set_font("Helvetica","B",10); pdf.set_text_color(27,31,59)
        pdf.cell(0,7,_ascii(cat),ln=True)
        for nome_ind, d in inds.items():
            pdf.set_font("Helvetica","BI",9); pdf.set_text_color(107,45,45)
            pdf.cell(0,6,_ascii(f"  {nome_ind} — Deducao potencial: {d['taxa']*100:.0f}%"),ln=True)
            pdf.set_font("Helvetica","",8); pdf.set_text_color(80,80,80)
            for ex in d["exemplos"][:3]:
                pdf.cell(0,5,_ascii(f"    • {ex}"),ln=True)
        pdf.ln(2)

    # CTA
    pdf.ln(5)
    pdf.set_fill_color(27,31,59); pdf.rect(10,pdf.get_y(),190,28,"F")
    pdf.set_text_color(255,255,255); pdf.set_font("Helvetica","B",12)
    pdf.set_xy(10,pdf.get_y()+4)
    pdf.cell(190,8,"RedWood Estrategia & Impacto",align="C",ln=True)
    pdf.set_font("Helvetica","",8); pdf.set_text_color(213,196,161)
    pdf.cell(190,5,_ascii("Consultoria em reforma tributaria, planejamento fiscal e estrategias ESG"),align="C",ln=True)
    pdf.cell(190,5,"fernando@redwood.report  |  redwood.report",align="C",ln=True)

    return bytes(pdf.output())

# ═══════════════════════════════════════════════════════════════════════════
# INTERFACE
# ═══════════════════════════════════════════════════════════════════════════

# ── Header ───────────────────────────────────────────────────────────────────
import base64 as _b64

def _logo_b64(name: str) -> str:
    p = os.path.join(os.path.dirname(__file__), "assets", name)
    if os.path.exists(p):
        with open(p, "rb") as f:
            return _b64.b64encode(f.read()).decode()
    return ""

# Logo branca para fundos escuros (header) e logo escura para fundos claros (PDF)
_LOGO_WHITE = _logo_b64("logo_redwood_white.png")
_LOGO_DARK  = _logo_b64("logo_redwood_vertical.png")

# Banner único integrando logo + título (visual coeso)
_logo_html = (
    f'<img src="data:image/png;base64,{_LOGO_WHITE}" alt="RedWood" '
    f'style="height:96px;width:auto;display:block;filter:drop-shadow(0 2px 4px rgba(0,0,0,.25))" />'
    if _LOGO_WHITE else '<div style="font-size:3rem;color:white">🌲</div>'
)

st.markdown(f"""
<div style="background:linear-gradient(135deg,{RW['navy']} 0%, #2A2F52 60%, {RW['dark_red']} 100%);
            padding:1.4rem 2rem;border-radius:14px;
            box-shadow:0 8px 24px rgba(27,31,59,.25);
            display:flex;align-items:center;gap:1.6rem;
            border:1px solid rgba(213,196,161,.15);">
  <div style="flex:0 0 auto;">{_logo_html}</div>
  <div style="flex:1 1 auto;">
    <h1 style="color:#FFFFFF;margin:0;font-size:1.7rem;font-weight:700;letter-spacing:-.5px;">
      Projeção da Reforma Tributária
    </h1>
    <p style="color:{RW['beige']};margin:.35rem 0 0 0;font-size:.92rem;line-height:1.4;">
      Simulador CBS/IBS&nbsp;·&nbsp;Comparativo atual vs. reforma&nbsp;·&nbsp;Ações ESG/GRI
    </p>
    <p style="color:rgba(213,196,161,.75);margin:.2rem 0 0 0;font-size:.78rem;font-style:italic;">
      RedWood Estratégia &amp; Impacto · Consultoria Tributária e ESG
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    if _LOGO_WHITE:
        st.markdown(
            f'<div style="text-align:center;padding:.4rem 0 .8rem 0;">'
            f'<img src="data:image/png;base64,{_LOGO_WHITE}" '
            f'style="width:60%;max-width:140px;opacity:.95" alt="RedWood"/>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        f"<h2 style='color:{RW['beige']};text-align:center;margin:0;"
        f"font-size:1.05rem;letter-spacing:.5px;text-transform:uppercase;'>"
        f"Dados da Empresa</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<hr style='border:none;border-top:1px solid {RW['dark_red']};margin:.6rem 0 1rem 0;opacity:.6'>",
        unsafe_allow_html=True,
    )

    # CNPJ
    cnpj_in = st.text_input("CNPJ", placeholder="00.000.000/0000-00")

    empresa_nome = st.session_state.get("emp_nome","")
    cnae_txt     = st.session_state.get("cnae_txt","")
    estado_idx   = st.session_state.get("estado_idx", ESTADOS_BR.index("PR"))

    if cnpj_in and len("".join(c for c in cnpj_in if c.isdigit())) == 14:
        if st.button("🔍 Buscar CNPJ", width='stretch'):
            with st.spinner("Consultando Receita Federal..."):
                d = buscar_cnpj(cnpj_in)
            if d:
                razao = d.get("razao_social","") or d.get("nome","")
                st.session_state["emp_nome"] = razao
                c_princ = d.get("cnae_fiscal","") or d.get("atividade_principal",[{}])[0].get("code","")
                c_desc  = d.get("cnae_fiscal_descricao","") or d.get("atividade_principal",[{}])[0].get("text","")
                cnaes_sec = d.get("cnaes_secundarios",[]) or d.get("atividades_secundarias",[])
                linhas = [f"Principal: {c_princ} — {c_desc}"]
                for cs in cnaes_sec[:5]:
                    cod  = cs.get("codigo","") or cs.get("code","")
                    desc = cs.get("descricao","") or cs.get("text","")
                    if cod:
                        linhas.append(f"Secundário: {cod} — {desc}")
                st.session_state["cnae_txt"] = "\n".join(linhas)
                uf = d.get("uf","") or d.get("municipio","")
                if uf in ESTADOS_BR:
                    st.session_state["estado_idx"] = ESTADOS_BR.index(uf)
                empresa_nome = st.session_state["emp_nome"]
                cnae_txt     = st.session_state["cnae_txt"]
                estado_idx   = st.session_state.get("estado_idx", ESTADOS_BR.index("PR"))
                st.success(f"✅ {razao[:40]}")
            else:
                st.error("CNPJ não encontrado. Preencha manualmente.")

    empresa_nome = st.text_input("Razão Social", value=empresa_nome)
    cnae_txt     = st.text_area("CNAEs (Principal e Secundários)", value=cnae_txt, height=110)

    if cnae_txt:
        st.markdown(f"""<div style='background:{RW['white']};border-left:3px solid {RW['dark_red']};
            border-radius:4px;padding:.5rem .8rem;font-size:.78rem;color:{RW['text']};margin-top:-.5rem'>
            {cnae_txt.replace(chr(10),'<br>').replace("Principal:","<b>Principal:</b>")
                     .replace("Secundário:","<span style='color:#888'>Secundário:</span>")}
            </div>""", unsafe_allow_html=True)

    st.markdown(f"<hr style='border:none;border-top:1px solid {RW['dark_red']};margin:1rem 0 .6rem 0;opacity:.5'>",unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{RW['beige']};font-size:.95rem;letter-spacing:.4px;text-transform:uppercase;margin:.2rem 0 .4rem 0'>⚙️ Parâmetros Fiscais</h3>", unsafe_allow_html=True)
    regime = st.selectbox("Regime Tributário", ["Lucro Real","Lucro Presumido","Simples Nacional"])
    estado = st.selectbox("Estado (UF)", ESTADOS_BR, index=estado_idx)

    st.markdown(f"<hr style='border:none;border-top:1px solid {RW['dark_red']};margin:1rem 0 .6rem 0;opacity:.5'>",unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{RW['beige']};font-size:.95rem;letter-spacing:.4px;text-transform:uppercase;margin:.2rem 0 .4rem 0'>💰 Dados Financeiros</h3>", unsafe_allow_html=True)

    # Dica de formato — entrada livre estilo calculadora
    st.markdown(
        f"""<div class="hint-box">
          💡 <b>Digite o valor como preferir:</b><br>
          • <code>5300300</code> &nbsp;ou&nbsp; <code>5.300.300,00</code><br>
          • <code>5,3 mi</code> &nbsp;·&nbsp; <code>500 mil</code> &nbsp;·&nbsp; <code>2 bi</code>
        </div>""",
        unsafe_allow_html=True,
    )

    # Receita Bruta — entrada livre
    receita_str = st.text_input(
        "Receita Bruta Anual (R$)",
        value=st.session_state.get("receita_str", "1.000.000,00"),
        placeholder="ex.: 5.300.300,00 ou 5,3 mi",
        help="É o total que sua empresa fatura no ano (todas as vendas somadas, antes de descontar impostos e custos).",
        key="receita_str",
    )
    receita_anual = parse_brl(receita_str)

    # CMV — entrada livre
    cmv_str = st.text_input(
        "Custo da Mercadoria — CMV (R$)",
        value=st.session_state.get("cmv_str", "500.000,00"),
        placeholder="ex.: 500.000,00 ou 500 mil",
        help=("É quanto você gasta para PRODUZIR ou COMPRAR o que vende — antes de revender. "
              "Inclui matéria-prima, mercadoria comprada, frete de entrada, embalagens diretas. "
              "NÃO inclui salários administrativos, aluguel, marketing ou impostos."),
        key="cmv_str",
    )
    cmv = parse_brl(cmv_str)

    # Caixa de exemplo do CMV — para quem não conhece o conceito
    st.markdown(
        f"""<div class="example-box">
          📚 <b>O que é CMV? (exemplo prático)</b><br>
          Uma <b>padaria</b> vende um pão por <b>R$ 1,00</b>. Para fazer cada pão,
          gasta <b>R$ 0,40</b> com farinha, fermento, energia e embalagem.<br>
          → CMV unitário = <b>R$ 0,40</b> por pão<br>
          → Se vende 1 milhão de pães por ano = <b>CMV anual de R$ 400.000</b><br><br>
          <span style="opacity:.85">É só o custo do <b>produto em si</b> — não inclui aluguel,
          salários do administrativo ou impostos.</span>
        </div>""",
        unsafe_allow_html=True,
    )

    # Preview formatado dos valores reconhecidos
    _r_ok = "✅" if receita_anual > 0 else "⚠️"
    _c_ok = "✅" if cmv > 0 else "⚠️"
    st.markdown(
        f"<div style='background:rgba(255,255,255,.12);border:1px solid rgba(213,196,161,.4);"
        f"border-radius:10px;padding:.7rem .9rem;font-size:.85rem;"
        f"color:#F5EBD9;margin:.4rem 0 .8rem 0;line-height:1.7;"
        f"box-shadow:0 2px 6px rgba(0,0,0,.15)'>"
        f"{_r_ok} <b style='color:#FFF'>Receita reconhecida</b><br>"
        f"<span style='color:#FFFFFF;font-size:1.05rem;font-weight:700;letter-spacing:.2px'>{fmt(receita_anual)}</span>"
        f"<hr style='border:none;border-top:1px dashed rgba(213,196,161,.4);margin:.5rem 0'>"
        f"{_c_ok} <b style='color:#FFF'>CMV reconhecido</b><br>"
        f"<span style='color:#FFFFFF;font-size:1.05rem;font-weight:700;letter-spacing:.2px'>{fmt(cmv)}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    if cmv > receita_anual and receita_anual > 0:
        st.warning("⚠️ CMV maior que a Receita — verifique os valores.")

    margem_lucro = st.slider("Margem de Lucro Bruto (%)", 5, 60, 25) / 100

    calcular = st.button("📊 Calcular Projeção", width='stretch', type="primary")

    # Contador de projeções (visível a qualquer visitante)
    _cnt = _ler_contador()
    if _cnt > 0:
        st.markdown(
            f"<p style='color:{RW['beige']};text-align:center;font-size:.72rem;"
            f"margin-top:1rem;opacity:.7'>📊 {_cnt} projeção{'ões' if _cnt!=1 else ''} realizada{'s' if _cnt!=1 else ''}</p>",
            unsafe_allow_html=True,
        )

# ── Cálculos & estado ────────────────────────────────────────────────────────
if calcular:
    r_atual   = calc_atual(cmv, regime, receita_anual, margem_lucro, estado)
    r_reforma = calc_reforma(cmv, margem_lucro)
    transicao = calc_transicao(cmv, margem_lucro)
    st.session_state.update({
        "r_atual":r_atual,"r_reforma":r_reforma,"transicao":transicao,
        "cmv":cmv,"margem":margem_lucro,"regime":regime,"estado":estado,
        "empresa_nome":empresa_nome,"cnae_txt":cnae_txt,
        "receita_anual":receita_anual,
    })
    # Notificação silenciosa + contador
    total = _incrementar_contador()
    ip  = get_client_ip()
    loc = obter_localizacao_ip(ip) if ip else "IP não disponível"
    notificar_relatorio(empresa_nome, regime, loc, total)

if "r_atual" in st.session_state:
    r_atual   = st.session_state["r_atual"]
    r_reforma = st.session_state["r_reforma"]
    transicao = st.session_state["transicao"]
    cmv       = st.session_state["cmv"]
    margem_lucro = st.session_state["margem"]
    regime    = st.session_state["regime"]
    estado    = st.session_state["estado"]
    receita_anual = st.session_state["receita_anual"]

    diff      = r_reforma["carga_tributaria"] - r_atual["carga_tributaria"]
    diff_r    = (r_reforma["total_iva"]+r_reforma["custo_adaptacao"]) - r_atual["total_tributos"]

    tab1,tab2,tab3,tab4,tab5 = st.tabs([
        "📊 Resumo Comparativo","📈 Transição 2026-2033",
        "🔍 Detalhamento","🌱 Ações ESG / GRI","📋 Relatório & PDF"
    ])

    # ── TAB 1 ─────────────────────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-title">Comparativo: Sistema Atual vs. Reforma (2033)</div>',
                    unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card metric-navy"><h3>Carga Atual</h3>'
                        f'<p class="value">{pct(r_atual["carga_tributaria"])}</p>'
                        f'<p class="sub">{regime}</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card metric-red"><h3>Carga Reforma 2033</h3>'
                        f'<p class="value">{pct(r_reforma["carga_tributaria"])}</p>'
                        f'<p class="sub">CBS+IBS+Adaptação</p></div>', unsafe_allow_html=True)
        with c3:
            dc = "metric-red" if diff>0 else "metric-green"
            st.markdown(f'<div class="metric-card {dc}"><h3>Variação</h3>'
                        f'<p class="value">{"+" if diff>0 else ""}{pct(diff)}</p>'
                        f'<p class="sub">pontos percentuais</p></div>', unsafe_allow_html=True)
        with c4:
            dr = "metric-red" if diff_r>0 else "metric-green"
            st.markdown(f'<div class="metric-card {dr}"><h3>Impacto em R$</h3>'
                        f'<p class="value">{"+" if diff_r>0 else ""}{fmt(diff_r)}</p>'
                        f'<p class="sub">CMV = {fmt(cmv)}</p></div>', unsafe_allow_html=True)
        st.write("")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f'<div class="section-title">Sistema Atual — {regime}</div>',
                        unsafe_allow_html=True)
            dados = {"Item":["Custo (CMV)","Markup Divisor","Preço de Venda","Lucro Bruto",
                              "Total Tributos","Carga Tributária"],
                     "Valor":[fmt(cmv),f"{r_atual['markup']:.4f}",
                               fmt(r_atual["preco_venda"]),fmt(r_atual["lucro_bruto"]),
                               fmt(r_atual["total_tributos"]),pct(r_atual["carga_tributaria"])]}
            st.table(pd.DataFrame(dados))

        with col_b:
            st.markdown('<div class="section-title">Reforma 2033 — IVA por fora</div>',
                        unsafe_allow_html=True)
            dados2 = {"Item":["Custo (CMV)","Markup Divisor","Base de Cálculo","Lucro Bruto",
                               "CBS Federal (9,5%)","IBS Estadual (13%)","IBS Municipal (5,5%)",
                               "Total IVA (28%)","Compliance e Obrig.","Split Payment",
                               "Preço Final NF-e","Carga Total"],
                      "Valor":[fmt(cmv),f"{r_reforma['markup']:.4f}",
                                fmt(r_reforma["preco_venda"]),fmt(r_reforma["lucro_bruto"]),
                                fmt(r_reforma["cbs"]),fmt(r_reforma["ibs_estadual"]),
                                fmt(r_reforma["ibs_municipal"]),fmt(r_reforma["total_iva"]),
                                fmt(r_reforma["custo_compliance"]),fmt(r_reforma["custo_split_payment"]),
                                fmt(r_reforma["preco_final_nfe"]),pct(r_reforma["carga_tributaria"])]}
            st.table(pd.DataFrame(dados2))

        # Gráfico
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Sistema Atual", x=["Tributos","Preço de Venda"],
            y=[r_atual["total_tributos"],r_atual["preco_venda"]],
            marker=dict(color=RW["navy"], line=dict(color="#0E1228", width=0)),
            text=[fmt(r_atual["total_tributos"]),fmt(r_atual["preco_venda"])],
            textposition="outside", textfont=dict(family="Figtree", size=12, color=RW["navy"]),
            hovertemplate="<b>%{x}</b><br>Atual: %{text}<extra></extra>",
        ))
        fig.add_trace(go.Bar(
            name="Reforma 2033", x=["Tributos","Preço de Venda"],
            y=[r_reforma["total_iva"]+r_reforma["custo_adaptacao"],r_reforma["preco_final_nfe"]],
            marker=dict(color=RW["dark_red"], line=dict(color="#4A1F1F", width=0)),
            text=[fmt(r_reforma["total_iva"]+r_reforma["custo_adaptacao"]),
                  fmt(r_reforma["preco_final_nfe"])],
            textposition="outside", textfont=dict(family="Figtree", size=12, color=RW["dark_red"]),
            hovertemplate="<b>%{x}</b><br>Reforma: %{text}<extra></extra>",
        ))
        fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.08)
        style_fig(fig, "Comparativo Tributário e Preço", h=400)
        st.plotly_chart(fig, width='stretch')

        st.markdown(f"""<div class="alert-box">
            <h4>⚠️ Atenção: Impacto da Reforma na Operação</h4>
            <p>Além da mudança no IVA (CBS+IBS), a reforma exige <strong>adaptação de sistemas fiscais,
            novos obrigações acessórias e adequação ao Split Payment</strong> — custos estimados em <strong>3,7%
            sobre a base de cálculo</strong>. Sem planejamento adequado, sua empresa pode
            pagar mais do que o necessário na transição. <strong>A consultoria especializada faz diferença.</strong></p>
        </div>""", unsafe_allow_html=True)

    # ── TAB 2 ─────────────────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-title">Cronograma de Transição — 2026 a 2033</div>',
                    unsafe_allow_html=True)
        df_t = pd.DataFrame(transicao)
        c1,c2 = st.columns(2)
        with c1:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df_t["ano"], y=df_t["carga_tributaria"]*100,
                mode="lines+markers+text", name="Carga Total",
                line=dict(color=RW["dark_red"], width=3.5, shape="spline", smoothing=0.4),
                marker=dict(size=11, color=RW["dark_red"], line=dict(color="white", width=2)),
                text=[f"{v:.1f}%" for v in df_t["carga_tributaria"]*100],
                textposition="top center",
                textfont=dict(family="Figtree", size=11, color=RW["dark_red"]),
                hovertemplate="<b>%{x}</b><br>Carga: %{y:.2f}%<extra></extra>",
                fill="tozeroy", fillcolor="rgba(107,45,45,.06)",
            ))
            fig2.add_hline(
                y=r_atual["carga_tributaria"]*100, line_dash="dash",
                line_color=RW["navy"], line_width=1.5,
                annotation_text=f"<b>Atual: {pct(r_atual['carga_tributaria'])}</b>",
                annotation_font=dict(family="Figtree", color=RW["navy"], size=11),
            )
            style_fig(fig2, "Evolução da Carga Tributária", h=400, legend_top=False)
            fig2.update_layout(xaxis_title="Ano", yaxis_title="Carga (%)", showlegend=False)
            st.plotly_chart(fig2, width='stretch')
        with c2:
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(name="ICMS",   x=df_t["ano"], y=df_t["icms"]*100,
                                  marker_color=TRIB_COLORS["ICMS"], hovertemplate="ICMS: %{y:.2f}%<extra></extra>"))
            fig3.add_trace(go.Bar(name="PIS",    x=df_t["ano"], y=df_t["pis"]*100,
                                  marker_color=TRIB_COLORS["PIS"], hovertemplate="PIS: %{y:.2f}%<extra></extra>"))
            fig3.add_trace(go.Bar(name="COFINS", x=df_t["ano"], y=df_t["cofins"]*100,
                                  marker_color=TRIB_COLORS["COFINS"], hovertemplate="COFINS: %{y:.2f}%<extra></extra>"))
            fig3.add_trace(go.Bar(name="CBS",    x=df_t["ano"], y=df_t["cbs"]*100,
                                  marker_color=TRIB_COLORS["CBS"], hovertemplate="CBS: %{y:.2f}%<extra></extra>"))
            fig3.add_trace(go.Bar(name="IBS",    x=df_t["ano"], y=df_t["ibs"]*100,
                                  marker_color=TRIB_COLORS["IBS"], hovertemplate="IBS: %{y:.2f}%<extra></extra>"))
            fig3.update_layout(barmode="stack", bargap=0.18)
            style_fig(fig3, "Composição Tributária por Ano", h=400)
            fig3.update_layout(xaxis_title="Ano", yaxis_title="Alíquota (%)")
            st.plotly_chart(fig3, width='stretch')

        st.markdown('<div class="section-title">Tabela Detalhada</div>',unsafe_allow_html=True)
        df_show = df_t.copy()
        df_show.columns=["Ano","CBS","IBS","ICMS","PIS","COFINS","Taxa Total","Preço Venda","Total Trib.","Carga"]
        for c in ["CBS","IBS","ICMS","PIS","COFINS","Taxa Total","Carga"]:
            df_show[c]=df_show[c].apply(lambda x:f"{x*100:.2f}%")
        for c in ["Preço Venda","Total Trib."]:
            df_show[c]=df_show[c].apply(fmt)
        st.dataframe(df_show,width='stretch',hide_index=True)

        st.markdown("""<div class="alert-box">
            <h4>📌 Pontos Críticos da Transição</h4>
            <p>
            • <b>2026:</b> CBS (0,9%) e IBS (0,1%) estreiam — convivem com PIS/COFINS e ICMS<br>
            • <b>2027:</b> CBS sobe para 9,5%; PIS e COFINS são extintos<br>
            • <b>2029–2032:</b> ICMS reduzido gradualmente; IBS cresce proporcionalmente<br>
            • <b>2033:</b> Sistema pleno — IVA de 28% (CBS 9,5% + IBS 18,5%)<br><br>
            <b>Empresas sem planejamento tributário adequado pagarão mais na transição.</b>
            </p></div>""", unsafe_allow_html=True)

    # ── TAB 3 ─────────────────────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-title">Detalhamento dos Cálculos</div>',unsafe_allow_html=True)
        cd1,cd2 = st.columns(2)
        with cd1:
            st.markdown(f"#### 🏢 Sistema Atual — {regime}")
            if regime=="Simples Nacional":
                fx = faixa_simples(receita_anual)
                st.info(f"**Faixa:** {fx['faixa']} | **Alíquota:** {fx['aliquota']*100:.1f}% | **Dedução:** {fmt(fx['deduzir'])}")
            st.markdown("**Mark Up Divisor:**")
            st.latex(rf"\text{{Markup}} = 1 - ({r_atual['aliquota_efetiva']:.4f} + {margem_lucro:.2f}) = {r_atual['markup']:.4f}")
            st.latex(rf"\text{{Preço}} = \frac{{{fmt_latex(cmv)}}}{{{r_atual['markup']:.4f}}} = {fmt_latex(r_atual['preco_venda'])}")
            if regime!="Simples Nacional":
                st.table(pd.DataFrame({
                    "Tributo":["ICMS","PIS","COFINS","Total"],
                    "Valor":[fmt(r_atual["icms"]),fmt(r_atual["pis"]),
                             fmt(r_atual["cofins"]),fmt(r_atual["total_tributos"])]}))
        with cd2:
            st.markdown("#### 🔄 Reforma 2033 — IVA Dual (por fora)")
            st.latex(rf"\text{{Base}} = \frac{{{fmt_latex(cmv)}}}{{1-{margem_lucro:.2f}}} = {fmt_latex(r_reforma['preco_venda'])}")
            st.latex(rf"\text{{IVA}} = {fmt_latex(r_reforma['preco_venda'])} \times 0{{,}}28 = {fmt_latex(r_reforma['total_iva'])}")
            st.latex(rf"\text{{NF-e}} = {fmt_latex(r_reforma['preco_venda'])} + {fmt_latex(r_reforma['total_iva'])} + {fmt_latex(r_reforma['custo_adaptacao'])} = {fmt_latex(r_reforma['preco_final_nfe'])}")
            st.table(pd.DataFrame({
                "Tributo":["CBS (9,5%)","IBS Estadual (13%)","IBS Municipal (5,5%)","Total IVA","Compliance","Split Payment"],
                "Valor":[fmt(r_reforma["cbs"]),fmt(r_reforma["ibs_estadual"]),
                         fmt(r_reforma["ibs_municipal"]),fmt(r_reforma["total_iva"]),
                         fmt(r_reforma["custo_compliance"]),fmt(r_reforma["custo_split_payment"])]}))

        st.markdown("---")
        st.markdown("#### ♻️ Não-Cumulatividade IBS/CBS")
        # Tabela com tipos uniformes (todas strings) para evitar erro de serialização Arrow
        df_nc = pd.DataFrame({
            "Etapa":["Produtor Rural","Indústria (+20%)","Distribuidor (+20%)","Varejista (+25%)","Consumidor Final"],
            "Valor":         [fmt(1000), fmt(1280), fmt(2048), fmt(3276.80), fmt(5593.60)],
            "IVA 28%":       [fmt(280),  fmt(448),  fmt(716.80), fmt(1223.60), fmt(1223.60)],
            "Total NF-e":    [fmt(1280), fmt(2048), fmt(3276.80), fmt(5593.60), fmt(5593.60)],
            "IVA a Recolher":[fmt(280),  fmt(168),  fmt(268.80),  fmt(506.80),  "—"],
        })
        st.table(df_nc)

    # ── TAB 4 — ESG ───────────────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-title">Ações ESG como Dedução Fiscal na Reforma</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        **ESG é tudo o que a empresa faz além das obrigações legais**, tanto internamente quanto externamente.
        Com a reforma tributária, ações ESG alinhadas aos indicadores GRI geram **deduções na base de cálculo** dos tributos.
        Selecione as ações que sua empresa já realiza ou planeja implementar:
        """)
        st.write("")

        acoes = []
        for cat, inds in GRI_INDICATORS.items():
            with st.expander(f"**{cat}**", expanded=False):
                for nome_ind, d in inds.items():
                    col_chk, col_info = st.columns([1, 3])
                    with col_chk:
                        sel = st.checkbox(
                            f"**{nome_ind}**",
                            help=d["desc"],
                            key=f"esg_{nome_ind}"
                        )
                        if sel:
                            acoes.append({"nome":nome_ind,"taxa":d["taxa"],"cat":cat})
                        st.caption(f"Dedução: **{d['taxa']*100:.0f}%**")
                    with col_info:
                        st.markdown(f"*{d['desc']}*")
                        st.markdown("**Exemplos de ações:**")
                        for ex in d["exemplos"]:
                            st.markdown(f'<div class="esg-example-item">• {ex}</div>',
                                        unsafe_allow_html=True)
                    st.markdown("---")

        if acoes:
            base = r_reforma["preco_venda"]
            esg  = calc_esg(base, acoes)

            st.markdown('<div class="section-title">Resultado das Ações ESG</div>',
                        unsafe_allow_html=True)
            ce1,ce2,ce3 = st.columns(3)
            with ce1:
                st.markdown(f'<div class="metric-card metric-green"><h3>Taxa de Dedução</h3>'
                            f'<p class="value">{pct(esg["taxa_total"])}</p>'
                            f'<p class="sub">da base tributável</p></div>', unsafe_allow_html=True)
            with ce2:
                st.markdown(f'<div class="metric-card metric-green"><h3>Dedução em R$</h3>'
                            f'<p class="value">{fmt(esg["valor_deducao"])}</p>'
                            f'<p class="sub">redução na base</p></div>', unsafe_allow_html=True)
            with ce3:
                st.markdown(f'<div class="metric-card metric-green"><h3>Economia Fiscal</h3>'
                            f'<p class="value">{fmt(esg["economia_fiscal"])}</p>'
                            f'<p class="sub">por operação</p></div>', unsafe_allow_html=True)

            fig_e = go.Figure()
            fig_e.add_trace(go.Bar(
                name="Sem ESG", x=["IVA Total"],
                y=[r_reforma["total_iva"]],
                marker=dict(color=RW["dark_red"]),
                text=[fmt(r_reforma["total_iva"])],
                textposition="outside",
                textfont=dict(family="Figtree", size=12, color=RW["dark_red"]),
                hovertemplate="Sem ESG: %{text}<extra></extra>",
            ))
            fig_e.add_trace(go.Bar(
                name="Com ESG", x=["IVA Total"],
                y=[r_reforma["total_iva"]-esg["economia_fiscal"]],
                marker=dict(color=RW["green"]),
                text=[fmt(r_reforma["total_iva"]-esg["economia_fiscal"])],
                textposition="outside",
                textfont=dict(family="Figtree", size=12, color=RW["green"]),
                hovertemplate="Com ESG: %{text}<extra></extra>",
            ))
            fig_e.update_layout(barmode="group", bargap=0.4, bargroupgap=0.1)
            style_fig(fig_e, "IVA Total: Sem ESG vs. Com Ações ESG", h=350)
            st.plotly_chart(fig_e, width='stretch')

            eco_anual = esg["economia_fiscal"] * max(receita_anual/cmv if cmv>0 else 1, 1)
            st.markdown(f"""<div class="alert-box">
                <h4>💡 Potencial de Economia Anual com ESG</h4>
                <p>Com as ações selecionadas, potencial de economizar até <strong>{fmt(eco_anual)}/ano</strong>.
                ESG não é só responsabilidade social — é <strong>inteligência fiscal</strong>.
                A RedWood pode estruturar um plano ESG personalizado para maximizar suas deduções.</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("👆 Abra as categorias acima e selecione as ações ESG da sua empresa.")

    # ── TAB 5 — Relatório & PDF ───────────────────────────────────────────────
    with tab5:
        st.markdown('<div class="section-title">Relatório Executivo</div>',unsafe_allow_html=True)

        nome_emp = st.session_state.get("empresa_nome","Empresa")
        st.markdown(f"""
        ### Projeção de Impacto — Reforma Tributária
        **Empresa:** {nome_emp} | **Regime:** {regime} | **UF:** {estado} | **Data:** {datetime.date.today().strftime('%d/%m/%Y')}

        ---

        #### Cenário Atual
        | Indicador | Valor |
        |-----------|-------|
        | CMV | {fmt(cmv)} |
        | Preço de Venda | {fmt(r_atual['preco_venda'])} |
        | Total Tributos | {fmt(r_atual['total_tributos'])} |
        | Carga Tributária | {pct(r_atual['carga_tributaria'])} |

        #### Cenário Reforma (2033)
        | Indicador | Valor |
        |-----------|-------|
        | Base de Cálculo | {fmt(r_reforma['preco_venda'])} |
        | IVA Total (28%) | {fmt(r_reforma['total_iva'])} |
        | Compliance + Obrigações | {fmt(r_reforma['custo_compliance'])} |
        | Split Payment | {fmt(r_reforma['custo_split_payment'])} |
        | Preço Final NF-e | {fmt(r_reforma['preco_final_nfe'])} |
        | Carga Tributária Total | {pct(r_reforma['carga_tributaria'])} |

        #### Impacto
        - Variação da carga: **{"+" if diff>0 else ""}{pct(diff)}**
        - Impacto por operação: **{"+" if diff_r>0 else ""}{fmt(diff_r)}**
        """)

        st.markdown(f"""<div class="cta-box">
            <h3>🌲 Precisa de apoio na transição para a Reforma?</h3>
            <p>A RedWood Estratégia & Impacto oferece consultoria especializada em reforma tributária,
            planejamento fiscal e estratégias ESG.<br><br>
            📧 <strong>fernando@redwood.report</strong> · 🌐 <strong>redwood.report</strong><br><br>
            <em>Entre em contato para uma análise personalizada da sua empresa.</em></p>
        </div>""", unsafe_allow_html=True)

        st.markdown("---")
        col_pdf1, col_pdf2 = st.columns([2,1])
        with col_pdf1:
            if st.button("📥 Gerar e Baixar Relatório em PDF", type="primary", width='stretch'):
                with st.spinner("Gerando PDF..."):
                    pdf_bytes = gerar_pdf(
                        nome_emp, regime, estado, cmv, margem_lucro,
                        r_atual, r_reforma, transicao, diff, diff_r
                    )
                st.success("✅ Relatório gerado! Clique em **Baixar PDF** abaixo.")
                st.download_button(
                    label="⬇️ Baixar PDF",
                    data=pdf_bytes,
                    file_name=f"reforma_tributaria_{nome_emp.replace(' ','_')}_{datetime.date.today()}.pdf",
                    mime="application/pdf",
                    width='stretch',
                )
        with col_pdf2:
            st.markdown("""
            **O PDF inclui:**
            - Comparativo atual vs. reforma
            - Tabela de transição 2026-2033
            - Indicadores GRI com exemplos
            - Call to action RedWood
            """)

else:
    # Tela de boas-vindas
    st.markdown(f"""
    <div style="text-align:center;padding:2.5rem 1rem">
        <h2 style="color:{RW['navy']}">Simule o Impacto da Reforma Tributária na Sua Empresa</h2>
        <p style="color:{RW['text']};font-size:1rem;max-width:650px;margin:1rem auto">
            Preencha os dados no painel lateral e clique em <strong>"Calcular Projeção"</strong>.
            Você pode buscar o CNPJ automaticamente para preencher os dados da empresa.
        </p>
    </div>""", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    cards = [
        ("metric-navy","📊 Comparativo","Atual vs. Reforma 2033","Carga tributária lado a lado"),
        ("metric-red","📈 Transição","2026 → 2033","Cronograma ano a ano"),
        ("metric-green","🌱 ESG / GRI","Deduções Fiscais","Ações sustentáveis = economia"),
    ]
    for col,(cls,title,val,sub) in zip([c1,c2,c3],cards):
        with col:
            st.markdown(f'<div class="metric-card {cls}"><h3>{title}</h3>'
                        f'<p class="value" style="font-size:1rem">{val}</p>'
                        f'<p class="sub">{sub}</p></div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="cta-box" style="margin-top:2rem">
        <h3>🌲 RedWood Estratégia & Impacto</h3>
        <p>Consultoria especializada em reforma tributária, planejamento fiscal e estratégias ESG.<br>
        📧 <strong>fernando@redwood.report</strong> · 🌐 <strong>redwood.report</strong></p>
    </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""<div class="footer-bar">
    🌲 <strong>RedWood Estratégia &amp; Impacto</strong> &nbsp;|&nbsp;
    📧 <a href="mailto:fernando@redwood.report" style="color:{RW['beige']}">fernando@redwood.report</a> &nbsp;|&nbsp;
    🌐 <strong>redwood.report</strong>
</div>""", unsafe_allow_html=True)
