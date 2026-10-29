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

    /* Divisores finos clássicos */
    hr {
        margin: 3px 0px !important;
        border: none !important;
        border-top: 1px solid #808080 !important;
        border-bottom: 1px solid #FFFFFF !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

CSV_FILE = "Base_Consolidada_COMPLETA_ACT.csv"

@st.cache_data(ttl=1)
def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, dtype=str).fillna("")
    else:
        df = pd.DataFrame()
    return df

df = load_data()

def remove_accents(text):
    if not text or pd.isna(text):
        return ""
    nfkd = unicodedata.normalize('NFKD', str(text))
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

def clean_cpf_only_digits(val):
    if not val or pd.isna(val):
        return ""
    digits = ''.join(filter(str.isdigit, str(val)))
    if len(digits) >= 11:
        return digits[-11:]
    elif len(digits) > 0:
        return digits.zfill(11)
    return ""

def format_cpf_display(digits):
    if len(digits) == 11:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    return digits

def format_cep_display(val):
    if not val or pd.isna(val):
        return ""
    digits = ''.join(filter(str.isdigit, str(val)))
    if len(digits) == 8:
        return f"{digits[:5]}-{digits[5:]}"
    return digits if digits else str(val)

def extract_first_name(full_name, current_pname):
    if current_pname and str(current_pname).strip():
        return str(current_pname).strip()
    if full_name and str(full_name).strip():
        parts = str(full_name).strip().split()
        return parts[0] if parts else ""
    return ""

def calculate_age(birth_date_str):
    if not birth_date_str or pd.isna(birth_date_str):
        return ""
    birth_date_str = str(birth_date_str).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            dt = datetime.strptime(birth_date_str, fmt)
            today = datetime.today()
            age = today.year - dt.year - ((today.month, today.day) < (dt.month, dt.day))
            return str(age)
        except ValueError:
            pass
    return ""

if 'index' not in st.session_state:
    st.session_state.index = 0

if 'cleared_fields' not in st.session_state:
    st.session_state.cleared_fields = set()

# Barra Superior (Busca e Navegação)
c_head1, c_head2, c_head3 = st.columns([4, 3, 2])

with c_head1:
    busca = st.text_input("Localizar (Nome / CPF / Benefício):", key="search_query")

if busca:
    filtered_df = df[
        df['NOME'].astype(str).str.contains(busca, case=False, na=False) |
        df['CPF_LIMPO'].astype(str).str.contains(busca, na=False) |
        df.get('NUM_BENEFICIO', pd.Series()).astype(str).str.contains(busca, na=False)
    ]
else:
    filtered_df = df

total_registros = len(filtered_df)

if total_registros > 0:
    if st.session_state.index >=