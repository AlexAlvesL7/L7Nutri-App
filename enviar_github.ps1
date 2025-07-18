Write-Host "====================================" -ForegroundColor Green
Write-Host "ENVIANDO ARQUIVOS PARA O GITHUB" -ForegroundColor Green  
Write-Host "====================================" -ForegroundColor Green

Set-Location "c:\Users\ALEX\OneDrive\Área de Trabalho\L7Nutri\app_nutricional\deploy_render"

Write-Host "Configurando Git..." -ForegroundColor Yellow
git config user.email "alexalves7.dev@gmail.com"
git config user.name "AlexAlves7"

Write-Host "Verificando arquivos..." -ForegroundColor Yellow
Get-ChildItem

Write-Host "Adicionando arquivos..." -ForegroundColor Yellow
git add .

Write-Host "Fazendo commit..." -ForegroundColor Yellow
git commit -m "Deploy L7Nutri App - Complete Files"

Write-Host "Enviando para GitHub..." -ForegroundColor Yellow
git push -u origin main

Write-Host "====================================" -ForegroundColor Green
Write-Host "PRONTO! Arquivos enviados!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

Read-Host "Pressione Enter para continuar"
