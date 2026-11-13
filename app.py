import streamlit as st
import pandas as pd
import numpy as np
import os

VERSAO_APP = "Act V55"

st.set_page_config(page_title=f"{VERSAO_APP} - Banco.dbf", page_icon="📑", layout="wide", initial_sidebar_state="expanded")

# -----------------------------------------------------------------------------
# 1. SEGURANÇA E TELA DE LOGIN CLÁSSICA ACT! (CLONE EXATO EM PORTUGUÊS - V55)
# -----------------------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    css_login = """
        <style>
        /* Oculta toda a interface padrão do Streamlit */
        header, footer, [data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
            display: none !important;
        }
        /* Fundo cinza sólido exato (#808080) */
        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background-color: #808080 !important;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important;
            overflow: hidden !important;
        }
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100vw !important;
            width: 100vw !important;
            height: 100vh !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        /* Centraliza o bloco horizontal da janela modal na tela */
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) {
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            margin: 0 !important;
        }
        /* Caixa Modal Windows 2000 exata (282px de largura, bordas 3D clássicas) */
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) > div[data-testid="column"]:nth-child(2) {
            width: 282px !important;
            min-width: 282px !important;
            max-width: 282px !important;
            flex: 0 0 282px !important;
            background-color: #D4D0C8 !important;
            border-radius: 0px !important;
            border-top: 1px solid #FFFFFF !important;
            border-left: 1px solid #FFFFFF !important;
            border-right: 1px solid #404040 !important;
            border-bottom: 1px solid #404040 !important;
            box-shadow: inset 1px 1px 0px #D4D0C8, inset -1px -1px 0px #808080, 1px 1px 0px #000000 !important;
            padding: 3px 3px 14px 3px !important;
            box-sizing: border-box !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) > div[data-testid="column"]:nth-child(1),
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) > div[data-testid="column"]:nth-child(3) {
            flex: 1 1 auto !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) > div[data-testid="column"]:nth-child(2) [data-testid="stVerticalBlock"] {
            gap: 0px !important;
        }
        /* Barra de Título Azul Degradê (#0A246A -> #A6CAF0) */
        .act-titlebar {
            background: linear-gradient(90deg, #0A246A 0%, #A6CAF0 100%);
            color: #FFFFFF;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif;
            font-weight: bold;
            font-size: 11px;
            height: 18px;
            padding: 0 2px 0 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 0 0 11px 0;
            width: 100%;
            box-sizing: border-box;
            letter-spacing: 0px;
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
            cursor: default;
        }
        /* Labels exatos acima dos campos */
        .act-label {
            color: #000000;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif;
            font-size: 11px;
            line-height: 13px;
            padding: 0 10px 2px 10px;
            margin: 0;
            white-space: nowrap;
        }
        .act-label-pass {
            padding-top: 10px;
        }
        /* Inputs 3D afundados (Sunken) exatos */
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stTextInput {
            padding: 0 10px !important;
            margin: 0 !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stTextInput label {
            display: none !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stTextInput div[data-baseweb="input"],
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stTextInput div[data-baseweb="base-input"] {
            background: transparent !important;
            border: none !important;
            border-radius: 0px !important;
            box-shadow: none !important;
            padding: 0 !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stTextInput input {
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
            padding: 1px 3px !important;
            font-size: 11px !important;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important;
            line-height: 16px !important;
        }
        /* Oculta o ícone de olho do Streamlit no campo senha */
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stTextInput button {
            display: none !important;
        }
        /* Checkbox Clássica Windows 2000 */
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stCheckbox {
            padding: 10px 10px 12px 10px !important;
            margin: 0 !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stCheckbox label {
            display: flex !important;
            align-items: center !important;
            gap: 6px !important;
            min-height: 0 !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stCheckbox label span[data-baseweb="checkbox"] {
            width: 13px !important;
            height: 13px !important;
            min-width: 13px !important;
            min-height: 13px !important;
            border-radius: 0px !important;
            background-color: #FFFFFF !important;
            border-top: 1px solid #808080 !important;
            border-left: 1px solid #808080 !important;
            border-right: 1px solid #FFFFFF !important;
            border-bottom: 1px solid #FFFFFF !important;
            box-shadow: inset 1px 1px 0px #404040 !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stCheckbox label span[data-baseweb="checkbox"] svg {
            fill: #000000 !important;
            color: #000000 !important;
            width: 11px !important;
            height: 11px !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stCheckbox label p {
            color: #000000 !important;
            font-size: 11px !important;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important;
            line-height: 13px !important;
            margin: 0 !important;
            white-space: nowrap !important;
        }
        /* Botões OK (com borda preta de foco) e Cancelar */
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) [data-testid="stHorizontalBlock"] {
            gap: 10px !important;
            padding: 0 42px !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) [data-testid="stHorizontalBlock"] [data-testid="column"] {
            padding: 0 !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stButton button {
            background-color: #D4D0C8 !important;
            color: #000000 !important;
            border-radius: 0px !important;
            border-top: 1px solid #FFFFFF !important;
            border-left: 1px solid #FFFFFF !important;
            border-right: 1px solid #404040 !important;
            border-bottom: 1px solid #404040 !important;
            box-shadow: inset -1px -1px 0px #808080 !important;
            height: 22px !important;
            min-height: 22px !important;
            width: 75px !important;
            min-width: 75px !important;
            padding: 0px !important;
            font-size: 11px !important;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif !important;
            display: block !important;
            margin: 0 auto !important;
        }
        /* Destaque do botão padrão OK (contorno externo preto + pontilhado interno) */
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child .stButton button {
            outline: 1px solid #000000 !important;
            outline-offset: -1px !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stButton button p {
            font-size: 11px !important;
            color: #000000 !important;
            margin: 0 !important;
            line-height: 20px !important;
            white-space: nowrap !important;
        }
        [data-testid="stHorizontalBlock"]:has(.act-titlebar) .stButton button:active {
            border-top: 1px solid #404040 !important;
            border-left: 1px solid #404040 !important;
            border-right: 1px solid #FFFFFF !important;
            border-bottom: 1px solid #FFFFFF !important;
            box-shadow: inset 1px 1px 0px #808080 !important;
        }
        .act-msg-erro {
            color: #800000;
            font-size: 11px;
            text-align: center;
            padding-top: 6px;
            font-family: 'Tahoma', 'MS Sans Serif', Arial, sans-serif;
        }
        </style>
    """
    st.markdown(css_login, unsafe_allow_html=True)

    _, col_modal, _ = st.columns([1, 0.3, 1])

    with col_modal:
        st.markdown("""
            <div class="act-titlebar">
                <span>Entrar em Banco.dbf</span>
                <span class="act-close-btn">×</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="act-label">Digite seu <u>n</u>ome de usuário para este banco de dados:</div>', unsafe_allow_html=True)
        user_input = st.text_input("user_label", value="Hamilton Flecha", key="user_key", label_visibility="collapsed")

        st.markdown('<div class="act-label act-label-pass">Digite sua <u>s</u>enha para este banco de dados:</div>', unsafe_allow_html=True)
        senha_input = st.text_input("pass_label", type="password", key="pass_key", label_visibility="collapsed")

        st.checkbox("Lembrar senha", value=True, key="rem_key")

        b_ok, b_cancel = st.columns(2)
        with b_ok:
            btn_ok = st.button("OK", key="btn_ok_act")
        with b_cancel:
            btn_cancel = st.button("Cancelar", key="btn_cancel_act")

        if btn_ok:
            if senha_input == "solucoes1986":
                st.session_state["autenticado"] = True
                st.session_state["operador_atual"] = user_input
                st.rerun()
            else:
                st.markdown('<div class="act-msg-erro">Senha inválida para Banco.dbf.</div>', unsafe_allow_html=True)
        if btn_cancel:
            st.markdown('<div class="act-msg-erro">Entrada cancelada.</div>', unsafe_allow_html=True)

    st.stop()

# -----------------------------------------------------------------------------
# 2. FUNÇÕES DE DADOS E LEITURA
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

with aba_tabela:
    st.subheader("Base Consolidação Geral")
    if not df_unificada.empty:
        busca_tab = st.text_input("Filtrar Tabela:", placeholder="Filtrar dados...")
        if busca_tab:
            res_tab = df_unificada[df_unificada.astype(str).apply(lambda x: x.str.contains(busca_tab, case=False)).any(axis=1)]
            st.dataframe(res_tab, use_container_width=True)
        else:
            st.dataframe(df_unificada.head(100), use_container_width=True)

with aba_quarentena:
    st.subheader("Contatos com Anotações Diferentes entre PC 1 (Hamilton) e PC 2 (Jaedna)")
    if not df_quarentena.empty:
        cols_quarantena = [c for c in ['NAME', 'ORIGEM', 'USER9', 'PHONE'] if c in df_quarentena.columns]
        st.dataframe(df_quarentena[cols_quarantena], use_container_width=True)
    else:
        st.success("Nenhum contato em quarentena! Todas as fichas foram unificadas sem divergências.")
