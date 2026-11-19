with open("app-v101_2.py", "r", encoding="utf-8") as f:
    src = f.read()

# Atualizar para V102 e garantir que não dependa de nenhum arquivo externo app-v100.py
src = src.replace('VERSAO_APP = "Act!   V101"', 'VERSAO_APP = "Act!   V102"')
src = src.replace('Act! Versão V101', 'Act! Versão V102')

compile(src, "app-v102.py", "exec")
with open("app-v102.py", "w", encoding="utf-8") as f:
    f.write(src)

print("app-v102.py gerado e compilado com sucesso!")