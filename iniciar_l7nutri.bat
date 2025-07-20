@echo off
echo ======================================
echo     L7NUTRI - INICIANDO SISTEMA
echo ======================================

cd /d "c:\Users\ALEX\OneDrive\Área de Trabalho\L7Nutri\app_nutricional"

echo Verificando Python...
python --version

echo.
echo Instalando dependencias...
pip install flask flask-sqlalchemy flask-migrate flask-bcrypt flask-jwt-extended python-dotenv

echo.
echo Verificando arquivos...
dir

echo.
echo Iniciando servidor...
echo Acesse: http://127.0.0.1:5000
echo Usuario: admin
echo Senha: admin123
echo.

python servidor_teste.py

pause
