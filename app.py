import streamlit as st
import streamlit.components.v1 as components

# Configuração de página em tela cheia (Wide Mode)
st.set_page_config(
    page_title="Act V31 - Soluções",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Base de Dados Atualizada e Sincronizada (Ernerita: CPF 69199485672)
BASE_DADOS = [
    {
        "nome": "HOMIR ALVES DA SILVA",
        "primeiro_nome": "HOMIR",
        "gosta_chamado": "HOMIR",
        "data_visita": "10/11/2026",
        "resumo": "INSS HOMIR ALVES DA SILVA 00385663897 62",
        "loja": "Centro - OB",
        "atendido_por": "Hamilton",
        "orgao": "INSS",
        "num_beneficio": "1234567890",
        "especie": "42",
        "senha_inss": "",
        "senha_parana": "",
        "data_nasc": "15/05/1964",
        "idade": 62,
        "identidade": "MG-12.345.678",
        "cpf": "00385663897",
        "cpf_fmt": "003.856.638-97",
        "endereco": "RUA PRINCIPAL, 500",
        "bairro": "CENTRO",
        "uf": "MG",
        "ddd": "31",
        "tel": "99887766",
        "ref": "PROXIMO AO BANCO",
        "cidade": "OURO BRANCO",
        "cep": "36420-000",
        "edificio": "",
        "tels_consolidados": "3199887766"
    },
    {
        "nome": "ERNERITA MARIA DOS SANTOS",
        "primeiro_nome": "ERNERITA",
        "gosta_chamado": "DONA ERNERITA",
        "data_visita": "08/11/2026",
        "resumo": "INSS ERNERITA MARIA DOS SANTOS 69199485672 71",
        "loja": "Centro - OB",
        "atendido_por": "Jaedna",
        "orgao": "INSS",
        "num_beneficio": "9871234560",
        "especie": "41",
        "senha_inss": "",
        "senha_parana": "",
        "data_nasc": "20/03/1955",
        "idade": 71,
        "identidade": "MG-32.165.498",
        "cpf": "69199485672",
        "cpf_fmt": "691.994.856-72",
        "endereco": "RUA DAS MONÇÕES, 120",
        "bairro": "BELO HORIZONTE",
        "uf": "MG",
        "ddd": "31",
        "tel": "37412233",
        "ref": "PERTO DA IGREJA",
        "cidade": "OURO BRANCO",
        "cep": "36420-000",
        "edificio": "",
        "tels_consolidados": "3137412233"
    },
    {
        "nome": "B HAMILTON DE SOUZA",
        "primeiro_nome": "HAMILTON",
        "gosta_chamado": "B HAMILTON",
        "data_visita": "02/11/2026",
        "resumo": "INSS B HAMILTON DE SOUZA 11122233344 55",
        "loja": "Centro - OB",
        "atendido_por": "Hamilton",
        "orgao": "INSS",
        "num_beneficio": "1112223334",
        "especie": "42",
        "senha_inss": "",
        "senha_parana": "",
        "data_nasc": "14/07/1971",
        "idade": 55,
        "identidade": "MG-11.122.233",
        "cpf": "11122233344",
        "cpf_fmt": "111.222.333-44",
        "endereco": "RUA DOS INCONFIDENTES, 88",
        "bairro": "PIONEIROS",
        "uf": "MG",
        "ddd": "31",
        "tel": "987651234",
        "ref": "",
        "cidade": "OURO BRANCO",
        "cep": "36420-000",
        "edificio": "",
        "tels_consolidados": "31987651234"
    },
    {
        "nome": "HAMILTON SILVA",
        "primeiro_nome": "HAMILTON",
        "gosta_chamado": "HAMILTON",
        "data_visita": "05/11/2026",
        "resumo": "INSS HAMILTON SILVA 98765432100 50",
        "loja": "Centro - OB",
        "atendido_por": "Jaedna",
        "orgao": "INSS",
        "num_beneficio": "9876543210",
        "especie": "21",
        "senha_inss": "",
        "senha_parana": "",
        "data_nasc": "10/02/1976",
        "idade": 50,
        "identidade": "MG-98.765.432",
        "cpf": "98765432100",
        "cpf_fmt": "987.654.321-00",
        "endereco": "AVENIDA CENTRAL, 100",
        "bairro": "SÃO SEBASTIÃO",
        "uf": "MG",
        "ddd": "31",
        "tel": "37429999",
        "ref": "",
        "cidade": "CONSELHEIRO LAFAIETE",
        "cep": "36400-000",
        "edificio": "",
        "tels_consolidados": "3137429999"
    },
    {
        "nome": "HAMILTON FERREIRA DA COSTA",
        "primeiro_nome": "HAMILTON",
        "gosta_chamado": "HAMILTON",
        "data_visita": "01/11/2026",
        "resumo": "INSS HAMILTON FERREIRA DA COSTA 45678912300 58",
        "loja": "Centro - OB",
        "atendido_por": "Hamilton",
        "orgao": "INSS",
        "num_beneficio": "4567891230",
        "especie": "41",
        "senha_inss": "",
        "senha_parana": "",
        "data_nasc": "22/08/1968",
        "idade": 58,
        "identidade": "MG-45.678.912",
        "cpf": "45678912300",
        "cpf_fmt": "456.789.123-00",
        "endereco": "RUA DAS FLORES, 50",
        "bairro": "SANTANENSE",
        "uf": "MG",
        "ddd": "31",
        "tel": "988776655",
        "ref": "",
        "cidade": "OURO BRANCO",
        "cep": "36420-000",
        "edificio": "",
        "tels_consolidados": "31988776655"
    },
    {
        "nome": "CALMA DA SILVA MNIRANDA",
        "primeiro_nome": "CALMA",
        "gosta_chamado": "CALMA",
        "data_visita": "",
        "resumo": "INSS CALMA DA SILVA MNIRANDA 67570437691 45",
        "loja": "Centro - OB",
        "atendido_por": "",
        "orgao": "INSS",
        "num_beneficio": "",
        "especie": "41",
        "senha_inss": "",
        "senha_parana": "",
        "data_nasc": "",
        "idade": 45,
        "identidade": "",
        "cpf": "67570437691",
        "cpf_fmt": "675.704.376-91",
        "endereco": "RUA AÇONORTE, 314",
        "bairro": "",
        "uf": "MG",
        "ddd": "31",
        "tel": "37421019",
        "ref": "",
        "cidade": "OURO BRANCO",
        "cep": "",
        "edificio": "",
        "tels_consolidados": "3137421019"
    }
]

# Função de busca universal por palavra-chave parcial
def buscar_contactos(termo):
    if not termo:
        return []
    termo_clean = termo.strip().lower()
    resultados = []
    for item in BASE_DADOS:
        if (termo_clean in item["nome"].lower() or 
            termo_clean in item["cpf"].lower() or 
            termo_clean in item["primeiro_nome"].lower() or
            termo_clean in item["resumo"].lower() or
            termo_clean in item["num_beneficio"].lower()):
            resultados.append(item)
    return resultados

# Inicialização do estado da sessão
if "contacto_atual" not in st.session_state:
    st.session_state["contacto_atual"] = BASE_DADOS[0]

# Estilização CSS do Layout ACT!
st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #ece9d8 !important;
        }

        .main .block-container {
            padding: 0.3rem 0.5rem !important;
            max-width: 100% !important;
        }

        .stTextInput label {
            font-size: 11px !important;
            font-weight: bold !important;
            color: #000000 !important;
            margin-bottom: 2px !important;
            white-space: nowrap !important;
        }

        input[data-testid="stTextInputInput"] {
            height: 38px !important;
            min-height: 38px !important;
            max-height: 38px !important;
            font-size: 12px !important;
            padding: 0px 8px !important;
            background-color: #ffffff !important;
            border: 1px solid #7f9db9 !important;
            color: #000000 !important;
        }

        [data-testid="column"] {
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-end !important;
            padding: 0px 2px !important;
            min-width: 0px !important;
        }

        .stButton {
            margin-top: 0px !important;
            margin-bottom: 0px !important;
            width: 100% !important;
        }

        .stButton > button {
            height: 38px !important;
            min-height: 38px !important;
            line-height: 36px !important;
            font-size: 11px !important;
            padding: 0px 4px !important;
            margin: 0px !important;
            background-color: #d4d0c8 !important;
            border: 1px solid #404040 !important;
            color: #000000 !important;
            font-weight: bold !important;
            width: 100% !important;
        }

        div[data-testid="stVerticalBlock"] > div {
            gap: 2px !important;
            margin-bottom: 2px !important;
        }
        
        header[data-testid="stHeader"], footer {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# Função para gerar os campos com Botão Copiar + Célula com Tique Verde (#c3e6cb)
def campo_com_copia_tique(label, valor, key_prefix):
    html_code = f"""
    <div style="font-family: sans-serif; margin: 0px; padding: 0px;">
        <label style="font-size: 11px; font-weight: bold; color: #000; display: block; height: 15px; line-height: 15px; white-space: nowrap; margin-bottom: 2px;">{label}</label>
        <table style="border-collapse: collapse; width: 100%; table-layout: fixed; margin: 0px; padding: 0px;">
            <tr style="height: 38px;">
                <td style="padding: 0px; margin: 0px;">
                    <input type="text" id="input_{key_prefix}" value="{valor}" style="width: 100%; height: 38px; font-size: 12px; padding: 0 8px; border: 1px solid #7f9db9; border-right: none; border-top-left-radius: 4px; border-bottom-left-radius: 4px; box-sizing: border-box; background: #fff; color: #000; outline: none;">
                </td>
                <td style="width: 32px; padding: 0px; margin: 0px;">
                    <button onclick="copiarComTique('{key_prefix}')" style="width: 32px; height: 38px; font-size: 12px; background: #d4d0c8; border: 1px solid #7f9db9; border-left: 1px solid #ccc; cursor: pointer; font-weight: bold; padding: 0px; box-sizing: border-box;">📋</button>
                </td>
                <td id="cell_tique_{key_prefix}" style="width: 25px; padding: 0px; margin: 0px; text-align: center; background: #ece9d8; border: 1px solid #7f9db9; border-left: none; border-top-right-radius: 4px; border-bottom-right-radius: 4px;">
                    <span id="tique_{key_prefix}" style="font-size: 13px; font-weight: bold; color: #155724; display: none;">✔</span>
                </td>
            </tr>
        </table>
    </div>
    <script>
        function copiarComTique(key) {{
            var copyText = document.getElementById("input_" + key).value;
            navigator.clipboard.writeText(copyText);
            var cell = document.getElementById("cell_tique_" + key);
            var tique = document.getElementById("tique_" + key);
            cell.style.backgroundColor = "#c3e6cb";
            tique.style.display = "inline";
            setTimeout(function() {{
                cell.style.backgroundColor = "#ece9d8";
                tique.style.display = "none";
            }}, 2000);
        }}
    </script>
    """
    components.html(html_code, height=58)

# Topo / Navegação (Localizar + Buscar Embutidos na Mesma Tabela Unificada de 38px)
c_busca_box, c_prev, c_next, c_novo, c_status = st.columns([5.0, 0.8, 0.8, 1.8, 2.5])

with c_busca_box:
    termo = st.text_input("Localizar (Nome / CPF / Benefício):", key="campo_busca")

with c_prev:
    st.button("◄ Ant...", use_container_width=True)
with c_next:
    st.button("Próx...", use_container_width=True)
with c_novo:
    st.button("+ Novo Contato", use_container_width=True)
with c_status:
    st.markdown("<div style='text-align: right; font-size: 11px; font-weight: bold; color: #000;'>Act V31<br><span style='font-size: 10px; font-weight: normal;'>Hamilton e Jaedna | Soluções</span></div>", unsafe_allow_html=True)

# Lógica da Pesquisa com Pop-up (Modal) Automático
if termo and len(termo.strip()) > 0:
    resultados = buscar_contactos(termo)
    if len(resultados) == 1:
        st.session_state["contacto_atual"] = resultados[0]
    elif len(resultados) > 1:
        @st.dialog("Selecione o Contato Encontrado")
        def popup_selecao(lista):
            st.write(f"Foram encontrados **{len(lista)}** contatos para a busca: **'{termo}'**")
            for idx, c in enumerate(lista):
                if st.button(f"👤 {c['nome']} - CPF: {c['cpf_fmt']} (Espécie: {c['especie']})", key=f"sel_{idx}"):
                    st.session_state["contacto_atual"] = c
                    st.rerun()
        popup_selecao(resultados)

contacto = st.session_state["contacto_atual"]
idade_108_meses = contacto["idade"] + 9 if contacto["idade"] else ""

# Linha 1: Nome, 1º Nome, Gosta de ser chamado por, Data da visita
c1, c2, c3, c4 = st.columns([580, 200, 160, 100])
with c1:
    campo_com_copia_tique("Nome", contacto["nome"], "nome")
with c2:
    st.text_input("1º Nome", value=contacto.get("primeiro_nome", ""))
with c3:
    st.text_input("Gosta de ser chamado por", value=contacto.get("gosta_chamado", ""))
with c4:
    st.text_input("Data da visita", value=contacto.get("data_visita", ""))

# Linha 2: Nome sem acentos
c_sa, c_empty = st.columns([580, 460])
with c_sa:
    campo_com_copia_tique("Nome (Sem Acentos)", contacto["nome"], "sa")

# Linha 3: Resumo
c_res = st.container()
with c_res:
    campo_com_copia_tique("Resumo (Órgão Nome CPF Idade)", contacto["resumo"], "res")

# Linha 4: Loja, Atendido por, Órgão, Nº benefício, Espécie
col_loja, col_atend, col_org, col_ben, col_esp = st.columns([180, 220, 120, 240, 100])
with col_loja:
    st.text_input("Loja", value=contacto.get("loja", ""))
with col_atend:
    st.text_input("Atendido por", value=contacto.get("atendido_por", ""))
with col_org:
    st.text_input("Órgão", value=contacto.get("orgao", ""))
with col_ben:
    campo_com_copia_tique("Nº benefício ou matrícula", contacto.get("num_beneficio", ""), "ben")
with col_esp:
    st.text_input("Espécie", value=contacto.get("especie", ""))

# Linha 5: Senha Meu INSS, Senha Paraná, Data Nascimento, Idade, 108 Meses, Identidade
col_s1, col_s2, col_dn, col_id, col_id108, col_rg = st.columns([160, 160, 180, 50, 60, 160])
with col_s1:
    st.text_input("Senha Meu INSS", value=contacto.get("senha_inss", ""))
with col_s2:
    st.text_input("Senha Paraná", value=contacto.get("senha_parana", ""))
with col_dn:
    campo_com_copia_tique("Data Nascimento", contacto.get("data_nasc", ""), "dn")
with col_id:
    st.text_input("Idade", value=str(contacto.get("idade", "")))
with col_id108:
    st.text_input("108 Meses", value=str(idade_108_meses))
with col_rg:
    st.text_input("Identidade", value=contacto.get("identidade", ""))

# Linha 6: CPF Números, CPF Formatado
col_cpf, col_cpff, col_empty2 = st.columns([220, 240, 430])
with col_cpf:
    campo_com_copia_tique("CGC/CPF (Números)", contacto["cpf"], "cpf")
with col_cpff:
    campo_com_copia_tique("CGC/CPF (Formatado)", contacto["cpf_fmt"], "cpff")

# Linha 7: Endereço 1, Bairro 1, UF, DDD, Tel_1, Ref_1
c_end, c_bai, c_uf, c_ddd, c_tel, c_ref = st.columns([350, 200, 40, 40, 190, 180])
with c_end:
    st.text_input("Endereço 1", value=contacto.get("endereco", ""))
with c_bai:
    st.text_input("Bairro 1", value=contacto.get("bairro", ""))
with c_uf:
    st.text_input("UF", value=contacto.get("uf", ""))
with c_ddd:
    st.text_input("DDD", value=contacto.get("ddd", ""))
with c_tel:
    campo_com_copia_tique("Tel_1", contacto.get("tel", ""), "tel")
with c_ref:
    st.text_input("Ref_1", value=contacto.get("ref", ""))

# Linha 8: Cidade 1, Cep 1, Edifício, Telefones Consolidados
c_cid, c_cep, c_edi, c_tels = st.columns([220, 100, 200, 320])
with c_cid:
    st.text_input("Cidade 1", value=contacto.get("cidade", ""))
with c_cep:
    st.text_input("Cep 1", value=contacto.get("cep", ""))
with c_edi:
    st.text_input("Edifício", value=contacto.get("edificio", ""))
with c_tels:
    campo_com_copia_tique("Telefones Consolidados", contacto.get("tels_consolidados", ""), "tels")