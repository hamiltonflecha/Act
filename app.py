import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="ACT! Soluções - Gerenciador Web", layout="wide")

CSV_FILE = "Base_Consolidada_COMPLETA_ACT.csv"

@st.cache_data(ttl=1)
def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, dtype=str).fillna("")
    else:
        df = pd.DataFrame(columns=[
            'UNIQUE_ID', 'NOME', 'PRIMEIRO_NOME', 'GOSTA_SER_CHAMADO', 'REFERENCIA', 'COMO_NOS_ACHOU',
            'INDICADO_POR', 'DATA_VISITA', 'LOJA', 'ATENDIDO_POR', 'DIGITADO_POR',
            'ORGAO', 'NUM_BENEFICIO', 'ESPECIE', 'SENHA_MEU_INSS', 'SENHA_PARANA', 'SENHA_BV',
            'DATA_NASCIMENTO', 'CPF_LIMPO', 'CPF_FORMATADO', 'IDENTIDADE',
            'PARA_QUE_USARA_DINHEIRO', 'BANCOS_FINANCEIRAS', 'EMAIL_1', 'EMAIL_2',
            'ENDERECO', 'BAIRRO', 'CIDADE', 'UF', 'CEP', 'EDIFICIO', 'RMC',
            'DDD_TEL1', 'TEL1', 'REF_TEL1', 'DDD_TEL2', 'TEL2', 'REF_TEL2', 'TELEFONES_CONSOLIDADOS',
            'COMENTARIOS_HISTORICO'
        ])
    return df

df = load_data()

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

if 'index' not in st.session_state:
    st.session_state.index = 0

st.title("📇 ACT! Soluções - Sistema Web Unificado")

top_col1, top_col2, top_col3 = st.columns([3, 2, 2])

with top_col1:
    busca = st.text_input("🔍 Pesquisar por Nome, CPF ou Benefício:", key="search_query")

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
    if st.session_state.index >= total_registros:
        st.session_state.index = 0
    curr_idx = st.session_state.index
    contato = filtered_df.iloc[curr_idx]
else:
    contato = {}
    curr_idx = 0

with top_col2:
    st.write("### ")
    c_prev, c_pos, c_next = st.columns([1, 2, 1])
    if c_prev.button("◀ Anterior") and curr_idx > 0:
        st.session_state.index -= 1
        st.rerun()
    c_pos.markdown(f"<h4 style='text-align: center;'><b>{curr_idx + 1} de {total_registros}</b></h4>", unsafe_allow_html=True)
    if c_next.button("Próximo ▶") and curr_idx < total_registros - 1:
        st.session_state.index += 1
        st.rerun()

with top_col3:
    st.write("### ")
    if st.button("➕ Cadastrar Novo Contato", type="primary"):
        st.session_state.novo_contato = True

st.divider()

if total_registros == 0:
    st.warning("Nenhum contato encontrado.")
