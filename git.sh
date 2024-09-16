#!/bin/bash

# Configura o Git para sempre usar o token PAT para este repositório remoto
git remote set-url origin https://$AZURE_DEVOPS_PAT@dev.azure.com/exactapucrio/FIT-SPARK-HHRisco/_git/FIT-SPARK-HHRisco

# Le e armazena a mensagem do último commit na branch
LAST_COMMIT_MSG=$(git log -1 --pretty=format:"%s")

# Extrai o nome da branch na mensagem do commit
BRANCH_NAME=$(echo "$LAST_COMMIT_MSG" | sed -n 's/.*from \([^ ]*\) into.*/\1/p')

# Se não encontrar o nome da branch na mensagem, tenta extrair o nome da branch do nome do branch atual
if [ -z "$BRANCH_NAME" ]; then
    BRANCH_NAME=$(git branch --show-current)
fi

# Print para debug
# echo "Branch atual: $BRANCH_NAME"

echo "Inicializando verificação do Git..."

# Git fetch de todos os repositorios e branches remotas (agora usando o PAT configurado)
git fetch --all > /dev/null
if [ $? -ne 0 ]; then
    echo "Git fetch falhou. Por favor, tente novamente."
    exit 1
fi
echo "Git fetch finalizado."

# Confere status da branch
STATUS=$(git status -uno | grep -o 'Your branch is behind')
if [ "$STATUS" ]; then
    echo "Branch está atrasada em relação ao remoto. Por favor, use git pull antes de prosseguir."
    exit 1
fi

# Confere se a branch está atrás da dev
DEVSTATUS=$(git rev-list --left-only --count origin/dev...origin/$BRANCH_NAME)
if [ $? -ne 0 ]; then
    echo "Erro ao verificar status da branch. Por favor, tente novamente."
    exit 1
fi

# Print para debug
# echo "Commits atrás da dev: $DEVSTATUS"

if [ "$DEVSTATUS" -ne 0 ]; then
    echo "Branch está atrás da origin/dev. Por favor, use rebase antes de prosseguir."
    exit 1
fi

echo "Branch está atualizada em relação à origin/dev."

echo "Verificação do Git concluída."