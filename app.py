import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime

VERSAO_APP = "Act!   V64"

st.set_page_config(page_title=f"{VERSAO_APP} - Banco.dbf", page_icon="📑", layout="wide", initial_sidebar_state="collapsed")

ARQ_UNIFICADA = "Base_Unificada_Master.csv"
ARQ_QUARENTENA = "Base_Quarentena_Master.csv"
ARQ_TRAVA = "fusao_concluida.lock"

# -----------------------------------------------------------------------------
# 1. FUNÇÕES DE DADOS, LEITURA E PERSISTÊNCIA ÚNICA
# -----------------------------------------------------------------------------
def corrigir_acentos(texto):
    if not isinstance(texto, str) or not texto:
        return ""
    substituicoes = {
        '╔': 'É', '┴': 'Á', '├': 'Ç', '╙': 'ÃO', '├╙': 'ÇÃO',
        '═': 'Í', 'Ò': 'Â', 'Ì': 'Ê', '╘': 'Õ', '╒': 'Ô',
        '┌': 'Ú', '╓': 'Ã', '╛': 'Ü', 'Â': 'Ô', 'Õ': 'Õ'
    }
    for char_errado, char_certo in substituicoes.items():
        texto = texto.replace(char_errado, char_certo)
    return texto.strip()

def remover_acentos(texto):
    if not isinstance(texto, str) or not texto:
        return ""
    mapa = str.maketrans("ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑáàâãäéèêëíìîïóòôõöúùûüçñ",
                         "AAAAAEEEEIIIIOOOOOUUUUCNaaaaaeeeeiiiiooooouuuucn")
    return texto.translate(mapa)

def limpar_cpf(val):
    if not val or pd.isna(val):
        return ""
    digitos = ''.join(filter(str.isdigit, str(val)))
    if len(digitos) >= 11:
        return digitos[-11:]
    elif len(digitos) > 0:
        return digitos.zfill(11)
    return ""

def formatar_cpf(digitos):
    if len(digitos) == 11:
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
    return digitos

def calcular_idade(data_nasc_str):
    if not data_nasc_str:
        return ""
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            dt = datetime.strptime(str(data_nasc_str).strip()[:10], fmt)
            hoje = datetime.today()
            idade = hoje.year - dt.year - ((hoje.month, hoje.day) < (dt.month, dt.day))
            if 0 <= idade <= 125:
                return str(idade)
        except Exception:
            continue
    return ""

def ler_arquivo(nome_base):
    for ext in ['.xlsx', '.csv', '.XLSX', '.CSV']:
        caminho = f"{nome_base}{ext}"
        if os.path.exists(caminho):
            try:
                if ext.lower() == '.csv':
                    df = pd.read_csv(caminho, dtype=str).fillna("")
                else:
                    df = pd.read_excel(caminho, dtype=str).fillna("")
                for col in df.columns:
                    df[col] = df[col].astype(str).apply(corrigir_acentos)
                return df
            except Exception as e:
                st.error(f"Erro ao ler {caminho}: {e}")
    return pd.DataFrame()

def salvar_bases_master(df_u, df_q):
    df_u.to_csv(ARQ_UNIFICADA, index=False, encoding="utf-8-sig")
    df_q.to_csv(ARQ_QUARENTENA, index=False, encoding="utf-8-sig")
    with open(ARQ_TRAVA, "w", encoding="utf-8") as f:
        f.write("UNIFICADO=TRUE")

def carregar_bases_master():
    if os.path.exists(ARQ_UNIFICADA):
        df_u = pd.read_csv(ARQ_UNIFICADA, dtype=str).fillna("")
    else:
        df_u = pd.DataFrame()
    if os.path.exists(ARQ_QUARENTENA):
        df_q = pd.read_csv(ARQ_QUARENTENA, dtype=str).fillna("")
    else:
        df_q = pd.DataFrame()
    return df_u, df_q

def executar_fusao_unica():
    df1 = ler_arquivo('DBF1_Local')
    df2 = ler_arquivo('DBF2_Copia')

    if df1.empty and df2.empty:
        return pd.DataFrame(), pd.DataFrame()

    if not df1.empty:
        df1['ORIGEM'] = 'PC 1 (Hamilton)'
    if not df2.empty:
        df2['ORIGEM'] = 'PC 2 (Jaedna)'

    df_todos = pd.concat([df1, df2], ignore_index=True)

    col_nome = 'NAME' if 'NAME' in df_todos.columns else df_todos.columns[0]
    
    col_cpf = None
    for c in ['USR1000', 'CPF', 'USER1000']:
        if c in df_todos.columns:
            col_cpf = c
            break
            
    if col_cpf:
        df_todos['CHAVE_BUSCA'] = df_todos[col_cpf].apply(limpar_cpf)
        mask_vazio = df_todos['CHAVE_BUSCA'] == ""
        df_todos.loc[mask_vazio, 'CHAVE_BUSCA'] = df_todos.loc[mask_vazio, col_nome].str.upper().str.strip()
    else:
        df_todos['CHAVE_BUSCA'] = df_todos[col_nome].str.upper().str.strip()

    col_obs = 'USER9' if 'USER9' in df_todos.columns else ('OBSERVACOES' if 'OBSERVACOES' in df_todos.columns else df_todos.columns[1])
    col_phone = 'PHONE' if 'PHONE' in df_todos.columns else df_todos.columns[2]

    base_unificada = []
    base_quarentena = []

    for chave, group in df_todos.groupby('CHAVE_BUSCA'):
        if not chave or len(chave) < 3:
            for _, row in group.iterrows():
                base_quarentena.append(row.to_dict())
            continue
            
        if len(group) == 1:
            base_unificada.append(group.iloc[0].to_dict())
        else:
            obs_distintas = set(filter(None, group[col_obs].str.strip().tolist()))
            tels_distintos = set(filter(None, group[col_phone].str.strip().tolist()))
            
            if len(obs_distintas) <= 1 and len(tels_distintos) <= 1:
                base_unificada.append(group.iloc[-1].to_dict())
            else:
                for _, row in group.iterrows():
                    base_quarentena.append(row.to_dict())

    df_u = pd.DataFrame(base_unificada)
    df_q = pd.DataFrame(base_quarentena)
    salvar_bases_master(df_u, df_q)
    return df_u, df_q

def get_campo(row, candidatos):
    for c in candidatos:
        if c in row.index and str(row[c]).strip() != "":
            return str(row[c]).strip()
    return ""