else:
    with st.container():
        r1_1, r1_2, r1_3 = st.columns([4, 2, 2])
        r1_1.text_input("Nome", value=str(contato.get('NOME', '')))
        r1_2.text_input("1º Nome", value=str(contato.get('PRIMEIRO_NOME', '')))
        r1_3.text_input("Gosta de ser chamado por", value=str(contato.get('GOSTA_SER_CHAMADO', '')))

        r2_1, r2_2, r2_3, r2_4 = st.columns([3, 2, 2, 2])
        r2_1.text_input("Referência", value=str(contato.get('REFERENCIA', '')))
        r2_2.text_input("Como nos achou?", value=str(contato.get('COMO_NOS_ACHOU', '')))
        r2_3.text_input("Indicado por", value=str(contato.get('INDICADO_POR', '')))
        r2_4.text_input("Data da visita", value=str(contato.get('DATA_VISITA', '')))

        r3_1, r3_2, r3_3 = st.columns([2, 3, 3])
        r3_1.text_input("Loja", value=str(contato.get('LOJA', 'Centro - OB')))
        r3_2.text_input("Atendido por", value=str(contato.get('ATENDIDO_POR', '')))
        r3_3.text_input("Digitado por", value=str(contato.get('DIGITADO_POR', '')))

        st.markdown("---")
        b1, b2, b3 = st.columns([3, 3, 2])
        b1.text_input("Órgão", value=str(contato.get('ORGAO', 'INSS')))
        b2.text_input("Nº Benefício ou matrícula", value=str(contato.get('NUM_BENEFICIO', '')))
        b3.text_input("Espécie", value=str(contato.get('ESPECIE', '')))

        s1, s2, s3 = st.columns([3, 3, 2])
        s1.text_input("Senha Meu INSS", value=str(contato.get('SENHA_MEU_INSS', '')))
        s2.text_input("Senha Paraná", value=str(contato.get('SENHA_PARANA', '')))
        s3.text_input("Senha BV", value=str(contato.get('SENHA_BV', '')))

        d1, d2, d3 = st.columns([3, 3, 2])
        d1.text_input("Data Nascimento", value=str(contato.get('DATA_NASCIMENTO', '')))
        
        raw_cpf = clean_cpf_only_digits(contato.get('CPF_LIMPO', ''))
        cpf_fmt = format_cpf_display(raw_cpf)
        
        cpf_col1, cpf_col2 = d2.columns([5, 1])
        cpf_col1.text_input("CGC/CPF (Apenas Números)", value=raw_cpf)
        cpf_col2.button("📋", key="cp_cpf_puro")

        d3.text_input("CPF (Formatado)", value=cpf_fmt)

        st.markdown("---")
        col_esq, col_dir = st.columns([1, 1])

        with col_esq:
            st.write("### 🏠 Endereço & Localização")
            st.text_input("Endereço 1", value=str(contato.get('ENDERECO', '')))
            bair, cid, uf = st.columns([2, 2, 1])
            bair.text_input("Bairro 1", value=str(contato.get('BAIRRO', '')))
            cid.text_input("Cidade 1", value=str(contato.get('CIDADE', '')))
            uf.text_input("Estado 1", value=str(contato.get('UF', 'MG')))
            cep, edif = st.columns([2, 2])
            cep.text_input("Cep 1", value=str(contato.get('CEP', '')))
            edif.text_input("Edifício", value=str(contato.get('EDIFICIO', '')))

            st.write("### 📝 Para quê vai usar o dinheiro / Observações")
            st.text_area("Finalidade / Observações Gerais", value=str(contato.get('COMENTARIOS_HISTORICO', '')), height=120)

            st.write("### 🏦 Bancos ou financeiras")
            st.text_area("Bancos / Financeiras", value=str(contato.get('BANCOS_FINANCEIRAS', '')), height=80)

        with col_dir:
            st.write("### 📞 Telefones & Contatos Rápidos")
            
            t1_ddd, t1_num, t1_ref = st.columns([1, 3, 2])
            t1_ddd.text_input("DDD", value=str(contato.get('DDD_TEL1', '31')))
            t1_num.text_input("Tel_1 (WhatsApp / Principal)", value=str(contato.get('TEL1', '')))
            t1_ref.text_input("Ref_1", value=str(contato.get('REF_TEL1', '')))

            t2_ddd, t2_num, t2_ref = st.columns([1, 3, 2])
            t2_ddd.text_input("DDD 2", value=str(contato.get('DDD_TEL2', '31')))
            t2_num.text_input("Tel_2", value=str(contato.get('TEL2', '')))
            t2_ref.text_input("Ref_2", value=str(contato.get('REF_TEL2', '')))

            st.text_input("Todos os Telefones Consolidados", value=str(contato.get('TELEFONES_CONSOLIDADOS', '')))

            e1, e2 = st.columns(2)
            e1.text_input("e-mail 1", value=str(contato.get('EMAIL_1', '')))
            e2.text_input("e-mail 2", value=str(contato.get('EMAIL_2', '')))
