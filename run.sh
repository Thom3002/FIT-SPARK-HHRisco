#!/bin/bash

# Definir o diretório base a partir da localização deste script
BASE_DIR=$(realpath "$(dirname "$0")")

echo "Diretório base: $BASE_DIR"

echo "Inicializando pipeline..."

# Verifica se a venv já existe
if [ -d "$BASE_DIR/venv" ]; then
    echo "Venv já existente no diretório $BASE_DIR."
else
    echo "Venv não encontrada. Criando nova venv..."
    python3 -m venv "$BASE_DIR/venv"
fi

# Ativar o ambiente virtual
source "$BASE_DIR/venv/bin/activate"

# Instala as dependências do requirements.txt
if [ -f "$BASE_DIR/requirements.txt" ]; then
    echo "Instalando dependências do requirements.txt..."
    pip install -r "$BASE_DIR/requirements.txt"
else
    echo "Arquivo requirements.txt não encontrado."
    exit 1
fi

# Converte arquivos Excel para CSV
echo "Executando traduz_input_excel.py..."
python "$BASE_DIR/src/util/traduz_input_excel.py" >/dev/null
if [ $? -ne 0 ]; then
    echo "Falha ao executar traduz_input_excel.py"
    exit 1
fi

# Executar o script Python de pré-processamento local
echo "Executando prep_local.py..."
python "$BASE_DIR/src/preprocessing/prep_local.py" >/dev/null
if [ $? -ne 0 ]; then
    echo "Falha ao executar prep_local.py"
    exit 1
fi


# Converter e executar os notebooks de acidentes
cd "$BASE_DIR/src/preprocessing/treinamento/acidentes"

jupyter nbconvert --to python pre-processamento.ipynb >/dev/null
echo "Executando acidentes/pre-processamento.py..."
python pre-processamento.py >/dev/null
if [ $? -ne 0 ]; then
    echo "Falha ao executar pre-processamento.py"
    rm pre-processamento.py
    exit 1
fi
rm pre-processamento.py


jupyter nbconvert --to python preparacao.ipynb >/dev/null
echo "Executando acidentes/preparacao.py..."
python preparacao.py >/dev/null
if [ $? -ne 0 ]; then
    echo "Falha ao executar preparacao.py"
    rm preparacao.py
    exit 1
fi
rm preparacao.py


# Converter e executar os notebooks de OS
cd "$BASE_DIR/src/preprocessing/treinamento/os"

jupyter nbconvert --to python pre-processamento.ipynb >/dev/null
echo "Executando os/pre-processamento.py..."
python pre-processamento.py >/dev/null
if [ $? -ne 0 ]; then
    echo "Falha ao executar pre-processamento.py"
    rm pre-processamento.py
    exit 1
fi
rm pre-processamento.py


jupyter nbconvert --to python preparacao.ipynb >/dev/null
echo "Executando os/preparacao.py..."
python preparacao.py >/dev/null
if [ $? -ne 0 ]; then
    echo "Falha ao executar preparacao.py"
    rm preparacao.py
    exit 1
fi
rm preparacao.py


# Converter e executar o notebook de cruzamento entre acidentes e operações
cd "$BASE_DIR/src/preprocessing/treinamento"

jupyter nbconvert --to python cruzamento_acidente_op.ipynb >/dev/null
echo "Executando treinamento/cruzamento_acidente_op.py..."
python cruzamento_acidente_op.py >/dev/null
if [ $? -ne 0 ]; then
    echo "Falha ao executar cruzamento_acidente_op.py"
    rm cruzamento_acidente_op.py
    exit 1
fi
rm cruzamento_acidente_op.py


# Converter e executar o notebook de agrupamento dos datasets para o treinamento
jupyter nbconvert --to python agrupamento.ipynb
echo "Executando treinamento/agrupamento.py"
python agrupamento.py
if [ $? -ne 0 ]; then
    echo "Falha ao executar agrupamento.py"
    rm agrupamento.py
    exit 1
fi
rm agrupamento.py


REM Converter e executar o notebook de adição dos dados meteorológicos
jupyter nbconvert --to python obtem_dados_meteorologicos.ipynb
echo "Executando treinamento/obtem_dados_meteorologicos.py"
python obtem_dados_meteorologicos.py
if [ $? -ne 0 ]; then
    echo "Falha ao executar obtem_dados_meteorologicos.py"
    rm obtem_dados_meteorologicos.py
    exit 1
fi
rm obtem_dados_meteorologicos.py

echo "Pipeline concluída."

# Voltar para o diretório raiz
cd "$BASE_DIR"

# Desativar o ambiente virtual
deactivate
