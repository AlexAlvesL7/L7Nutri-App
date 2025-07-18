#!/usr/bin/env python3
"""
Teste de dependências para L7Nutri
"""
import sys
import os

print("=== TESTE DE DEPENDÊNCIAS L7NUTRI ===")
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")
print("")

# Lista de dependências críticas
dependencies = [
    'flask',
    'flask_sqlalchemy',
    'flask_bcrypt',
    'flask_jwt_extended',
    'psycopg2',
    'google.generativeai',
    'requests',
    'gunicorn'
]

print("Testando importações...")
for dep in dependencies:
    try:
        if dep == 'psycopg2':
            import psycopg2
            print(f"✓ {dep} - OK")
        elif dep == 'google.generativeai':
            import google.generativeai as genai
            print(f"✓ {dep} - OK")
        else:
            __import__(dep)
            print(f"✓ {dep} - OK")
    except ImportError as e:
        print(f"✗ {dep} - ERRO: {e}")
    except Exception as e:
        print(f"? {dep} - AVISO: {e}")

print("")
print("=== VARIÁVEIS DE AMBIENTE ===")
env_vars = [
    'DATABASE_URL',
    'GEMINI_API_KEY',
    'SECRET_KEY',
    'JWT_SECRET_KEY',
    'PORT'
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        if var in ['DATABASE_URL', 'GEMINI_API_KEY']:
            print(f"✓ {var} - Configurada ({value[:10]}...)")
        else:
            print(f"✓ {var} - Configurada")
    else:
        print(f"✗ {var} - Não configurada")

print("")
print("=== TESTE DE CONEXÃO COM BANCO ===")
try:
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        import psycopg2
        from urllib.parse import urlparse
        
        parsed = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password
        )
        
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        print(f"✓ Conexão com PostgreSQL bem-sucedida")
        print(f"  Versão: {version[0][:50]}...")
        
        cursor.close()
        conn.close()
    else:
        print("✗ DATABASE_URL não configurada")
        
except Exception as e:
    print(f"✗ Erro ao conectar com banco: {e}")

print("")
print("=== TESTE FINALIZADO ===")
