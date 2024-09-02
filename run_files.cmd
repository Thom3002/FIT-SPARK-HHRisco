@echo off
setlocal

REM Definir o diretório base a partir da localização deste script bat
set BASE_DIR=%~dp0

echo Inicializando pipeline...

REM Verifica se a venv já existe
if exist "%BASE_DIR%venv\" (
    echo Venv ja existente no diretorio %BASE_DIR%.
) else (
    echo Venv nao encontrada. Criando nova venv...
    python -m venv "%BASE_DIR%venv"

    REM Ativa a venv
    call "%BASE_DIR%venv\Scripts\activate.bat"
)

REM Instala as dependências do requirements.txt
    if exist "%BASE_DIR%requirements.txt" (
        echo Instalando dependencias do requirements.txt...
        pip install -r "%BASE_DIR%requirements.txt"
    ) else (
        echo Arquivo requirements.txt nao encontrado.
        exit
    )

REM Ativar o ambiente virtual
call venv\Scripts\activate

REM Converte arquivos Excel para csv
echo Executando traduz_input_excel.py...
python src\util\traduz_input_excel.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar traduz_input_excel.py
    exit /b %ERRORLEVEL%
)


REM Executar o script Python de pré-processamento local
cd "%BASE_DIR%"
echo Executando prep_local.py...
python src\util\prep_local.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar prep_local.py
    exit /b %ERRORLEVEL%
)


REM Converter e executar os notebooks de acidentes
cd "%BASE_DIR%src\preprocessing\treinamento\acidentes"
jupyter nbconvert --to python pre-processamento.ipynb >nul
echo Executando pre-processamento.py...
python pre-processamento.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar pre-processamento.py
    exit /b %ERRORLEVEL%
)
del pre-processamento.py


jupyter nbconvert --to python preparacao.ipynb >nul
echo Executando preparacao.py...
python preparacao.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar preparacao.py
    exit /b %ERRORLEVEL%
)
del preparacao.py


jupyter nbconvert --to python agrupamento.ipynb >nul
echo Executando agrupamento.py...
python agrupamento.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar agrupamento.py
    exit /b %ERRORLEVEL%
)
del agrupamento.py


REM Converter e executar os notebooks de os
cd "%BASE_DIR%src\preprocessing\treinamento\os"
jupyter nbconvert --to python pre-processamento-IW47.ipynb >nul
echo Executando pre-processamento-IW47.py...
python pre-processamento-IW47.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar pre-processamento-IW47.py
    exit /b %ERRORLEVEL%
)
del pre-processamento-IW47.py


jupyter nbconvert --to python preparacao-IW47.ipynb >nul
echo Executando preparacao-IW47.py...
python preparacao-IW47.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar preparacao-IW47.py
    exit /b %ERRORLEVEL%
)
del preparacao-IW47.py


jupyter nbconvert --to python agrupamento.ipynb >nul
echo Executando agrupamento.py...
python agrupamento.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar agrupamento.py
    exit /b %ERRORLEVEL%
)
del agrupamento.py

REM Converter e executar o notebook de integração
cd "%BASE_DIR%src\preprocessing\treinamento"
jupyter nbconvert --to python cruzamento_acidentes_os.ipynb >nul
echo Executando cruzamento_acidentes_os.py...
python cruzamento_acidentes_os.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar cruzamento_acidentes_os.py
    exit /b %ERRORLEVEL%
)
del cruzamento_acidentes_os.py


echo Pipeline concluida.

REM Voltar para o diretório raiz
cd "%BASE_DIR%

REM Desativar o ambiente virtual
deactivate

endlocal
@echo on
