import streamlit as st
import pandas as pd
import numpy as np
import os

VERSAO_APP = "Act V47"

st.set_page_config(page_title=f"{VERSAO_APP} - Banco.dbf", page_icon="📑", layout="wide", initial_sidebar_state="expanded")

# -----------------------------------------------------------------------------
# 1. SEGURANÇA E TELA DE LOGIN CLÁSSICA ACT! (ACABAMENTO SIMÉTRICO)
# -----------------------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("""
        <style>
        /* Oculta elementos padrão do Streamlit */
        header, footer, [data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stToolbar"] {
            display: none !important;
        }
        /* Fundo cinza da área de trabalho do Act! */
        .stApp {
            background-color: #808080 !important;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important;
        }
        .main .block-container {
            padding-top: 160px !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
        }
        /* Janela Modal "Login to Banco.dbf" */
        div[data-testid="stVerticalBlock"] > div:has(div.act-titlebar) {
            background-color: #D4D0C8 !important;
            border-top: 2px solid #FFFFFF !important;
            border-left: 2px solid #FFFFFF !important;
            border-right: 2px solid #404040 !important;
            border-bottom: 2px solid #404040 !important;
            box-shadow: 1px 1px 0px #000000 !important;
            padding: 3px 3px 12px 3px !important;
            width: 332px !important;
            min-width: 332px !important;
            max-width: 332px !important;
            margin: 0 auto !important;
            box-sizing: border-box !important;
            gap: 0.4rem !important;
        }
        /* Neutraliza largura excessiva nos wrappers do Markdown da barra azul */
        div[data-testid="stVerticalBlock"] > div:has(div.act-titlebar) > div:first-child,
        div[data-testid="stVerticalBlock"] > div:has(div.act-titlebar) > div:first-child > div,
        div[data-testid="stVerticalBlock"] > div:has(div.act-titlebar) [data-testid="stMarkdownContainer"] {
            width: auto !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            box-sizing: border-box !important;
        }
        /* Barra de Título Azul Degradê com acabamento simétrico nos dois lados */
        .act-titlebar {
            background: linear-gradient(90deg, #0A246A 0%, #A6CAF0 100%);
            color: #FFFFFF;
            font-weight: bold;
            font-size: 11px;
            padding: 2px 3px 2px 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 0 1px 8px 1px;
            width: calc(100% - 2px);
            box-sizing: border-box;
            white-space: nowrap;
        }
        .act-close-btn {
            background-color: #D4D0C8;
            color: #000000;
            border-top: 1px solid #FFFFFF;
            border-left: 1px solid #FFFFFF;
            border-right: 1px solid #404040;
            border-bottom: 1px solid #404040;
            font-size: 9px;
            font-weight: bold;
            width: 14px;
            height: 13px;
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1;
            flex-shrink: 0;
        }
        /* Remoção total de qualquer fundo branco arredondado externo nos inputs */
        div[data-testid="stVerticalBlock"] > div:has(div.act-titlebar) .stTextInput {
            padding: 0 12px !important;
            margin-bottom: 0px !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        div[data-testid="stVerticalBlock"] > div:has(div.act-titlebar) .stTextInput label {
            color: #000000 !important;
            font-size: 11px !important;
            font-family: 'Tahoma', Arial, sans-serif !important;
            margin-bottom: 2px !important;
            min-height: 0 !important;
        }
        div[data-testid="stVerticalBlock"] > div:has(div.act-titlebar) .stTextInput div {
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            border-radius: 0px !important;
            box-shadow: none !important;
        }
        div[data-testid="stVerticalBlock"] > div:has(div.act-titlebar) .stTextInput input {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border-radius: 0px !important;
            border-top: 2px solid #808080 !important;
            border-left: 2px solid #808080 !important;
            border-right: 1px solid #FFFFFF !important;
            border-bottom: 1px solid #FFFFFF !important;
            box-shadow: inset 1px 1px 0px #404040 !important;
            height: 22px !important;
            min-height: 22px !important;
            padding: 1px 4px !important;
            font-size: 11px !important;
            font-family: 'Tahoma', Arial, sans-serif !important;
        }
        div[data-testid="stVerticalBlock"] > div:has(div.act-titlebar) .stTextInput button {
            display: none !important;
        }
        /* Checkbox Clássica */
        div[data-testid="stVerticalBlock"] > div:has(div.act-titlebar) .stCheckbox {
            padding: 4px 12px 4px 12px !important;
        }
        div[data-testid="stVerticalBlock"] > div:has(div.act-titlebar) .stCheckbox label p {
            color: #000000 !important;
            font-size: 11px !important;
            font-family: 'Tahoma', Arial, sans-serif !important;
            white-space: nowrap !important;
        }
        /* Botões OK e Cancel */
        div[data-testid="stVerticalBlock"] > div:has(div.act-titlebar) [data-testid="column"] {
            padding: 0 4px !important;
        }
        div[data-testid="stVerticalBlock"] > div:has(div.act-titlebar) .stButton button {
            background-color: #D4D0C8 !important;
            color: #000000 !important;
            border-radius: 0px !important;
            border-top: 2px solid #FFFFFF !important;
            border-left: 2px solid #FFFFFF !important;
            border-right: 2px solid #404040 !important;
            border-bottom: 2px solid #404040 !important;
            box-shadow: inset -1px -1px 0px #808080 !important;
            height: 23px !important;
            min-height: 23px !important;
            width: 78px !important;
            min-width: 78px !important;
            padding: 0px !important;
            font-size: 11px !important;
            font-family: 'Tahoma', Arial, sans-serif !important;
            display: block !important;
            margin: 0 auto !important;
        }
        div[data-testid="stVerticalBlock"] > div:has(div.act-titlebar) .stButton button p {
            font-size: 11px !important;
            color: #000000 !important;
            margin: 0 !important;
            line-height: 19px !important;
            white-space: nowrap !important;
        }
        div[data-testid="stVerticalBlock"] > div:has(div.act-titlebar) .stButton button:active {
            border-top: 2px solid #404040 !important;
            border-left: 2px solid #404040 !important;
            border-right: 2px solid #FFFFFF !important;
            border-bottom: 2px solid #FFFFFF !important;
        }
        .act-msg-erro {
            color: #800000;
            font-size: 11px;
            text-align: center;
            padding-top: 6px;
            font-family: 'Tahoma', Arial, sans-serif;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""
            <div class="act-titlebar">
                <span>Login to Banco.dbf</span>
                <span class="act-close-btn">×</span>
            </div>
        """, unsafe_allow_html=True)

        user_input = st.text_input("Enter your user name for this database:", value="Hamilton Flecha", key="user_key")
        senha_input = st.text_input("Enter your password for this database:", type="password", key="pass_key")
        st.checkbox("Remember password", value=True, key="rem_key")

        _, b_ok, b_cancel, _ = st.columns([0.8, 1.2, 1.2, 0.8])
        with b_ok:
            btn_ok = st.button("OK", key="btn_ok_act")
        with b_cancel:
            btn_cancel = st.button("Cancel", key="btn_cancel_act")

        if btn_ok:
            if senha_input == "solucoes1986":
                st.session_state["autenticado"] = True
                st.session_state["operador_atual"] = user_input
                st.rerun()
            else:
                st.markdown('<div class="act-msg-erro">Invalid password for Banco.dbf.</div>', unsafe_allow_html=True)
        if btn_cancel:
            st.markdown('<div class="act-msg-erro">Login cancelled.</div>', unsafe_allow_html=True)

    st.stop()

# -----------------------------------------------------------------------------
# 2. FUNÇÕES DE DADOS E LEITURA (INALTERADAS)
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

def executar_fusao():
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

    return pd.DataFrame(base_unificada), pd.DataFrame(base_quarentena)

# Inicialização e carregamento automático das bases
if "df_unificada" not in st.session_state or st.session_state["df_unificada"].empty:
    with st.spinner("Carregando e unificando as bases de dados..."):
        st.session_state["df_unificada"], st.session_state["df_quarentena"] = executar_fusao()

if "idx_cliente" not in st.session_state:
    st.session_state["idx_cliente"] = 0

df_unificada = st.session_state["df_unificada"]
df_quarentena = st.session_state["df_quarentena"]

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL (PAINEL DE CONTROLE)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("Painel de Controle")
    st.markdown(f"**Sistema {VERSAO_APP}**")
    st.markdown("Operadores: Hamilton & Jaedna")
    st.markdown("---")
    st.write(f"Base Unificada: **{len(df_unificada)}** fichas")
    st.write(f"Quarentena: **{len(df_quarentena)}** fichas")
    st.markdown("---")
    if st.button("Recalcular / Atualizar Bases", use_container_width=True):
        with st.spinner("Processando fusão das bases..."):
            st.session_state["df_unificada"], st.session_state["df_quarentena"] = executar_fusao()
            st.session_state["idx_cliente"] = 0
            st.success("Bases atualizadas com sucesso!")
            st.rerun()

# -----------------------------------------------------------------------------
# 4. ESTRUTURA DE ABAS E INTERFACE ZEROSCROLL
# -----------------------------------------------------------------------------
aba_ficha, aba_tabela, aba_quarentena = st.tabs([
    "👤 Ficha Act! (Trabalho)", 
    f"📊 Tabela Unificada ({len(df_unificada)})", 
    f"⚠️ Quarentena / Revisão ({len(df_quarentena)})"
])

# ----- ABA 1: FICHA ZEROSCROLL -----
with aba_ficha:
    if not df_unificada.empty:
        c_busca, c_prev, c_pos, c_next = st.columns([3, 1, 1, 1])
        
        with c_busca:
            termo_busca = st.text_input("Buscar por Nome, CPF ou Benefício:", placeholder="Digite para filtrar...", label_visibility="collapsed")
            
        if termo_busca:
            df_filtrado = df_unificada[df_unificada.astype(str).apply(lambda x: x.str.contains(termo_busca, case=False)).any(axis=1)]
        else:
            df_filtrado = df_unificada

        total_registros = len(df_filtrado)
        
        if st.session_state["idx_cliente"] >= total_registros:
            st.session_state["idx_cliente"] = max(0, total_registros - 1)
            
        with c_prev:
            if st.button("◀ Anterior", use_container_width=True):
                if st.session_state["idx_cliente"] > 0:
                    st.session_state["idx_cliente"] -= 1
                    st.rerun()
                    
        with c_pos:
            st.markdown(f"<h5 style='text-align: center; margin-top: 5px;'>{st.session_state['idx_cliente'] + 1} de {total_registros}</h5>", unsafe_allow_html=True)
            
        with c_next:
            if st.button("Próximo ▶", use_container_width=True):
                if st.session_state["idx_cliente"] < total_registros - 1:
                    st.session_state["idx_cliente"] += 1
                    st.rerun()

        st.markdown("---")
        
        if total_registros > 0:
            cliente = df_filtrado.iloc[st.session_state["idx_cliente"]]
            
            cpf_bruto = cliente.get('USR1000', cliente.get('CPF', ''))
            cpf_limpo = limpar_cpf(cpf_bruto)
            cpf_formatado = formatar_cpf(cpf_limpo)
            
            col_nome, col_cpf, col_copy = st.columns([3, 2, 1])
            with col_nome:
                st.subheader(f"👤 {cliente.get('NAME', 'Sem Nome')}")
            with col_cpf:
                st.subheader(f"📄 CPF: {cpf_formatado if cpf_formatado else 'SEM CPF'}")
            with col_copy:
                st.code(cpf_limpo if cpf_limpo else "SEM_CPF", language=None)
                
            g1, g2, g3 = st.columns(3)
            with g1:
                st.text_input("Telefone (PHONE):", value=str(cliente.get('PHONE', '')), disabled=True)
                st.text_input("Endereço (ADDR1):", value=str(cliente.get('ADDR1', '')), disabled=True)
            with g2:
                st.text_input("Bairro (ADDR3):", value=str(cliente.get('ADDR3', '')), disabled=True)
                st.text_input("Cidade / UF:", value=f"{cliente.get('CITY', '')} / {cliente.get('STATE', '')}", disabled=True)
            with g3:
                st.text_input("CEP (ZIP):", value=str(cliente.get('ZIP', '')), disabled=True)
                st.text_input("Origem do Registro:", value=str(cliente.get('ORIGEM', 'Unificado')), disabled=True)

            st.markdown("### 📝 Histórico / Observações (USER9)")
            st.text_area("USER9_AREA", value=str(cliente.get('USER9', '')), height=140, label_visibility="collapsed", disabled=True)

            with st.expander("Ver todos os 183 campos desta ficha"):
                df_campos = pd.DataFrame(list(cliente.items()), columns=["Campo", "Valor"])
                st.dataframe(df_campos, use_container_width=True, height=350)
        else:
            st.warning("Nenhum registro encontrado para o termo pesquisado.")
    else:
        st.warning("Nenhuma base carregada. Verifique se os arquivos DBF1_Local e DBF2_Copia estão salvos no repositório.")

# ----- ABA 2: VISUALIZAÇÃO EM TABELA -----
with aba_tabela:
    st.subheader("Base Consolidação Geral")
    if not df_unificada.empty:
        busca_tab = st.text_input("Filtrar Tabela:", placeholder="Filtrar dados...")
        if busca_tab:
            res_tab = df_unificada[df_unificada.astype(str).apply(lambda x: x.str.contains(busca_tab, case=False)).any(axis=1)]
            st.dataframe(res_tab, use_container_width=True)
        else:
            st.dataframe(df_unificada.head(100), use_container_width=True)

# ----- ABA 3: QUARENTENA -----
with aba_quarentena:
    st.subheader("Contatos com Anotações Diferentes entre PC 1 (Hamilton) e PC 2 (Jaedna)")
    if not df_quarentena.empty:
        cols_quarantena = [c for c in ['NAME', 'ORIGEM', 'USER9', 'PHONE'] if c in df_quarentena.columns]
        st.dataframe(df_quarentena[cols_quarantena], use_container_width=True)
    else:
        st.success("Nenhum contacto em quarentena! Todas as fichas foram unificadas sem divergências.")