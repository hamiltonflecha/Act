import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit.components.v1 as components

VERSAO_APP = "Act!   V74"

st.set_page_config(page_title=f"{VERSAO_APP} - Banco.dbf", page_icon="📑", layout="wide", initial_sidebar_state="collapsed")

ARQ_UNIFICADA = "Base_Unificada_Master.csv"
ARQ_QUARENTENA = "Base_Quarentena_Master.csv"
ARQ_TRAVA = "fusao_concluida.lock"

# -----------------------------------------------------------------------------
# 1. FUNÇÕES DE DADOS, LEITURA E PERSISTÊNCIA ÚNICA
# -----------------------------------------------------------------------------
def corrigir_acentos(texto):
    if not isinstance(texto, str) or not texto:
        return ""
    substituicoes = {
        '╔': 'É', '┴': 'Á', '├': 'Ç', '╙': 'ÃO', '├╙': 'ÇÃO',
        '═': 'Í', 'Ò': 'Â', 'Ì': 'Ê', '╘': 'Õ', '╒': 'Ô',
        '┌': 'Ú', '╓': 'Ã', '╛': 'Ü', 'Â': 'Ô', 'Õ': 'Õ'
    }
    for char_errado, char_certo in substituicoes.items():
        texto = texto.replace(char_errado, char_certo)
    return texto.strip()

def remover_acentos(texto):
    if not isinstance(texto, str) or not texto:
        return ""
    mapa = str.maketrans("ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑáàâãäéèêëíìîïóòôõöúùûüçñ",
                         "AAAAAEEEEIIIIOOOOOUUUUCNaaaaaeeeeiiiiooooouuuucn")
    return texto.translate(mapa)

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

def analisar_idade(data_nasc_str):
    if not data_nasc_str:
        return "", False
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            dt = datetime.strptime(str(data_nasc_str).strip()[:10], fmt)
            hoje = datetime.today()
            anos = hoje.year - dt.year - ((hoje.month, hoje.day) < (dt.month, dt.day))
            if anos < 0 or anos > 125:
                continue
            alerta = anos >= 80
            return str(anos), alerta
        except Exception:
            continue
    return "", False

def extrair_ddd_tel(valor_bruto):
    if not valor_bruto:
        return "", ""
    s = str(valor_bruto).strip()
    if s.startswith("(") and ")" in s:
        ddd = ''.join(filter(str.isdigit, s[1:s.find(")")]))
        num = ''.join(filter(str.isdigit, s[s.find(")")+1:]))
        return ddd, num
    digitos = ''.join(filter(str.isdigit, s))
    if len(digitos) >= 10:
        return digitos[:2], digitos[2:]
    return "", digitos

def ler_arquivo(nome_base):
    for ext in ['.xlsx', '.csv', '.XLSX', '.CSV']:
        caminho = f"{nome_base}{ext}"
        if os.path.exists(caminho):
            try:
                if ext.lower() == '.csv':
                    df = pd.read_csv(caminho, dtype=str).fillna("")
                else:
                    df = pd.read_excel(caminho, dtype=str).fillna("")
                for col in df.columns:
                    df[col] = df[col].astype(str).apply(corrigir_acentos)
                return df
            except Exception as e:
                st.error(f"Erro ao ler {caminho}: {e}")
    return pd.DataFrame()

def salvar_bases_master(df_u, df_q):
    df_u.to_csv(ARQ_UNIFICADA, index=False, encoding="utf-8-sig")
    df_q.to_csv(ARQ_QUARENTENA, index=False, encoding="utf-8-sig")
    with open(ARQ_TRAVA, "w", encoding="utf-8") as f:
        f.write("UNIFICADO=TRUE")

def carregar_bases_master():
    if os.path.exists(ARQ_UNIFICADA):
        df_u = pd.read_csv(ARQ_UNIFICADA, dtype=str).fillna("")
    else:
        df_u = pd.DataFrame()
    if os.path.exists(ARQ_QUARENTENA):
        df_q = pd.read_csv(ARQ_QUARENTENA, dtype=str).fillna("")
    else:
        df_q = pd.DataFrame()
    return df_u, df_q

def executar_fusao_unica():
    df1 = ler_arquivo('DBF1_Local')
    df2 = ler_arquivo('DBF2_Copia')

    if df1.empty and df2.empty:
        return pd.DataFrame(), pd.DataFrame()

    if not df1.empty:
        df1['ORIGEM'] = 'PC 1 (Hamilton)'
    if not df2.empty:
        df2['ORIGEM'] = 'PC 2 (Jaedna)'

    df_todos = pd.concat([df1, df2], ignore_index