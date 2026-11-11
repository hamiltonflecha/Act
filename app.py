import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re

st.set_page_config(page_title="Act V33 - Soluções", layout="wide", initial_sidebar_state="collapsed")

# Função de higienização de CPF (Chave Primária Absoluta)
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

# Função para carregar, fundir os 2 DBFs (Excel) e aplicar a Quarentena
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

df_unificada, df_quarentena = carregar_e_fundir_bases()

# Interface em Abas (Main App e Quarentena)
aba_principal, aba_quarentena = st.tabs(["🔍 Consulta de Contatos (Base Unificada)", f"⚠️ Quarentena / Revisão ({len(df_quarentena)})"])

with aba_principal:
    st.title("Act V33 - Soluções Financeiras")
    st.write(f"Total de contatos consolidados e ativos: **{len(df_unificada)}**")
    # Aqui renderiza a busca zeroscroll tradicional de 38px
    if not df_unificada.empty:
        busca = st.text_input("Pesquisar por Nome, CPF ou Benefício:", "")
        if busca:
            resultado = df_unificada[df_unificada.astype(str).apply(lambda x: x.str.contains(busca, case=False)).any(axis=1)]
            st.dataframe(resultado, use_container_width=True)

with aba_quarentena:
    st.subheader("Contatos com Divergência entre PC 1 e PC 2")
    st.write("Estes registros possuem telefones ou observações diferentes nas duas máquinas. Escolha a ficha correta para aprovar:")
    if not df_quarentena.empty:
        st.dataframe(df_quarentena[['CPF_LIMPO', 'NAME', 'ORIGEM', 'USER9', 'PHONE']], use_container_width=True)