#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import json

def preparar_deploy_render():
    """Prepara todos os arquivos para deploy no Render"""
    
    print("🚀 PREPARANDO DEPLOY PARA RENDER")
    print("=" * 50)
    
    # 1. Verificar arquivos essenciais
    arquivos_essenciais = [
        'app.py',
        'requirements.txt',
        'templates/',
        'nutricao.db'
    ]
    
    print("📋 Verificando arquivos essenciais...")
    for arquivo in arquivos_essenciais:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo} - FALTANDO!")
    
    # 2. Criar requirements.txt otimizado para Render
    requirements_render = """Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
Flask-Bcrypt==1.0.1
Flask-JWT-Extended==4.5.3
python-dotenv==1.0.0
google-generativeai==0.3.2
psycopg2-binary==2.9.7
gunicorn==21.2.0
Werkzeug==2.3.7"""

    with open('requirements_render.txt', 'w') as f:
        f.write(requirements_render)
    print("✅ requirements_render.txt criado")
    
    # 3. Criar app_render.py otimizado
    print("📄 Criando app_render.py...")
    
    # 4. Criar gunicorn.conf.py para produção
    gunicorn_config = """bind = "0.0.0.0:10000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True"""

    with open('gunicorn_render.conf.py', 'w') as f:
        f.write(gunicorn_config)
    print("✅ gunicorn_render.conf.py criado")
    
    # 5. Verificar estrutura do banco
    print("\n🗄️ Verificando banco de dados...")
    if os.path.exists('nutricao.db'):
        import sqlite3
        conn = sqlite3.connect('nutricao.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM alimento")
        alimentos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM usuario")
        usuarios = cursor.fetchone()[0]
        
        print(f"✅ {alimentos} alimentos, {usuarios} usuários")
        conn.close()
    
    print("\n🎯 DEPLOY RENDER - PRÓXIMOS PASSOS:")
    print("1. Acesse: https://render.com")
    print("2. Conecte seu GitHub")
    print("3. Crie novo Web Service")
    print("4. Selecione este repositório")
    print("5. Configure:")
    print("   - Build Command: pip install -r requirements_render.txt")
    print("   - Start Command: gunicorn -c gunicorn_render.conf.py app:app")
    print("   - Port: 10000")
    print("\n🌐 URL final: https://l7nutri.onrender.com")

if __name__ == "__main__":
    preparar_deploy_render()
