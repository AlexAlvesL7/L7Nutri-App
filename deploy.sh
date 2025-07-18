#!/bin/bash
# Script para deploy automatico no Render

echo "L7Nutri - Deploy para Render"
echo "=============================="

# Verificar arquivos essenciais
echo "Verificando arquivos..."
if [ ! -f "main.py" ]; then
    echo "ERRO: main.py não encontrado!"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "ERRO: requirements.txt não encontrado!"
    exit 1
fi

if [ ! -f "Procfile" ]; then
    echo "ERRO: Procfile não encontrado!"
    exit 1
fi

echo "Todos os arquivos encontrados!"

# Fazer commit
echo "Fazendo commit das alterações..."
git add .
git commit -m "Deploy L7Nutri - Template fix"

# Fazer push para trigger deploy no Render
echo "Enviando para GitHub..."
git push origin main

echo "Deploy enviado! Render será notificado automaticamente."
echo "URL: https://l7nutri-app.onrender.com"
