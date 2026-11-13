import streamlit as st
import pandas as pd
import numpy as np
import os

VERSAO_APP = "Act V53"

st.set_page_config(page_title=f"{VERSAO_APP} - Banco.dbf", page_icon="📑", layout="wide", initial_sidebar_state="expanded")

# -----------------------------------------------------------------------------
# 1. SEGURANÇA E TELA DE LOGIN CLÁSSICA ACT! (CAIXA COMPACTA 320PX - V53)
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
            padding-top: 150px !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            margin: 0 auto !important;
            max-width: 100% !important;
        }
        /* Força a coluna central a ter exatamente 320px (redução >80% da largura da tela) */
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) {
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) > div[data-testid="column"]:nth-child(2) {
            width: 320px !important;
            min-width: 320px !important;
            max-width: 320px !important;
            flex: 0 0 320px !important;
            background-color: #D4D0C8 !important;
            border-radius: 0px !important;
            border-top: 2px solid #FFFFFF !important;
            border-left: 2px solid #FFFFFF !important;
            border-right: 2px solid #404040 !important;
            border-bottom: 2px solid #404040 !important;
            box-shadow: 1px 1px 0px #000000 !important;
            padding: 2px 2px 12px 2px !important;
            box-sizing: border-box !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) > div[data-testid="column"]:nth-child(1),
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) > div[data-testid="column"]:nth-child(3) {
            flex: 1 1 auto !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) > div[data-testid="column"]:nth-child(2) [data-testid="stVerticalBlock"] {
            gap: 0.35rem !important;
        }
        /* Barra de Título Azul Degradê */
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
        /* Inputs clássicos quadrados Windows 2000 */
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stTextInput {
            padding: 0 12px !important;
            margin-bottom: 0px !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stTextInput label {
            color: #000000 !important;
            font-size: 11px !important;
            font-family: 'Tahoma', Arial, sans-serif !important;
            margin-bottom: 2px !important;
            min-height: 0 !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stTextInput div[data-baseweb="input"],
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stTextInput div[data-baseweb="base-input"] {
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            border-radius: 0px !important;
            box-shadow: none !important;
            padding: 0 !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stTextInput input {
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
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stTextInput button {
            display: none !important;
        }
        /* Checkbox Clássica */
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stCheckbox {
            padding: 4px 12px !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stCheckbox label p {
            color: #000000 !important;
            font-size: 11px !important;
            font-family: 'Tahoma', Arial, sans-serif !important;
            white-space: nowrap !important;
        }
        /* Botões OK e Cancel */
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stButton button {
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
            width: 76px !important;
            min-width: 76px !important;
            padding: 0px !important;
            font-size: 11px !important;
            font-family: 'Tahoma', Arial, sans-serif !important;
            display: block !important;
            margin: 0 auto !important;
        }
        [data