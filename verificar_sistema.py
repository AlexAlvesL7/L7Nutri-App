#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("🔍 DIAGNÓSTICO L7NUTRI")
print("=" * 40)

# 1. Verificar Python
import sys
print(f"✅ Python: {sys.version}")

# 2. Verificar diretório
import os
print(f"✅ Diretório: {os.getcwd()}")

# 3. Verificar arquivos
arquivos = os.listdir('.')
print(f"✅ Arquivos encontrados: {len(arquivos)}")
for arquivo in sorted(arquivos):
    if arquivo.endswith('.py') or arquivo.endswith('.db'):
        print(f"   📄 {arquivo}")

# 4. Verificar banco
if 'nutricao.db' in arquivos:
    try:
        import sqlite3
        conn = sqlite3.connect('nutricao.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM alimento")
        alimentos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM usuario")
        usuarios = cursor.fetchone()[0]
        
        print(f"✅ Banco: {alimentos} alimentos, {usuarios} usuários")
        conn.close()
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
else:
    print("❌ Banco nutricao.db não encontrado")

# 5. Verificar Flask
try:
    import flask
    print(f"✅ Flask: {flask.__version__}")
except ImportError:
    print("❌ Flask não instalado")
    print("💡 Execute: pip install flask")

# 6. Tentar importar app
try:
    print("\n🚀 Testando importação do app...")
    import app
    print("✅ App importado com sucesso!")
    
    print("\n🌐 Para iniciar o servidor:")
    print("1. Execute: python app.py")
    print("2. Acesse: http://127.0.0.1:5000")
    print("3. Login: admin / admin123")
    
except Exception as e:
    print(f"❌ Erro ao importar app: {e}")

print("\n" + "=" * 40)
print("DIAGNÓSTICO CONCLUÍDO")
