import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Teste de Conectividade - Soluções",
    page_icon="🌐",
    layout="centered"
)

st.title("🌐 Teste de Conectividade e Rota")
st.subtitle("Página de Verificação para Suporte Técnico da CN Telecom")

st.success("✅ Conexão com o servidor Render estabelecida com sucesso!")

st.write("---")

st.markdown("### 📊 Status do Sistema")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Status do Servidor", value="ONLINE")
with col2:
    st.metric(label="Protocolo HTTP/HTTPS", value="Ativo")

st.write("---")

st.markdown("""
### ℹ️ Informações Técnicas para a TI
* **Plataforma de Hospedagem:** Render Cloud Services
* **Aplicação:** Streamlit Python Web Server
* **Objetivo:** Confirmar que as rotas de tráfego e resolução DNS da rede local estão alcançando o domínio `*.onrender.com` através dos navegadores padrão (Chrome, Edge, Firefox e Opera).
""")

st.caption(f"Verificação gerada em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")