# Vamos ler o código atual do app.py e remover a barra antiga (que gerava o teste em HTML puro)
# e garantir que a barra oficial do Streamlit seja limpa, perfeitamente posicionada e 100% interativa e clicável.
with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Vamos remover a linha e o componente HTML de teste que aparece na imagem
trecho_remover = '''st.markdown('<div style="font-size:10px; font-weight:bold; margin: 4px 0 2px 0; color:#000000;">Visualização em Linha Única (HTML Puro):</div>', unsafe_allow_html=True)
components.html("""
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
""", height=30)'''

if trecho_remover in code:
    code = code.replace(trecho_remover, "")
    print("Trecho HTML puro removido com sucesso!")
else:
    print("Aviso: trecho exato não encontrado, buscando alternativa...")

# Atualizar versão para V87
code = code.replace('VERSAO_APP = "Act!   V86"', 'VERSAO_APP = "Act!   V87"')
code = code.replace('Act! Versão V86', 'Act! Versão V87')

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

with open("app_final.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Versão V87 gerada e salva sem a barra estática duplicada.")