Python

import streamlit as st
import pandas as pd
import re

# Configuração da página
st.set_page_config(page_title="Gerenciador de Contatos - Banco de Soluções", layout="wide")

st.title("📇 Gerenciador de Contatos Unificado")
st.caption("Base consolidada e sincronizada via GitHub / Google Drive")

# Carregar base de dados completa (4.029 contatos)
@st.cache_data
def load_data():
    return pd.read_csv("Base_Consolidada_COMPLETA_ACT.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao carregar o arquivo CSV. Verifique se 'Base_Consolidada_COMPLETA_ACT.csv' está no repositório: {e}")
    st.stop()

# Campo de busca
busca = st.text_input("🔍 Buscar Contato por CPF ou Nome:")

if busca:
    resultado = df[df['NOME'].astype(str).str.contains(busca, case=False, na=False) | df['CPF_LIMPO'].astype(str).str.contains(busca, na=False)]
    if not resultado.empty:
        contato = resultado.iloc[0]
        st.subheader(f"Contato: {contato.get('NOME', '')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Documentos")
            c1_1, c1_2, c1_3 = st.columns([6, 1, 1])
            c1_1.text_input("CPF (Formatado)", value=str(contato.get('CPF_FORMATADO', '')))
            c1_2.button("📋", key="cp_cpf_f")
            c1_3.button("🧹", key="cl_cpf_f")
            
            c2_1, c2_2, c2_3 = st.columns([6, 1, 1])
            c2_1.text_input("CPF (Apenas Números)", value=str(contato.get('CPF_LIMPO', '')))
            c2_2.button("📋", key="cp_cpf_l")
            c2_3.button("🧹", key="cl_cpf_l")

        with col2:
            st.write("### Contatos Telefônicos")
            t1_1, t1_2, t1_3 = st.columns([6, 1, 1])
            t1_1.text_input("Telefones Consolidados", value=str(contato.get('TELEFONES_CONSOLIDADOS', '')))
            t1_2.button("📋", key="cp_tel")
            t1_3.button("🧹", key="cl_tel")

        st.write("### Histórico e Observações")
        st.text_area("Observações Concatenadas", value=str(contato.get('COMENTARIOS_HISTORICO', '')), height=150)
    else:
        st.warning("Nenhum contato encontrado com o parâmetro informado.")
