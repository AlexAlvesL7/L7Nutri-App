#!/usr/bin/env python3
# Script para migrar/criar tabelas no MySQL Hostinger

import os
from app import app, db

# Forçar modo produção
os.environ['FLASK_ENV'] = 'production'

with app.app_context():
    print("🗄️ Criando tabelas no MySQL...")
    try:
        db.create_all()
        print("✅ Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
