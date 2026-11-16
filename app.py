import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit.components.v1 as components

VERSAO_APP = "Act!   V69"

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
    """Retorna (idade_str, alerta_80_anos_bool) usando idade exata (anos, meses, dias)."""
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

    df_todos = pd.concat([df1, df2], ignore_index=True)

    col_nome = 'NAME' if 'NAME' in df_todos.columns else df_todos.columns[0]
    col_cpf = None
    for c in ['USR1000', 'CPF', 'USER1000']:
        if c in df_todos.columns:
            col_cpf = c
            break

    if col_cpf:
        df_todos['CHAVE_BUSCA'] = df_todos[col_cpf].apply(limpar_cpf)
        mask_vazio = df_todos['CHAVE_BUSCA'] == ""
        df_todos.loc[mask_vazio, 'CHAVE_BUSCA'] = df_todos.loc[mask_vazio, col_nome].str.upper().str.strip()
    else:
        df_todos['CHAVE_BUSCA'] = df_todos[col_nome].str.upper().str.strip()

    col_obs = 'USER9' if 'USER9' in df_todos.columns else ('OBSERVACOES' if 'OBSERVACOES' in df_todos.columns else df_todos.columns[1])
    col_phone = 'PHONE' if 'PHONE' in df_todos.columns else df_todos.columns[2]

    base_unificada = []
    base_quarentena = []

    for chave, group in df_todos.groupby('CHAVE_BUSCA'):
        if not chave or len(chave) < 3:
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

    df_u = pd.DataFrame(base_unificada)
    df_q = pd.DataFrame(base_quarentena)
    salvar_bases_master(df_u, df_q)
    return df_u, df_q

def get_campo(row, candidatos):
    for c in candidatos:
        if c in row.index and str(row[c]).strip() != "":
            return str(row[c]).strip()
    return ""

def garantir_coluna(df, col):
    if col not in df.columns:
        df[col] = ""

def copiar_texto_js(texto):
    """Copia para a área de transferência do navegador via JS silencioso."""
    texto_esc = str(texto).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
    components.html(f"""
        <script>
        try {{
            navigator.clipboard.writeText('{texto_esc}');
        }} catch(e) {{
            var ta = document.createElement('textarea');
            ta.value = '{texto_esc}';
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
        }}
        </script>
    """, height=0, width=0)

# -----------------------------------------------------------------------------
# 2. SEGURANÇA E TELA DE LOGIN CLÁSSICA ACT! (V69)
# -----------------------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    css_login = """
        <style>
        header, footer, [data-testid="stSidebar"], [data-testid="collapsedControl"],
        [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
            display: none !important;
        }
        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
            background-color: #808080 !important;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .main .block-container {
            padding: 0 !important;
            margin: 0 auto !important;
            max-width: 100% !important;
            min-height: 100vh !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        [data-testid="stForm"] {
            width: 286px !important;
            min-width: 286px !important;
            max-width: 286px !important;
            background-color: #D4D