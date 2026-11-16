import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit.components.v1 as components

VERSAO_APP = "Act!   V73"

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
# 2. SEGURANÇA E TELA DE LOGIN CLÁSSICA ACT! (V73)
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
            background-color: #D4D0C8 !important;
            border-radius: 0px !important;
            border-top: 1px solid #FFFFFF !important;
            border-left: 1px solid #FFFFFF !important;
            border-right: 1px solid #404040 !important;
            border-bottom: 1px solid #404040 !important;
            box-shadow: inset 1px 1px 0px #D4D0C8, inset -1px -1px 0px #808080, 1px 1px 0px #000000 !important;
            padding: 3px 3px 14px 3px !important;
            margin: 0 auto !important;
            box-sizing: border-box !important;
        }
        [data-testid="stForm"] [data-testid="stVerticalBlock"] { gap: 0px !important; overflow: visible !important; }
        [data-testid="stForm"] [data-testid="stElementContainer"],
        [data-testid="stForm"] [data-testid="stMarkdownContainer"] { margin: 0 !important; padding: 0 !important; overflow: visible !important; }
        [data-testid="stForm"] [data-testid="stMarkdownContainer"] p { margin: 0 !important; padding: 0 !important; overflow: visible !important; }
        .act-titlebar {
            background: linear-gradient(90deg, #0A246A 0%, #A6CAF0 100%);
            color: #FFFFFF;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif;
            font-weight: bold;
            font-size: 11px;
            height: 18px;
            padding: 0 2px 0 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 0 0 12px 0;
            width: 100%;
            box-sizing: border-box;
        }
        .act-close-btn {
            background-color: #D4D0C8;
            color: #000000;
            border-top: 1px solid #FFFFFF;
            border-left: 1px solid #FFFFFF;
            border-right: 1px solid #404040;
            border-bottom: 1px solid #404040;
            box-shadow: inset -1px -1px 0px #808080;
            font-size: 10px;
            font-weight: bold;
            width: 15px;
            height: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1;
        }
        .act-label {
            color: #000000;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif;
            font-size: 11px;
            line-height: 16px;
            padding: 2px 11px 4px 11px;
            margin: 0;
            display: block;
            white-space: nowrap;
        }
        .act-label-pass { padding-top: 10px; }
        [data-testid="stForm"] [data-testid="stTextInput"] { padding: 0 11px !important; margin: 0 !important; width: 100% !important; box-sizing: border-box !important; }
        [data-testid="stForm"] [data-testid="stTextInput"] label { display: none !important; }
        [data-testid="stForm"] [data-testid="stTextInput"] > div,
        [data-testid="stForm"] [data-testid="stTextInput"] > div > div {
            background: transparent !important; border: none !important; border-radius: 0px !important; box-shadow: none !important; padding: 0 !important; min-height: 0 !important;
        }
        [data-testid="stForm"] [data-testid="stTextInput"] input {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border-radius: 0px !important;
            border-top: 1px solid #808080 !important;
            border-left: 1px solid #808080 !important;
            border-right: 1px solid #FFFFFF !important;
            border-bottom: 1px solid #FFFFFF !important;
            box-shadow: inset 1px 1px 0px #404040, inset -1px -1px 0px #D4D0C8 !important;
            height: 20px !important;
            min-height: 20px !important;
            max-height: 20px !important;
            padding: 1px 4px !important;
            font-size: 11px !important;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important;
        }
        [data-testid="stForm"] [data-testid="stTextInput"] button,
        [data-testid="stForm"] [data-testid="InputInstructions"] { display: none !important; }
        [data-testid="stForm"] [data-testid="stCheckbox"] { padding: 11px 11px 13px 11px !important; margin: 0 !important; }
        [data-testid="stForm"] [data-testid="stCheckbox"] label { display: flex !important; align-items: center !important; gap: 6px !important; min-height: 0 !important; }
        [data-testid="stForm"] [data-testid="stCheckbox"] label > span:first-child,
        [data-testid="stForm"] [data-testid="stCheckbox"] [data-baseweb="checkbox"] > span:first-child,
        [data-testid="stForm"] [data-testid="stCheckbox"] [data-baseweb="checkbox"] > div:first-child {
            width: 13px !important; height: 13px !important; min-width: 13px !important; min-height: 13px !important; max-width: 13px !important; max-height: 13px !important;
            border-radius: 0px !important; background-color: #FFFFFF !important;
            border-top: 1px solid #808080 !important; border-left: 1px solid #808080 !important; border-right: 1px solid #FFFFFF !important; border-bottom: 1px solid #FFFFFF !important;
            box-shadow: inset 1px 1px 0px #404040 !important;
        }
        [data-testid="stForm"] [data-testid="stCheckbox"] svg { fill: #000000 !important; color: #000000 !important; stroke: #000000 !important; width: 10px !important; height: 10px !important; }
        [data-testid="stForm"] [data-testid="stCheckbox"] label p { color: #000000 !important; font-size: 11px !important; font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important; margin: 0 !important; }
        [data-testid="stForm"] [data-testid="stCheckbox"] label p::first-letter { text-decoration: underline !important; }
        [data-testid="stForm"] [data-testid="stHorizontalBlock"] {
            display: flex !important; flex-direction: row !important; justify-content: center !important; align-items: center !important; gap: 10px !important; padding: 0 40px !important; width: 100% !important;
        }
        [data-testid="stForm"] [data-testid="stHorizontalBlock"] > div { width: 75px !important; min-width: 75px !important; max-width: 75px !important; flex: 0 0 75px !important; padding: 0 !important; }
        [data-testid="stForm"] button {
            background-color: #D4D0C8 !important; color: #000000 !important; border-radius: 0px !important;
            border-top: 1px solid #FFFFFF !important; border-left: 1px solid #FFFFFF !important; border-right: 1px solid #404040 !important; border-bottom: 1px solid #404040 !important;
            box-shadow: inset -1px -1px 0px #808080 !important; height: 22px !important; min-height: 22px !important; max-height: 22px !important; width: 75px !important; font-size: 11px !important;
        }
        [data-testid="stForm"] [data-testid="stHorizontalBlock"] > div:first-child button {
            border: 1px solid #000000 !important; box-shadow: inset 1px 1px 0px #FFFFFF, inset -1px -1px 0px #404040, inset -2px -2px 0px #808080 !important;
        }
        [data-testid="stForm"] [data-testid="stHorizontalBlock"] > div:nth-child(2) button p::first-letter { text-decoration: underline !important; }
        [data-testid="stForm"] button p { font-size: 11px !important; color: #000000 !important; margin: 0 !important; }
        .act-msg-erro { color: #800000; font-size: 11px; text-align: center; padding-top: 8px; }
        </style>
    """
    st.markdown(css_login, unsafe_allow_html=True)

    with st.form("form_login_act", border=False):
        st.markdown(f"""
            <div class="act-titlebar">
                <span style="white-space: pre;">{VERSAO_APP}</span>
                <span class="act-close-btn">×</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="act-label">Digite seu nome de <u>u</u>suário:</div>', unsafe_allow_html=True)
        user_input = st.text_input("user_label", value="Hamilton Flecha", key="user_key", label_visibility="collapsed")

        st.markdown('<div class="act-label act-label-pass">Digite sua <u>s</u>enha para este banco de dados:</div>', unsafe_allow_html=True)
        senha_input = st.text_input("pass_label", type="password", key="pass_key", label_visibility="collapsed")

        st.checkbox("Lembrar senha", value=True, key="rem_key")

        b_ok, b_cancel = st.columns(2)
        with b_ok:
            btn_ok = st.form_submit_button("OK")
        with b_cancel:
            btn_cancel = st.form_submit_button("Cancelar")

        if btn_ok:
            if senha_input.strip() == "solucoes1986":
                st.session_state["autenticado"] = True
                st.session_state["operador_atual"] = user_input
                st.rerun()
            else:
                st.markdown('<div class="act-msg-erro">Senha inválida para Banco.dbf.</div>', unsafe_allow_html=True)
        if btn_cancel:
            st.markdown('<div class="act-msg-erro">Entrada cancelada.</div>', unsafe_allow_html=True)

    st.stop()

# -----------------------------------------------------------------------------
# 3. ESTADO E CONTROLE DE LOOKUP ACT! (V73)
# -----------------------------------------------------------------------------
ja_unificado = os.path.exists(ARQ_TRAVA) and os.path.exists(ARQ_UNIFICADA)

if "df_unificada" not in st.session_state:
    if ja_unificado:
        st.session_state["df_unificada"], st.session_state["df_quarentena"] = carregar_bases_master()
    else:
        st.session_state["df_unificada"] = pd.DataFrame()
        st.session_state["df_quarentena"] = pd.DataFrame()

if "idx_cliente" not in st.session_state:
    st.session_state["idx_cliente"] = 0

if "visao_ativa" not in st.session_state:
    st.session_state["visao_ativa"] = "ficha"

if "confirmar_nova_fusao" not in st.session_state:
    st.session_state["confirmar_nova_fusao"] = False

if "confirmar_exclusao" not in st.session_state:
    st.session_state["confirmar_exclusao"] = False

if "lookup_indices" not in st.session_state:
    st.session_state["lookup_indices"] = None
if "lookup_termo" not in st.session_state:
    st.session_state["lookup_termo"] = ""
if "lookup_modal_aberto" not in st.session_state:
    st.session_state["lookup_modal_aberto"] = False
if "lookup_candidatos" not in st.session_state:
    st.session_state["lookup_candidatos"] = []

df_unificada = st.session_state["df_unificada"]
df_quarentena = st.session_state["df_quarentena"]

if st.session_state["lookup_indices"] is not None and not df_unificada.empty:
    validos = [i for i in st.session_state["lookup_indices"] if i in df_unificada.index]
    df_ativo = df_unificada.loc[validos]
else:
    df_ativo = df_unificada

total_registros = len(df_ativo)
if total_registros > 0 and st.session_state["idx_cliente"] >= total_registros:
    st.session_state["idx_cliente"] = max(0, total_registros - 1)
elif total_registros == 0:
    st.session_state["idx_cliente"] = 0

alerta_idade_80 = False
if total_registros > 0 and st.session_state["visao_ativa"] == "ficha":
    cli_temp = df_ativo.iloc[st.session_state["idx_cliente"]]
    nasc_temp = get_campo(cli_temp, ['USER1', 'BIRTHDATE', 'NASCIMENTO', 'DATA_NASC'])
    _, alerta_idade_80 = analisar_idade(nasc_temp)

# -----------------------------------------------------------------------------
# 4. CSS CLÁSSICO ACT! V73 (ALTA DENSIDADE VERTICAL — CABE SEM ROLAGEM)
# -----------------------------------------------------------------------------
cor_idade_bg = "#CC0000" if alerta_idade_80 else "#FFFFFF"
cor_idade_fg = "#FFFFFF" if alerta_idade_80 else "#000000"
cor_idade_bd = "#800000" if alerta_idade_80 else "#7A7265"

css_act_v73 = f"""
    <style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="InputInstructions"] {{
        display: none !important;
    }}

    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {{
        background-color: #9E9382 !important;
        font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important;
        color: #000000 !important;
        overflow-x: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    .main .block-container {{
        max-width: 990px !important;
        width: 990px !important;
        padding: 2px 6px 2px 6px !important;
        margin: 0 auto !important;
        box-sizing: border-box !important;
    }}

    [data-testid="stVerticalBlock"] {{
        gap: 0px !important;
    }}
    [data-testid="stElementContainer"] {{
        margin: 0 !important;
        padding: 0 !important;
        overflow: visible !important;
    }}
    [data-testid="stHorizontalBlock"] {{
        gap: 4px !important;
        align-items: flex-end !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    [data-testid="stMarkdownContainer"] {{
        margin: 0 !important;
        padding: 0 !important;
        overflow: visible !important;
    }}
    .act-lbl {{
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        font-size: 10px !important;
        font-weight: normal !important;
        color: #000000 !important;
        line-height: 11px !important;
        min-height: 11px !important;
        height: 11px !important;
        margin: 1px 0 0 0 !important;
        padding: 0 !important;
        white-space: nowrap !important;
        overflow: visible !important;
    }}
    .act-lbl-zap {{
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        font-size: 10px !important;
        font-weight: bold !important;
        color: #004400 !important;
        line-height: 11px !important;
        min-height: 11px !important;
        height: 11px !important;
        margin: 1px 0 0 0 !important;
        padding: 0 !important;
        text-align: center !important;
    }}

    [data-testid="stTextInput"] label {{
        display: none !important;
    }}
    [data-testid="stTextInput"] > div,
    [data-testid="stTextInput"] > div > div {{
        background: transparent !important;
        border: none !important;
        border-radius: 0px !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        min-height: 18px !important;
        height: 18px !important;
    }}
    [data-testid="stTextInput"] input {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border-radius: 1px !important;
        border: 1px solid #6E6659 !important;
        height: 18px !important;
        min-height: 18px !important;
        max-height: 18px !important;
        padding: 0px 4px !important;
        margin: 0 !important;
        font-size: 11px !important;
        font-family: 'Tahoma', Arial, sans-serif !important;
        line-height: 16px !important;
        opacity: 1 !important;
        box-sizing: border-box !important;
    }}
    [data-testid="stTextInput"] input:focus {{
        border: 1px solid #0A246A !important;
        background-color: #FFFFEE !important;
    }}

    [data-testid="stTextInput"] input[aria-label="cnt_box"] {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        text-align: center !important;
        font-weight: normal !important;
        border-top: 1px solid #808080 !important;
        border-left: 1px solid #808080 !important;
        border-right: 1px solid #FFFFFF !important;
        border-bottom: 1px solid #FFFFFF !important;
        cursor: default !important;
        padding: 0 2px !important;
    }}

    [data-testid="stTextInput"] input[aria-label="lk_cell"] {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: 1px solid #808080 !important;
        cursor: default !important;
        padding: 0 4px !important;
    }}

    [data-testid="stTextInput"] input[aria-label="f_idade"] {{
        background-color: {cor_idade_bg} !important;
        color: {cor_idade_fg} !important;
        -webkit-text-fill-color: {cor_idade_fg} !important;
        border: 1px solid {cor_idade_bd} !important;
        font-weight: {'bold' if alerta_idade_80 else 'normal'} !important;
        text-align: center !important;
    }}

    [data-testid="stTextArea"] label {{
        display: none !important;
    }}
    [data-testid="stTextArea"] textarea {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border-radius: 1px !important;
        border: 1px solid #6E6659 !important;
        font-size: 11px !important;
        font-family: 'Tahoma', Arial, sans-serif !important;
        padding: 1px 4px !important;
        line-height: 12px !important;
        opacity: 1 !important;
    }}

    [data-testid="stButton"] button {{
        background-color: #D4D0C8 !important;
        color: #000000 !important;
        border-radius: 1px !important;
        border-top: 1px solid #FFFFFF !important;
        border-left: 1px solid #FFFFFF !important;
        border-right: 1px solid #404040 !important;
        border-bottom: 1px solid #404040 !important;
        height: 18px !important;
        min-height: 18px !important;
        max-height: 18px !important;
        padding: 0 4px !important;
        font-size: 10.5px !important;
        font-family: 'Tahoma', Arial, sans-serif !important;
        line-height: 16px !important;
        margin: 0 !important;
        box-sizing: border-box !important;
    }}
    [data-testid="stButton"] button:hover {{
        background-color: #E4E0D8 !important;
    }}
    [data-testid="stButton"] button p {{
        font-size: 10.5px !important;
        color: #000000 !important;
        margin: 0 !important;
        line-height: 16px !important;
        white-space: nowrap !important;
    }}
    [data-testid="stButton"] button[kind="primary"] {{
        background-color: #C6D9F1 !important;
        border: 1px solid #0A246A !important;
        font-weight: bold !important;
    }}

    /* Caixa de Sexo (M / F) compacta (18px de altura) */
    [data-testid="stRadio"] {{
        margin: 0 !important;
        padding: 0 !important;
        height: 18px !important;
        min-height: 18px !important;
        max-height: 18px !important;
        overflow: hidden !important;
    }}
    [data-testid="stRadio"] > label {{
        display: none !important;
    }}
    [data-testid="stRadio"] [role="radiogroup"] {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        gap: 6px !important;
        align-items: center !important;
        height: 18px !important;
        min-height: 18px !important;
        max-height: 18px !important;
        background-color: #D4D0C8 !important;
        border: 1px solid #6E6659 !important;
        padding: 0 6px !important;
        margin: 0 !important;
        box-sizing: border-box !important;
    }}
    [data-testid="stRadio"] [role="radiogroup"] label {{
        display: flex !important;
        align-items: center !important;
        margin: 0 !important;
        padding: 0 !important;
        gap: 4px !important;
        height: 16px !important;
        min-height: 16px !important;
        max-height: 16px !important;
    }}
    [data-testid="stRadio"] [role="radiogroup"] label > div:first-child {{
        width: 11px !important;
        height: 11px !important;
        min-width: 11px !important;
        min-height: 11px !important;
        max-width: 11px !important;
        max-height: 11px !important;
        margin: 0 !important;
    }}
    [data-testid="stRadio"] [role="radiogroup"] label p {{
        font-size: 10.5px !important;
        color: #000000 !important;
        margin: 0 !important;
        line-height: 15px !important;
    }}

    [data-testid="stCheckbox"] {{
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        height: 18px !important;
    }}
    [data-testid="stCheckbox"] label {{
        gap: 3px !important;
        min-height: 0 !important;
        margin: 0 !important;
    }}
    [data-testid="stCheckbox"] label p {{
        font-size: 10px !important;
        color: #000000 !important;
        margin: 0 !important;
    }}

    .act-lookup-box {{
        background-color: #D4D0C8;
        border-top: 2px solid #FFFFFF;
        border-left: 2px solid #FFFFFF;
        border-right: 2px solid #404040;
        border-bottom: 2px solid #404040;
        padding: 3px 6px 4px 6px;
        margin: 2px 0;
    }}
    .act-lookup-title {{
        background: linear-gradient(90deg, #0A246A 0%, #A6CAF0 100%);
        color: #FFFFFF;
        font-size: 11px;
        font-weight: bold;
        padding: 1px 6px;
        margin-bottom: 2px;
    }}

    .act-hr {{
        border: none;
        border-top: 1px solid #6E6659;
        border-bottom: 1px solid #B5AC9D;
        margin: 2px 0 1px 0;
        height: 2px;
    }}

    .act-statusbar {{
        background-color: #D4D0C8;
        border-top: 1px solid #808080;
        padding: 1px 6px;
        font-size: 10px;
        color: #000000;
        display: flex;
        justify-content: space-between;
        margin-top: 2px;
    }}
    </style>
"""
st.markdown(css_act_v73, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. BARRA ÚNICA SUPERIOR (990px, WIDGETS NATIVOS ALINHADOS AO PIXEL)
# -----------------------------------------------------------------------------
pos_display = 0 if total_registros == 0 else (st.session_state["idx_cliente"] + 1)

(
    b_first, b_prev, b_cnt, b_next, b_last,
    b_loc_in, b_loc_go, b_all,
    b_novo, b_excluir,
    b_v_ficha, b_v_tab, b_v_quar, b_v_camp,
    b_unif, b_sair
) = st.columns([0.36, 0.36, 1.05, 0.36, 0.36, 1.45, 0.62, 0.58, 0.58, 0.65, 0.58, 0.62, 0.95, 0.65, 1.05, 0.48], vertical_alignment="center")

with b_first:
    if st.button("|<", use_container_width=True, help="Primeiro registro"):
        st.session_state["idx_cliente"] = 0
        st.session_state["visao_ativa"] = "ficha"
        st.rerun()

with b_prev:
    if st.button("<", use_container_width=True, help="Registro anterior"):
        if st.session_state["idx_cliente"] > 0:
            st.session_state["idx_cliente"] -= 1
            st.session_state["visao_ativa"] = "ficha"
            st.rerun()

with b_cnt:
    st.text_input("cnt_box", value=f"{pos_display} de {total_registros}", disabled=True, label_visibility="collapsed", key=f"cnt_top_{pos_display}_{total_registros}")

with b_next:
    if st.button(">", use_container_width=True, help="Próximo registro"):
        if st.session_state["idx_cliente"] < total_registros - 1:
            st.session_state["idx_cliente"] += 1
            st.session_state["visao_ativa"] = "ficha"
            st.rerun()

with b_last:
    if st.button(">|", use_container_width=True, help="Último registro"):
        if total_registros > 0:
            st.session_state["idx_cliente"] = total_registros - 1
            st.session_state["visao_ativa"] = "ficha"
            st.rerun()

with b_loc_in:
    termo_lookup_input = st.text_input("lookup_box", value=st.session_state["lookup_termo"], placeholder="Localizar...", label_visibility="collapsed", key="inp_lookup_top")

with b_loc_go:
    if st.button("Buscar", use_container_width=True, help="Pesquisar string em todos os campos"):
        q = termo_lookup_input.strip()
        if q and not df_unificada.empty:
            mask = df_unificada.astype(str).apply(lambda col: col.str.contains(q, case=False, regex=False)).any(axis=1)
            encontrados = df_unificada[mask].index.tolist()
            st.session_state["lookup_termo"] = q
            st.session_state["lookup_candidatos"] = encontrados
            st.session_state["lookup_modal_aberto"] = True
            st.session_state["visao_ativa"] = "ficha"
            st.rerun()

with b_all:
    lbl_todos = f"Lookup({len(st.session_state['lookup_indices'])})" if st.session_state["lookup_indices"] is not None else "Todos"
    if st.button(lbl_todos, use_container_width=True, type="primary" if st.session_state["lookup_indices"] is not None else "secondary", help="Reabrir lista do Lookup ativo ou mostrar todos"):
        if st.session_state["lookup_indices"] is not None and not st.session_state["lookup_modal_aberto"]:
            st.session_state["lookup_modal_aberto"] = True
            st.rerun()
        else:
            st.session_state["lookup_indices"] = None
            st.session_state["lookup_termo"] = ""
            st.session_state["lookup_modal_aberto"] = False
            st.session_state["idx_cliente"] = 0
            st.rerun()

with b_novo:
    if st.button("Novo", use_container_width=True, help="Inserir novo contato em branco"):
        nova_linha = {col: "" for col in df_unificada.columns} if not df_unificada.empty else {}
        nova_linha["NAME"] = "NOVO CONTATO"
        nova_linha["COMPANY"] = "INSS"
        nova_linha["USER2"] = "Centro - OB"
        nova_linha["ORIGEM"] = f"Inserido ({st.session_state.get('operador_atual', 'Hamilton')})"
        df_unificada = pd.concat([df_unificada, pd.DataFrame([nova_linha])], ignore_index=True)
        st.session_state["df_unificada"] = df_unificada
        salvar_bases_master(df_unificada, df_quarentena)
        st.session_state["lookup_indices"] = None
        st.session_state["lookup_modal_aberto"] = False
        st.session_state["idx_cliente"] = len(df_unificada) - 1
        st.session_state["visao_ativa"] = "ficha"
        st.rerun()

with b_excluir:
    if st.button("Excluir", use_container_width=True, help="Excluir contato atual") and total_registros > 0:
        st.session_state["confirmar_exclusao"] = True
        st.rerun()

with b_v_ficha:
    if st.button("Ficha", use_container_width=True, type="primary" if st.session_state["visao_ativa"] == "ficha" else "secondary"):
        st.session_state["visao_ativa"] = "ficha"
        st.rerun()

with b_v_tab:
    if st.button("Tabela", use_container_width=True, type="primary" if st.session_state["visao_ativa"] == "tabela" else "secondary"):
        st.session_state["visao_ativa"] = "tabela"
        st.rerun()

with b_v_quar:
    if st.button(f"Quarent({len(df_quarentena)})", use_container_width=True, type="primary" if st.session_state["visao_ativa"] == "quarentena" else "secondary"):
        st.session_state["visao_ativa"] = "quarentena"
        st.rerun()

with b_v_camp:
    if st.button("Campos", use_container_width=True, type="primary" if st.session_state["visao_ativa"] == "todos_campos" else "secondary"):
        st.session_state["visao_ativa"] = "todos_campos"
        st.rerun()

with b_unif:
    if not ja_unificado:
        if st.button("Unificar", type="primary", use_container_width=True, help="Executar unificação única"):
            u, q = executar_fusao_unica()
            st.session_state["df_unificada"] = u
            st.session_state["df_quarentena"] = q
            st.session_state["idx_cliente"] = 0
            st.rerun()
    else:
        if not st.session_state["confirmar_nova_fusao"]:
            if st.button("Travada", use_container_width=True, help="Base Master travada. Clique para destravar."):
                st.session_state["confirmar_nova_fusao"] = True
                st.rerun()
        else:
            if st.button("Confirmar?", type="primary", use_container_width=True):
                u, q = executar_fusao_unica()
                st.session_state["df_unificada"] = u
                st.session_state["df_quarentena"] = q
                st.session_state["idx_cliente"] = 0
                st.session_state["confirmar_nova_fusao"] = False
                st.rerun()

with b_sair:
    if st.button("Sair", use_container_width=True):
        st.session_state["autenticado"] = False
        st.rerun()

if st.session_state["confirmar_exclusao"] and total_registros > 0:
    ex_msg, ex_sim, ex_nao = st.columns([6, 1, 1], vertical_alignment="center")
    with ex_msg:
        st.markdown(f'<div style="background:#FFF3CD; border:1px solid #806600; padding:1px 6px; font-size:11px;">Confirma a exclusão definitiva de <b>{df_ativo.iloc[st.session_state["idx_cliente"]].get("NAME", "")}</b>?</div>', unsafe_allow_html=True)
    with ex_sim:
        if st.button("Sim, Excluir", type="primary", use_container_width=True):
            idx_del = df_ativo.iloc[st.session_state["idx_cliente"]].name
            df_unificada = df_unificada.drop(index=idx_del).reset_index(drop=True)
            st.session_state["df_unificada"] = df_unificada
            salvar_bases_master(df_unificada, df_quarentena)
            st.session_state["lookup_indices"] = None
            st.session_state["confirmar_exclusao"] = False
            st.session_state["idx_cliente"] = max(0, st.session_state["idx_cliente"] - 1)
            st.rerun()
    with ex_nao:
        if st.button("Cancelar", use_container_width=True):
            st.session_state["confirmar_exclusao"] = False
            st.rerun()

st.markdown('<hr class="act-hr">', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. JANELA DE RESULTADOS DO LOOKUP ACT! (APENAS NOME + CPF + ABRIR, -50% LARGURA)
# -----------------------------------------------------------------------------
if st.session_state["lookup_modal_aberto"]:
    cand_indices = [i for i in st.session_state["lookup_candidatos"] if i in df_unificada.index]
    st.markdown(f"""
        <div class="act-lookup-box">
            <div class="act-lookup-title">Lookup ACT! — Resultados para "{st.session_state['lookup_termo']}" ({len(cand_indices)} encontrados) — Clique em Abrir para carregar a ficha</div>
        </div>
    """, unsafe_allow_html=True)

    lk_top1, lk_top2, lk_top3 = st.columns([5, 1.5, 1.5], vertical_alignment="center")
    with lk_top1:
        st.markdown('<div style="font-size:11px;">Colunas exibidas: <b>Nome | CPF</b></div>', unsafe_allow_html=True)
    with lk_top2:
        if st.button("Limpar Lookup (Ver Todos)", use_container_width=True):
            st.session_state["lookup_indices"] = None
            st.session_state["lookup_termo"] = ""
            st.session_state["lookup_modal_aberto"] = False
            st.session_state["idx_cliente"] = 0
            st.rerun()
    with lk_top3:
        if st.button("Fechar Janela", use_container_width=True):
            st.session_state["lookup_modal_aberto"] = False
            st.rerun()

    if len(cand_indices) == 0:
        st.warning(f"Nenhum registro encontrado contendo '{st.session_state['lookup_termo']}'.")
    else:
        h1, h2, h3, _ = st.columns([1.5, 0.6, 0.4, 6.2], vertical_alignment="center")
        h1.markdown('<div class="act-lbl"><b>Nome</b></div>', unsafe_allow_html=True)
        h2.markdown('<div class="act-lbl"><b>CPF</b></div>', unsafe_allow_html=True)
        h3.markdown('<div class="act-lbl"><b>Ação</b></div>', unsafe_allow_html=True)

        for pos_lk, idx_real_lk in enumerate(cand_indices[:30]):
            r_lk = df_unificada.loc[idx_real_lk]
            c1, c2, c3, _ = st.columns([1.5, 0.6, 0.4, 6.2], vertical_alignment="center")
            with c1:
                st.text_input("lk_cell", value=get_campo(r_lk, ["NAME"]), disabled=True, label_visibility="collapsed", key=f"lk_c1_{idx_real_lk}")
            with c2:
                st.text_input("lk_cell", value=limpar_cpf(get_campo(r_lk, ["USR1000", "CPF"])), disabled=True, label_visibility="collapsed", key=f"lk_c2_{idx_real_lk}")
            with c3:
                if st.button("Abrir", key=f"open_lk_{idx_real_lk}", use_container_width=True):
                    st.session_state["lookup_indices"] = cand_indices
                    st.session_state["idx_cliente"] = pos_lk
                    st.session_state["lookup_modal_aberto"] = False
                    st.session_state["visao_ativa"] = "ficha"
                    st.rerun()

# -----------------------------------------------------------------------------
# 7. VISÃO PRINCIPAL: FICHA ACT! V73
# -----------------------------------------------------------------------------
elif st.session_state["visao_ativa"] == "ficha":
    if total_registros > 0:
        cliente = df_ativo.iloc[st.session_state["idx_cliente"]]
        real_idx = cliente.name

        nome_val = get_campo(cliente, ['NAME', 'NOME'])
        sexo_raw = get_campo(cliente, ['SEXO', 'GENDER']).upper()
        sexo_val = "F" if sexo_raw.startswith("F") else "M"
        primeiro_nome = nome_val.split()[0] if nome_val else ""
        apelido_val = get_campo(cliente, ['FIRST_NAME', 'SALUTATION', 'APELIDO'])
        data_visita_val = get_campo(cliente, ['LAST_REACH', 'USER5', 'DATA_VISITA'])
        nome_sem_acento = remover_acentos(nome_val)

        cpf_bruto = get_campo(cliente, ['USR1000', 'CPF', 'USER1000'])
        cpf_limpo = limpar_cpf(cpf_bruto)
        cpf_fmt = formatar_cpf(cpf_limpo)

        data_nasc_val = get_campo(cliente, ['USER1', 'BIRTHDATE', 'NASCIMENTO', 'DATA_NASC'])
        idade_val, _ = analisar_idade(data_nasc_val)
        if not idade_val:
            idade_val = get_campo(cliente, ['USER4', 'IDADE'])

        orgao1_val = get_campo(cliente, ['COMPANY', 'ORGAO', 'USER3']) or "INSS"
        esp1_val = get_campo(cliente, ['USER8', 'ESPECIE', 'TITLE'])
        ben1_val = get_campo(cliente, ['ID_STAT', 'BENEFICIO', 'USER7', 'MATRICULA'])

        orgao2_val = get_campo(cliente, ['ORGAO_2'])
        esp2_val = get_campo(cliente, ['ESPECIE_2'])
        ben2_val = get_campo(cliente, ['BENEFICIO_2'])

        orgao3_val = get_campo(cliente, ['ORGAO_3'])
        esp3_val = get_campo(cliente, ['ESPECIE_3'])
        ben3_val = get_campo(cliente, ['BENEFICIO_3'])

        resumo_val = f"{orgao1_val} {nome_sem_acento} {cpf_limpo} {idade_val}".strip()

        loja_val = get_campo(cliente, ['USER2', 'LOJA', 'DEPARTMENT']) or "Centro - OB"
        atendido_val = get_campo(cliente, ['USER6', 'ATENDIDO_POR', 'MANAGER'])
        senha_inss_val = get_campo(cliente, ['USER10', 'SENHA_INSS'])
        senha_parana_val = get_campo(cliente, ['USER11', 'SENHA_PARANA'])
        identidade_val = get_campo(cliente, ['USER12', 'IDENTIDADE', 'RG'])

        end1_val = get_campo(cliente, ['ADDR1', 'ENDERECO'])
        bairro1_val = get_campo(cliente, ['ADDR3', 'BAIRRO'])
        estado1_val = get_campo(cliente, ['STATE', 'UF'])
        cidade1_val = get_campo(cliente, ['CITY', 'CIDADE'])
        cep1_val = get_campo(cliente, ['ZIP', 'CEP'])
        edificio_val = get_campo(cliente, ['ADDR2', 'EDIFICIO'])

        ddd1_val, tel1_val = extrair_ddd_tel(get_campo(cliente, ['PHONE', 'TELEFONE']))
        if get_campo(cliente, ['DDD_1']):
            ddd1_val = get_campo(cliente, ['DDD_1'])
        if get_campo(cliente, ['TEL_1']):
            tel1_val = get_campo(cliente, ['TEL_1'])
        zap1_val = get_campo(cliente, ['ZAP_1']) == "Sim"
        ref1_val = get_campo(cliente, ['REF_1'])

        ddd2_val, tel2_val = extrair_ddd_tel(get_campo(cliente, ['HOME_PHONE', 'ALT_PHONE', 'TEL_2']))
        if get_campo(cliente, ['DDD_2']):
            ddd2_val = get_campo(cliente, ['DDD_2'])
        if get_campo(cliente, ['TEL_2']):
            tel2_val = get_campo(cliente, ['TEL_2'])
        zap2_val = get_campo(cliente, ['ZAP_2']) == "Sim"
        ref2_val = get_campo(cliente, ['REF_2'])

        ddd3_val, tel3_val = extrair_ddd_tel(get_campo(cliente, ['MOBILE_PHONE', 'TEL_3']))
        if get_campo(cliente, ['DDD_3']):
            ddd3_val = get_campo(cliente, ['DDD_3'])
        if get_campo(cliente, ['TEL_3']):
            tel3_val = get_campo(cliente, ['TEL_3'])
        zap3_val = get_campo(cliente, ['ZAP_3']) == "Sim"
        ref3_val = get_campo(cliente, ['REF_3'])

        obs_val = get_campo(cliente, ['USER9', 'OBSERVACOES'])
    else:
        real_idx = "vazio"
        nome_val = primeiro_nome = apelido_val = data_visita_val = nome_sem_acento = ""
        sexo_val = "M"
        cpf_limpo = cpf_fmt = data_nasc_val = idade_val = resumo_val = ""
        orgao1_val = esp1_val = ben1_val = ""
        orgao2_val = esp2_val = ben2_val = ""
        orgao3_val = esp3_val = ben3_val = ""
        loja_val = atendido_val = senha_inss_val = senha_parana_val = identidade_val = ""
        end1_val = bairro1_val = estado1_val = cidade1_val = cep1_val = edificio_val = ""
        ddd1_val = tel1_val = ref1_val = ""
        ddd2_val = tel2_val = ref2_val = ""
        ddd3_val = tel3_val = ref3_val = ""
        zap1_val = zap2_val = zap3_val = False
        obs_val = ""

    # --- LINHA 1 ---
    r1_1, r1_2, r1_3, r1_4, r1_5, r1_6 = st.columns([3.15, 0.52, 0.72, 1.45, 1.55, 1.13])
    with r1_1:
        st.markdown('<div class="act-lbl">Nome</div>', unsafe_allow_html=True)
        ed_nome = st.text_input("f_nome", value=nome_val, key=f"nome_{real_idx}", label_visibility="collapsed")
    with r1_2:
        st.markdown('<div class="act-lbl">&nbsp;</div>', unsafe_allow_html=True)
        if st.button("Copiar", key=f"cp_nome_{real_idx}", use_container_width=True):
            copiar_texto_js(ed_nome)
    with r1_3:
        st.markdown('<div class="act-lbl">Sexo</div>', unsafe_allow_html=True)
        ed_sexo = st.radio("f_sexo", ["M", "F"], index=0 if sexo_val == "M" else 1, horizontal=True, key=f"sexo_{real_idx}", label_visibility="collapsed")
    with r1_4:
        st.markdown('<div class="act-lbl">1º Nome</div>', unsafe_allow_html=True)
        st.text_input("f_pnome", value=primeiro_nome, key=f"pnome_{real_idx}", label_visibility="collapsed")
    with r1_5:
        st.markdown('<div class="act-lbl">Gosta de ser chamado por</div>', unsafe_allow_html=True)
        ed_apelido = st.text_input("f_apelido", value=apelido_val, key=f"apelido_{real_idx}", label_visibility="collapsed")
    with r1_6:
        st.markdown('<div class="act-lbl">Data da visita</div>', unsafe_allow_html=True)
        ed_visita = st.text_input("f_visita", value=data_visita_val, key=f"visita_{real_idx}", label_visibility="collapsed")

    # --- LINHA 2 ---
    r2_1, r2_2, r2_3, r2_4 = st.columns([3.15, 0.52, 4.33, 0.52])
    with r2_1:
        st.markdown('<div class="act-lbl">Nome (Sem Acentos)</div>', unsafe_allow_html=True)
        st.text_input("f_nsem", value=nome_sem_acento, key=f"nsem_{real_idx}", label_visibility="collapsed")
    with r2_2:
        st.markdown('<div class="act-lbl">&nbsp;</div>', unsafe_allow_html=True)
        if st.button("Copiar", key=f"cp_nsem_{real_idx}", use_container_width=True):
            copiar_texto_js(nome_sem_acento)
    with r2_3:
        st.markdown('<div class="act-lbl">Resumo (Órgão Nome CPF Idade)</div>', unsafe_allow_html=True)
        st.text_input("f_resumo", value=resumo_val, key=f"resumo_{real_idx}", label_visibility="collapsed")
    with r2_4:
        st.markdown('<div class="act-lbl">&nbsp;</div>', unsafe_allow_html=True)
        if st.button("Copiar", key=f"cp_res_{real_idx}", use_container_width=True):
            copiar_texto_js(resumo_val)

    st.markdown('<hr class="act-hr">', unsafe_allow_html=True)

    # --- LINHAS 3A, 3B e 3C: ÓRGÃO, ESPÉCIE E MATRÍCULA/BENEFÍCIO UM ABAIXO DO OUTRO ---
    b1_org, b1_esp, b1_mat, b1_cp, _ = st.columns([1.30, 0.85, 2.20, 0.55, 3.62])
    with b1_org:
        st.markdown('<div class="act-lbl">Órgão (1 / 2 / 3)</div>', unsafe_allow_html=True)
        ed_org1 = st.text_input("f_org1", value=orgao1_val, key=f"org1_{real_idx}", label_visibility="collapsed")
    with b1_esp:
        st.markdown('<div class="act-lbl">Espécie</div>', unsafe_allow_html=True)
        ed_esp1 = st.text_input("f_esp1", value=esp1_val, key=f"esp1_{real_idx}", label_visibility="collapsed")
    with b1_mat:
        st.markdown('<div class="act-lbl">Benefício / Matrícula</div>', unsafe_allow_html=True)
        ed_ben1 = st.text_input("f_ben1", value=ben1_val, key=f"ben1_{real_idx}", label_visibility="collapsed")
    with b1_cp:
        st.markdown('<div class="act-lbl">&nbsp;</div>', unsafe_allow_html=True)
        if st.button("Copiar", key=f"cp_ben1_{real_idx}", use_container_width=True):
            copiar_texto_js(ed_ben1)

    b2_org, b2_esp, b2_mat, b2_cp, _ = st.columns([1.30, 0.85, 2.20, 0.55, 3.62])
    with b2_org:
        ed_org2 = st.text_input("f_org2", value=orgao2_val, key=f"org2_{real_idx}", label_visibility="collapsed")
    with b2_esp:
        ed_esp2 = st.text_input("f_esp2", value=esp2_val, key=f"esp2_{real_idx}", label_visibility="collapsed")
    with b2_mat:
        ed_ben2 = st.text_input("f_ben2", value=ben2_val, key=f"ben2_{real_idx}", label_visibility="collapsed")
    with b2_cp:
        if st.button("Copiar", key=f"cp_ben2_{real_idx}", use_container_width=True):
            copiar_texto_js(ed_ben2)

    b3_org, b3_esp, b3_mat, b3_cp, _ = st.columns([1.30, 0.85, 2.20, 0.55, 3.62])
    with b3_org:
        ed_org3 = st.text_input("f_org3", value=orgao3_val, key=f"org3_{real_idx}", label_visibility="collapsed")
    with b3_esp:
        ed_esp3 = st.text_input("f_esp3", value=esp3_val, key=f"esp3_{real_idx}", label_visibility="collapsed")
    with b3_mat:
        ed_ben3 = st.text_input("f_ben3", value=ben3_val, key=f"ben3_{real_idx}", label_visibility="collapsed")
    with b3_cp:
        if st.button("Copiar", key=f"cp_ben3_{real_idx}", use_container_width=True):
            copiar_texto_js(ed_ben3)

    st.markdown('<hr class="act-hr">', unsafe_allow_html=True)

    # --- LINHA 4 ---
    r4_1, r4_2, r4_3, r4_4, r4_5, r4_6, r4_7 = st.columns([1.45, 0.52, 1.55, 0.52, 1.15, 1.15, 1.45])
    with r4_1:
        st.markdown('<div class="act-lbl">CGC/CPF (Apenas Números)</div>', unsafe_allow_html=True)
        ed_cpfn = st.text_input("f_cpfn", value=cpf_limpo, key=f"cpfn_{real_idx}", label_visibility="collapsed")
    with r4_2:
        st.markdown('<div class="act-lbl">&nbsp;</div>', unsafe_allow_html=True)
        if st.button("Copiar", key=f"cp_cpfn_{real_idx}", use_container_width=True):
            copiar_texto_js(ed_cpfn)
    with r4_3:
        st.markdown('<div class="act-lbl">CGC/CPF (Formatado)</div>', unsafe_allow_html=True)
        st.text_input("f_cpff", value=cpf_fmt, key=f"cpff_{real_idx}", label_visibility="collapsed")
    with r4_4:
        st.markdown('<div class="act-lbl">&nbsp;</div>', unsafe_allow_html=True)
        if st.button("Copiar", key=f"cp_cpff_{real_idx}", use_container_width=True):
            copiar_texto_js(cpf_fmt)
    with r4_5:
        st.markdown('<div class="act-lbl">Data Nascimento</div>', unsafe_allow_html=True)
        ed_nasc = st.text_input("f_nasc", value=data_nasc_val, key=f"nasc_{real_idx}", label_visibility="collapsed")
    with r4_6:
        lbl_idade = "Idade (ALERTA 80+)" if alerta_idade_80 else "Idade (Anos)"
        st.markdown(f'<div class="act-lbl" style="color:{"#800000" if alerta_idade_80 else "#000000"} !important; font-weight:{"bold" if alerta_idade_80 else "normal"} !important;">{lbl_idade}</div>', unsafe_allow_html=True)
        st.text_input("f_idade", value=idade_val, key=f"idade_{real_idx}", label_visibility="collapsed")
    with r4_7:
        st.markdown('<div class="act-lbl">Identidade</div>', unsafe_allow_html=True)
        ed_ident = st.text_input("f_ident", value=identidade_val, key=f"ident_{real_idx}", label_visibility="collapsed")

    # --- LINHA 5 ---
    r5_1, r5_2, r5_3, r5_4 = st.columns([2.0, 2.0, 1.8, 2.2])
    with r5_1:
        st.markdown('<div class="act-lbl">Senha Meu INSS</div>', unsafe_allow_html=True)
        ed_sinss = st.text_input("f_sinss", value=senha_inss_val, key=f"sinss_{real_idx}", label_visibility="collapsed")
    with r5_2:
        st.markdown('<div class="act-lbl">Senha Paraná</div>', unsafe_allow_html=True)
        ed_spar = st.text_input("f_spar", value=senha_parana_val, key=f"spar_{real_idx}", label_visibility="collapsed")
    with r5_3:
        st.markdown('<div class="act-lbl">Loja</div>', unsafe_allow_html=True)
        ed_loja = st.text_input("f_loja", value=loja_val, key=f"loja_{real_idx}", label_visibility="collapsed")
    with r5_4:
        st.markdown('<div class="act-lbl">Atendido por</div>', unsafe_allow_html=True)
        ed_atend = st.text_input("f_atend", value=atendido_val, key=f"atend_{real_idx}", label_visibility="collapsed")

    st.markdown('<hr class="act-hr">', unsafe_allow_html=True)

    # --- LINHAS 6, 7 e 8: TELEFONES 1, 2 e 3 ---
    t1_1, t1_2, t1_3, t1_4, t1_5, t1_6 = st.columns([0.55, 1.45, 0.65, 1.65, 0.55, 2.55])
    with t1_1:
        st.markdown('<div class="act-lbl">DDD 1</div>', unsafe_allow_html=True)
        ed_ddd1 = st.text_input("f_ddd1", value=ddd1_val, key=f"ddd1_{real_idx}", label_visibility="collapsed")
    with t1_2:
        st.markdown('<div class="act-lbl">Telefone 1</div>', unsafe_allow_html=True)
        ed_tel1 = st.text_input("f_tel1", value=tel1_val, key=f"tel1_{real_idx}", label_visibility="collapsed")
    with t1_3:
        st.markdown('<div class="act-lbl-zap">Zap 1</div>', unsafe_allow_html=True)
        ed_zap1 = st.checkbox("Zap", value=zap1_val, key=f"zap1_{real_idx}", label_visibility="collapsed")
    with t1_4:
        unido1 = f"{''.join(filter(str.isdigit, ed_ddd1))}{''.join(filter(str.isdigit, ed_tel1))}"
        st.markdown('<div class="act-lbl">DDD + Tel 1 (Unido)</div>', unsafe_allow_html=True)
        st.text_input("f_uni1", value=unido1, key=f"uni1_{real_idx}", label_visibility="collapsed")
    with t1_5:
        st.markdown('<div class="act-lbl">&nbsp;</div>', unsafe_allow_html=True)
        if st.button("Copiar", key=f"cp_uni1_{real_idx}", use_container_width=True):
            copiar_texto_js(unido1)
    with t1_6:
        st.markdown('<div class="act-lbl">Ref_1 / Observação Tel 1</div>', unsafe_allow_html=True)
        ed_ref1 = st.text_input("f_ref1", value=ref1_val, key=f"ref1_{real_idx}", label_visibility="collapsed")

    t2_1, t2_2, t2_3, t2_4, t2_5, t2_6 = st.columns([0.55, 1.45, 0.65, 1.65, 0.55, 2.55])
    with t2_1:
        st.markdown('<div class="act-lbl">DDD 2</div>', unsafe_allow_html=True)
        ed_ddd2 = st.text_input("f_ddd2", value=ddd2_val, key=f"ddd2_{real_idx}", label_visibility="collapsed")
    with t2_2:
        st.markdown('<div class="act-lbl">Telefone 2</div>', unsafe_allow_html=True)
        ed_tel2 = st.text_input("f_tel2", value=tel2_val, key=f"tel2_{real_idx}", label_visibility="collapsed")
    with t2_3:
        st.markdown('<div class="act-lbl-zap">Zap 2</div>', unsafe_allow_html=True)
        ed_zap2 = st.checkbox("Zap", value=zap2_val, key=f"zap2_{real_idx}", label_visibility="collapsed")
    with t2_4:
        unido2 = f"{''.join(filter(str.isdigit, ed_ddd2))}{''.join(filter(str.isdigit, ed_tel2))}"
        st.markdown('<div class="act-lbl">DDD + Tel 2 (Unido)</div>', unsafe_allow_html=True)
        st.text_input("f_uni2", value=unido2, key=f"uni2_{real_idx}", label_visibility="collapsed")
    with t2_5:
        st.markdown('<div class="act-lbl">&nbsp;</div>', unsafe_allow_html=True)
        if st.button("Copiar", key=f"cp_uni2_{real_idx}", use_container_width=True):
            copiar_texto_js(unido2)
    with t2_6:
        st.markdown('<div class="act-lbl">Ref_2 / Observação Tel 2</div>', unsafe_allow_html=True)
        ed_ref2 = st.text_input("f_ref2", value=ref2_val, key=f"ref2_{real_idx}", label_visibility="collapsed")

    t3_1, t3_2, t3_3, t3_4, t3_5, t3_6 = st.columns([0.55, 1.45, 0.65, 1.65, 0.55, 2.55])
    with t3_1:
        st.markdown('<div class="act-lbl">DDD 3</div>', unsafe_allow_html=True)
        ed_ddd3 = st.text_input("f_ddd3", value=ddd3_val, key=f"ddd3_{real_idx}", label_visibility="collapsed")
    with t3_2:
        st.markdown('<div class="act-lbl">Telefone 3</div>', unsafe_allow_html=True)
        ed_tel3 = st.text_input("f_tel3", value=tel3_val, key=f"tel3_{real_idx}", label_visibility="collapsed")
    with t3_3:
        st.markdown('<div class="act-lbl-zap">Zap 3</div>', unsafe_allow_html=True)
        ed_zap3 = st.checkbox("Zap", value=zap3_val, key=f"zap3_{real_idx}", label_visibility="collapsed")
    with t3_4:
        unido3 = f"{''.join(filter(str.isdigit, ed_ddd3))}{''.join(filter(str.isdigit, ed_tel3))}"
        st.markdown('<div class="act-lbl">DDD + Tel 3 (Unido)</div>', unsafe_allow_html=True)
        st.text_input("f_uni3", value=unido3, key=f"uni3_{real_idx}", label_visibility="collapsed")
    with t3_5:
        st.markdown('<div class="act-lbl">&nbsp;</div>', unsafe_allow_html=True)
        if st.button("Copiar", key=f"cp_uni3_{real_idx}", use_container_width=True):
            copiar_texto_js(unido3)
    with t3_6:
        st.markdown('<div class="act-lbl">Ref_3 / Observação Tel 3</div>', unsafe_allow_html=True)
        ed_ref3 = st.text_input("f_ref3", value=ref3_val, key=f"ref3_{real_idx}", label_visibility="collapsed")

    st.markdown('<hr class="act-hr">', unsafe_allow_html=True)

    # --- LINHA 9 ---
    e1, e2, e3, e4, e5, e6 = st.columns([2.5, 1.4, 1.5, 0.55, 0.95, 1.1])
    with e1:
        st.markdown('<div class="act-lbl">Endereço 1</div>', unsafe_allow_html=True)
        ed_end1 = st.text_input("f_end1", value=end1_val, key=f"end1_{real_idx}", label_visibility="collapsed")
    with e2:
        st.markdown('<div class="act-lbl">Bairro 1</div>', unsafe_allow_html=True)
        ed_bai1 = st.text_input("f_bai1", value=bairro1_val, key=f"bai1_{real_idx}", label_visibility="collapsed")
    with e3:
        st.markdown('<div class="act-lbl">Cidade 1</div>', unsafe_allow_html=True)
        ed_cid1 = st.text_input("f_cid1", value=cidade1_val, key=f"cid1_{real_idx}", label_visibility="collapsed")
    with e4:
        st.markdown('<div class="act-lbl">UF</div>', unsafe_allow_html=True)
        ed_uf1 = st.text_input("f_uf1", value=estado1_val, key=f"uf1_{real_idx}", label_visibility="collapsed")
    with e5:
        st.markdown('<div class="act-lbl">Cep 1</div>', unsafe_allow_html=True)
        ed_cep1 = st.text_input("f_cep1", value=cep1_val, key=f"cep1_{real_idx}", label_visibility="collapsed")
    with e6:
        st.markdown('<div class="act-lbl">Edifício</div>', unsafe_allow_html=True)
        ed_edif = st.text_input("f_edif", value=edificio_val, key=f"edif_{real_idx}", label_visibility="collapsed")

    # --- LINHA 10 ---
    o1, o2 = st.columns([6.8, 1.2])
    with o1:
        st.markdown('<div class="act-lbl">Histórico / Observações (USER9)</div>', unsafe_allow_html=True)
        ed_obs = st.text_area("f_obs", value=obs_val, height=38, key=f"obs_{real_idx}", label_visibility="collapsed")
    with o2:
        st.markdown('<div class="act-lbl">&nbsp;</div>', unsafe_allow_html=True)
        if st.button("Salvar Ficha", type="primary", use_container_width=True, key=f"save_{real_idx}") and total_registros > 0:
            campos_salvar = {
                'NAME': ed_nome.strip(),
                'SEXO': ed_sexo,
                'FIRST_NAME': ed_apelido.strip(),
                'USER5': ed_visita.strip(),
                'COMPANY': ed_org1.strip(),
                'USER8': ed_esp1.strip(),
                'ID_STAT': ed_ben1.strip(),
                'ORGAO_2': ed_org2.strip(),
                'ESPECIE_2': ed_esp2.strip(),
                'BENEFICIO_2': ed_ben2.strip(),
                'ORGAO_3': ed_org3.strip(),
                'ESPECIE_3': ed_esp3.strip(),
                'BENEFICIO_3': ed_ben3.strip(),
                'USR1000': limpar_cpf(ed_cpfn),
                'USER1': ed_nasc.strip(),
                'USER12': ed_ident.strip(),
                'USER10': ed_sinss.strip(),
                'USER11': ed_spar.strip(),
                'USER2': ed_loja.strip(),
                'USER6': ed_atend.strip(),
                'DDD_1': ed_ddd1.strip(),
                'TEL_1': ed_tel1.strip(),
                'PHONE': f"({ed_ddd1.strip()}) {ed_tel1.strip()}" if ed_ddd1.strip() else ed_tel1.strip(),
                'ZAP_1': "Sim" if ed_zap1 else "Não",
                'REF_1': ed_ref1.strip(),
                'DDD_2': ed_ddd2.strip(),
                'TEL_2': ed_tel2.strip(),
                'HOME_PHONE': f"({ed_ddd2.strip()}) {ed_tel2.strip()}" if ed_ddd2.strip() else ed_tel2.strip(),
                'ZAP_2': "Sim" if ed_zap2 else "Não",
                'REF_2': ed_ref2.strip(),
                'DDD_3': ed_ddd3.strip(),
                'TEL_3': ed_tel3.strip(),
                'MOBILE_PHONE': f"({ed_ddd3.strip()}) {ed_tel3.strip()}" if ed_ddd3.strip() else ed_tel3.strip(),
                'ZAP_3': "Sim" if ed_zap3 else "Não",
                'REF_3': ed_ref3.strip(),
                'ADDR1': ed_end1.strip(),
                'ADDR3': ed_bai1.strip(),
                'CITY': ed_cid1.strip(),
                'STATE': ed_uf1.strip(),
                'ZIP': ed_cep1.strip(),
                'ADDR2': ed_edif.strip(),
                'USER9': ed_obs.strip()
            }
            for k_col, v_col in campos_salvar.items():
                garantir_coluna(df_unificada, k_col)
                df_unificada.at[real_idx, k_col] = v_col

            st.session_state["df_unificada"] = df_unificada
            salvar_bases_master(df_unificada, df_quarentena)
            st.toast("Ficha salva na Base Master!")
            st.rerun()

# -----------------------------------------------------------------------------
# 8. VISÕES AUXILIARES
# -----------------------------------------------------------------------------
elif st.session_state["visao_ativa"] == "tabela":
    st.markdown('<div style="font-size:11px; font-weight:bold; margin-bottom:2px;">Tabela Unificada (Base Master)</div>', unsafe_allow_html=True)
    if not df_ativo.empty:
        st.dataframe(df_ativo.head(300), use_container_width=True, height=450)

elif st.session_state["visao_ativa"] == "quarentena":
    st.markdown('<div style="font-size:11px; font-weight:bold; margin-bottom:2px;">Quarentena / Revisão (PC 1 Hamilton vs PC 2 Jaedna)</div>', unsafe_allow_html=True)
    if not df_quarentena.empty:
        cols_q = [c for c in ['NAME', 'ORIGEM', 'USER9', 'PHONE'] if c in df_quarentena.columns]
        st.dataframe(df_quarentena[cols_q], use_container_width=True, height=450)
    else:
        st.success("Nenhum contato em quarentena!")

elif st.session_state["visao_ativa"] == "todos_campos":
    st.markdown('<div style="font-size:11px; font-weight:bold; margin-bottom:2px;">Todos os Campos da Ficha Atual</div>', unsafe_allow_html=True)
    if not df_ativo.empty:
        cli_atual = df_ativo.iloc[st.session_state["idx_cliente"]]
        df_campos = pd.DataFrame(list(cli_atual.items()), columns=["Campo", "Valor"])
        st.dataframe(df_campos, use_container_width=True, height=450)

status_lk = f" | Lookup ativo: '{st.session_state['lookup_termo']}' ({total_registros})" if st.session_state["lookup_indices"] is not None else ""
st.markdown(f"""
    <div class="act-statusbar">
        <span>{VERSAO_APP} | {'Base Master Travada' if ja_unificado else 'Aguardando Unificação'}{status_lk}</span>
        <span>Origem: {df_ativo.iloc[st.session_state['idx_cliente']].get('ORIGEM', 'Master') if not df_ativo.empty else '-'}</span>
    </div>
""", unsafe_allow_html=True)