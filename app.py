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
""", unsafe_allow_html=True)

# Exemplo de valores e cálculo da idade em +108 meses (+9 anos)
idade_atual = 45  # Exemplo de valor de idade
idade_108_meses = idade_atual + 9 if idade_atual is not None else ""

# Cabeçalho / Navegação
c_busca, c_prev, c_next, c_novo, c_status = st.columns([4, 1, 1, 2, 4])
with c_busca:
    st.text_input("Localizar (Nome / CPF / Benefício):", key="busca")
with c_prev:
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.button("◄ Ant...", use_container_width=True)
with c_next:
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.button("Próx...", use_container_width=True)
with c_novo:
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.button("+ Novo Contato", use_container_width=True)
with c_status:
    st.markdown("<div style='text-align: right; font-size: 11px; font-weight: bold;'>Act V17<br><span style='font-size: 10px; font-weight: normal;'>Hamilton e Jaedna<br>Soluções</span></div>", unsafe_allow_html=True)

# Linha 1: Nome completo, Primeiro Nome, Gosta de ser chamado por, Data da visita
c1, c1_btn1, c1_btn2, c2, c3, c4 = st.columns([4, 0.4, 0.4, 3, 3, 3])
with c1:
    st.text_input("Nome", value="CALMA DA SILVA MNIRANDA")
with c1_btn1:
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.button("📋", key="cp_nome")
with c1_btn2:
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.button("✂️", key="cl_nome")
with c2:
    st.text_input("1º Nome", value="CALMA")
with c3:
    st.text_input("Gosta de ser chamado por", value="")
with c4:
    st.text_input("Data da visita", value="")

# Linha 2: Nome sem acentos
c_sa, c_sa_btn1, c_sa_btn2, c_empty = st.columns([4, 0.4, 0.4, 9])
with c_sa:
    st.text_input("Nome (Sem Acentos)", value="CALMA DA SILVA MNIRANDA")
with c_sa_btn1:
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.button("📋", key="cp_sa")
with c_sa_btn2:
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.button("✂️", key="cl_sa")

# Linha 3: Resumo
c_res, c_res_btn1, c_res_btn2 = st.columns([8, 0.4, 0.4])
with c_res:
    st.text_input("Resumo (Órgão Nome CPF Idade)", value="INSS CALMA DA SILVA MNIRANDA 67570437691")
with c_res_btn1:
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.button("📋", key="cp_res")
with c_res_btn2:
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.button("✂️", key="cl_res")

# Linha 4: Loja, Atendido por, Órgão, Nº benefício, Espécie
col_loja, col_atend, col_org, col_ben, col_esp = st.columns([3, 3, 2, 4, 2])
with col_loja:
    st.text_input("Loja", value="Centro - OB")
with col_atend:
    st.text_input("Atendido por", value="")
with col_org:
    st.text_input("Órgão", value="INSS")
with col_ben:
    st.text_input("Nº benefício ou matrícula", value="")
with col_esp:
    st.text_input("Espécie", value="")

# Linha 5: Senha Meu INSS, Senha Paraná, Data Nascimento, Idade, Idade daqui a 108 meses, Identidade
col_s1, col_s2, col_dn, col_id, col_id108, col_rg = st.columns([3, 3, 3, 2, 3, 3])
with col_s1:
    st.text_input("Senha Meu INSS", value="")
with col_s2:
    st.text_input("Senha Paraná", value="")
with col_dn:
    st.text_input("Data Nascimento", value="")
with col_id:
    st.text_input("Idade", value=str(idade_atual))
with col_id108:
    st.text_input("Idade daqui a 108 meses", value=str(idade_108_meses))
with col_rg:
    st.text_input("