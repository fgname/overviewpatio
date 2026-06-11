import streamlit as st
import base64

USUARIO_CORRETO = "admin"
SENHA_CORRETA = "@tecadi2026"

if "logado" not in st.session_state:
    st.session_state.logado = False

def get_base64_img(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

def login_screen():
    bg_b64 = get_base64_img("assets/tecadi.png")
    bg_css = f'background-image: url("data:image/png;base64,{bg_b64}");' if bg_b64 else 'background-color: #000000;'

    # O SEGREDO ESTÁ AQUI: ESTILIZAR O CONTAINER NATIVO (.block-container)
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

        /* 1. RESET DE FONTE E IMAGEM DE FUNDO GLOBAL */
        html, body, [class*="css"], [class*="st-"] {{
            font-family: 'Montserrat', sans-serif !important;
        }}

        [data-testid="stApp"] {{
            {bg_css}
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}

        /* 2. ANIQUILA O CABEÇALHO E A SIDEBAR */
        [data-testid="stHeader"], [data-testid="stDecoration"], [data-testid="stToolbar"], 
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {{
            display: none !important;
        }}
        
        /* Mata o fundo forçado do Streamlit */
        section[data-testid="stMain"] {{
            background: transparent !important;
        }}

        /* 3. A MÁGICA: O CONTAINER DO STREAMLIT VIRA O CARTÃO DE LOGIN */
        .block-container {{
            background: rgba(15, 25, 40, 0.85) !important; /* Cor escura com transparência */
            backdrop-filter: blur(10px) !important; /* Vidro embaçado */
            -webkit-backdrop-filter: blur(10px) !important;
            
            max-width: 400px !important; /* Largura da caixa */
            margin: 12vh auto !important; /* Centraliza na tela */
            padding: 40px 30px !important; /* Espaçamento interno */
            
            border-radius: 16px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8) !important;
        }}

        /* 4. ESTILOS DOS TEXTOS */
        .titulo-login {{
            color: #ffffff !important;
            font-size: 38px !important;
            font-weight: 700 !important;
            text-align: center !important;
            margin-bottom: 5px !important;
            text-shadow: 0px 2px 5px rgba(0,0,0,0.5);
        }}
        .subtitulo-login {{
            color: #b0c4de !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            text-align: center !important;
            letter-spacing: 1px !important;
            margin-bottom: 30px !important;
            text-transform: uppercase !important;
        }}

        /* 5. ESTILOS DAS CAIXAS DE DIGITAR (Inputs) */
        div[data-testid="stTextInput"] label p {{
            color: #ffffff !important;
            font-weight: 600 !important;
        }}
        div[data-testid="stTextInput"] input {{
            background-color: #ffffff !important; /* Fundo branco pra leitura */
            color: #000000 !important; 
            -webkit-text-fill-color: #000000 !important; /* Trava o texto em preto */
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 8px !important;
            padding: 12px !important;
            font-weight: bold !important;
        }}
        div[data-testid="stTextInput"] input:focus {{
            border-color: #00aaff !important;
            box-shadow: 0 0 8px rgba(0, 170, 255, 0.5) !important;
        }}

        /* 6. ESTILOS DO BOTÃO */
        div[data-testid="stButton"] button {{
            background-color: #004e92 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            width: 100% !important;
            padding: 12px !important;
            font-size: 16px !important;
            font-weight: bold !important;
            margin-top: 20px !important;
            transition: 0.3s !important;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.5) !important;
        }}
        div[data-testid="stButton"] button:hover {{
            background-color: #00aaff !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    # Note que não há mais nenhuma <div> HTML envolvendo o conteúdo!
    st.markdown("""
        <div class="titulo-login">🔐 Login</div>
        <div class="subtitulo-login">Dashboard Operação Pátio</div>
    """, unsafe_allow_html=True)

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("ENTRAR", use_container_width=True):
        if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

def check_auth():
    return st.session_state.get("logado", False)