# -----------------------------------------------------------------------------
# 2. SEGURANÇA E TELA DE LOGIN CLÁSSICA ACT! (V64)
# -----------------------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    css_login = """
        <style>
        header, footer, [data-testid="stSidebar"], [data-testid="collapsedControl"],
        [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
            display: none !important;
        }
        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
            background-color: #808080 !important;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .main .block-container {
            padding: 0 !important;
            margin: 0 auto !important;
            max-width: 100% !important;
            min-height: 100vh !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        [data-testid="stForm"] {
            width: 286px !important;
            min-width: 286px !important;
            max-width: 286px !important;
            background-color: #D4D0C8 !important;
            border-radius: 0px !important;
            border-top: 1px solid #FFFFFF !important;
            border-left: 1px solid #FFFFFF !important;
            border-right: 1px solid #404040 !important;
            border-bottom: 1px solid #404040 !important;
            box-shadow: inset 1px 1px 0px #D4D0C8, inset -1px -1px 0px #808080, 1px 1px 0px #000000 !important;
            padding: 3px 3px 14px 3px !important;
            margin: 0 auto !important;
            box-sizing: border-box !important;
        }
        [data-testid="stForm"] [data-testid="stVerticalBlock"] {
            gap: 0px !important;
            overflow: visible !important;
        }
        [data-testid="stForm"] [data-testid="stElementContainer"],
        [data-testid="stForm"] [data-testid="stMarkdownContainer"] {
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
        }
        [data-testid="stForm"] [data-testid="stMarkdownContainer"] p {
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
        }
        .act-titlebar {
            background: linear-gradient(90deg, #0A246A 0%, #A6CAF0 100%);
            color: #FFFFFF;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif;
            font-weight: bold;
            font-size: 11px;
            height: 18px;
            padding: 0 2px 0 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 0 0 12px 0;
            width: 100%;
            box-sizing: border-box;
        }
        .act-close-btn {
            background-color: #D4D0C8;
            color: #000000;
            border-top: 1px solid #FFFFFF;
            border-left: 1px solid #FFFFFF;
            border-right: 1px solid #404040;
            border-bottom: 1px solid #404040;
            box-shadow: inset -1px -1px 0px #808080;
            font-size: 10px;
            font-weight: bold;
            width: 15px;
            height: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1;
        }
        .act-label {
            color: #000000;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif;
            font-size: 11px;
            line-height: 16px;
            height: auto;
            padding: 2px 11px 4px 11px;
            margin: 0;
            display: block;
            white-space: nowrap;
            overflow: visible;
        }
        .act-label-pass {
            padding-top: 10px;
        }
        [data-testid="stForm"] [data-testid="stTextInput"] {
            padding: 0 11px !important;
            margin: 0 !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        [data-testid="stForm"] [data-testid="stTextInput"] label {
            display: none !important;
        }
        [data-testid="stForm"] [data-testid="stTextInput"] > div,
        [data-testid="stForm"] [data-testid="stTextInput"] > div > div {
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            border-radius: 0px !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            min-height: 0 !important;
        }
        [data-testid="stForm"] [data-testid="stTextInput"] input {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border-radius: 0px !important;
            border-top: 1px solid #808080 !important;
            border-left: 1px solid #808080 !important;
            border-right: 1px solid #FFFFFF !important;
            border-bottom: 1px solid #FFFFFF !important;
            box-shadow: inset 1px 1px 0px #404040, inset -1px -1px 0px #D4D0C8 !important;
            height: 20px !important;
            min-height: 20px !important;
            max-height: 20px !important;
            padding: 1px 4px !important;
            font-size: 11px !important;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important;
            line-height: 16px !important;
        }
        [data-testid="stForm"] [data-testid="stTextInput"] button,
        [data-testid="stForm"] [data-testid="InputInstructions"] {
            display: none !important;
        }
        [data-testid="stForm"] [data-testid="stCheckbox"] {
            padding: 11px 11px 13px 11px !important;
            margin: 0 !important;
        }
        [data-testid="stForm"] [data-testid="stCheckbox"] label {
            display: flex !important;
            align-items: center !important;
            gap: 6px !important;
            min-height: 0 !important;
            cursor: default !important;
        }
        [data-testid="stForm"] [data-testid="stCheckbox"] label > span:first-child,
        [data-testid="stForm"] [data-testid="stCheckbox"] [data-baseweb="checkbox"] > span:first-child,
        [data-testid="stForm"] [data-testid="stCheckbox"] [data-baseweb="checkbox"] > div:first-child {
            width: 13px !important;
            height: 13px !important;
            min-width: 13px !important;
            min-height: 13px !important;
            max-width: 13px !important;
            max-height: 13px !important;
            border-radius: 0px !important;
            background-color: #FFFFFF !important;
            background: #FFFFFF !important;
            border-top: 1px solid #808080 !important;
            border-left: 1px solid #808080 !important;
            border-right: 1px solid #FFFFFF !important;
            border-bottom: 1px solid #FFFFFF !important;
            box-shadow: inset 1px 1px 0px #404040 !important;
        }
        [data-testid="stForm"] [data-testid="stCheckbox"] input[type="checkbox"] {
            accent-color: #FFFFFF !important;
        }
        [data-testid="stForm"] [data-testid="stCheckbox"] svg {
            fill: #000000 !important;
            color: #000000 !important;
            stroke: #000000 !important;
            width: 10px !important;
            height: 10px !important;
        }
        [data-testid="stForm"] [data-testid="stCheckbox"] label p {
            color: #000000 !important;
            font-size: 11px !important;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important;
            line-height: 14px !important;
            margin: 0 !important;
        }
        [data-testid="stForm"] [data-testid="stCheckbox"] label p::first-letter {
            text-decoration: underline !important;
        }
        [data-testid="stForm"] [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            justify-content: center !important;
            align-items: center !important;
            gap: 10px !important;
            padding: 0 40px !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        [data-testid="stForm"] [data-testid="stHorizontalBlock"] > div {
            width: 75px !important;
            min-width: 75px !important;
            max-width: 75px !important;
            flex: 0 0 75px !important;
            padding: 0 !important;
        }
        [data-testid="stForm"] button {
            background-color: #D4D0C8 !important;
            color: #000000 !important;
            border-radius: 0px !important;
            border-top: 1px solid #FFFFFF !important;
            border-left: 1px solid #FFFFFF !important;
            border-right: 1px solid #404040 !important;
            border-bottom: 1px solid #404040 !important;
            box-shadow: inset -1px -1px 0px #808080 !important;
            height: 22px !important;
            min-height: 22px !important;
            max-height: 22px !important;
            width: 75px !important;
            min-width: 75px !important;
            padding: 0px !important;
            font-size: 11px !important;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            line-height: 20px !important;
        }
        [data-testid="stForm"] [data-testid="stHorizontalBlock"] > div:first-child button {
            border-top: 1px solid #000000 !important;
            border-left: 1px solid #000000 !important;
            border-right: 1px solid #000000 !important;
            border-bottom: 1px solid #000000 !important;
            box-shadow: inset 1px 1px 0px #FFFFFF, inset -1px -1px 0px #404040, inset -2px -2px 0px #808080 !important;
        }
        [data-testid="stForm"] [data-testid="stHorizontalBlock"] > div:nth-child(2) button p::first-letter {
            text-decoration: underline !important;
        }
        [data-testid="stForm"] button p,
        [data-testid="stForm"] button div {
            font-size: 11px !important;
            color: #000000 !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 20px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        [data-testid="stForm"] button:active {
            border-top: 1px solid #404040 !important;
            border-left: 1px solid #404040 !important;
            border-right: 1px solid #FFFFFF !important;
            border-bottom: 1px solid #FFFFFF !important;
            box-shadow: inset 1px 1px 0px #808080 !important;
        }
        .act-msg-erro {
            color: #800000;
            font-size: 11px;
            text-align: center;
            padding-top: 8px;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif;
        }
        </style>
    """
    st.markdown(css_login, unsafe_allow_html=True)

    with st.form("form_login_act", border=False):
        st.markdown(f"""
            <div class="act-titlebar">
                <span style="white-space: pre;">{VERSAO_APP}</span>
                <span class="act-close-btn">×</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="act-label">Digite seu nome de <u>u</u>suário:</div>', unsafe_allow_html=True)
        user_input = st.text_input("user_label", value="Hamilton Flecha", key="user_key", label_visibility="collapsed")

        st.markdown('<div class="act-label act-label-pass">Digite sua <u>s</u>enha para este banco de dados:</div>', unsafe_allow_html=True)
        senha_input = st.text_input("pass_label", type="password", key="pass_key", label_visibility="collapsed")

        st.checkbox("Lembrar senha", value=True, key="rem_key")

        b_ok, b_cancel = st.columns(2)
        with b_ok:
            btn_ok = st.form_submit_button("OK")
        with b_cancel:
            btn_cancel = st.form_submit_button("Cancelar")

        if btn_ok:
            if senha_input.strip() == "solucoes1986":
                st.session_state["autenticado"] = True
                st.session_state["operador_atual"] = user_input
                st.rerun()
            else:
                st.markdown('<div class="act-msg-erro">Senha inválida para Banco.dbf.</div>', unsafe_allow_html=True)
        if btn_cancel:
            st.markdown('<div class="act-msg-erro">Entrada cancelada.</div>', unsafe_allow_html=True)

    st.stop()

# -----------------------------------------------------------------------------
# 3. ESTADO E CARREGAMENTO PASSIVO (SEM BARRA LATERAL)
# -----------------------------------------------------------------------------
ja_unificado = os.path.exists(ARQ_TRAVA) and os.path.exists(ARQ_UNIFICADA)

if "df_unificada" not in st.session_state:
    if ja_unificado:
        st.session_state["df_unificada"], st.session_state["df_quarentena"] = carregar_bases_master()
    else:
        st.session_state["df_unificada"] = pd.DataFrame()
        st.session_state["df_quarentena"] = pd.DataFrame()

if "idx_cliente" not in st.session_state:
    st.session_state["idx_cliente"] = 0

if "visao_ativa" not in st.session_state:
    st.session_state["visao_ativa"] = "ficha"

if "confirmar_nova_fusao" not in st.session_state:
    st.session_state["confirmar_nova_fusao"] = False

if "modo_novo_contato" not in st.session_state:
    st.session_state["modo_novo_contato"] = False

df_unificada = st.session_state["df_unificada"]
df_quarentena = st.session_state["df_quarentena"]

# -----------------------------------------------------------------------------
# 4. ESTILO CLÁSSICO SYMANTEC ACT! (FUNDO TAUPE #9E9382, CAMPOS 19px, ZERO SIDEBAR)
# -----------------------------------------------------------------------------
css_act_classic = """
    <style>
    /* Oculta completamente a barra lateral e o botão de abrir sidebar */
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
    }

    /* Fundo clássico taupe/bege escuro do Act! (#9E9382) ocupando 100% da tela */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
        background-color: #9E9382 !important;
        font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important;
        color: #000000 !important;
    }

    .main .block-container {
        padding: 4px 10px 6px 10px !important;
        max-width: 100% !important;
        margin: 0 !important;
    }

    /* Compacta blocos verticais e colunas */
    [data-testid="stVerticalBlock"] {
        gap: 2px !important;
    }
    [data-testid="stElementContainer"] {
        margin-bottom: 1px !important;
    }

    /* Barra de Menu Superior estilo Windows/Act! (#D4D0C8) */
    .act-menubar {
        background-color: #D4D0C8;
        border-top: 1px solid #FFFFFF;
        border-left: 1px solid #FFFFFF;
        border-right: 1px solid #404040;
        border-bottom: 1px solid #808080;
        padding: 2px 8px;
        font-size: 11px;
        color: #000000;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
    }
    .act-menu-items span {
        margin-right: 14px;
        cursor: default;
    }

    /* Rótulos dos campos (11px preto direto sobre o fundo #9E9382) */
    .act-fld-lbl {
        font-size: 11px;
        font-weight: normal;
        color: #000000;
        line-height: 13px;
        margin: 2px 0 1px 0;
        padding: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Inputs brancos compactos de 19px-21px estilo Act! */
    [data-testid="stTextInput"] label {
        display: none !important;
    }
    [data-testid="stTextInput"] > div,
    [data-testid="stTextInput"] > div > div {
        background: transparent !important;
        border: none !important;
        border-radius: 0px !important;
        box-shadow: none !important;
        padding: 0 !important;
        min-height: 0 !important;
    }
    [data-testid="stTextInput"] input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border-radius: 2px !important;
        border: 1px solid #7A7265 !important;
        height: 21px !important;
        min-height: 21px !important;
        max-height: 21px !important;
        padding: 1px 5px !important;
        font-size: 11px !important;
        font-family: 'Tahoma', Arial, sans-serif !important;
        line-height: 17px !important;
        opacity: 1 !important;
    }
    [data-testid="stTextInput"] input:focus {
        border: 1px solid #0A246A !important;
        background-color: #FFFFF0 !important;
    }

    /* TextArea USER9 compacta */
    [data-testid="stTextArea"] label {
        display: none !important;
    }
    [data-testid="stTextArea"] textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border-radius: 2px !important;
        border: 1px solid #7A7265 !important;
        font-size: 11px !important;
        font-family: 'Tahoma', Arial, sans-serif !important;
        padding: 3px 5px !important;
        line-height: 14px !important;
        opacity: 1 !important;
    }

    /* Botões clássicos cinza claro (#E4E0D8 / #D4D0C8) com borda fina */
    [data-testid="stButton"] button {
        background-color: #E4E0D8 !important;
        color: #000000 !important;
        border-radius: 2px !important;
        border-top: 1px solid #FFFFFF !important;
        border-left: 1px solid #FFFFFF !important;
        border-right: 1px solid #505050 !important;
        border-bottom: 1px solid #505050 !important;
        height: 21px !important;
        min-height: 21px !important;
        max-height: 21px !important;
        padding: 0 6px !important;
        font-size: 11px !important;
        font-family: 'Tahoma', Arial, sans-serif !important;
        line-height: 19px !important;
        margin: 0 !important;
    }
    [data-testid="stButton"] button:hover {
        background-color: #EFECE6 !important;
    }
    [data-testid="stButton"] button p {
        font-size: 11px !important;
        color: #000000 !important;
        margin: 0 !important;
        line-height: 19px !important;
        white-space: nowrap !important;
    }

    /* Botão primário de destaque (Salvar / Unificar) */
    [data-testid="stButton"] button[kind="primary"] {
        background-color: #D4E4F7 !important;
        border: 1px solid #0A246A !important;
        font-weight: bold !important;
    }

    /* Crachá branco superior direito (Act! V64 / Hamilton e Jaedna / Soluções) */
    .act-badge {
        background-color: #FFFFFF;
        border: 1px solid #7A7265;
        border-radius: 2px;
        padding: 2px 6px;
        text-align: center;
        font-size: 10px;
        line-height: 12px;
        color: #000000;
        height: 40px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* Divisor horizontal fino estilo Act! */
    .act-hr {
        border: none;
        border-top: 1px solid #7A7265;
        border-bottom: 1px solid #B5AC9D;
        margin: 3px 0;
        height: 2px;
    }

    /* Barra de status inferior */
    .act-statusbar {
        background-color: #D4D0C8;
        border-top: 1px solid #808080;
        padding: 2px 8px;
        font-size: 11px;
        color: #000000;
        display: flex;
        justify-content: space-between;
        margin-top: 4px;
    }
    </style>
"""
st.markdown(css_act_classic, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. BARRA SUPERIOR DE MENU E COMANDOS (SUBSTITUI A BARRA LATERAL)
# -----------------------------------------------------------------------------
st.markdown(f"""
    <div class="act-menubar">
        <div class="act-menu-items">
            <span><u>A</u>rquivo</span>
            <span><u>E</u>ditar</span>
            <span><u>E</u>xibir</span>
            <span><u>C</u>ontato</span>
            <span><u>P</u>esquisar</span>
            <span><u>F</u>erramentas</span>
            <span><u>A</u>juda</span>
        </div>
        <div>
            <b>Banco.dbf</b> &nbsp;|&nbsp; Operador: <b>{st.session_state.get('operador_atual', 'Hamilton Flecha')}</b> &nbsp;|&nbsp; Base: <b>{len(df_unificada)}</b> &nbsp;|&nbsp; Quarentena: <b>{len(df_quarentena)}</b>
        </div>
    </div>
""", unsafe_allow_html=True)

# Barra de botões superiores (todos os antigos controles laterais + abas aqui em cima)
top1, top2, top3, top4, top5, top6 = st.columns([1.2, 1.3, 1.4, 1.4, 2.2, 1.0])

with top1:
    if st.button("👤 Ficha Act!", use_container_width=True, type="primary" if st.session_state["visao_ativa"] == "ficha" else "secondary"):
        st.session_state["visao_ativa"] = "ficha"
        st.rerun()

with top2:
    if st.button(f"📊 Tabela ({len(df_unificada)})", use_container_width=True, type="primary" if st.session_state["visao_ativa"] == "tabela" else "secondary"):
        st.session_state["visao_ativa"] = "tabela"
        st.rerun()

with top3:
    if st.button(f"⚠️ Quarentena ({len(df_quarentena)})", use_container_width=True, type="primary" if st.session_state["visao_ativa"] == "quarentena" else "secondary"):
        st.session_state["visao_ativa"] = "quarentena"
        st.rerun()

with top4:
    if st.button("📋 Todos os Campos", use_container_width=True, type="primary" if st.session_state["visao_ativa"] == "todos_campos" else "secondary"):
        st.session_state["visao_ativa"] = "todos_campos"
        st.rerun()

with top5:
    if not ja_unificado:
        if st.button("⚡ Unificar Bases (Comando Único)", type="primary", use_container_width=True):
            with st.spinner("Executando unificação única..."):
                u, q = executar_fusao_unica()
                st.session_state["df_unificada"] = u
                st.session_state["df_quarentena"] = q
                st.session_state["idx_cliente"] = 0
                st.rerun()
    else:
        if not st.session_state["confirmar_nova_fusao"]:
            if st.button("🔒 Base Travada (Destravar p/ Troca)", use_container_width=True):
                st.session_state["confirmar_nova_fusao"] = True
                st.rerun()
        else:
            c_ok_f, c_can_f = st.columns(2)
            with c_ok_f:
                if st.button("✅ Confirmar", type="primary", use_container_width=True):
                    u, q = executar_fusao_unica()
                    st.session_state["df_unificada"] = u
                    st.session_state["df_quarentena"] = q
                    st.session_state["idx_cliente"] = 0
                    st.session_state["confirmar_nova_fusao"] = False
                    st.rerun()
            with c_can_f:
                if st.button("❌ Cancelar", use_container_width=True):
                    st.session_state["confirmar_nova_fusao"] = False
                    st.rerun()

with top6:
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state["autenticado"] = False
        st.rerun()

st.markdown('<hr class="act-hr">', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. VISÃO PRINCIPAL: FICHA ACT! ORIGINAL (IGUAL AO PRINT 2)
# -----------------------------------------------------------------------------
if st.session_state["visao_ativa"] == "ficha":
    if not ja_unificado and df_unificada.empty:
        st.info("A unificação automática está desativada. Clique em **⚡ Unificar Bases (Comando Único)** na barra superior para gerar a Base Master pela primeira vez.")
    elif df_unificada.empty and not st.session_state["modo_novo_contato"]:
        st.warning("Nenhuma base encontrada. Verifique os arquivos ou clique em '+ Novo Contato'.")
    else:
        # Linha de Localizar, Navegação (◀ Ant | 1 de X | Próx ▶), + Novo Contato e Crachá Act!
        c_loc, c_ant, c_prox, c_novo, c_badge = st.columns([3.2, 0.8, 0.8, 1.3, 1.6])

        with c_loc:
            st.markdown('<div class="act-fld-lbl">Localizar (Nome / CPF / Benefício)</div>', unsafe_allow_html=True)
            termo_busca = st.text_input("loc_input", placeholder="", label_visibility="collapsed", key="busca_act_top")

        if termo_busca and not df_unificada.empty:
            df_filtrado = df_unificada[df_unificada.astype(str).apply(lambda x: x.str.contains(termo_busca, case=False)).any(axis=1)]
        else:
            df_filtrado = df_unificada

        total_registros = len(df_filtrado)
        if total_registros > 0 and st.session_state["idx_cliente"] >= total_registros:
            st.session_state["idx_cliente"] = max(0, total_registros - 1)

        with c_ant:
            st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
            if st.button("◀ Ant...", use_container_width=True):
                st.session_state["modo_novo_contato"] = False
                if st.session_state["idx_cliente"] > 0:
                    st.session_state["idx_cliente"] -= 1
                    st.rerun()

        with c_prox:
            st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
            if st.button("Próx... ▶", use_container_width=True):
                st.session_state["modo_novo_contato"] = False
                if st.session_state["idx_cliente"] < total_registros - 1:
                    st.session_state["idx_cliente"] += 1
                    st.rerun()

        with c_novo:
            st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
            if st.button("+ Novo Contato", use_container_width=True):
                st.session_state["modo_novo_contato"] = not st.session_state["modo_novo_contato"]
                st.rerun()

        with c_badge:
            st.markdown(f"""
                <div class="act-badge">
                    <b>{VERSAO_APP}</b>
                    <span>Hamilton e Jaedna</span>
                    <span>Soluções</span>
                </div>
            """, unsafe_allow_html=True)

        # Contador centralizado logo abaixo dos botões Ant / Próx
        pos_atual = 0 if (total_registros == 0 or st.session_state["modo_novo_contato"]) else (st.session_state["idx_cliente"] + 1)
        st.markdown(f'<div style="text-align:center; font-size:10px; line-height:11px; margin:-4px 0 2px 0;">{pos_atual} de {total_registros}</div>', unsafe_allow_html=True)
        st.markdown('<hr class="act-hr">', unsafe_allow_html=True)

        # Se estiver em modo Novo Contato, exibe formulário limpo de inserção
        if st.session_state["modo_novo_contato"]:
            st.markdown('<div style="font-size:11px; font-weight:bold; margin-bottom:4px;">➕ Inserir Novo Contato na Base Master</div>', unsafe_allow_html=True)
            n1, n2, n3, n4 = st.columns([3, 1.5, 1.5, 1.5])
            with n1:
                st.markdown('<div class="act-fld-lbl">Nome Completo</div>', unsafe_allow_html=True)
                novo_nome = st.text_input("novo_nome", label_visibility="collapsed")
            with n2:
                st.markdown('<div class="act-fld-lbl">CPF (Apenas Números)</div>', unsafe_allow_html=True)
                novo_cpf = st.text_input("novo_cpf", label_visibility="collapsed")
            with n3:
                st.markdown('<div class="act-fld-lbl">Órgão</div>', unsafe_allow_html=True)
                novo_orgao = st.text_input("novo_orgao", value="INSS", label_visibility="collapsed")
            with n4:
                st.markdown('<div class="act-fld-lbl">Nº Benefício / Matrícula</div>', unsafe_allow_html=True)
                novo_benef = st.text_input("novo_benef", label_visibility="collapsed")

            n5, n6, n7, n8 = st.columns([1.2, 2.8, 1.5, 1.5])
            with n5:
                st.markdown('<div class="act-fld-lbl">DDD</div>', unsafe_allow_html=True)
                novo_ddd = st.text_input("novo_ddd", value="31", label_visibility="collapsed")
            with n6:
                st.markdown('<div class="act-fld-lbl">Telefone 1</div>', unsafe_allow_html=True)
                novo_tel = st.text_input("novo_tel", label_visibility="collapsed")
            with n7:
                st.markdown('<div class="act-fld-lbl">Data Nascimento</div>', unsafe_allow_html=True)
                novo_nasc = st.text_input("novo_nasc", label_visibility="collapsed")
            with n8:
                st.markdown('<div class="act-fld-lbl">Loja</div>', unsafe_allow_html=True)
                novo_loja = st.text_input("novo_loja", value="Centro - OB", label_visibility="collapsed")

            st.markdown('<div class="act-fld-lbl">Observações (USER9)</div>', unsafe_allow_html=True)
            novo_obs = st.text_area("novo_obs", height=60, label_visibility="collapsed")

            bs1, bs2, _ = st.columns([1.3, 1.3, 5])
            with bs1:
                if st.button("💾 Salvar Novo Contato", type="primary", use_container_width=True):
                    if novo_nome.strip():
                        cpf_l = limpar_cpf(novo_cpf)
                        nova_linha = {col: "" for col in df_unificada.columns} if not df_unificada.empty else {}
                        nova_linha["NAME"] = novo_nome.strip().upper()
                        nova_linha["USR1000"] = cpf_l
                        nova_linha["COMPANY"] = novo_orgao.strip().upper()
                        nova_linha["ID_STAT"] = novo_benef.strip()
                        nova_linha["PHONE"] = f"({novo_ddd.strip()}) {novo_tel.strip()}" if novo_ddd.strip() else novo_tel.strip()
                        nova_linha["USER1"] = novo_nasc.strip()
                        nova_linha["USER2"] = novo_loja.strip()
                        nova_linha["USER9"] = novo_obs.strip()
                        nova_linha["ORIGEM"] = f"Inserido ({st.session_state.get('operador_atual', 'Hamilton')})"
                        nova_linha["CHAVE_BUSCA"] = cpf_l if cpf_l else novo_nome.strip().upper()

                        df_unificada = pd.concat([df_unificada, pd.DataFrame([nova_linha])], ignore_index=True)
                        st.session_state["df_unificada"] = df_unificada
                        salvar_bases_master(df_unificada, df_quarentena)
                        st.session_state["idx_cliente"] = len(df_unificada) - 1
                        st.session_state["modo_novo_contato"] = False
                        st.rerun()
            with bs2:
                if st.button("Cancelar Inserção", use_container_width=True):
                    st.session_state["modo_novo_contato"] = False
                    st.rerun()

        elif total_registros > 0:
            row_idx_filtrado = st.session_state["idx_cliente"]
            cliente = df_filtrado.iloc[row_idx_filtrado]
            real_idx = cliente.name

            # Extração inteligente dos campos do banco Act!
            nome_val = get_campo(cliente, ['NAME', 'NOME'])
            primeiro_nome = nome_val.split()[0] if nome_val else ""
            apelido_val = get_campo(cliente, ['FIRST_NAME', 'SALUTATION', 'APELIDO'])
            data_visita_val = get_campo(cliente, ['LAST_REACH', 'USER5', 'DATA_VISITA'])
            nome_sem_acento = remover_acentos(nome_val)

            orgao_val = get_campo(cliente, ['COMPANY', 'ORGAO', 'USER3']) or "INSS"
            cpf_bruto = get_campo(cliente, ['USR1000', 'CPF', 'USER1000'])
            cpf_limpo = limpar_cpf(cpf_bruto)
            cpf_fmt = formatar_cpf(cpf_limpo)

            data_nasc_val = get_campo(cliente, ['USER1', 'BIRTHDATE', 'NASCIMENTO', 'DATA_NASC'])
            idade_val = get_campo(cliente, ['USER4', 'IDADE']) or calcular_idade(data_nasc_val)
            resumo_val = f"{orgao_val} {nome_sem_acento} {cpf_limpo} {idade_val}".strip()

            loja_val = get_campo(cliente, ['USER2', 'LOJA', 'DEPARTMENT']) or "Centro - OB"
            atendido_val = get_campo(cliente, ['USER6', 'ATENDIDO_POR', 'MANAGER'])
            beneficio_val = get_campo(cliente, ['ID_STAT', 'BENEFICIO', 'USER7', 'MATRICULA'])
            especie_val = get_campo(cliente, ['USER8', 'ESPECIE', 'TITLE'])

            senha_inss_val = get_campo(cliente, ['USER10', 'SENHA_INSS'])
            senha_parana_val = get_campo(cliente, ['USER11', 'SENHA_PARANA'])
            identidade_val = get_campo(cliente, ['USER12', 'IDENTIDADE', 'RG'])

            end1_val = get_campo(cliente, ['ADDR1', 'ENDERECO'])
            bairro1_val = get_campo(cliente, ['ADDR3', 'BAIRRO'])
            estado1_val = get_campo(cliente, ['STATE', 'UF'])
            cidade1_val = get_campo(cliente, ['CITY', 'CIDADE'])
            cep1_val = get_campo(cliente, ['ZIP', 'CEP'])
            edificio_val = get_campo(cliente, ['ADDR2', 'EDIFICIO'])

            tel_bruto = get_campo(cliente, ['PHONE', 'TELEFONE'])
            ddd_val = ""
            tel1_val = tel_bruto
            if tel_bruto.startswith("(") and ")" in tel_bruto:
                ddd_val = tel_bruto[1:tel_bruto.find(")")].strip()
                tel1_val = tel_bruto[tel_bruto.find(")")+1:].strip()
            ref1_val = get_campo(cliente, ['HOME_PHONE', 'ALT_PHONE', 'REF1'])
            tels_consol_val = " / ".join(filter(None, [tel_bruto, ref1_val]))
            obs_val = get_campo(cliente, ['USER9', 'OBSERVACOES'])

            # --- LINHA 1: Nome | Copiar | Limpar | 1º Nome | Gosta de ser chamado por | Data da visita ---
            r1_1, r1_2, r1_3, r1_4, r1_5, r1_6 = st.columns([3.2, 0.35, 0.35, 1.3, 1.5, 1.3])
            with r1_1:
                st.markdown('<div class="act-fld-lbl">Nome</div>', unsafe_allow_html=True)
                ed_nome = st.text_input("f_nome", value=nome_val, key=f"nome_{real_idx}", label_visibility="collapsed")
            with r1_2:
                st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
                st.code(nome_val, language=None) if False else st.button("📋", key=f"cp_nome_{real_idx}", help=f"Copiar: {nome_val}")
            with r1_3:
                st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
                if st.button("🗑", key=f"cl_nome_{real_idx}", help="Limpar Nome"):
                    df_unificada.at[real_idx, 'NAME'] = ""
                    salvar_bases_master(df_unificada, df_quarentena)
                    st.rerun()
            with r1_4:
                st.markdown('<div class="act-fld-lbl">1º Nome</div>', unsafe_allow_html=True)
                st.text_input("f_pnome", value=primeiro_nome, key=f"pnome_{real_idx}", label_visibility="collapsed")
            with r1_5:
                st.markdown('<div class="act-fld-lbl">Gosta de ser chamado por</div>', unsafe_allow_html=True)
                ed_apelido = st.text_input("f_apelido", value=apelido_val, key=f"apelido_{real_idx}", label_visibility="collapsed")
            with r1_6:
                st.markdown('<div class="act-fld-lbl">Data da visita</div>', unsafe_allow_html=True)
                ed_visita = st.text_input("f_visita", value=data_visita_val, key=f"visita_{real_idx}", label_visibility="collapsed")

            # --- LINHA 2: Nome (Sem Acentos) | Copiar | Limpar ---
            r2_1, r2_2, r2_3, r2_4 = st.columns([3.2, 0.35, 0.35, 4.1])
            with r2_1:
                st.markdown('<div class="act-fld-lbl">Nome (Sem Acentos)</div>', unsafe_allow_html=True)
                st.text_input("f_nsem", value=nome_sem_acento, key=f"nsem_{real_idx}", label_visibility="collapsed")
            with r2_2:
                st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
                st.button("📋", key=f"cp_nsem_{real_idx}", help=f"Copiar: {nome_sem_acento}")
            with r2_3:
                st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
                st.button("🗑", key=f"cl_nsem_{real_idx}", help="Limpar")
            with r2_4:
                st.empty()

            # --- LINHA 3: Resumo (Órgão Nome CPF Idade) | Copiar | Limpar ---
            r3_1, r3_2, r3_3, r3_4 = st.columns([5.2, 0.35, 0.35, 2.1])
            with r3_1:
                st.markdown('<div class="act-fld-lbl">Resumo (Órgão Nome CPF Idade)</div>', unsafe_allow_html=True)
                st.text_input("f_resumo", value=resumo_val, key=f"resumo_{real_idx}", label_visibility="collapsed")
            with r3_2:
                st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
                st.button("📋", key=f"cp_res_{real_idx}", help=f"Copiar: {resumo_val}")
            with r3_3:
                st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
                st.button("🗑", key=f"cl_res_{real_idx}", help="Limpar")
            with r3_4:
                st.empty()

            st.markdown('<hr class="act-hr">', unsafe_allow_html=True)

            # --- LINHA 4: Loja | Atendido por | Órgão | Nº benefício ou matrícula | Copiar | Limpar | Espécie ---
            r4_1, r4_2, r4_3, r4_4, r4_5, r4_6, r4_7 = st.columns([1.3, 1.8, 1.1, 1.8, 0.35, 0.35, 1.3])
            with r4_1:
                st.markdown('<div class="act-fld-lbl">Loja</div>', unsafe_allow_html=True)
                ed_loja = st.text_input("f_loja", value=loja_val, key=f"loja_{real_idx}", label_visibility="collapsed")
            with r4_2:
                st.markdown('<div class="act-fld-lbl">Atendido por</div>', unsafe_allow_html=True)
                ed_atend = st.text_input("f_atend", value=atendido_val, key=f"atend_{real_idx}", label_visibility="collapsed")
            with r4_3:
                st.markdown('<div class="act-fld-lbl">Órgão</div>', unsafe_allow_html=True)
                ed_orgao = st.text_input("f_orgao", value=orgao_val, key=f"orgao_{real_idx}", label_visibility="collapsed")
            with r4_4:
                st.markdown('<div class="act-fld-lbl">Nº benefício ou matrícula</div>', unsafe_allow_html=True)
                ed_benef = st.text_input("f_benef", value=beneficio_val, key=f"benef_{real_idx}", label_visibility="collapsed")
            with r4_5:
                st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
                st.button("📋", key=f"cp_ben_{real_idx}", help=f"Copiar: {beneficio_val}")
            with r4_6:
                st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
                if st.button("🗑", key=f"cl_ben_{real_idx}", help="Limpar Benefício"):
                    if 'ID_STAT' in df_unificada.columns:
                        df_unificada.at[real_idx, 'ID_STAT'] = ""
                        salvar_bases_master(df_unificada, df_quarentena)
                        st.rerun()
            with r4_7:
                st.markdown('<div class="act-fld-lbl">Espécie</div>', unsafe_allow_html=True)
                ed_especie = st.text_input("f_esp", value=especie_val, key=f"esp_{real_idx}", label_visibility="collapsed")

            # --- LINHA 5: Senha Meu INSS | Senha Paraná | Data Nascimento | Idade | Identidade ---
            r5_1, r5_2, r5_3, r5_4, r5_5 = st.columns([1.8, 1.8, 1.5, 0.9, 2.0])
            with r5_1:
                st.markdown('<div class="act-fld-lbl">Senha Meu INSS</div>', unsafe_allow_html=True)
                ed_sinss = st.text_input("f_sinss", value=senha_inss_val, key=f"sinss_{real_idx}", label_visibility="collapsed")
            with r5_2:
                st.markdown('<div class="act-fld-lbl">Senha Paraná</div>', unsafe_allow_html=True)
                ed_spar = st.text_input("f_spar", value=senha_parana_val, key=f"spar_{real_idx}", label_visibility="collapsed")
            with r5_3:
                st.markdown('<div class="act-fld-lbl">Data Nascimento</div>', unsafe_allow_html=True)
                ed_nasc = st.text_input("f_nasc", value=data_nasc_val, key=f"nasc_{real_idx}", label_visibility="collapsed")
            with r5_4:
                st.markdown('<div class="act-fld-lbl">Idade</div>', unsafe_allow_html=True)
                st.text_input("f_idade", value=idade_val, key=f"idade_{real_idx}", label_visibility="collapsed")
            with r5_5:
                st.markdown('<div class="act-fld-lbl">Identidade</div>', unsafe_allow_html=True)
                ed_ident = st.text_input("f_ident", value=identidade_val, key=f"ident_{real_idx}", label_visibility="collapsed")

            # --- LINHA 6: CGC/CPF (Apenas Números) | Copiar | Limpar | CGC/CPF (Formatado) | Copiar ---
            r6_1, r6_2, r6_3, r6_4, r6_5 = st.columns([3.3, 0.35, 0.35, 3.65, 0.35])
            with r6_1:
                st.markdown('<div class="act-fld-lbl">CGC/CPF (Apenas Números)</div>', unsafe_allow_html=True)
                ed_cpf_num = st.text_input("f_cpfn", value=cpf_limpo, key=f"cpfn_{real_idx}", label_visibility="collapsed")
            with r6_2:
                st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
                st.button("📋", key=f"cp_cpfn_{real_idx}", help=f"Copiar: {cpf_limpo}")
            with r6_3:
                st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
                if st.button("🗑", key=f"cl_cpfn_{real_idx}", help="Limpar CPF"):
                    for c_cpf_col in ['USR1000', 'CPF', 'USER1000']:
                        if c_cpf_col in df_unificada.columns:
                            df_unificada.at[real_idx, c_cpf_col] = ""
                    salvar_bases_master(df_unificada, df_quarentena)
                    st.rerun()
            with r6_4:
                st.markdown('<div class="act-fld-lbl">CGC/CPF (Formatado)</div>', unsafe_allow_html=True)
                st.text_input("f_cpff", value=cpf_fmt, key=f"cpff_{real_idx}", label_visibility="collapsed")
            with r6_5:
                st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
                st.button("📋", key=f"cp_cpff_{real_idx}", help=f"Copiar: {cpf_fmt}")

            st.markdown('<hr class="act-hr">', unsafe_allow_html=True)

            # --- LINHA 7: Endereço 1 | Bairro 1 | Estado 1 | DDD | Tel_1 | Copiar | Limpar | Ref_1 ---
            r7_1, r7_2, r7_3, r7_4, r7_5, r7_6, r7_7, r7_8 = st.columns([2.3, 1.4, 0.65, 0.55, 1.2, 0.35, 0.35, 1.2])
            with r7_1:
                st.markdown('<div class="act-fld-lbl">Endereço 1</div>', unsafe_allow_html=True)
                ed_end1 = st.text_input("f_end1", value=end1_val, key=f"end1_{real_idx}", label_visibility="collapsed")
            with r7_2:
                st.markdown('<div class="act-fld-lbl">Bairro 1</div>', unsafe_allow_html=True)
                ed_bai1 = st.text_input("f_bai1", value=bairro1_val, key=f"bai1_{real_idx}", label_visibility="collapsed")
            with r7_3:
                st.markdown('<div class="act-fld-lbl">Estado 1</div>', unsafe_allow_html=True)
                ed_uf1 = st.text_input("f_uf1", value=estado1_val, key=f"uf1_{real_idx}", label_visibility="collapsed")
            with r7_4:
                st.markdown('<div class="act-fld-lbl">DDD</div>', unsafe_allow_html=True)
                ed_ddd = st.text_input("f_ddd", value=ddd_val, key=f"ddd_{real_idx}", label_visibility="collapsed")
            with r7_5:
                st.markdown('<div class="act-fld-lbl">Tel_1</div>', unsafe_allow_html=True)
                ed_tel1 = st.text_input("f_tel1", value=tel1_val, key=f"tel1_{real_idx}", label_visibility="collapsed")
            with r7_6:
                st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
                st.button("📋", key=f"cp_tel1_{real_idx}", help=f"Copiar: {tel1_val}")
            with r7_7:
                st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
                st.button("🗑", key=f"cl_tel1_{real_idx}", help="Limpar Tel")
            with r7_8:
                st.markdown('<div class="act-fld-lbl">Ref_1</div>', unsafe_allow_html=True)
                ed_ref1 = st.text_input("f_ref1", value=ref1_val, key=f"ref1_{real_idx}", label_visibility="collapsed")

            # --- LINHA 8: Cidade 1 | Cep 1 | Edifício | Telefones Consolidados ---
            r8_1, r8_2, r8_3, r8_4 = st.columns([2.3, 1.4, 1.2, 3.1])
            with r8_1:
                st.markdown('<div class="act-fld-lbl">Cidade 1</div>', unsafe_allow_html=True)
                ed_cid1 = st.text_input("f_cid1", value=cidade1_val, key=f"cid1_{real_idx}", label_visibility="collapsed")
            with r8_2:
                st.markdown('<div class="act-fld-lbl">Cep 1</div>', unsafe_allow_html=True)
                ed_cep1 = st.text_input("f_cep1", value=cep1_val, key=f"cep1_{real_idx}", label_visibility="collapsed")
            with r8_3:
                st.markdown('<div class="act-fld-lbl">Edifício</div>', unsafe_allow_html=True)
                ed_edif = st.text_input("f_edif", value=edificio_val, key=f"edif_{real_idx}", label_visibility="collapsed")
            with r8_4:
                st.markdown('<div class="act-fld-lbl">Telefones Consolidados</div>', unsafe_allow_html=True)
                st.text_input("f_tcons", value=tels_consol_val, key=f"tcons_{real_idx}", label_visibility="collapsed")

            # --- LINHA 9: Observações (USER9) + Botão Salvar Alterações ---
            r9_1, r9_2 = st.columns([6.6, 1.4])
            with r9_1:
                st.markdown('<div class="act-fld-lbl">Histórico / Observações (USER9)</div>', unsafe_allow_html=True)
                ed_obs = st.text_area("f_obs", value=obs_val, height=46, key=f"obs_{real_idx}", label_visibility="collapsed")
            with r9_2:
                st.markdown('<div class="act-fld-lbl">&nbsp;</div>', unsafe_allow_html=True)
                if st.button("💾 Salvar Ficha", type="primary", use_container_width=True, key=f"save_{real_idx}"):
                    df_unificada.at[real_idx, 'NAME'] = ed_nome.strip()
                    if 'FIRST_NAME' in df_unificada.columns:
                        df_unificada.at[real_idx, 'FIRST_NAME'] = ed_apelido.strip()
                    if 'USER5' in df_unificada.columns:
                        df_unificada.at[real_idx, 'USER5'] = ed_visita.strip()
                    if 'USER2' in df_unificada.columns:
                        df_unificada.at[real_idx, 'USER2'] = ed_loja.strip()
                    if 'USER6' in df_unificada.columns:
                        df_unificada.at[real_idx, 'USER6'] = ed_atend.strip()
                    if 'COMPANY' in df_unificada.columns:
                        df_unificada.at[real_idx, 'COMPANY'] = ed_orgao.strip()
                    if 'ID_STAT' in df_unificada.columns:
                        df_unificada.at[real_idx, 'ID_STAT'] = ed_benef.strip()
                    if 'USER8' in df_unificada.columns:
                        df_unificada.at[real_idx, 'USER8'] = ed_especie.strip()
                    if 'USER10' in df_unificada.columns:
                        df_unificada.at[real_idx, 'USER10'] = ed_sinss.strip()
                    if 'USER11' in df_unificada.columns:
                        df_unificada.at[real_idx, 'USER11'] = ed_spar.strip()
                    if 'USER1' in df_unificada.columns:
                        df_unificada.at[real_idx, 'USER1'] = ed_nasc.strip()
                    if 'USER12' in df_unificada.columns:
                        df_unificada.at[real_idx, 'USER12'] = ed_ident.strip()
                    if 'USR1000' in df_unificada.columns:
                        df_unificada.at[real_idx, 'USR1000'] = limpar_cpf(ed_cpf_num)
                    if 'ADDR1' in df_unificada.columns:
                        df_unificada.at[real_idx, 'ADDR1'] = ed_end1.strip()
                    if 'ADDR3' in df_unificada.columns:
                        df_unificada.at[real_idx, 'ADDR3'] = ed_bai1.strip()
                    if 'STATE' in df_unificada.columns:
                        df_unificada.at[real_idx, 'STATE'] = ed_uf1.strip()
                    if 'CITY' in df_unificada.columns:
                        df_unificada.at[real_idx, 'CITY'] = ed_cid1.strip()
                    if 'ZIP' in df_unificada.columns:
                        df_unificada.at[real_idx, 'ZIP'] = ed_cep1.strip()
                    if 'ADDR2' in df_unificada.columns:
                        df_unificada.at[real_idx, 'ADDR2'] = ed_edif.strip()
                    if 'PHONE' in df_unificada.columns:
                        df_unificada.at[real_idx, 'PHONE'] = f"({ed_ddd.strip()}) {ed_tel1.strip()}" if ed_ddd.strip() else ed_tel1.strip()
                    if 'HOME_PHONE' in df_unificada.columns:
                        df_unificada.at[real_idx, 'HOME_PHONE'] = ed_ref1.strip()
                    if 'USER9' in df_unificada.columns:
                        df_unificada.at[real_idx, 'USER9'] = ed_obs.strip()

                    st.session_state["df_unificada"] = df_unificada
                    salvar_bases_master(df_unificada, df_quarentena)
                    st.toast("Ficha salva na Base Master!")

# -----------------------------------------------------------------------------
# 7. VISÕES AUXILIARES ACESSADAS PELOS BOTÕES DO TOPO
# -----------------------------------------------------------------------------
elif st.session_state["visao_ativa"] == "tabela":
    st.markdown('<div style="font-size:12px; font-weight:bold; margin-bottom:4px;">📊 Tabela Unificada (Base Master)</div>', unsafe_allow_html=True)
    if not df_unificada.empty:
        busca_tab = st.text_input("Filtrar Tabela:", placeholder="Digite para filtrar registros...", label_visibility="collapsed")
        if busca_tab:
            res_tab = df_unificada[df_unificada.astype(str).apply(lambda x: x.str.contains(busca_tab, case=False)).any(axis=1)]
            st.dataframe(res_tab, use_container_width=True, height=460)
        else:
            st.dataframe(df_unificada.head(200), use_container_width=True, height=460)

elif st.session_state["visao_ativa"] == "quarentena":
    st.markdown('<div style="font-size:12px; font-weight:bold; margin-bottom:4px;">⚠️ Quarentena / Revisão (PC 1 Hamilton vs PC 2 Jaedna)</div>', unsafe_allow_html=True)
    if not df_quarentena.empty:
        cols_quarantena = [c for c in ['NAME', 'ORIGEM', 'USER9', 'PHONE'] if c in df_quarentena.columns]
        st.dataframe(df_quarentena[cols_quarantena], use_container_width=True, height=460)
    else:
        st.success("Nenhum contato em quarentena!")

elif st.session_state["visao_ativa"] == "todos_campos":
    st.markdown('<div style="font-size:12px; font-weight:bold; margin-bottom:4px;">📋 Todos os Campos da Ficha Atual</div>', unsafe_allow_html=True)
    if not df_unificada.empty:
        cliente = df_unificada.iloc[st.session_state["idx_cliente"]]
        df_campos = pd.DataFrame(list(cliente.items()), columns=["Campo", "Valor"])
        st.dataframe(df_campos, use_container_width=True, height=460)

# Barra de status inferior clássica
st.markdown(f"""
    <div class="act-statusbar">
        <span>{VERSAO_APP} Carregado com sucesso | Modo: {'Base Master Travada' if ja_unificado else 'Aguardando Unificação Única'}</span>
        <span>Origem: {df_unificada.iloc[st.session_state['idx_cliente']].get('ORIGEM', 'Master') if not df_unificada.empty else '-'}</span>
    </div>
""", unsafe_allow_html=True)
