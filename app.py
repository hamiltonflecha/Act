# Vamos corrigir a tela de login na versão V89 para restaurar o design compacto original e perfeito (cantos retos, botões corretos, sem bordas arredondadas e com o layout idêntico ao que o Hamilton usava na V85).
# Vamos ler o app.py atual e ajustar o bloco de login e estilos CSS.

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Vamos restaurar o CSS de login exato e perfeito da versão clássica compacta:
css_login_perfeito = '''        <style>
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
        [data-testid="stForm"] button p { font-size: 11px !important; color: #000000 !important; margin: 0 !important; }
        .act-msg-erro { color: #800000; font-size: 11px; text-align: center; padding-top: 8px; }
        </style>'''

# Substituir o bloco css_login no código
start_idx = code.find("css_login = \"\"\"")
end_idx = code.find("    st.markdown(css_login, unsafe_allow_html=True)")

if start_idx != -1 and end_idx != -1:
    code = code[:start_idx] + f"css_login = '''\n{css_login_perfeito}\n    '''\n" + code[end_idx:]

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

with open("app_final.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Tela de login corrigida e restaurada para o padrão clássico exato!")