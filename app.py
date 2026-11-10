import streamlit as st

# Configuração de página em tela cheia (Wide Mode)
st.set_page_config(
    page_title="Act V17 - Soluções",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS customizada para réplica exata da interface ACT!
st.markdown("""
    <style>
        /* 1. Zerar margens e remover barras de rolagem da página principal */
        .main .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 0rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        
        body {
            overflow: hidden; /* Elimina a rolagem vertical */
            background-color: #f4f4f4; /* Fundo cinza suave clássico do ACT! */
        }

        /* 2. Compactar rótulos (labels) dos campos */
        .stTextInput label, .stSelectbox label, .stTextArea label {
            font-size: 11px !important;
            font-weight: 600 !important;
            color: #444444 !important;
            margin-bottom: 1px !important;
            height: 15px !important;
            line-height: 15px !important;
        }

        /* 3. Definir altura exata de 19px para as caixas de entrada de texto */
        .stTextInput input, .stSelectbox > div > div {
            height: 19px !important;
            min-height: 19px !important;
            max-height: 19px !important;
            font-size: 11px !important;
            padding: 0px 4px !important;
            line-height: 19px !important;
            background-color: #ffffff !important;
            border: 1px solid #7a7a7a !important;
            border-radius: 2px !important;
            color: #000000 !important;
        }

        /* 4. Estilizar botões de ação e cópia inline */
        .stButton > button {
            height: 19px !important;
            min-height: 19px !important;
            line-height: 17px !important;
            font-size: 10px !important;
            padding: 0px 6px !important;
            margin-top: 0px !important;
            background-color: #e1e1e1 !important;
            border: 1px solid #adadad !important;
            color: #333333 !important;
            border-radius: 2px !important;
        }
        
        .stButton > button:hover {
            background-color: #d0d0d0 !important;
            border-color: #707070 !important;
        }

        /* 5. Ajustar espaçamentos entre linhas de colunas */
        [data-testid="column"] {
            padding: 0px 2px !important;
        }
        
        div[data-testid="stVerticalBlock"] > div {
            gap: 2px !important;
        }
    </style>
""", unsafe_unsafe_html=True)