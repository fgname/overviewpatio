import streamlit as st
import pandas as pd
import datetime
import requests
from io import BytesIO

# Função que traduz a sua lógica do Power Query (M) para Python
def padronizar_cliente(nome):
    c = str(nome).upper()
    if "ANTIBIOTICOS" in c: return "ABL"
    elif "COMEXPORT" in c: return "BYD"
    elif "EUROQUADROS" in c: return "EUROQUADROS"
    elif "BTG" in c: return "BTG"    
    elif "FOUR" in c: return "TECADI - TRANSPORTES"
    elif "INEOS" in c: return "INEOS"
    elif "JCS" in c: return "JCS"
    elif "RIACHUELO" in c: return "RIACHUELO"
    elif "MILLESIMA" in c: return "MILLESIMA"
    elif "PARNASSA" in c: return "PARNASSA"
    elif "SAMSONITE" in c: return "SAMSONITE"
    elif "SOVENA" in c: return "SOVENA"
    elif "SPRINGER" in c: return "MIDEA"
    elif "ARMAZENS" in c: return "TECADI - TRANSPORTES"
    elif "FARBE" in c: return "FARBE"
    elif "WANHUA" in c: return "WANHUA"
    elif "ZEN" in c: return "ZEN"
    elif "DVT" in c: return "TALGE"
    elif "MASTER" in c: return "MASTER"
    elif "JCB" in c: return "JCB"
    elif "MONDAX" in c: return "MONDAX"
    elif "ALLOG" in c: return "ALTONA"
    elif "SENSE" in c: return "HISENSE"
    elif "PBG" in c: return "PORTO BELO"
    elif "AMTRANS" in c: return "ALTONA"
    elif "GINASTICA" in c: return "SMARTFIT"
    elif "IMPOMED" in c: return "IMPOMED"
    elif "MULTIEIXO" in c: return "MULTIEIXO"
    else: return str(nome).title()

@st.cache_data(ttl=300)
def load_data():
    # Links diretos de download do SharePoint
    url_controle = "https://tecadi-my.sharepoint.com/:x:/g/personal/thiago_dias_tecadi_com_br/IQDpxnKHykhHSbfasHXQURbOAUkOFzIhrxtiJKU8Mcgq3PA?download=1"
    url_freetime = "https://tecadi-my.sharepoint.com/:x:/g/personal/felipe_nonato_tecadi_com_br/IQAIQPuxUo5jQ6jmsh-d9X66AfZI20ZmGg3HQgNugWWzhPE?download=1"

    # Conexão com o SharePoint em memória: CONTROLE DE PÁTIO
    try:
        r_controle = requests.get(url_controle, timeout=15)
        r_controle.raise_for_status() 
        df_tecadi = pd.read_excel(BytesIO(r_controle.content), sheet_name="Controle", header=0, engine='openpyxl')
    except Exception as e:
        st.error(f"Falha ao conectar com o Controle de Pátio no SharePoint: {e}")
        df_tecadi = pd.DataFrame()

    # Conexão com o SharePoint em memória: FREETIME
    try:
        r_freetime = requests.get(url_freetime, timeout=15)
        r_freetime.raise_for_status()
        df_freetime = pd.read_excel(BytesIO(r_freetime.content), header=1, engine='openpyxl')
    except Exception as e:
        st.error(f"Falha ao conectar com o Freetime no SharePoint: {e}")
        df_freetime = pd.DataFrame()

    # Aplicação de otimizações na base TECADI
    if not df_tecadi.empty and 'Data Chegada' in df_tecadi.columns:
        df_tecadi.rename(columns={'Data Chegada': 'DT Chegada'}, inplace=True)
        
    if not df_tecadi.empty and 'STATUS' in df_tecadi.columns:
        df_tecadi = df_tecadi[df_tecadi['STATUS'] != 'No Show']
        df_tecadi['STATUS'] = df_tecadi['STATUS'].replace('AGUARD. SAIDA', 'AGUARD. SAÍDA')

    # Limpeza de IDs para cruzamento exato
    if not df_tecadi.empty:
        df_tecadi['CNTR_CLEAN'] = df_tecadi['CONTAINER'].astype(str).str.replace(r'[^A-Za-z0-9]', '', regex=True).str.upper()
        df_tecadi = df_tecadi.dropna(subset=['CNTR_CLEAN'])
    else:
        df_tecadi['CNTR_CLEAN'] = pd.Series(dtype='str')

    if not df_freetime.empty:
        df_freetime['CNTR_CLEAN'] = df_freetime['Container'].astype(str).str.replace(r'[^A-Za-z0-9]', '', regex=True).str.upper()
        # Aplicação da padronização de clientes
        if 'Cliente' in df_freetime.columns:
            df_freetime['Cliente'] = df_freetime['Cliente'].apply(padronizar_cliente)

    # Separação Armador x Tecadi (Anti-join)
    if not df_tecadi.empty and not df_freetime.empty:
        tecadi_ids = df_tecadi['CNTR_CLEAN'].unique()
        df_armador = df_freetime[~df_freetime['CNTR_CLEAN'].isin(tecadi_ids)].copy()
    else:
        df_armador = df_freetime.copy() if not df_freetime.empty else pd.DataFrame()

    return df_tecadi, df_armador, df_freetime
