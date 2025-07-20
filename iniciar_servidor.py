import os
import sys

# Adicionar o diretório atual ao path do Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Testando importações...")
    
    # Testar importações básicas
    import flask
    print(f"✅ Flask versão: {flask.__version__}")
    
    from flask_sqlalchemy import SQLAlchemy
    print("✅ Flask-SQLAlchemy importado")
    
    from werkzeug.security import generate_password_hash
    print("✅ Werkzeug importado")
    
    # Verificar se o banco existe
    if os.path.exists('nutricao.db'):
        print("✅ Banco nutricao.db encontrado")
        
        import sqlite3
        conn = sqlite3.connect('nutricao.db')
        cursor = conn.cursor()
        
        # Verificar alimentos
        cursor.execute("SELECT COUNT(*) FROM alimento")
        count_alimentos = cursor.fetchone()[0]
        print(f"✅ {count_alimentos} alimentos no banco")
        
        # Verificar usuários
        cursor.execute("SELECT COUNT(*) FROM usuario")
        count_usuarios = cursor.fetchone()[0]
        print(f"✅ {count_usuarios} usuários no banco")
        
        conn.close()
    else:
        print("❌ Banco nutricao.db não encontrado")
    
    # Tentar importar o app
    print("\n🚀 Importando aplicação...")
    from app import app
    print("✅ App importado com sucesso")
    
    # Iniciar servidor
    print("\n🌐 Iniciando servidor Flask...")
    print("🔗 Acesse: http://127.0.0.1:5000")
    print("👤 Login: admin")
    print("🔑 Senha: admin123")
    print("\n" + "="*50)
    
    # Configurar para execução local
    app.config['ENV'] = 'development'
    app.config['DEBUG'] = True
    
    # Iniciar o servidor
    app.run(host='127.0.0.1', port=5000, debug=True)
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("💡 Instalando dependências...")
    os.system("pip install flask flask-sqlalchemy flask-migrate flask-bcrypt flask-jwt-extended python-dotenv")
    
except Exception as e:
    print(f"❌ Erro geral: {e}")
    print(f"Tipo do erro: {type(e)}")
    import traceback
    traceback.print_exc()
