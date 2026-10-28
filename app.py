import streamlit as st
import pandas as pd
import os
import re
import unicodedata
from datetime import datetime

st.set_page_config(page_title="ACT! Soluções", layout="wide")

# CSS para replicar EXATAMENTE a altura dos campos, cores, fontes e relevo do ACT!
st.markdown("""
<style>
    /* Fundo geral cinza clássico do ACT! / Windows 95/98/2000 */
    .stApp {
        background-color: #D4D0C8 !important;
        font-family: 'Tahoma', 'MS Sans Serif', 'Arial', sans-serif !important;
        color: #000000 !important;
    }
    
    /* Container compacto sem rolagem */
    .block-container {
        padding-top: 0.3rem !important;
        padding-bottom: 0.3rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        background-color: #D4D0C8 !important;
    }

    /* Rótulos dos campos no padrão ACT! */
    label {
        font-family: 'Tahoma', 'MS Sans Serif', sans-serif !important;
        font-size: 11px !important;
        font-weight: normal !important;
        color: #000000 !important;
        margin-bottom: 1px !important;
        padding-bottom: 0px !important;
        line-height: 1.1 !important;
    }

    /* Caixas de Texto com ALTURA EXATA DO ACT! (22px) e efeito 3D Inset */
    div[data-baseweb="input"] {
        min-height: 22px !important;
        height: 22px !important;
        background-color: #FFFFFF !important;
        border: 2px solid !important;
        border-color: #808080 #FFFFFF #FFFFFF #808080 !important;
        border-radius: 0px !important;
        padding: 0px 3px !important;
    }

    div[data-baseweb="input"] input {
        font-family: 'Tahoma', 'MS Sans Serif', sans-serif !important;
        font-size: 11px !important;
        color: #000000 !important;
        height: 18px !important;
        padding: 0px 2px !important;
    }

    /* Área de Observações */
    div[data-baseweb="textarea"] textarea {
        font-family: 'Tahoma', 'MS Sans Serif', sans-serif !important;
        font-size: 11px !important;
        background-color: #FFFFFF !important;
        border: 2px solid !important;
        border-color: #808080 #FFFFFF #FFFFFF #808080 !important;
        border-radius: 0px !important;
        color: #000000 !important;
        padding: 2px 4px !important;
    }

    /* Botões 3D em Relevo Saliente */
    .stButton>button {
        background-color: #D4D0C8 !important;
        color: #000000 !important;
        font-family: 'Tahoma', 'MS Sans Serif', sans-serif !important;
        font-size: 11px !important;
        font-weight: bold !important;
        border: 2px solid !important;
        border-color: #FFFFFF #808080 #808080 #FFFFFF !important;
        border-radius: 0px !important;
        height: 22px !important;
        min-height: 22px !important;
        padding: 0px 4px !important;
        margin: 0px !important;
        box-shadow: none !important;
    }

    .stButton>button:active {
        border-color: #808080 #FFFFFF #FFFFFF #808080 !important;
    }

    /* Divisores finos cláss