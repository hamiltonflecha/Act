with open("app.py", "r", encoding="utf-8") as f:
    src = f.read()

# Atualizar versão para V84
src = src.replace('VERSAO_APP = "Act!   V83"', 'VERSAO_APP = "Act!   V84"')
src = src.replace('Act! Versão V83', 'Act! Versão V84')

# Vamos inserir o componente HTML com a barra unificada como uma terceira linha logo abaixo da barra atual do Streamlit
target_str = "st.markdown('<hr class=\"act-hr\">', unsafe_allow_html=True)"

html_terceira_linha = """
st.markdown('<div style="font-size:10px; font-weight:bold; margin: 4px 0 2px 0; color:#000000;">Visualização em Linha Única (HTML Puro):</div>', unsafe_allow_html=True)
components.html(\"""
<table style="width: 100%; border-collapse: collapse; background-color: #D4D0C8; border-top: 1px solid #FFFFFF; border-left: 1px solid #FFFFFF; border-right: 1px solid #404040; border-bottom: 1px solid #404040; font-family: 'Tahoma', 'MS Sans Serif', sans-serif; font-size: 11px;">
  <tr>
    <td style="padding: 2px; white-space: nowrap;">
      <button style="background-color: #D4D0C8; border-top: 1px solid #FFFFFF; border-left: 1px solid #FFFFFF; border-right: 1px solid #404040; border-bottom: 1px solid #404040; height: 20px; padding: 0 4px; font-size: 11px; cursor: pointer;">&lt;|</button>
      <button style="background-color: #D4D0C8; border-top: 1px solid #FFFFFF; border-left: 1px solid #FFFFFF; border-right: 1px solid #404040; border-bottom: 1px solid #404040; height: 20px; padding: 0 4px; font-size: 11px; cursor: pointer;">&lt;</button>
      <input type="text" value="0 de 0" disabled style="width: 55px; height: 20px; text-align: center; background-color: #FFFFFF; border-top: 1px solid #808080; border-left: 1px solid #808080; border-right: 1px solid #FFFFFF; border-bottom: 1px solid #FFFFFF; font-size: 11px; vertical-align: middle;" />
      <button style="background-color: #D4D0C8; border-top: 1px solid #FFFFFF; border-left: 1px solid #FFFFFF; border-right: 1px solid #404040; border-bottom: 1px solid #404040; height: 20px; padding: 0 4px; font-size: 11px; cursor: pointer;">&gt;</button>
      <button style="background-color: #D4D0C8; border-top: 1px solid #FFFFFF; border-left: 1px solid #FFFFFF; border-right: 1px solid #404040; border-bottom: 1px solid #404040; height: 20px; padding: 0 4px; font-size: 11px; cursor: pointer;">&gt;|</button>
      
      <input type="text" placeholder="Localizar..." style="width: 95px; height: 20px; background-color: #FFFFFF; border: 1px solid #808080; padding: 0 4px; font-size: 11px; vertical-align: middle; margin-left: 4px;" />
      <button style="background-color: #D4D0C8; border-top: 1px solid #FFFFFF; border-left: 1px solid #FFFFFF; border-right: 1px solid #404040; border-bottom: 1px solid #404040; height: 20px; padding: 0 6px; font-size: 11px; cursor: pointer;">Buscar</button>
      
      <button style="background-color: #D4D0C8; border-top: 1px solid #FFFFFF; border-left: 1px solid #FFFFFF; border-right: 1px solid #404040; border-bottom: 1px solid #404040; height: 20px; padding: 0 6px; font-size: 11px; cursor: pointer; margin-left: 2px;">Todos</button>
      <button style="background-color: #D4D0C8; border-top: 1px solid #FFFFFF; border-left: 1px solid #FFFFFF; border-right: 1px solid #404040; border-bottom: 1px solid #404040; height: 20px; padding: 0 6px; font-size: 11px; cursor: pointer;">Novo</button>
      <button style="background-color: #D4D0C8; border-top: 1px solid #FFFFFF; border-left: 1px solid #FFFFFF; border-right: 1px solid #404040; border-bottom: 1px solid #404040; height: 20px; padding: 0 6px; font-size: 11px; cursor: pointer;">Excluir</button>
      <button style="background-color: #D4D0C8; border-top: 1px solid #FFFFFF; border-left: 1px solid #FFFFFF; border-right: 1px solid #404040; border-bottom: 1px solid #404040; height: 20px; padding: 0 6px; font-size: 11px; cursor: pointer;">Tabela</button>
      <button style="background-color: #D4D0C8; border-top: 1px solid #FFFFFF; border-left: 1px solid #FFFFFF; border-right: 1px solid #404040; border-bottom: 1px solid #404040; height: 20px; padding: 0 6px; font-size: 11px; cursor: pointer;">Quarent(0)</button>
      <button style="background-color: #D4D0C8; border-top: 1px solid #FFFFFF; border-left: 1px solid #FFFFFF; border-right: 1px solid #404040; border-bottom: 1px solid #404040; height: 20px; padding: 0 6px; font-size: 11px; cursor: pointer;">Campos</button>
      <button style="background-color: #C6D9F1; border: 1px solid #0A246A; height: 20px; padding: 0 6px; font-size: 11px; font-weight: bold; cursor: pointer;">Unificar</button>
      <button style="background-color: #D4D0C8; border-top: 1px solid #FFFFFF; border-left: 1px solid #FFFFFF; border-right: 1px solid #404040; border-bottom: 1px solid #404040; height: 20px; padding: 0 6px; font-size: 11px; cursor: pointer;">Sair</button>
    </td>
  </tr>
</table>
\""", height=30)
"""

assert target_str in src
src = src.replace(target_str, html_terceira_linha + "\n" + target_str, 1)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(src)

print("app.py atualizado para V84 com a terceira linha HTML adicionada com sucesso!")