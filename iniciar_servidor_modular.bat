@echo off
echo ==========================================
echo 🧠 L7NUTRI - SISTEMA DE ANALISE NUTRICIONAL INTELIGENTE
echo ==========================================
echo.
echo [INFO] Iniciando servidor com nova classe modular...
echo [INFO] Nova estrutura com prompts especificos implementada!
echo.

cd /d "c:\Users\ALEX\OneDrive\Área de Trabalho\L7Nutri\app_nutricional"

echo [INFO] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [INFO] Verificando dependências...
python -c "import flask, sqlite3, os; print('[OK] Dependências principais encontradas')"

echo.
echo [INFO] Iniciando servidor Flask...
echo [INFO] Acesse: http://localhost:5000
echo [INFO] Teste modular: http://localhost:5000/teste-analise-modular
echo.
echo [CTRL+C] para parar o servidor
echo ==========================================

python app.py

pause
