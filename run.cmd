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

REM Ativar o ambiente virtual
call venv\Scripts\activate

REM Instala as dependências do requirements.txt
    if exist "%BASE_DIR%requirements.txt" (
        echo Instalando dependencias do requirements.txt...
        pip install -r "%BASE_DIR%requirements.txt"
    ) else (
        echo Arquivo requirements.txt nao encontrado.
        exit
    )

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
python src\preprocessing\prep_local.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar prep_local.py
    exit /b %ERRORLEVEL%
)


REM Converter e executar os notebooks de acidentes
cd "%BASE_DIR%src\preprocessing\treinamento\acidentes"
jupyter nbconvert --to python pre-processamento.ipynb >nul
echo Executando acidentes/pre-processamento.py...
python pre-processamento.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar pre-processamento.py
    del pre-processamento.py
    exit /b %ERRORLEVEL%
)
del pre-processamento.py


jupyter nbconvert --to python preparacao.ipynb >nul
echo Executando acidentes/preparacao.py...
python preparacao.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar preparacao.py
    del preparacao.py
    exit /b %ERRORLEVEL%
)
del preparacao.py


REM Converter e executar os notebooks de os
cd "%BASE_DIR%src\preprocessing\treinamento\os"

jupyter nbconvert --to python pre-processamento.ipynb >nul
echo Executando os/pre-processamento.py...
python pre-processamento.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar pre-processamento.py
    del pre-processamento.py
    exit /b %ERRORLEVEL%
)
del pre-processamento.py


jupyter nbconvert --to python preparacao.ipynb >nul
echo Executando os/preparacao.py...
python preparacao.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar preparacao.py
    del preparacao.py
    exit /b %ERRORLEVEL%
)
del preparacao.py


REM Converter e executar o notebook de cruzamento entre acidentes e operações
cd "%BASE_DIR%src\preprocessing\treinamento"

jupyter nbconvert --to python cruzamento_acidente_op.ipynb >nul
echo Executando treinamento/cruzamento_acidente_op.py...
python cruzamento_acidente_op.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar cruzamento_acidente_op.py
    del cruzamento_acidente_op.py
    exit /b %ERRORLEVEL%
)
del cruzamento_acidente_op.py


REM Converter e executar o notebook de agrupamento dos datasets para o treinamento
jupyter nbconvert --to python agrupamento.ipynb >nul
echo Executando treinamento/agrupamento.py
python agrupamento.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar agrupamento.py
    del agrupamento.py
    exit /b %ERRORLEVEL%
)
del agrupamento.py

REM Converter e executar o notebook de adição dos dados meteorológicos
jupyter nbconvert --to python obtem_dados_meteorologicos.ipynb >nul
echo Executando treinamento/obtem_dados_meteorologicos.py
python obtem_dados_meteorologicos.py >nul
if %ERRORLEVEL% neq 0 (
    echo Falha ao executar obtem_dados_meteorologicos.py
    del obtem_dados_meteorologicos.py
    exit /b %ERRORLEVEL%
)
del obtem_dados_meteorologicos.py

echo Pipeline concluida.

REM Voltar para o diretório raiz
cd "%BASE_DIR%

REM Desativar o ambiente virtual
deactivate

endlocal
@echo on
