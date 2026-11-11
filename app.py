import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re
import os

st.set_page_config(page_title="Act V33 - Soluções", page_icon="📑", layout="wide", initial_sidebar_state="collapsed")

# -----------------------------------------------------------------------------
# 1. SEGURANÇA E LOGIN
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
# 2. CARREGAMENTO E FUSÃO DOS DADOS
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

def ler_arquivo(nome_base):
    for ext in ['.xlsx', '.csv', '.XLSX', '.CSV']:
        caminho = f"{nome_base}{ext}"
        if os.path.exists(caminho):
            try:
                if ext.lower() == '.csv':
                    return pd.read_csv(caminho, dtype=str).fillna("")
                else:
                    return pd.read_excel(caminho, dtype=str).fillna("")
            except Exception as e:
                st.error(f"Erro ao ler {caminho}: {e}")
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def carregar_e_fundir_bases():
    df1 = ler_arquivo('DBF1_Local')
    df2 = ler_arquivo('DBF2_Copia')

    if df1.empty and df2.empty:
        return pd.DataFrame(), pd.DataFrame()

    if not df1.empty:
        df1['ORIGEM'] = 'PC 1 (Hamilton)'
        col_cpf_1 = 'USR1000' if 'USR1000' in df1.columns else ('CPF' if 'CPF' in df1.columns else df1.columns[0])
        df1['CPF_LIMPO'] = df1[col_cpf_1].apply(limpar_cpf)

    if not df2.empty:
        df2['ORIGEM'] = 'PC 2 (Jaedna)'
        col_cpf_2 = 'USR1000' if 'USR1000' in df2.columns else ('CPF' if 'CPF' in df2.columns else df2.columns[0])
        df2['CPF_LIMPO'] = df2[col_cpf_2].apply(limpar_cpf)

    df_todos = pd.concat([df1, df2], ignore_index=True)

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

    return pd.DataFrame(base_unificada), pd.DataFrame(base_quarentena)

df_unificada, df_quarentena = carregar_e_fundir_bases()

# -----------------------------------------------------------------------------
# 3. INTERFACE PRINCIPAL
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
            st.dataframe(df_unificada.head(100), use_container_width=True)
    else:
        st.warning("Nenhuma base encontrada no repositório. Verifique se os arquivos DBF1_Local e DBF2_Copia estão salvos no GitHub.")

with aba_quarentena:
    st.subheader("Contatos com Divergência entre PC 1 (Hamilton) e PC 2 (Jaedna)")
    if not df_quarentena.empty:
        colunas_exibir = [c for c in ['CPF_LIMPO', 'NAME', 'ORIGEM', 'USER9', 'PHONE'] if c in df_quarentena.columns]
        st.dataframe(df_quarentena[colunas_exibir], use_container_width=True)
    else:
        st.success("Nenhum contacto em quarentena! Todas as fichas foram unificadas sem divergências.")