@echo off
echo ===================================
echo ENVIANDO ARQUIVOS PARA O GITHUB
echo ===================================

cd /d "c:\Users\ALEX\OneDrive\Área de Trabalho\L7Nutri\app_nutricional\deploy_render"

echo Verificando se estamos no diretório correto...
dir

echo Configurando Git...
git config user.email "alexalves7.dev@gmail.com"
git config user.name "AlexAlves7"

echo Verificando status do Git...
git status

echo Enviando arquivos...
git add .
git commit -m "Deploy L7Nutri App - Todos os arquivos"
git push -u origin main

echo ===================================
echo PRONTO! Arquivos enviados!
echo ===================================
pause
