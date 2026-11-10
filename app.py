import streamlit as st
import streamlit.components.v1 as components

# Configuração de página em tela cheia (Wide Mode)
st.set_page_config(
    page_title="Act V26 - Soluções",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Base de Dados Atualizada (Com CPF correto do Homir e cadastro do Hamilton)
BASE_DADOS = [
    {
        "nome": "HOMIR ALVES DA SILVA",
        "primeiro_nome": "HOMIR",
        "resumo": "INSS HOMIR ALVES DA SILVA 00385663897 62",
        "loja": "Centro - OB",
        "orgao": "INSS",
        "idade": 62,
        "cpf": "00385663897",
        "cpf_fmt": "003.856.638-97",
        "endereco": "RUA PRINCIPAL, 500",
        "uf": "MG",
        "ddd": "31",
        "tel": "99887766",
        "cidade": "OURO BRANCO"
    },
    {
        "nome": "HAMILTON SILVA",
        "primeiro_nome": "HAMILTON",
        "resumo": "INSS HAMILTON SILVA 98765432100 50",
        "loja": "Centro - OB",
        "orgao": "INSS",
        "idade": 50,
        "cpf": "98765432100",
        "cpf_fmt": "987.654.321-00",
        "endereco": "AVENIDA CENTRAL, 100",
        "uf": "MG",
        "ddd": "31",
        "tel": "37429999",
        "cidade": "CONSELHEIRO LAFAIETE"
    },
    {
        "nome": "CALMA DA SILVA MNIRANDA",
        "primeiro_nome": "CALMA",
        "resumo": "INSS CALMA DA SILVA MNIRANDA 67570437691 45",
        "loja": "Centro - OB",
        "orgao": "INSS",
        "idade": 45,
        "cpf": "67570437691",
        "cpf_fmt": "675.704.376-91",
        "endereco": "RUA AÇONORTE, 314",
        "uf": "MG",
        "ddd": "31",
        "tel": "37421019",
        "cidade": "OURO BRANCO"
    }
]

# Função para pesquisar na base (Nome, CPF, 1º Nome, etc.)
def pesquisar_contacto(termo):
    if not termo:
        return BASE_DADOS[0]
    termo_clean = termo.strip().lower()
    for item in BASE_DADOS:
        if (termo_clean in item["nome"].lower() or 
            termo_clean in item["cpf"] or 
            termo_clean in item["primeiro_nome"].lower()):
            return item
    return BASE_DADOS[0]

# Inicialização do estado da sessão
if "contacto_atual" not in st.session_state:
    st.session_state["contacto_atual"] = BASE_DADOS[0]

# Estilização CSS do Layout ACT!
st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #ece9d8 !important;
            overflow: hidden !important;
        }

        .main .block-container {
            padding: 0.2rem 0.4rem !important;
            max-width: 100% !important;
        }

        div[data-baseweb="input"], div[data-baseweb="base-input"] {
            background-color: transparent !important;
            border: none !important;
            padding: 0px !important;
            margin: 0px !important;
            box-shadow: none !important;
        }

        .stTextInput label {
            font-size: 10.5px !important;
            font-weight: bold !important;
            color: #000000 !important;
            margin-bottom: 0px !important;
            height: 13px !important;
            line-height: 13px !important;
            white-space: nowrap !important;
        }

        input[data-testid="stTextInputInput"] {
            height: 19px !important;
            min-height: 19px !important;
            max-height: 19px !important;
            font-size: 11px !important;
            padding: 0px 3px !important;
            line-height: 19px !important;
            background-color: #ffffff !important;
            border: 1px solid #7f9db9 !important;
            border-radius: 0px !important;
            color: #000000 !important;
            box-shadow: none !important;
        }

        [data-testid="column"] {
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-end !important;
            padding: 0px 1px !important;
            min-width: 0px !important;
        }

        .stButton {
            margin-top: 0px !important;
            margin-bottom: 0px !important;
            width: 100% !important;
        }

        .stButton > button {
            height: 19px !important;
            min-height: 19px !important;
            line-height: 17px !important;
            font-size: 10px !important;
            padding: 0px 2px !important;
            margin: 0px !important;
            background-color: #d4d0c8 !important;
            border: 1px solid #404040 !important;
            color: #000000 !important;
            border-radius: 0px !important;
            font-weight: bold !important;
            width: 100% !important;
        }

        div[data-testid="stVerticalBlock"] > div {
            gap: 0px !important;
            margin-bottom: 0px !important;
        }
        
        header[data-testid="stHeader"], footer {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# Função para gerar a tabela de 1 linha e 3 células (Campo + Botão Copiar + Tique de Confirmação)
def campo_com_copia_tique(label, valor, key_prefix):
    html_code = f"""
    <div style="font-family: sans-serif; margin: 0px; padding: 0px;">
        <label style="font-size: 10.5px; font-weight: bold; color: #000; display: block; height: 13px; line-height: 13px; white-space: nowrap; margin-bottom: 0px;">{label}</label>
        <table style="border-collapse: collapse; width: 100%; table-layout: fixed; margin: 0px; padding: 0px;">
            <tr style="height: 19px;">
                <td style="padding: 0px; margin: 0px;">
                    <input type="text" id="input_{key_prefix}" value="{valor}" style="width: 100%; height: 19px; font-size: 11px; padding: 0 3px; border: 1px solid #7f9db9; border-right: none; box-sizing: border-box; background: #fff; color: #000; outline: none;">
                </td>
                <td style="width: 22px; padding: 0px; margin: 0px;">
                    <button onclick="copiarComTique('{key_prefix}')" style="width: 22px; height: 19px; font-size: 10px; background: #d4d0c8; border: 1px solid #404040; border-right: none; cursor: pointer; font-weight: bold; padding: 0px; box-sizing: border-box;">📋</button>
                </td>
                <td style="width: 20px; padding: 0px; margin: 0px; text-align: center; background: #ece9d8; border: 1px solid #7f9db9; border-left: none;">
                    <span id="tique_{key_prefix}" style="font-size: 11px; font-weight: bold; color: #008000; display: none;">✔</span>
                </td>
            </tr>
        </table>
    </div>
    <script>
        function copiarComTique(key) {{
            var copyText = document.getElementById("input_" + key).value;
            navigator.clipboard.writeText(copyText);
            var tique = document.getElementById("tique_" + key);
            tique.style.display = "inline";
            setTimeout(function() {{
                tique.style.display = "none";
            }}, 2000);
        }}
    </script>
    """
    components.html(html_code, height=34)

# Topo / Navegação
c_busca, c_btn_busca, c_prev, c_next, c_novo, c_status = st.columns([4.0, 1.0, 0.8, 0.8, 1.8, 2.5])
with c_busca:
    termo = st.text_input("Localizar (Nome / CPF / Benefício):", key="campo_busca")
with c_btn_busca:
    btn_buscar = st.button("🔍 Buscar", key="btn_buscar")
with c_prev:
    st.button("◄ Ant...", use_container_width=True)
with c_next:
    st.button("Próx...", use_container_width=True)
with c_novo:
    st.button("+ Novo Contato", use_container_width=True)
with c_status:
    st.markdown("<div style='text-align: right; font-size: 11px; font-weight: bold; color: #000;'>Act V26<br><span style='font-size: 10px; font-weight: normal;'>Hamilton e Jaedna | Soluções</span></div>", unsafe_allow_html=True)

# Executar Busca ao clicar ou dar Enter
if btn_buscar or termo:
    st.session_state["contacto_atual"] = pesquisar_contacto(termo)

contacto = st.session_state["contacto_atual"]
idade_108_meses = contacto["idade"] + 9 if contacto["idade"] else ""

# Linha 1: Nome (Com Cópia e Tique), 1º Nome, Gosta de ser chamado por, Data da visita
c1, c2, c3, c4 = st.columns([580, 200, 160, 100])
with c1:
    campo_com_copia_tique("Nome", contacto["nome"], "nome")
with c2:
    st.text_input("1º Nome", value=contacto["primeiro_nome"])
with c3:
    st.text_input("Gosta de ser chamado por", value="")
with c4:
    st.text_input("Data da visita", value="")

# Linha 2: Nome sem acentos (Com Cópia e Tique)
c_sa, c_empty = st.columns([580, 460])
with c_sa:
    campo_com_copia_tique("Nome (Sem Acentos)", contacto["nome"], "sa")

# Linha 3: Resumo (Com Cópia e Tique)
c_res = st.container()
with c_res:
    campo_com_copia_tique("Resumo (Órgão Nome CPF Idade)", contacto["resumo"], "res")

# Linha 4: Loja, Atendido por, Órgão, Nº benefício, Espécie
col_loja, col_atend, col_org, col_ben, col_esp = st.columns([180, 220, 120, 200, 100])
with col_loja:
    st.text_input("Loja", value=contacto["loja"])
with col_atend:
    st.text_input("Atendido por", value="")
with col_org:
    st.text_input("Órgão", value=contacto["orgao"])
with col_ben:
    st.text_input("Nº benefício ou matrícula", value="")
with col_esp:
    st.text_input("Espécie", value="")

# Linha 5: Senha Meu INSS, Senha Paraná, Data Nascimento, Idade, 108 Meses, Identidade
col_s1, col_s2, col_dn, col_id, col_id108, col_rg = st.columns([160, 160, 110, 50, 60, 160])
with col_s1:
    st.text_input("Senha Meu INSS", value="")
with col_s2:
    st.text_input("Senha Paraná", value="")
with col_dn:
    st.text_input("Data Nascimento", value="")
with col_id:
    st.text_input("Idade", value=str(contacto["idade"]))
with col_id108:
    st.text_input("108 Meses", value=str(idade_108_meses))
with col_rg:
    st.text_input("Identidade", value="")

# Linha 6: CPF Números (Com Cópia e Tique), CPF Formatado (Com Cópia e Tique)
col_cpf, col_cpff, col_empty2 = st.columns([220, 240, 430])
with col_cpf:
    campo_com_copia_tique("CGC/CPF (Números)", contacto["cpf"], "cpf")
with col_cpff:
    campo_com_copia_tique("CGC/CPF (Formatado)", contacto["cpf_fmt"], "cpff")

# Linha 7: Endereço 1, Bairro 1, UF, DDD, Tel_1 (Com Cópia e Tique), Ref_1
c_end, c_bai, c_uf, c_ddd, c_tel, c_ref = st.columns([350, 200, 40, 40, 190, 180])
with c_end:
    st.text_input("Endereço 1", value=contacto["endereco"])
with c_bai:
    st.text_input("Bairro 1", value="")
with c_uf:
    st.text_input("UF", value=contacto["uf"])
with c_ddd:
    st.text_input("DDD", value=contacto["ddd"])
with c_tel:
    campo_com_copia_tique("Tel_1", contacto["tel"], "tel")
with c_ref:
    st.text_input("Ref_1", value="")

# Linha 8: Cidade 1, Cep 1, Edifício, Telefones Consolidados (Com Cópia e Tique)
c_cid, c_cep, c_edi, c_tels = st.columns([220, 100, 200, 320])
with c_cid:
    st.text_input("Cidade 1", value=contacto["cidade"])
with c_cep:
    st.text_input("Cep 1", value="")
with c_edi:
    st.text_input("Edifício", value="")
with c_tels:
    campo_com_copia_tique("Telefones Consolidados", contacto["tel"], "tels")