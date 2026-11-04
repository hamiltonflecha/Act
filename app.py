import streamlit as st
import pandas as pd
import os
import re
import unicodedata
from datetime import datetime

st.set_page_config(page_title="ACT! Soluções", layout="wide")

st.markdown("""
<style>
    .stApp {
        background-color: #D4D0C8 !important;
        font-family: 'Tahoma', 'MS Sans Serif', sans-serif !important;
        color: #000000 !important;
    }
    
    .block-container {
        padding-top: 0.1rem !important;
        padding-bottom: 0.1rem !important;
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
    }

    /* Alinhamento perfeito dos campos e botões pela base */
    div[data-testid="column"] {
        display: flex !important;
        align-items: flex-end !important;
    }

    label {
        font-family: 'Tahoma', 'MS Sans Serif', sans-serif !important;
        font-size: 11px !important;
        color: #000000 !important;
        margin-bottom: 1px !important;
        line-height: 1 !important;
    }

    /* Caixas com altura exata de 22px do ACT! */
    div[data-baseweb="input"] {
        min-height: 22px !important;
        height: 22px !important;
        background-color: #FFFFFF !important;
        border: 2px solid !important;
        border-color: #808080 #FFFFFF #FFFFFF #808080 !important;
        border-radius: 0px !important;
        padding: 0px 2px !important;
    }

    div[data-baseweb="input"] input {
        font-family: 'Tahoma', 'MS Sans Serif', sans-serif !important;
        font-size: 11px !important;
        color: #000000 !important;
        height: 18px !important;
        padding: 0px 2px !important;
    }

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
        padding: 0px 3px !important;
        margin: 0px !important;
    }

    hr {
        margin: 2px 0px !important;
        border-top: 1px solid #808080 !important;
        border-bottom: 1px solid #FFFFFF !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)