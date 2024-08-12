@echo off
setlocal

REM Definir o diretório base a partir da localização deste script bat
set BASE_DIR=%~dp0

REM Verifica se a venv já existe
if exist "%BASE_DIR%venv\" (
    echo Venv já existe no diretório %BASE_DIR%.
) else (
    echo Venv não encontrada. Criando nova venv...
    python -m venv "%BASE_DIR%venv"

    REM Ativa a venv
    call "%BASE_DIR%venv\Scripts\activate.bat"
)

REM Instala as dependências do requirements.txt
    if exist "%BASE_DIR%requirements.txt" (
        echo Instalando dependências do requirements.txt...
        pip install -r "%BASE_DIR%requirements.txt"
    ) else (
        echo Arquivo requirements.txt não encontrado.
        exit
    )

REM Ativar o ambiente virtual
call venv\Scripts\activate


REM Executar o script Python de pré-processamento local
cd "%BASE_DIR%"
echo Executando prep_local_inst.py...
python src\util\prep_local_inst.py >nul
if %ERRORLEVEL% neq 0 echo Falha ao executar prep_local_inst.py

REM Converter e executar os notebooks de acidentes
cd "%BASE_DIR%src\preprocessing\acidentes"
jupyter nbconvert --to python preparacao.ipynb >nul
echo Executando preparacao.py...
python preparacao.py >nul
if %ERRORLEVEL% neq 0 echo Falha ao executar preparacao.py
del preparacao.py

jupyter nbconvert --to python pre-processamento.ipynb >nul
echo Executando pre-processamento.py...
python pre-processamento.py >nul
if %ERRORLEVEL% neq 0 echo Falha ao executar pre-processamento.py
del pre-processamento.py

jupyter nbconvert --to python agrupamento.ipynb >nul
echo Executando agrupamento.py...
python agrupamento.py >nul
if %ERRORLEVEL% neq 0 echo Falha ao executar agrupamento.py
del agrupamento.py

REM Converter e executar os notebooks de os
cd "%BASE_DIR%src\preprocessing\os"
jupyter nbconvert --to python preparacao-IW47.ipynb >nul
echo Executando preparacao-IW47.py...
python preparacao-IW47.py >nul
if %ERRORLEVEL% neq 0 echo Falha ao executar preparacao-IW47.py
del preparacao-IW47.py

jupyter nbconvert --to python agrupamento.ipynb >nul
echo Executando agrupamento.py...
python agrupamento.py >nul
if %ERRORLEVEL% neq 0 echo Falha ao executar agrupamento.py
del agrupamento.py

REM Voltar para o diretório raiz
cd "%BASE_DIR%"

REM Desativar o ambiente virtual
deactivate

endlocal
@echo on
