import streamlit as st
import pandas as pd
import numpy as np
import os

VERSAO_APP = "Act V49"

st.set_page_config(page_title=f"{VERSAO_APP} - Banco.dbf", page_icon="📑", layout="wide", initial_sidebar_state="expanded")

# -----------------------------------------------------------------------------
# 1. SEGURANÇA E TELA DE LOGIN CLÁSSICA ACT! (PLACA ÚNICA SEM DUPLICIDADE)
# -----------------------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("""
        <style>
        /* Oculta elementos padrão do Streamlit */
        header, footer, [data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stToolbar"] {
            display: none !important;
        }
        /* Fundo cinza da área de trabalho do Act! */
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
        /* Remove qualquer borda ou fundo do contêiner pai externo */
        div[data-testid="stVerticalBlock"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        /* Aplica a moldura 3D APENAS na placa interna única onde fica o formulário */
        div[data-testid="stVerticalBlock"]:has(> div div.act-titlebar):not(:has(div[data-testid="stVerticalBlock"])) {
            background-color: #D4D0C8 !important;
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
            gap: 0.4rem !important;
        }
        /* Zera bordas e largura do wrapper interno do st.markdown */
        div[data-testid="stVerticalBlock"]:has(> div div.act-titlebar) > div:first-child,
        div[data-testid="stVerticalBlock"]:has(> div div.act-titlebar) > div:first-child > div,
        div[data-testid="stVerticalBlock"]:has(> div div.act-titlebar) [data-testid="stMarkdownContainer"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            box-sizing: border-box !important;
        }
        /* Barra de Título Azul Degradê preenchida por igual nos dois lados */
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
        div[data-testid="stVerticalBlock"]:has(> div div.act-titlebar) .stTextInput {
            padding: 0 12px !important;
            margin-bottom: 0px !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        div[data-testid="stVerticalBlock"]:has(> div div.act-titlebar) .stTextInput label {
            color: #000000 !important;
            font-size: 11px !important;
            font-family: 'Tahoma', Arial, sans-serif !important;
            margin-bottom: 2px !important;
            min-height: 0 !important;
        }
        div[data-testid="stVerticalBlock"]:has(> div div.act-titlebar) .stTextInput div {
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            border-radius: 0px !important;
            box-shadow: none !important;
        }
        div[data-testid="stVerticalBlock"]:has(> div div.act-titlebar) .stTextInput input {
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
        div[data-testid="stVerticalBlock"]:has(> div div.act-titlebar) .stTextInput button {
            display: none !important;
        }
        /* Checkbox Clássica */
        div[data-testid="stVerticalBlock"]:has(> div div.act-titlebar) .stCheckbox {
            padding: 4px 12px 4px 12px !important;
        }