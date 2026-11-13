import streamlit as st
import pandas as pd
import numpy as np
import os

VERSAO_APP = "Act V51"

st.set_page_config(page_title=f"{VERSAO_APP} - Banco.dbf", page_icon="📑", layout="wide", initial_sidebar_state="expanded")

# -----------------------------------------------------------------------------
# 1. SEGURANÇA E TELA DE LOGIN CLÁSSICA ACT! (JANELA ÚNICA E SIMÉTRICA - V51)
# -----------------------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    css_login = """
        <style>
        header, footer, [data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stToolbar"] {
            display: none !important;
        }
        .stApp {
            background-color: #808080 !important;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important;
        }
        .main .block-container {
            padding-top: 160px !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
        }
        /* Janela Modal Única usando o contêiner com borda nativa */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) {
            background-color: #D4D0C8 !important;
            border-radius: 0px !important;
            border-top: 2px solid #FFFFFF !important;
            border-left: 2px solid #FFFFFF !important;
            border-right: 2px solid #404040 !important;
            border-bottom: 2px solid #404040 !important;
            box-shadow: 1px 1px 0px #000000 !important;
            padding: 2px 2px 12px 2px !important;
            width: 332px !important;
            min-width: 332px !important;
            max-width: 332px !important;
            margin: 0 auto !important;
            box-sizing: border-box !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) > div {
            width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) [data-testid="stVerticalBlock"] {
            gap: 0.4rem !important;
            width: 100% !important;
        }
        /* Zera deslocamentos no bloco do título */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) [data-testid="stElementContainer"]:first-child,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) [data-testid="stMarkdownContainer"] {
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            box-sizing: border-box !important;
        }
        /* Barra de Título Azul Degradê alinhada por igual nos dois lados */
        .act-titlebar {
            background: linear-gradient(90deg, #0A246A 0%, #A6CAF0 100%);
            color: #FFFFFF;
            font-weight: bold;
            font-size: 11px;
            padding: 2px 3px 2px 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 0 0 8px 0;
            width: 100%;
            box-sizing: border-box;
            white-space: nowrap;
        }
        .act-close-btn {
            background-color: #D4D0C8;
            color: #000000;
            border-top: 1px solid #FFFFFF;
            border-left: 1px solid #FFFFFF;
            border-right: 1px solid #404040;
            border-bottom: 1px solid #404040;
            font-size: 9px;
            font-weight: bold;
            width: 14px;
            height: 13px;
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1;
            flex-shrink: 0;
        }
        /* Inputs clássicos sem bordas arredondadas */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) .stTextInput {
            padding: 0 12px !important;
            margin-bottom: 0px !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) .stTextInput label {
            color: #000000 !important;
            font-size: 11px !important;
            font-family: 'Tahoma', Arial, sans-serif !important;
            margin-bottom: 2px !important;
            min-height: 0 !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) .stTextInput div {
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            border-radius: 0px !important;
            box-shadow: none !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) .stTextInput input {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border-radius: 0px !important;
            border-top: 2px solid #808080 !important;
            border-left: 2px solid #808080 !important;
            border-right: 1px solid #FFFFFF !important;
            border-bottom: 1px solid #FFFFFF !important;
            box-shadow: inset 1px 1px 0px #404040 !important;
            height: 22px !important;
            min-height: 22px !important;
            padding: 1px 4px !important;
            font-size: 11px !important;
            font-family: 'Tahoma', Arial, sans-serif !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) .stTextInput button {
            display: none !important;
        }
        /* Checkbox Clássica */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) .stCheckbox {
            padding: 4px 12px 4px 12px !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) .stCheckbox label p {
            color: #000000 !important;
            font-size: 11px !important;
            font-family: 'Tahoma', Arial, sans-serif !important;
            white-space: nowrap !important;
        }
        /* Botões OK e Cancel */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) [data-testid="column"] {
            padding: 0 4px !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) .stButton button {
            background-color: #D4D0C8 !important;
            color: #000000 !important;
            border-radius: 0px !important;
            border-top: 2px solid #FFFFFF !important;
            border-left: 2px solid #FFFFFF !important;
            border-right: 2px solid #404040 !important;
            border-bottom: 2px solid #404040 !important;
            box-shadow: inset -1px -1px 0px #808080 !important;
            height: 23px !important;
            min-height: 23px !important;
            width: 78px !important;
            min-width: 78px !important;
            padding: 0px !important;
            font-size: 11px !important;
            font-family: 'Tahoma', Arial, sans-serif !important;
            display: block !important;
            margin: 0 auto !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) .stButton button p {
            font-size: 11px !important;
            color: #000000 !important;
            margin: 0 !important;
            line-height: 19px !important;
            white-space: nowrap !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.act-titlebar) .stButton button:active {
            border-top: 2px solid #404040 !important;
            border-left: 2px solid #404040 !important;
            border-right: 2px solid #FFFFFF !important;
            border-bottom: 2px solid #FFFFFF !important;
        }
        .act-msg-erro {
            color: #800000;
            font-size: 11px;
            text-align: center;
            padding-top: 6px;
            font-family: 'Tahoma', Arial, sans-serif;
        }
        </style>
    """
    st.markdown(css_login, unsafe_allow_html=True)

    with st.container(border=True):
        html_title = """
            <div class="act-titlebar">
                <span>Login to Banco.dbf</span>
                <span class="act-close-btn">×</span>
            </div>
        """
        st.markdown(html_title, unsafe_allow_html=True)

        user_input = st.text_input("Enter your user name for this database:", value="Hamilton Flecha", key="user_key")
        senha_input = st.text_input("Enter your password for this database:", type="password", key="pass_key")
        st.checkbox("Remember password", value=True, key="rem_key")

        _, b_ok, b_cancel, _ = st.columns([0.8, 1.2, 1.2, 0.8])
        with b_ok:
            btn_ok = st.button("OK", key="btn_ok_act")
        with b_cancel:
            btn_cancel = st.button("Cancel", key="btn_cancel_act")

        if btn_ok:
            if senha_input == "solucoes1986":
                st.session_state["autenticado"] = True
                st.session_state["operador_atual"] = user_input
                st.rerun()
            else:
                st.markdown('<div class="act-msg-erro">Invalid password for Banco.dbf.</div>', unsafe_allow_html=True)
        if btn_cancel:
            st.markdown('<div class="act-msg-erro">Login cancelled.</div>', unsafe_allow_html=True)

    st.stop()

# -----------------------------------------------------------------------------
# 2. FUNÇÕES DE DADOS E LEITURA
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

def ler_arquivo(nome_base):
    for ext in ['.xlsx', '.csv', '.XLSX', '.CSV']:
        caminho = f"{nome_base}{ext}"
        if os.path.exists(caminho):
            try:
                if ext.lower() == '.csv':
                    df = pd.read_csv(caminho, dtype=str).fillna("")
                else:
                    df = pd.read_excel(caminho, dtype=str).fillna("")
                for col