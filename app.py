with open("app-v102.py", "r", encoding="utf-8") as f:
    src = f.read()

# Verificar que não há 'with open("app-v101_2.py"' nem 'with open("app-v100.py"'
assert "app-v101_2.py" not in src
assert "app-v100.py" not in src

# Atualizar para V103
src = src.replace('VERSAO_APP = "Act!   V102"', 'VERSAO_APP = "Act!   V103"')
src = src.replace('Act! Versão V102', 'Act! Versão V103')

compile(src, "app-v103.py", "exec")

with open("app-v103.py", "w", encoding="utf-8") as f:
    f.write(src)

print("app-v103.py pronto, autossuficiente e compilado!")