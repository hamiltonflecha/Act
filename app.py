import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re

# Configuração da página em modo Wide
st.set_page_config(page_title="Act V33 - Soluções", page_icon="📑", layout="wide", initial_sidebar_state="collapsed")

# -----------------------------------------------------------------------------
# 1. SISTEMA DE SEGURANÇA E LOGIN
# -----------------------------------------------------------------------------
def verificar_senha():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🔒 Act V33 - Soluções")
            st.subheader("Acesso Restrito")
            senha_digitada = st.text_input("Digite a senha de acesso:", type="password")
            
            # Senha padrão de acesso (pode alterar aqui se desejar)
            if st.button("Entrar", use_container_width=True):
                if senha_digitada == "solucoes1986":
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Senha incorreta. Tente novamente.")
        return False
    return True

if not verificar_senha():
    st.stop()

# -----------------------------------------------------------------------------
# 2. FUNÇÕES DE TRATAMENTO DE DADOS (CPF E FUSÃO)
# -----------------------------------------------------------------------------
def limpar_cpf(val):
    if not val or pd.isna(val):
        return ""
    digitos = ''.join(filter(str.isdigit, str(val)))
    if len(digitos) >= 11:
        return digitos[-11:]
    elif len(digitos) > 0:
        return digitos.zfill(11)
    return ""

def formatar_cpf(digitos):
    if len(digitos) == 11:
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
    return digitos

@st.cache_data(ttl=3600)
def carregar_e_fundir_bases():
    try:
        df1 = pd.read_excel('DBF1_Local.xlsx', dtype=str).fillna("")
    except:
        df1 = pd.DataFrame()
        
    try:
        df2 = pd.read_excel('DBF2_Copia.xlsx', dtype=str).fillna("")
    except:
        df2 = pd.DataFrame()

    df1['ORIGEM'] = 'PC 1 (Hamilton)'
    df2['ORIGEM'] = 'PC 2 (Jaedna)'
    
    col_cpf_1 = 'USR1000' if 'USR1000' in df1.columns else ('CPF' if 'CPF' in df1.columns else df1.columns[0] if not df1.empty else '')
    col_cpf_2 = 'USR1000' if 'USR1000' in df2.columns else ('CPF' if 'CPF' in df2.columns else df2.columns[0] if not df2.empty else '')

    if not df1.empty:
        df1['CPF_LIMPO'] = df1[col_cpf_1].apply(limpar_cpf)
    if not df2.empty:
        df2['CPF_LIMPO'] = df2[col_cpf_2].apply(limpar_cpf)

    df_todos = pd.concat([df1, df2], ignore_index=True)
    if df_todos.empty:
        return pd.DataFrame(), pd.DataFrame()

    base_unificada = []
    base_quarentena = []

    col_obs = 'USER9' if 'USER9' in df_todos.columns else ('OBSERVACOES' if 'OBSERVACOES' in df_todos.columns else df_todos.columns[1])
    col_phone = 'PHONE' if 'PHONE' in df_todos.columns else df_todos.columns[2]

    for cpf, group in df_todos.groupby('CPF_LIMPO'):
        if cpf == "":
            for _, row in group.iterrows():
                base_quarentena.append(row.to_dict())
            continue
            
        if len(group) == 1:
            base_unificada.append(group.iloc[0].to_dict())
        else:
            obs_distintas = set(filter(None, group[col_obs].str.strip().tolist()))
            tels_distintos = set(filter(None, group[col_phone].str.strip().tolist()))
            
            if len(obs_distintas) <= 1 and len(tels_distintos) <= 1:
                base_unificada.append(group.iloc[-1].to_dict())
            else:
                for _, row in group.iterrows():
                    base_quarentena.append(row.to_dict())

    df_unificada = pd.DataFrame(base_unificada)
    df_quarentena = pd.DataFrame(base_quarentena)
    return df_unificada, df_quarentena

# Carregar dados
df_unificada, df_quarentena = carregar_e_fundir_bases()

# -----------------------------------------------------------------------------
# 3. INTERFACE PRINCIPAL (ABAS DE NAVEGAÇÃO)
# -----------------------------------------------------------------------------
aba_principal, aba_quarentena = st.tabs([
    "🔍 Consulta de Contatos (Base Unificada)", 
    f"⚠️ Quarentena / Revisão ({len(df_quarentena)})"
])

with aba_principal:
    st.title("Act V33 - Soluções Financeiras")
    st.markdown(f"Total de contactos consolidados e ativos: **{len(df_unificada)}**")
    
    if not df_unificada.empty:
        busca = st.text_input("Pesquisar por Nome, CPF ou Benefício:", placeholder="Digite para buscar...")
        if busca:
            resultado = df_unificada[df_unificada.astype(str).apply(lambda x: x.str.contains(busca, case=False)).any(axis=1)]
            st.dataframe(resultado, use_container_width=True)
        else:
            st.dataframe(df_unificada.head(50), use_container_width=True)
    else:
        st.warning("Nenhuma base encontrada. Verifique se os ficheiros DBF1_Local.xlsx e DBF2_Copia.xlsx estão no repositório.")

with aba_quarentena:
    st.subheader("Contatos com Divergência entre PC 1 (Hamilton) e PC 2 (Jaedna)")
    st.write("Estes registos possuem telefones ou observações diferentes nas duas máquinas:")
    if not df_quarentena.empty:
        colunas_exibir = [c for c in ['CPF_LIMPO', 'NAME', 'ORIGEM', 'USER9', 'PHONE'] if c in df_quarentena.columns]
        st.dataframe(df_quarentena[colunas_exibir], use_container_width=True)
    else:
        st.success("Nenhum contacto em quarentena! Todas as fichas foram unificadas sem divergências.")