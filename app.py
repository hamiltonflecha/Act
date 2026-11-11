import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Act V33 - Soluções", page_icon="📑", layout="wide", initial_sidebar_state="expanded")

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
# 2. TRATAMENTO DE TEXTO E LEITURA DE ARQUIVOS
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

# Inicializar dados na sessão
if "df_unificada" not in st.session_state or "df_quarentena" not in st.session_state:
    st.session_state["df_unificada"], st.session_state["df_quarentena"] = executar_fusao()

if "idx_cliente" not in st.session_state:
    st.session_state["idx_cliente"] = 0

df_unificada = st.session_state["df_unificada"]
df_quarentena = st.session_state["df_quarentena"]

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL (MENU E BOTÃO DE FUSÃO SOB DEMANDA)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Painel de Controle")
    st.markdown("**Sistema Act V33**")
    st.markdown("👥 **Operadores:** Hamilton & Jaedna")
    st.markdown("---")
    st.write(f"📊 **Base Unificada:** {len(df_unificada)} fichas")
    st.write(f"⚠️ **Quarentena:** {len(df_quarentena)} fichas")
    st.markdown("---")
    if st.button("🔄 Recalcular / Atualizar Bases", use_container_width=True):
        with st.spinner("Refazendo a fusão das bases..."):
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

# ----- ABA 1: INTERFACE ZEROSCROLL DO ACT! -----
with aba_ficha:
    if not df_unificada.empty:
        c_busca, c_prev, c_pos, c_next = st.columns([3, 1, 1, 1])
        
        with c_busca:
            termo_busca = st.text_input("🔍 Buscar por Nome, CPF ou Benefício:", placeholder="Digite para filtrar...", label_visibility="collapsed")
            
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
                st.subheader(f"📄 CPF: {cpf_formatado}")
            with col_copy:
                st.code(cpf_limpo if cpf_limpo else "SEM_CPF", language=None)
                
            g1, g2, g3 = st.columns(3)
            with g1:
                st.text_input("Telefone (PHONE):", value=cliente.get('PHONE', ''), disabled=True)
                st.text_input("Endereço (ADDR1):", value=cliente.get('ADDR1', ''), disabled=True)
            with g2:
                st.text_input("Bairro (ADDR3):", value=cliente.get('ADDR3', ''), disabled=True)
                st.text_input("Cidade / UF:", value=f"{cliente.get('CITY', '')} / {cliente.get('STATE', '')}", disabled=True)
            with g3:
                st.text_input("CEP (ZIP):", value=cliente.get('ZIP', ''), disabled=True)
                st.text_input("Origem do Registro:", value=cliente.get('ORIGEM', 'Unificado'), disabled=True)

            st.markdown("### 📝 Histórico / Observações (USER9)")
            st.text_area("USER9", value=cliente.get('USER9', ''), height=140, label_visibility="collapsed", disabled