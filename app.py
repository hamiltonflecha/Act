import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime

VERSAO_APP = "Act!   V89"

st.set_page_config(page_title=f"{VERSAO_APP} - Banco.dbf", page_icon="📑", layout="wide", initial_sidebar_state="collapsed")

ARQ_UNIFICADA = "Base_Unificada_Master.csv"
ARQ_QUARENTENA = "Base_Quarentena_Master.csv"
ARQ_TRAVA = "fusao_concluida.lock"

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
            padding: 1px 4px !important;
            font-size: 11px !important;
        }
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
    st.stop()

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

cor_idade_bg = "#CC0000" if alerta_idade_80 else "#FFFFFF"
cor_idade_fg = "#FFFFFF" if alerta_idade_80 else "#000000"
cor_idade_bd = "#800000" if alerta_idade_80 else "#7A7265"

css_act_v89 = f"""
    <style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {{
        display: none !important;
    }}
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {{
        background-color: #9E9382 !important;
        font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important;
        color: #000000 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    .block-container {{
        max-width: 990px !important;
        width: 990px !important;
        padding: 4px 6px !important;
        margin: 0 auto !important;
    }}
    .act-topbar-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 0 0 3px 0;
        background-color: #D4D0C8;
        border-top: 1px solid #FFFFFF;
        border-left: 1px solid #FFFFFF;
        border-right: 1px solid #404040;
        border-bottom: 1px solid #404040;
    }}
    .act-topbar-table td {{
        padding: 1px 6px;
        font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif;
        font-size: 11px;
        font-weight: bold;
        color: #000000;
        border: 1px solid #808080;
        line-height: 15px;
    }}
    .act-top-left {{
        text-align: left;
        background: linear-gradient(90deg, #0A246A 0%, #A6CAF0 100%);
        color: #FFFFFF !important;
    }}
    .act-top-right {{
        text-align: right;
        width: 165px;
        white-space: nowrap;
        background-color: #D4D0C8;
        color: #0A246A !important;
    }}
    .act-lbl {{
        font-size: 10px !important;
        color: #000000 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    .act-hr {{ border: none; border-top: 1px solid #6E6659; margin: 3px 0; height: 1px; }}
    .act-statusbar {{ background-color: #D4D0C8; border-top: 1px solid #808080; padding: 1px 6px; font-size: 10px; color: #000000; display: flex; justify-content: space-between; margin-top: 4px; }}
    </style>
"""
st.markdown(css_act_v89, unsafe_allow_html=True)

st.markdown(f"""
    <table class="act-topbar-table">
        <tr>
            <td class="act-top-left">Hamilton e Jaedna</td>
            <td class="act-top-right">{VERSAO_APP}</td>
        </tr>
    </table>
""", unsafe_allow_html=True)

pos_display = 0 if total_registros == 0 else (st.session_state["idx_cliente"] + 1)

# Barra de ferramentas limpa e funcional em Streamlit puro (sem barra estática duplicada)
b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13, b14, b15 = st.columns([
    0.4, 0.4, 1.0, 0.4, 0.4, 1.5, 0.8, 0.8, 0.6, 0.8, 0.8, 1.0, 0.8, 0.9, 0.6
])

with b1:
    if st.button("|<", use_container_width=True, help="Primeiro registro"):
        st.session_state["idx_cliente"] = 0
        st.session_state["visao_ativa"] = "ficha"
        st.rerun()
with b2:
    if st.button("<", use_container_width=True, help="Registro anterior"):
        if st.session_state["idx_cliente"] > 0:
            st.session_state["idx_cliente"] -= 1
            st.session_state["visao_ativa"] = "ficha"
            st.rerun()
with b3:
    st.text_input("cnt", value=f"{pos_display} de {total_registros}", disabled=True, label_visibility="collapsed")
with b4:
    if st.button(">", use_container_width=True, help="Próximo registro"):
        if st.session_state["idx_cliente"] < total_registros - 1:
            st.session_state["idx_cliente"] += 1
            st.session_state["visao_ativa"] = "ficha"
            st.rerun()
with b5:
    if st.button(">|", use_container_width=True, help="Último registro"):
        if total_registros > 0:
            st.session_state["idx_cliente"] = total_registros - 1
            st.session_state["visao_ativa"] = "ficha"
            st.rerun()
with b6:
    termo_busca = st.text_input("loc", value=st.session_state["lookup_termo"], placeholder="Localizar...", label_visibility="collapsed")
with b7:
    if st.button("Buscar", use_container_width=True, help="Localizar string"):
        q = termo_busca.strip()
        if q and not df_unificada.empty:
            mask = df_unificada.astype(str).apply(lambda col: col.str.contains(q, case=False, regex=False)).any(axis=1)
            encontrados = df_unificada[mask].index.tolist()
            st.session_state["lookup_termo"] = q
            st.session_state["lookup_candidatos"] = encontrados
            st.session_state["lookup_modal_aberto"] = True
            st.session_state["visao_ativa"] = "ficha"
            st.rerun()
