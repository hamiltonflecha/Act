import streamlit as st
import pandas as pd
import numpy as np
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

# Função de fusão executada apenas sob demanda
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

# Inicializar estado dos dados na memória do navegador
if "df_unificada" not in st.session_state or "df_quarentena" not in st.session_state:
    st.session_state["df_unificada"], st.session_state["df_quarentena"] = executar_fusao()

df_unificada = st.session_state["df_unificada"]
df_quarentena = st.session_state["df_quarentena"]

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL (CONTROLE E REPROCESSAMENTO)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.subheader("⚙️ Gerenciamento de Bases")
    st.write(f"Contatos Unificados: **{len(df_unificada)}**")
    st.write(f"Em Quarentena: **{len(df_quarentena)}**")
    st.markdown("---")
    if st.button("🔄 Recalcular / Atualizar Bases", use_container_width=True):
        with st.spinner("Refazendo a fusão dos arquivos Excel..."):
            st.session_state["df_unificada"], st.session_state["df_quarentena"] = executar_fusao()
            st.success("Bases atualizadas com sucesso!")
            st.rerun()

# -----------------------------------------------------------------------------
# 4. INTERFACE PRINCIPAL
# -----------------------------------------------------------------------------
aba_ficha, aba_tabela, aba_quarentena = st.tabs([
    "👤 Ficha Act! (Trabalho)", 
    f"📊 Tabela Unificada ({len(df_unificada)})", 
    f"⚠️ Quarentena / Revisão ({len(df_quarentena)})"
])

# ----- ABA 1: INTERFACE DE TRABALHO -----
with aba_ficha:
    st.title("Act! Soluções - Ficha do Cliente")
    
    if not df_unificada.empty:
        busca_input = st.text_input("🔍 Buscar por CPF, Nome ou Benefício:", placeholder="Digite o CPF ou Nome e pressione Enter...")
        
        if busca_input:
            res = df_unificada[df_unificada.astype(str).apply(lambda x: x.str.contains(busca_input, case=False)).any(axis=1)]
            
            if not res.empty:
                if len(res) > 1:
                    opcoes = [f"{row.get('NAME', 'Sem Nome')} - CPF: {formatar_cpf(limpar_cpf(row.get('USR1000', '')))}" for _, row in res.iterrows()]
                    escolha = st.selectbox("Selecione o registro encontrado:", opcoes)
                    idx = opcoes.index(escolha)
                    cliente = res.iloc[idx]
                else:
                    cliente = res.iloc[0]
                
                st.markdown("---")
                cpf_bruto = cliente.get('USR1000', cliente.get('CPF', ''))
                cpf_limpo = limpar_cpf(cpf_bruto)
                cpf_formatado = formatar_cpf(cpf_limpo)
                
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    st.markdown(f"### 👤 **{cliente.get('NAME', 'N/A')}**")
                with c2:
                    st.markdown(f"### 📄 **CPF: {cpf_formatado}**")
                with c3:
                    st.code(cpf_limpo, language=None)
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.markdown("**Telefone Principal:**")
                    st.info(cliente.get('PHONE', 'Não informado'))
                    st.markdown("**Endereço (ADDR1):**")
                    st.write(cliente.get('ADDR1', '-'))
                with col_b:
                    st.markdown("**Bairro / Região (ADDR3):**")
                    st.write(cliente.get('ADDR3', '-'))
                    st.markdown("**Cidade / Estado:**")
                    st.write(f"{cliente.get('CITY', '-')} / {cliente.get('STATE', '-')}")
                with col_c:
                    st.markdown("**CEP:**")
                    st.write(cliente.get('ZIP', '-'))
                    st.markdown("**Origem:**")
                    st.caption(cliente.get('ORIGEM', 'Base Unificada'))
                
                st.markdown("---")
                st.markdown("### 📝 Observações / Histórico (USER9)")
                st.text_area("", value=cliente.get('USER9', ''), height=150, disabled=True)
                
                with st.expander("🛠️ Ver todos os 183 campos da ficha completa"):
                    df_campos = pd.DataFrame(list(cliente.items()), columns=["Campo", "Valor"])
                    st.dataframe(df_campos, use_container_width=True, height=400)
            else:
                st.warning("Nenhum cliente encontrado com esse termo de busca.")
        else:
            st.info("Digite um Nome ou CPF na caixa acima para abrir a ficha de trabalho zeroscroll.")

# ----- ABA 2: VISUALIZAÇÃO EM TABELA COMPLETA -----
with aba_tabela:
    st.subheader("Base Geral Consolidada")
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
        colunas_exibir = [c for c in ['NAME', 'ORIGEM', 'USER9', 'PHONE'] if c in df_quarentena.columns]
        st.dataframe(df_quarentena[colunas_exibir], use_container_width=True)
    else:
        st.success("Nenhum contacto em quarentena! Todas as fichas foram unificadas sem divergências.")