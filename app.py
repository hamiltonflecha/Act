import streamlit as st

# Configuração de página em tela cheia (Wide Mode)
st.set_page_config(
    page_title="Act V22 - Soluções",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS customizada - Réplica exata das cores, bordas e larguras de coluna do ACT!
st.markdown("""
    <style>
        /* 1. Zerar margens e remover barras de rolagem da página principal */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #ece9d8 !important; /* Cor bege/cinza clássica do ACT! */
            overflow: hidden !important; /* Elimina a rolagem vertical */
        }

        .main .block-container {
            padding-top: 0.1rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0.3rem !important;
            padding-right: 0.3rem !important;
            max-width: 100% !important;
        }

        /* 2. REMOVER MOLDURAS BRANCAS E DESATIVAR LARGURA MÍNIMA PADRÃO DAS COLUNAS */
        div[data-baseweb="input"], 
        div[data-baseweb="base-input"] {
            background-color: transparent !important;
            border: none !important;
            padding: 0px !important;
            margin: 0px !important;
            box-shadow: none !important;
        }

        /* Libera as colunas para assumirem as larguras exatas da tabela de caracteres */
        [data-testid="column"] {
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-end !important;
            padding: 0px 1px !important;
            min-width: 0px !important; /* Permite encolher campos pequenos */
        }

        /* 3. Compactar rótulos (labels) dos campos */
        .stTextInput label, .stSelectbox label {
            font-size: 10.5px !important;
            font-weight: bold !important;
            color: #000000 !important;
            margin-bottom: 0px !important;
            height: 13px !important;
            line-height: 13px !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }

        /* 4. Caixa de texto retangular de 19px estilo Windows clássico */
        input[data-testid="stTextInputInput"] {
            height: 19px !important;
            min-height: 19px !important;
            max-height: 19px !important;
            font-size: 11px !important;
            padding: 0px 3px !important;
            line-height: 19px !important;
            background-color: #ffffff !important;
            border: 1px solid #7f9db9 !important; /* Borda fina clássica do Windows */
            border-radius: 0px !important;
            color: #000000 !important;
            box-shadow: none !important;
        }

        /* 5. Botões inline com 19px e alinhamento na base dos campos */
        .stButton {
            margin-top: 0px !important;
            margin-bottom: 0px !important;
            width: 100% !important;
        }

        .stButton > button {
            height: 19px !important;
            min-height: 19px !important;
            line-height: 17px !important;
            font-size: 10px !important;
            padding: 0px 2px !important;
            margin: 0px !important;
            background-color: #d4d0c8 !important; /* Cinza metálico clássico */
            border: 1px solid #404040 !important;
            color: #000000 !important;
            border-radius: 0px !important;
            font-weight: bold !important;
            width: 100% !important;
        }
        
        .stButton > button:hover {
            background-color: #0a246a !important;
            color: #ffffff !important;
        }

        /* 6. Zerar espaçamentos entre linhas para garantir zero rolagem */
        div[data-testid="stVerticalBlock"] > div {
            gap: 0px !important;
            margin-bottom: 0px !important;
        }
        
        /* Ocultar barra superior padrão do Streamlit */
        header[data-testid="stHeader"], footer {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# Exemplo de valores e cálculo da idade em +108 meses (+9 anos)
idade_atual = 45
idade_108_meses = idade_atual + 9 if idade_atual is not None else ""

# Topo / Navegação (Marcado como ACT V22)
c_busca, c_prev, c_next, c_novo, c_status = st.columns([5.4, 1.0, 1.0, 2.0, 3.0])
with c_busca:
    st.text_input("Localizar (Nome / CPF / Benefício):", key="busca")
with c_prev:
    st.button("◄ Ant...", use_container_width=True)
with c_next:
    st.button("Próx...", use_container_width=True)
with c_novo:
    st.button("+ Novo Contato", use_container_width=True)
with c_status:
    st.markdown("<div style='text-align: right; font-size: 11px; font-weight: bold; color: #000; padding-bottom: 2px;'>Act V22<br><span style='font-size: 10px; font-weight: normal;'>Hamilton e Jaedna | Soluções</span></div>", unsafe_allow_html=True)

# Linha 1: Nome (78 char), 1º Nome (30 char), Gosta de ser chamado por (24 char), Data da visita (10 char)
c1, c1_b1, c1_b2, c2, c3, c4 = st.columns([7.8, 0.4, 0.4, 3.0, 2.4, 1.0])
with c1:
    st.text_input("Nome", value="CALMA DA SILVA MNIRANDA")
with c1_b1:
    st.button("📋", key="cp_nome")
with c1_b2:
    st.button("✂️", key="cl_nome")
with c2:
    st.text_input("1º Nome", value="CALMA")
with c3:
    st.text_input("Gosta de ser chamado por", value="")
with c4:
    st.text_input("Data da visita", value="")

# Linha 2: Nome sem acentos (78 char)
c_sa, c_sa_b1, c_sa_b2, c_empty = st.columns([7.8, 0.4, 0.4, 6.4])
with c_sa:
    st.text_input("Nome (Sem Acentos)", value="CALMA DA SILVA MNIRANDA")
with c_sa_b1:
    st.button("📋", key="cp_sa")
with c_sa_b2:
    st.button("✂️", key="cl_sa")

# Linha 3: Resumo (114 char)
c_res, c_res_b1, c_res_b2 = st.columns([11.4, 0.4, 0.4])
with c_res:
    st.text_input("Resumo (Órgão Nome CPF Idade)", value="INSS CALMA DA SILVA MNIRANDA 67570437691")
with c_res_b1:
    st.button("📋", key="cp_res")
with c_res_b2:
    st.button("✂️", key="cl_res")

# Linha 4: Loja (24), Atendido por (36), Órgão (18), Nº benefício (24), Espécie (12)
col_loja, col_atend, col_org, col_ben, col_esp = st.columns([2.4, 3.6, 1.8, 2.4, 1.2])
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

# Linha 5: Senha Meu INSS (24), Senha Paraná (24), Data Nascimento (10), Idade (4), 108 Meses (4), Identidade (24)
col_s1, col_s2, col_dn, col_id, col_id108, col_rg = st.columns([2.4, 2.4, 1.0, 0.4, 0.4, 2.4])
with col_s1:
    st.text_input("Senha Meu INSS", value="")
with col_s2:
    st.text_input("Senha Paraná", value="")
with col_dn:
    st.text_input("Data Nascimento", value="")
with col_id:
    st.text_input("Idade", value=str(idade_atual))
with col_id108:
    st.text_input("108 Meses", value=str(idade_108_meses))
with col_rg:
    st.text_input("Identidade", value="")

# Linha 6: CPF Números (11), CPF Formatado (14)
col_cpf, col_cpf_b1, col_cpf_b2, col_cpff, col_cpff_b1 = st.columns([1.1, 0.4, 0.4, 1.4, 0.4])
with col_cpf:
    st.text_input("CGC/CPF (Números)", value="67570437691")
with col_cpf_b1:
    st.button("📋", key="cp_cpf")
with col_cpf_b2:
    st.button("✂️", key="cl_cpf")
with col_cpff:
    st.text_input("CGC/CPF (Formatado)", value="675.704.376-91")
with col_cpff_b1:
    st.button("📋", key="cp_cpff")

# Linha 7: Endereço 1 (84), Bairro 1 (42), Estado 1 (3), DDD (3), Tel_1 (12), Ref_1 (36)
c_end, c_bai, c_uf, c_ddd, c_tel, c_tel_b1, c_tel_b2, c_ref = st.columns([8.4, 4.2, 0.3, 0.3, 1.2, 0.4, 0.4, 3.6])
with c_end:
    st.text_input("Endereço 1", value="RUA AÇONORTE, 314")
with c_bai:
    st.text_input("Bairro 1", value="")
with c_uf:
    st.text_input("UF", value="MG")
with c_ddd:
    st.text_input("DDD", value="31")
with c_tel:
    st.text_input("Tel_1", value="37421019")
with c_tel_b1:
    st.button("📋", key="cp_tel")
with c_tel_b2:
    st.button("✂️", key="cl_tel")
with c_ref:
    st.text_input("Ref_1", value="")

# Linha 8: Cidade 1 (42), Cep 1 (9), Edifício (36), Telefones Consolidados (60)
c_cid, c_cep, c_edi, c_tels, c_tels_b1 = st.columns([4.2, 0.9, 3.6, 6.0, 0.4])
with c_cid:
    st.text_input("Cidade 1", value="OURO BRANCO")
with c_cep:
    st.text_input("Cep 1", value="")
with c_edi:
    st.text_input("Edifício", value="")
with c_tels:
    st.text_input("Telefones Consolidados", value="37421019")
with c_tels_b1:
    st.button("📋", key="cp_tels")