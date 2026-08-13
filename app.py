import streamlit as st
import pandas as pd
import os
import re

st.set_page_config(page_title="ACT! Soluções", layout="wide")

# CSS para tornar a interface bem compacta e enquadrada em tela única
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; padding-left: 2rem; padding-right: 2rem; }
    div[data-baseweb="input"] { min-height: 30px; font-size: 13px; }
    label { font-size: 11px !important; font-weight: 600 !important; margin-bottom: 2px !important; }
    .stButton>button { height: 30px; padding-left: 4px; padding-right: 4px; font-size: 12px; min-width: 32px; }
    hr { margin: 6px 0px !important; }
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

if 'index' not in st.session_state:
    st.session_state.index = 0

if 'cleared_fields' not in st.session_state:
    st.session_state.cleared_fields = set()

# Cabeçalho compacto
c_head1, c_head2, c_head3 = st.columns([4, 3, 2])

with c_head1:
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
    contato = filtered_df.iloc[curr_idx].to_dict()
else:
    contato = {}
    curr_idx = 0

with c_head2:
    c_prev, c_pos, c_next = st.columns([1, 2, 1])
    if c_prev.button("◀ Anterior") and curr_idx > 0:
        st.session_state.index -= 1
        st.session_state.cleared_fields.clear()
        st.rerun()
    c_pos.markdown(f"<h5 style='text-align: center; margin-top: 5px;'><b>{curr_idx + 1} de {total_registros}</b></h5>", unsafe_allow_html=True)
    if c_next.button("Próximo ▶") and curr_idx < total_registros - 1:
        st.session_state.index += 1
        st.session_state.cleared_fields.clear()
        st.rerun()

with c_head3:
    if st.button("➕ Novo Contato", type="primary"):
        st.session_state.novo_contato = True

st.markdown("<hr>", unsafe_allow_html=True)

if total_registros == 0:
    st.warning("Nenhum contato encontrado.")
else:
    # Tratamentos de dados automáticos
    nome_completo = str(contato.get('NOME', '')).strip()
    primeiro_nome = extract_first_name(nome_completo, contato.get('PRIMEIRO_NOME', ''))
    
    tel1_val = str(contato.get('TEL1', '')).strip()
    tel_cons = str(contato.get('TELEFONES_CONSOLIDADOS', '')).strip()
    if not tel1_val and tel_cons:
        primeiro_tel = re.split(r'[,;/\|-]', tel_cons)[0].strip()
        tel1_val = primeiro_tel

    raw_cpf = clean_cpf_only_digits(contato.get('CPF_LIMPO', ''))
    cpf_fmt = format_cpf_display(raw_cpf)
    cep_fmt = format_cep_display(contato.get('CEP', ''))

    # Função auxiliar para renderizar qualquer campo com botões 📋 e 🧹
    def input_with_tools(label, value, field_id, col_spec=[5, 1, 1]):
        val = "" if field_id in st.session_state.cleared_fields else value
        c1, c2, c3 = st.columns(col_spec)
        c1.text_input(label, value=val, key=f"inp_{field_id}")
        if c2.button("📋", key=f"cp_{field_id}", help="Copiar"):
            st.toast(f"Copiado: {val}")
        if c3.button("🧹", key="cl_" + field_id, help="Limpar"):
            st.session_state.cleared_fields.add(field_id)
            st.rerun()

    # Linha 1: Identificação (com Nome equipado com 📋/🧹 e sem Indicado por)
    r1_1, r1_2, r1_3, r1_4 = st.columns([5, 2, 2, 2])
    with r1_1:
        input_with_tools("Nome", nome_completo, "nome")
    
    r1_2.text_input("1º Nome (Extraído)", value=primeiro_nome, key="f_pnome")
    r1_3.text_input("Gosta de ser chamado", value=str(contato.get('GOSTA_SER_CHAMADO', '')), key="f_chama")
    r1_4.text_input("Data da visita", value=str(contato.get('DATA_VISITA', '')), key="f_dvis")

    # Linha 2: Loja, Atendido por, Órgão, Benefício (com 📋/🧹), Espécie
    r2_1, r2_2, r2_3, r2_4, r2_5 = st.columns([2, 3, 2, 4, 2])
    r2_1.text_input("Loja", value=str(contato.get('LOJA', 'Centro - OB')), key="f_loja")
    r2_2.text_input("Atendido por", value=str(contato.get('ATENDIDO_POR', '')), key="f_atend")
    r2_3.text_input("Órgão", value=str(contato.get('ORGAO', 'INSS')), key="f_orgao")
    
    with r2_4:
        input_with_tools("Nº Benefício / Matrícula", str(contato.get('NUM_BENEFICIO', '')), "ben")
    
    r2_5.text_input("Espécie", value=str(contato.get('ESPECIE', '')), key="f_esp")

    # Linha 3: Senhas, Data Nasc, Identidade
    r3_1, r3_2, r3_3, r3_4 = st.columns([3, 3, 3, 3])
    r3_1.text_input("Senha Meu INSS", value=str(contato.get('SENHA_MEU_INSS', '')), key="f_s1")
    r3_2.text_input("Senha Paraná", value=str(contato.get('SENHA_PARANA', '')), key="f_s2")
    r3_3.text_input("Data Nascimento", value=str(contato.get('DATA_NASCIMENTO', '')), key="f_dnasc")
    r3_4.text_input("Identidade", value=str(contato.get('IDENTIDADE', '')), key="f_rg")

    # Linha 4: CPF Apenas Números e CPF Formatado
    cpf_col1, cpf_col2 = st.columns(2)
    with cpf_col1:
        input_with_tools("CPF (Apenas Números - Sem Ponto)", raw_cpf, "cpfl")
    with cpf_col2:
        input_with_tools("CPF (Formatado)", cpf_fmt, "cpff")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Linha 5: Endereço & Telefones (com CEP equipado com 📋/🧹)
    col_esq, col_dir = st.columns([1, 1])

    with col_esq:
        e1, e2, e3 = st.columns([3, 2, 1])
        e1.text_input("Endereço", value=str(contato.get('ENDERECO', '')), key="f_end")
        e2.text_input("Bairro", value=str(contato.get('BAIRRO', '')), key="f_bai")
        e3.text_input("UF", value=str(contato.get('UF', 'MG')), key="f_uf")

        c1, c2, c3 = st.columns([3, 3, 2])
        c1.text_input("Cidade", value=str(contato.get('CIDADE', '')), key="f_cid")
        
        with c2:
            input_with_tools("CEP", cep_fmt, "cep")
            
        c3.text_input("Edifício", value=str(contato.get('EDIFICIO', '')), key="f_edif")

    with col_dir:
        t1_1, t1_2, t1_3 = st.columns([1, 3, 2])
        t1_1.text_input("DDD", value=str(contato.get('DDD_TEL1', '31')), key="f_ddd1")
        
        with t1_2:
            input_with_tools("Tel_1 (Principal)", tel1_val, "t1", col_spec=[4, 1, 1])
            
        t1_3.text_input("Ref_1", value=str(contato.get('REF_TEL1', '')), key="f_ref1")

        input_with_tools("Telefones Consolidados", tel_cons, "tcons")

    # Linha 6: Observações
    st.text_area("Observações", value=str(contato.get('COMENTARIOS_HISTORICO', '')), height=65, key="f_obs")
