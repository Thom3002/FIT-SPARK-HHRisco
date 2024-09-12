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
python "$BASE_DIR/src/preprocessing/treinamento/prep_local.py" >/dev/null
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

jupyter nbconvert --to python agrupamento.ipynb >/dev/null
echo "Executando acidentes/agrupamento.py..."
python agrupamento.py >/dev/null
if [ $? -ne 0 ]; then
    echo "Falha ao executar agrupamento.py"
    rm agrupamento.py
    exit 1
fi
rm agrupamento.py

# Converter e executar os notebooks de OS
cd "$BASE_DIR/src/preprocessing/treinamento/os"
jupyter nbconvert --to python pre-processamento-IW47.ipynb >/dev/null
echo "Executando os/pre-processamento-IW47.py..."
python pre-processamento-IW47.py >/dev/null
if [ $? -ne 0 ]; then
    echo "Falha ao executar pre-processamento-IW47.py"
    rm pre-processamento-IW47.py
    exit 1
fi
rm pre-processamento-IW47.py

jupyter nbconvert --to python preparacao-IW47.ipynb >/dev/null
echo "Executando os/preparacao-IW47.py..."
python preparacao-IW47.py >/dev/null
if [ $? -ne 0 ]; then
    echo "Falha ao executar preparacao-IW47.py"
    rm preparacao-IW47.py
    exit 1
fi
rm preparacao-IW47.py

jupyter nbconvert --to python agrupamento.ipynb >/dev/null
echo "Executando os/agrupamento.py..."
python agrupamento.py >/dev/null
if [ $? -ne 0 ]; then
    echo "Falha ao executar agrupamento.py"
    rm agrupamento.py
    exit 1
fi
rm agrupamento.py

# Converter e executar o notebook de integração
cd "$BASE_DIR/src/preprocessing/treinamento"
jupyter nbconvert --to python cruzamento_acidentes_os.ipynb >/dev/null
echo "Executando treinamento/cruzamento_acidentes_os.py..."
python cruzamento_acidentes_os.py >/dev/null
if [ $? -ne 0 ]; then
    echo "Falha ao executar cruzamento_acidentes_os.py"
    rm cruzamento_acidentes_os.py
    exit 1
fi
rm cruzamento_acidentes_os.py

# Converter e executar o notebook de preparação do dataset de treinamento
jupyter nbconvert --to python preparacao.ipynb >/dev/null
echo "Executando treinamento/preparacao.py"
python preparacao.py >/dev/null
if [ $? -ne 0 ]; then
    echo "Falha ao executar preparacao.py"
    rm preparacao.py
    exit 1
fi
rm preparacao.py

echo "Pipeline concluída."

# Voltar para o diretório raiz
cd "$BASE_DIR"

# Desativar o ambiente virtual
deactivate