with b8:
    lbl_t = f"Lookup({len(st.session_state['lookup_indices'])})" if st.session_state["lookup_indices"] is not None else "Todos"
    if st.button(lbl_t, use_container_width=True):
        if st.session_state["lookup_indices"] is not None:
            st.session_state["lookup_indices"] = None
            st.session_state["lookup_termo"] = ""
            st.session_state["lookup_modal_aberto"] = False
            st.session_state["idx_cliente"] = 0
            st.rerun()
with b9:
    if st.button("Novo", use_container_width=True, help="Inserir novo contato"):
        nova_linha = {col: "" for col in df_unificada.columns} if not df_unificada.empty else {}
        nova_linha["NAME"] = "NOVO CONTATO"
        nova_linha["COMPANY"] = "INSS"
        nova_linha["ORIGEM"] = f"Inserido ({st.session_state.get('operador_atual', 'Hamilton')})"
        df_unificada = pd.concat([df_unificada, pd.DataFrame([nova_linha])], ignore_index=True)
        st.session_state["df_unificada"] = df_unificada
        salvar_bases_master(df_unificada, df_quarentena)
        st.session_state["lookup_indices"] = None
        st.session_state["idx_cliente"] = len(df_unificada) - 1
        st.session_state["visao_ativa"] = "ficha"
        st.rerun()
with b10:
    if st.button("Excluir", use_container_width=True, help="Excluir contato atual") and total_registros > 0:
        st.session_state["confirmar_exclusao"] = True
        st.rerun()
with b11:
    if st.button("Tabela", use_container_width=True, help="Ver tabela unificada"):
        st.session_state["visao_ativa"] = "ficha" if st.session_state["visao_ativa"] == "tabela" else "tabela"
        st.rerun()
with b12:
    if st.button(f"Quarent({len(df_quarentena)})", use_container_width=True, help="Ver quarentena"):
        st.session_state["visao_ativa"] = "ficha" if st.session_state["visao_ativa"] == "quarentena" else "quarentena"
        st.rerun()
with b13:
    if st.button("Campos", use_container_width=True, help="Ver campos da ficha"):
        st.session_state["visao_ativa"] = "ficha" if st.session_state["visao_ativa"] == "todos_campos" else "todos_campos"
        st.rerun()
with b14:
    if not ja_unificado:
        if st.button("Unificar", type="primary", use_container_width=True, help="Executar fusão de bases"):
            u, q = executar_fusao_unica()
            st.session_state["df_unificada"] = u
            st.session_state["df_quarentena"] = q
            st.session_state["idx_cliente"] = 0
            st.rerun()
    else:
        if st.button("Travada", use_container_width=True):
            pass
with b15:
    if st.button("Sair", use_container_width=True, help="Encerrar sessão"):
        st.session_state["autenticado"] = False
        st.rerun()

st.markdown('<hr class="act-hr">', unsafe_allow_html=True)

if total_registros > 0 and st.session_state["visao_ativa"] == "ficha":
    cliente = df_ativo.iloc[st.session_state["idx_cliente"]]
    real_idx = cliente.name
    nome_val = get_campo(cliente, ['NAME', 'NOME'])
    cpf_bruto = get_campo(cliente, ['USR1000', 'CPF'])
    cpf_limpo = limpar_cpf(cpf_bruto)
    cpf_fmt = formatar_cpf(cpf_limpo)
    
    c1, c2, c3 = st.columns([4, 2, 2])
    with c1:
        st.markdown('<div class="act-lbl">Nome do Cliente</div>', unsafe_allow_html=True)
        ed_nome = st.text_input("fnome", value=nome_val, key=f"n_{real_idx}", label_visibility="collapsed")
    with c2:
        st.markdown('<div class="act-lbl">CPF</div>', unsafe_allow_html=True)
        ed_cpf = st.text_input("fcpf", value=cpf_fmt, key=f"c_{real_idx}", label_visibility="collapsed")
    with c3:
        st.markdown('<div class="act-lbl" style="visibility:hidden;">.</div>', unsafe_allow_html=True)
        if st.button("Salvar Ficha", type="primary", key=f"s_{real_idx}", use_container_width=True):
            df_unificada.at[real_idx, 'NAME'] = ed_nome.strip()
            salvar_bases_master(df_unificada, df_quarentena)
            st.toast("Salvo com sucesso!")
            st.rerun()
elif st.session_state["visao_ativa"] == "tabela":
    if not df_ativo.empty:
        st.dataframe(df_ativo.head(200), use_container_width=True, height=400)
elif st.session_state["visao_ativa"] == "quarentena":
    if not df_quarentena.empty:
        st.dataframe(df_quarentena, use_container_width=True, height=400)
    else:
        st.success("Nenhum registro em quarentena.")

st.markdown(f"""
    <div class="act-statusbar">
        <span>{VERSAO_APP} | {'Base Master Travada' if ja_unificado else 'Aguardando Unificação'}</span>
        <span>Total: {total_registros}</span>
    </div>
""", unsafe_allow_html=True)