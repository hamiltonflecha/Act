# Vamos verificar o conteúdo do arquivo app.py e criar um instalador/lançador em batch (.bat) chamado 'iniciar_act.bat'
# Esse arquivo .bat vai localizar automaticamente o Python no computador do Hamilton (inclusive caminhos comuns do Windows 7 ou AppData)
# e iniciar o aplicativo Streamlit perfeitamente, sem precisar digitar comandos no CMD.

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Vamos garantir que a VERSAO_APP seja V88 e esteja explícita no código
code = code.replace('VERSAO_APP = "Act!   V87"', 'VERSAO_APP = "Act!   V88"')
code = code.replace('Act! Versão V87', 'Act! Versão V88')
if 'VERSAO_APP = "Act!' not in code:
    code = 'VERSAO_APP = "Act!   V88"\n' + code

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

with open("app_final.py", "w", encoding="utf-8") as f:
    f.write(code)

# Criar o script .bat para facilitar a inicialização na pasta C:\Users\Banco\Documents\000000-act
bat_content = """@echo off
TITLE Act! - Solucoes 1986
cd /d "%~dp0"
echo Iniciando o Act! Versao V88...

REM Tenta encontrar o Python nos caminhos mais comuns do Windows 7 / AppData
if exist "%LocalAppData%\\Programs\\Python\\Python39\\python.exe" (
    "%LocalAppData%\\Programs\\Python\\Python39\\python.exe" -m streamlit run app.py
    goto end
)
if exist "%LocalAppData%\\Programs\\Python\\Python310\\python.exe" (
    "%LocalAppData%\\Programs\\Python\\Python310\\python.exe" -m streamlit run app.py
    goto end
)
if exist "C:\\Python39\\python.exe" (
    C:\\Python39\\python.exe -m streamlit run app.py
    goto end
)
if exist "C:\\Python310\\python.exe" (
    C:\\Python310\\python.exe -m streamlit run app.py
    goto end
)
if exist "C:\\Python311\\python.exe" (
    C:\\Python311\\python.exe -m streamlit run app.py
    goto end
)

REM Tenta comando direto python ou py
python -m streamlit run app.py
if %errorlevel% equ 0 goto end

py -m streamlit run app.py
if %errorlevel% equ 0 goto end

echo.
echo [ERRO] O Python nao foi encontrado automaticamente neste computador.
echo Por favor, verifique onde o Python esta instalado.
pause

:end
"""

with open("iniciar_act.bat", "w", encoding="utf-8") as f:
    f.write(bat_content)

print("Arquivo app.py atualizado para V88 e script 'iniciar_act.bat' gerado com sucesso!")