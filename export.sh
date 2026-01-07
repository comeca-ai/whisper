#!/bin/bash

echo "=== Exportando Projeto Whisper com FastAPI ==="
echo ""

# Verificar se tem configuração git
if ! git config user.email > /dev/null 2>&1; then
    echo "Configurando Git..."
    read -p "Digite seu email do GitHub: " email
    read -p "Digite seu nome: " name
    git config --global user.email "$email"
    git config --global user.name "$name"
fi

# Adicionar arquivos
echo "Adicionando arquivos novos..."
git add api.py requirements-api.txt Dockerfile docker-compose.yml test_api.py README_API.md

# Mostrar o que será commitado
echo ""
echo "Arquivos que serão commitados:"
git status --short

echo ""
read -p "Deseja commitar estes arquivos? (s/n): " confirm

if [[ $confirm == "s" || $confirm == "S" ]]; then
    git commit -m "feat: Add FastAPI endpoint for Whisper transcription

- Add FastAPI REST API with transcription endpoints
- Add Docker support (Dockerfile and docker-compose.yml)
- Add API documentation and test script
- Add requirements-api.txt with FastAPI dependencies"
    
    echo ""
    echo "✅ Commit realizado!"
    echo ""
    echo "Para fazer push para um novo repositório:"
    echo "1. Crie um novo repositório no GitHub (ex: seu-usuario/whisper-api)"
    echo "2. Execute:"
    echo "   git remote set-url origin https://github.com/SEU-USUARIO/whisper-api.git"
    echo "   git push -u origin main"
    echo ""
    echo "Ou para clonar no seu computador local:"
    echo "   git clone https://github.com/openai/whisper.git"
    echo "   cd whisper"
    echo "   git cherry-pick $(git rev-parse HEAD)"
else
    echo "Commit cancelado."
fi
