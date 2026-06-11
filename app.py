import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
import base64
import pytz

# ─────────────────────────────────────────────────────────────
# 1. CONFIGURAÇÃO BASE
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartView | Visão Geral do Pátio",
    page_icon="assets\favicon.ico",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import auth
import backend as bk

# ─────────────────────────────────────────────────────────────
# 2. BLOQUEIO DE TELA
# ─────────────────────────────────────────────────────────────
if not auth.check_auth():
    auth.login_screen()
    st.stop()

# ─────────────────────────────────────────────────────────────
# 3. CSS GLOBAL — DESIGN PREMIUM
# ─────────────────────────────────────────────────────────────
def get_base64_img(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

bg_path = "assets\tecadi.png"
bg_b64 = get_base64_img(bg_path)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');

/* ── BASE ─────────────────────────────────────────────────── */
html, body, [class*="css"], [class*="st-"] {{
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important;
}}

::-webkit-scrollbar {{ width: 0px !important; height: 0px !important; background: transparent !important; }}
* {{ scrollbar-width: none !important; }}

[data-testid="stApp"] {{
    background-image: url("data:image/png;base64,{bg_b64}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

.block-container {{
    max-width: 98% !important;
    background: transparent !important;
    padding: 0.5rem 1.4rem 1.2rem 1.4rem !important;
    margin-top: 0 !important;
}}

header[data-testid="stHeader"], footer {{ display: none !important; }}

/* ── KPI CARDS ────────────────────────────────────────────── */
[data-testid="stPlotlyChart"] {{
    background-color: rgba(15, 20, 28, 0.88) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border-radius: 14px !important;
    padding: 10px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.55) !important;
    overflow: hidden !important;
    transition: box-shadow 0.25s ease !important;
}}
[data-testid="stPlotlyChart"]:hover {{
    box-shadow: 0 12px 42px rgba(0, 159, 238, 0.18) !important;
}}
[data-testid="stPlotlyChart"] iframe {{ overflow: hidden !important; }}

/* ── DATAFRAME ────────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}
[data-testid="stDataFrame"] > div {{ background-color: transparent !important; }}

/* ── TABS ─────────────────────────────────────────────────── */
[data-testid="stTabs"] > div:first-child {{
    background-color: rgba(10, 14, 22, 0.75) !important;
    border-radius: 12px 12px 0 0 !important;
    border-bottom: 2px solid rgba(255,255,255,0.08) !important;
    padding: 0 8px !important;
    backdrop-filter: blur(10px) !important;
}}
button[data-baseweb="tab"] {{
    color: #7A8CA0 !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 10px 22px !important;
    letter-spacing: 0.3px !important;
    transition: color 0.2s ease !important;
}}
button[data-baseweb="tab"]:hover {{
    color: #CBD5E1 !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: #FFFFFF !important;
    border-bottom: 3px solid #009fee !important;
    text-shadow: 0 0 12px rgba(0,159,238,0.5) !important;
}}
[data-testid="stTabsContent"] {{
    background-color: transparent !important;
    padding-top: 12px !important;
}}

/* ── BOTÕES STREAMLIT ─────────────────────────────────────── */
[data-testid="stButton"] > button {{
    background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(239,68,68,0.05)) !important;
    border: 1px solid rgba(239,68,68,0.45) !important;
    color: #EF4444 !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    border-radius: 8px !important;
    padding: 6px 14px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.3px !important;
}}
[data-testid="stButton"] > button:hover {{
    background: linear-gradient(135deg, rgba(239,68,68,0.3), rgba(239,68,68,0.12)) !important;
    border-color: rgba(239,68,68,0.7) !important;
    box-shadow: 0 0 14px rgba(239,68,68,0.25) !important;
    transform: translateY(-1px) !important;
}}
[data-testid="stButton"] > button:active {{
    transform: translateY(0px) !important;
}}

/* ── ANIMAÇÃO FADE-IN ─────────────────────────────────────── */
@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.fenix-card {{
    animation: fadeInUp 0.35s ease both;
}}

/* ── BARRA DE OCUPAÇÃO ────────────────────────────────────── */
@keyframes barFill {{
    from {{ width: 0%; }}
    to   {{ width: var(--bar-width); }}
}}
.ocupacao-bar-track {{
    background: rgba(255,255,255,0.06);
    border-radius: 6px;
    height: 7px;
    width: 100%;
    overflow: hidden;
    margin-top: 6px;
}}
.ocupacao-bar-fill {{
    height: 100%;
    border-radius: 6px;
    animation: barFill 1.1s cubic-bezier(.4,0,.2,1) both;
    animation-delay: 0.15s;
}}

/* ── HEADER CARD ─────────────────────────────────────────── */
.fenix-header {{
    background: linear-gradient(135deg, rgba(10,14,22,0.92), rgba(19,58,104,0.45));
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 14px;
    border: 1px solid rgba(0,159,238,0.2);
    box-shadow: 0 4px 24px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06);
    padding: 10px 20px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# 4. FUNÇÃO CARDS KPI — altura uniforme 110px, todos iguais
# ─────────────────────────────────────────────────────────────
CARD_HEIGHT = "110px"
CARD_BASE = """
    background: linear-gradient(160deg, rgba(15,20,28,0.92), rgba(10,14,22,0.88));
    backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
    border-radius: 14px; padding: 0 14px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    border-right: 1px solid rgba(255,255,255,0.04);
    border-left: 1px solid rgba(255,255,255,0.04);
    box-shadow: 0 8px 32px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.05);
    font-family: 'Montserrat', sans-serif;
    display: flex; flex-direction: column;
    justify-content: center; align-items: center;
    width: 100%; box-sizing: border-box;
"""


def create_kpi_card(title, value, accent_color="#009fee", subtitle="", subtitle_color=None):
    sub_color = subtitle_color or accent_color
    subtitle_html = (
        f'<p style="color:{sub_color};font-size:10px;font-weight:700;margin:2px 0 0 0;'
        f'letter-spacing:0.2px;line-height:1;">{subtitle}</p>'
    ) if subtitle else '<p style="margin:0;font-size:10px;">&nbsp;</p>'

    html = f"""
    <div class="fenix-card" style="{CARD_BASE} height:{CARD_HEIGHT}; border-top:3px solid {accent_color};">
        <p style="color:#7A8CA0;font-size:10px;font-weight:700;text-transform:uppercase;
                  margin:0;text-align:center;line-height:1.3;letter-spacing:0.8px;">{title}</p>
        <h1 style="color:#FFFFFF;font-size:28px;font-weight:800;margin:4px 0 0 0;
                   text-shadow:0px 0px 10px {accent_color}55;line-height:1;">{value}</h1>
        {subtitle_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def create_kpi_card_ocupacao(title, pct, max_cap, total):
    """Card de ocupação: barra animada com % sobreposta dentro da barra."""
    cor = "#EF4444" if pct > 80 else ("#F59E0B" if pct > 60 else "#10B981")
    bar_gradient = (
        "linear-gradient(90deg,#EF4444,#F87171)" if pct > 80
        else ("linear-gradient(90deg,#F59E0B,#FCD34D)" if pct > 60
              else "linear-gradient(90deg,#10B981,#34D399)")
    )
    fill_pct = min(pct, 100)

    html = f"""
    <div class="fenix-card" style="{CARD_BASE} height:{CARD_HEIGHT}; border-top:3px solid {cor};">
        <p style="color:#7A8CA0;font-size:10px;font-weight:700;text-transform:uppercase;
                  margin:0;letter-spacing:0.8px;">{title}</p>
        <h1 style="color:#FFFFFF;font-size:28px;font-weight:800;margin:4px 0 3px 0;
                   text-shadow:0px 0px 10px {cor}55;line-height:1;">{pct:.1f}%</h1>
        <!-- barra com % sobreposta -->
        <div style="position:relative;width:100%;height:16px;
                    background:rgba(255,255,255,0.06);border-radius:8px;overflow:hidden;">
            <div style="
                position:absolute;top:0;left:0;height:100%;
                width:{fill_pct:.1f}%;
                background:{bar_gradient};
                border-radius:8px;
                box-shadow:0 0 8px {cor}88;
                animation:barFill 1.1s cubic-bezier(.4,0,.2,1) both;
                animation-delay:0.15s;
                --bar-width:{fill_pct:.1f}%;
            "></div>
            <span style="
                position:absolute;top:50%;left:50%;
                transform:translate(-50%,-50%);
                font-size:9px;font-weight:800;color:#FFFFFF;
                text-shadow:0 1px 3px rgba(0,0,0,0.8);
                letter-spacing:0.5px;white-space:nowrap;
                z-index:2;
            ">{total} / {max_cap} CNTR</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def create_kpi_card_total(title, value, max_cap, accent_color="#133a68"):
    """Card Total em Pátio com capacidade máxima — mesma altura."""
    html = f"""
    <div class="fenix-card" style="{CARD_BASE} height:{CARD_HEIGHT}; border-top:3px solid {accent_color};">
        <p style="color:#7A8CA0;font-size:10px;font-weight:700;text-transform:uppercase;
                  margin:0;letter-spacing:0.8px;">{title}</p>
        <h1 style="color:#FFFFFF;font-size:28px;font-weight:800;margin:4px 0 2px 0;
                   text-shadow:0px 0px 10px {accent_color}55;line-height:1;">{value}</h1>
        <div style="display:flex;align-items:center;gap:5px;">
            <div style="width:6px;height:6px;border-radius:50%;
                        background:{accent_color};box-shadow:0 0 6px {accent_color};"></div>
            <p style="color:#7A8CA0;font-size:10px;font-weight:700;margin:0;
                      letter-spacing:0.4px;">Cap. Máx: {max_cap} CNTR</p>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# 5. CARREGAMENTO DOS DADOS
# ─────────────────────────────────────────────────────────────
df_tecadi, df_armador, df_freetime = bk.load_data()

total_tecadi   = len(df_tecadi)
total_armador  = len(df_armador)
total_geral    = total_tecadi + total_armador
max_capacidade = 2159
ocupacao_pct   = (total_geral / max_capacidade) * 100

vazios_tecadi = (
    len(df_tecadi[df_tecadi['CLIENTE'].astype(str).str.strip().str.upper() == 'VAZIO'])
    if not df_tecadi.empty else 0
)
df_vazios_armador     = df_armador[df_armador['Conteudo'].astype(str).str.strip().str.upper() == 'VAZIO']
total_vazios_armador  = len(df_vazios_armador)

df_armador['Dt. free'] = pd.to_datetime(df_armador['Dt. free'], errors='coerce')
fuso_br  = pytz.timezone('America/Sao_Paulo')
hoje     = pd.to_datetime(datetime.datetime.now(fuso_br).date())
df_vencidos_armador = df_armador[df_armador['Dt. free'] < hoje]

COR_TECADI  = '#133a68'
COR_ARMADOR = '#009fee'


# ─────────────────────────────────────────────────────────────
# 6. FUNÇÃO PLOTLY BASE
# ─────────────────────────────────────────────────────────────
def apply_plotly_transparency(fig, custom_height=300):
    fig.update_layout(
        height=custom_height,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF', family="Montserrat"),
        margin=dict(l=10, r=10, t=40, b=80),
        title_font=dict(size=14, color='#FFFFFF', family="Montserrat"),
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(color='#CBD5E1', family='Montserrat', size=10),
            tickangle=-35,
            automargin=True,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            zeroline=False,
            tickfont=dict(color='#CBD5E1', family='Montserrat', size=11),
        ),
        barmode='stack',
        legend=dict(
            font=dict(color="white", family='Montserrat', size=11),
            title=dict(font=dict(color="white", family='Montserrat')),
            bgcolor='rgba(0,0,0,0)',
        )
    )
    return fig


# ─────────────────────────────────────────────────────────────
# 7. CABEÇALHO — centralizado, estilo premium
# ─────────────────────────────────────────────────────────────
agora_brasil = datetime.datetime.now(fuso_br)

c_logo, c_titulo, c_data = st.columns([1, 6, 2])
with c_logo:
    st.image(
        "assets\logosemfundotecadi.png",
        width=100
    )
with c_titulo:
    st.markdown("""
        <div style="display:flex; flex-direction:column; align-items:center;
                    justify-content:center; height:100%; padding-top:8px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="width:3px; height:28px;
                            background:linear-gradient(180deg,#009fee,#0077cc);
                            border-radius:2px;"></div>
                <h2 style="
                    margin:0; font-weight:900; font-size:23px; letter-spacing:0.6px;
                    background: linear-gradient(90deg, #009fee, #66ccff, #009fee);
                    background-size: 200% auto;
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    animation: shimmer 3s linear infinite;
                    filter: drop-shadow(0px 0px 8px rgba(0,159,238,0.55));
                ">
                    SmartView | Visão Geral do Pátio
                </h2>
                <div style="width:3px; height:28px;
                            background:linear-gradient(180deg,#0077cc,#009fee);
                            border-radius:2px;"></div>
            </div>
            <div style="height:2px; width:240px; margin-top:5px;
                        background:linear-gradient(90deg, transparent, #009fee, transparent);
                        border-radius:1px;"></div>
        </div>
        <style>
        @keyframes shimmer {{
            0%   {{ background-position: 0% center; }}
            100% {{ background-position: 200% center; }}
        }}
        </style>
    """, unsafe_allow_html=True)
with c_data:
    st.markdown(f"""
        <div style="text-align:right; margin-top:14px; font-family:'Montserrat',sans-serif;">
            <p style="color:#009fee; font-size:9.5px; font-weight:700; text-transform:uppercase;
                      letter-spacing:0.9px; margin:0; opacity:0.75;">Última Atualização</p>
            <p style="
                font-size:15px; font-weight:800; margin:3px 0 0 0;
                background: linear-gradient(90deg, #009fee, #66ccff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                filter: drop-shadow(0 0 8px rgba(0,159,238,0.5));
            ">
                {agora_brasil.strftime('%d/%m/%Y %H:%M')}
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# 8. LINHA KPI — 6 cards
# ─────────────────────────────────────────────────────────────
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

with kpi1:
    create_kpi_card_total("Total em Pátio", total_geral, max_capacidade, COR_TECADI)
with kpi2:
    create_kpi_card_ocupacao("Ocupação do Pátio", ocupacao_pct, max_capacidade, total_geral)
with kpi3:
    create_kpi_card("CNTR Locado (Tecadi)", total_tecadi, COR_TECADI)
with kpi4:
    create_kpi_card("CNTR Armador", total_armador, COR_ARMADOR)
with kpi5:
    create_kpi_card("Vazios Tecadi", vazios_tecadi, COR_TECADI)
with kpi6:
    create_kpi_card("Vazios Armador", total_vazios_armador, COR_ARMADOR)

st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# 9. TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📦   Distribuição por Cliente", "⚠️   Freetime & Status Vazio"])


# ══════════════════════════════════════════════════════════════
# TAB 1 — Gráficos EMPILHADOS (um abaixo do outro, 100%)
# ══════════════════════════════════════════════════════════════
with tab1:

    # ── Gráfico 1: CNTR Locado Tecadi ──────────────────────────
    if not df_tecadi.empty:
        df_g1 = (
            df_tecadi.groupby('CLIENTE').size()
            .reset_index(name='Qtd')
            .sort_values('Qtd', ascending=False)
        )
        fig1 = px.bar(
            df_g1, x='CLIENTE', y='Qtd',
            title="📦  CNTR Locado Tecadi por Cliente",
            text='Qtd',
            color_discrete_sequence=[COR_TECADI]
        )
        fig1.update_traces(
            textposition='outside',
            cliponaxis=False,
            textfont=dict(color='white', size=11, family='Montserrat'),
            marker=dict(
                line=dict(width=0),
                opacity=0.92,
            ),
            hovertemplate="<b>%{x}</b><br>Qtd: %{y}<extra></extra>",
        )
        fig1 = apply_plotly_transparency(fig1, custom_height=320)
        fig1.update_layout(
            margin=dict(l=10, r=10, t=42, b=90),
            xaxis=dict(tickangle=-40, automargin=True, tickfont=dict(size=10)),
        )
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("⚠️ Aguardando carregamento da base Tecadi...")

    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

    # ── Gráfico 2: CNTR Armador ─────────────────────────────────
    if not df_armador.empty:
        df_g2 = (
            df_armador.groupby('Cliente').size()
            .reset_index(name='Qtd')
            .sort_values('Qtd', ascending=False)
        )
        fig2 = px.bar(
            df_g2, x='Cliente', y='Qtd',
            title="🚢  CNTR Armador por Cliente",
            text='Qtd',
            color_discrete_sequence=[COR_ARMADOR]
        )
        fig2.update_traces(
            textposition='outside',
            cliponaxis=False,
            textfont=dict(color='white', size=11, family='Montserrat'),
            marker=dict(line=dict(width=0), opacity=0.92),
            hovertemplate="<b>%{x}</b><br>Qtd: %{y}<extra></extra>",
        )
        fig2 = apply_plotly_transparency(fig2, custom_height=320)
        fig2.update_layout(
            margin=dict(l=10, r=10, t=42, b=90),
            xaxis=dict(tickangle=-40, automargin=True, tickfont=dict(size=10)),
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("⚠️ Aguardando carregamento da base Armador...")


# ══════════════════════════════════════════════════════════════
# TAB 2 — Freetime & Status Vazio (100% width, sem cortes)
# ══════════════════════════════════════════════════════════════
with tab2:

    ALTURA_TAB2 = 370

    if 'cliente_selecionado' not in st.session_state:
        st.session_state.cliente_selecionado = None

    # ── Linha superior: Pizza | Vazios | Freetime ─────────────
    col_pie, col_vazios, col_free = st.columns([1, 0.75, 1.6])

    # ── PIZZA ────────────────────────────────────────────────
    with col_pie:
        df_pizza = pd.DataFrame({
            'Tipo': ['Tecadi', 'Armador'],
            'Quantidade': [total_tecadi, total_armador]
        })
        fig_pie = px.pie(
            df_pizza, values='Quantidade', names='Tipo',
            hole=0.58,
            title="Distribuição do Pátio",
            color_discrete_sequence=[COR_TECADI, COR_ARMADOR]
        )
        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            showlegend=False,
            textfont=dict(color='white', size=12, family='Montserrat'),
            hovertemplate="<b>%{label}</b><br>%{value} containers<br>%{percent}<extra></extra>",
            pull=[0.03, 0.03],
        )
        fig_pie = apply_plotly_transparency(fig_pie, custom_height=ALTURA_TAB2)
        fig_pie.update_layout(margin=dict(t=42, b=8, l=8, r=8))
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

    # ── TABELA VAZIOS ARMADOR ─────────────────────────────────
    with col_vazios:
        st.markdown(
            "<div style='background:linear-gradient(160deg,rgba(15,20,28,0.92),rgba(10,14,22,0.88));"
            "backdrop-filter:blur(14px); border-radius:14px; padding:14px 16px;"
            "border:1px solid rgba(255,255,255,0.07); box-shadow:0 8px 32px rgba(0,0,0,0.55);'>"
            "<p style='color:#7A8CA0; font-size:10px; font-weight:700; text-transform:uppercase;"
            "letter-spacing:0.8px; margin:0 0 10px 0;'>🧊 Armadores — Status Vazio</p>",
            unsafe_allow_html=True
        )
        if not df_vazios_armador.empty:
            df_vazios_agrupado = (
                df_vazios_armador.groupby('Cliente').size()
                .reset_index(name='QTD')
                .sort_values('QTD', ascending=False)
            )
            st.dataframe(
                df_vazios_agrupado,
                use_container_width=True,
                hide_index=True,
                height=ALTURA_TAB2 - 58
            )
        else:
            st.markdown(
                "<p style='color:#10B981; font-size:12px; text-align:center; margin-top:20px;'>"
                "✓ Nenhum vazio encontrado.</p>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── FREETIME VENCIDO ──────────────────────────────────────
    with col_free:
        if not df_vencidos_armador.empty:
            df_stack = (
                df_vencidos_armador.groupby(['Cliente', 'Conteudo'])
                .size().reset_index(name='Qtd')
            )
            fig_stack = px.bar(
                df_stack, x='Cliente', y='Qtd', color='Conteudo',
                barmode='stack',
                title="⚠️  Freetime Vencido — clique para detalhar",
                text_auto=True,
                color_discrete_map={'CHEIO': COR_TECADI, 'VAZIO': COR_ARMADOR}
            )
            fig_stack.update_traces(
                textposition="inside",
                textfont=dict(color='white', family='Montserrat', size=11),
                hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y}<extra></extra>",
            )
            fig_stack = apply_plotly_transparency(fig_stack, custom_height=ALTURA_TAB2)
            fig_stack.update_layout(
                margin=dict(l=10, r=10, t=42, b=90),
                xaxis=dict(
                    tickangle=-40,
                    automargin=True,
                    tickfont=dict(color='#CBD5E1', size=10),
                ),
                yaxis=dict(tickfont=dict(color='#CBD5E1')),
                legend=dict(
                    title=dict(font=dict(color='white')),
                    bgcolor='rgba(0,0,0,0)',
                ),
            )

            evento = st.plotly_chart(
                fig_stack,
                use_container_width=True,
                config={'displayModeBar': False},
                on_select="rerun",
                key="freetime_chart"
            )

            if evento and evento.get("selection") and evento["selection"].get("points"):
                ponto = evento["selection"]["points"][0]
                cliente_clicado = ponto.get("x") or ponto.get("label")
                if cliente_clicado:
                    st.session_state.cliente_selecionado = cliente_clicado

        else:
            st.markdown("""
            <div style="background:linear-gradient(135deg,rgba(16,185,129,0.12),rgba(16,185,129,0.05));
                        backdrop-filter:blur(12px); border:1px solid rgba(16,185,129,0.35);
                        padding:20px; border-radius:14px; text-align:center;
                        box-shadow:0 4px 20px rgba(0,0,0,0.3); margin-top:12px;">
                <div style='font-size:28px; margin-bottom:8px;'>✅</div>
                <span style='color:#10B981; font-weight:800; font-size:13px; letter-spacing:0.3px;'>
                    Nenhum Armador com Freetime vencido detectado.
                </span>
            </div>
            """, unsafe_allow_html=True)

    # ── DRILL-DOWN ───────────────────────────────────────────
    if st.session_state.cliente_selecionado and not df_vencidos_armador.empty:
        cliente  = st.session_state.cliente_selecionado
        df_drill = df_vencidos_armador[df_vencidos_armador['Cliente'] == cliente].copy()

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        header_col, close_col = st.columns([10, 1])
        with header_col:
            st.markdown(
                f"<div style='background:linear-gradient(135deg,rgba(239,68,68,0.12),rgba(15,20,28,0.9));"
                f"border-left:4px solid #EF4444; border:1px solid rgba(239,68,68,0.25);"
                f"border-radius:10px; padding:10px 18px; animation: fadeInUp 0.3s ease both;'>"
                f"<span style='color:#EF4444; font-size:13px; font-weight:800; text-transform:uppercase;"
                f"letter-spacing:0.5px;'>⚠️ Containers Freetime Vencido — {cliente}</span>"
                f"<span style='color:#7A8CA0; font-size:11px; margin-left:12px;'>"
                f"({len(df_drill)} containers)</span></div>",
                unsafe_allow_html=True
            )
        with close_col:
            if st.button("✕ Fechar", key="fechar_drill", use_container_width=True):
                st.session_state.cliente_selecionado = None
                st.rerun()

        st.markdown("<div style='height:5px;'></div>", unsafe_allow_html=True)

        colunas_exibir = [
            c for c in ['Container', 'CNTR', 'Numero', 'Conteudo', 'Dt. free', 'Cliente']
            if c in df_drill.columns
        ]
        if not colunas_exibir:
            colunas_exibir = df_drill.columns.tolist()

        df_exibir = df_drill[colunas_exibir].copy()
        for col_data in ['Dt. free']:
            if col_data in df_exibir.columns:
                df_exibir[col_data] = (
                    pd.to_datetime(df_exibir[col_data], errors='coerce')
                    .dt.strftime('%d/%m/%Y')
                )

        st.dataframe(df_exibir, use_container_width=True, hide_index=True, height=230)
