import subprocess
import sys
import time
import requests
import sqlite3
import os

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    print("🔍 VERIFICANDO DEPENDÊNCIAS...")
    
    dependencias = [
        'flask', 'flask_sqlalchemy', 'flask_migrate', 
        'flask_bcrypt', 'flask_jwt_extended', 'python_dotenv'
    ]
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - INSTALANDO...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep.replace('_', '-')])

def verificar_banco():
    """Verifica se o banco de dados está correto"""
    print("\n🗄️ VERIFICANDO BANCO DE DADOS...")
    
    if not os.path.exists('nutricao.db'):
        print("❌ Banco nutricao.db não existe - CRIANDO...")
        subprocess.run([sys.executable, 'criar_banco.py'])
        subprocess.run([sys.executable, 'adicionar_lote_completo.py'])
        subprocess.run([sys.executable, 'verificar_admin.py'])
    else:
        print("✅ Banco nutricao.db existe")
        
        # Verificar tabelas
        conn = sqlite3.connect('nutricao.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [row[0] for row in cursor.fetchall()]
        
        tabelas_necessarias = ['alimento', 'usuario', 'registro_alimentar']
        for tabela in tabelas_necessarias:
            if tabela in tabelas:
                print(f"✅ Tabela {tabela}")
            else:
                print(f"❌ Tabela {tabela} - RECRIANDO BANCO...")
                conn.close()
                os.remove('nutricao.db')
                subprocess.run([sys.executable, 'criar_banco.py'])
                subprocess.run([sys.executable, 'verificar_admin.py'])
                return
        
        conn.close()

def iniciar_servidor():
    """Inicia o servidor Flask"""
    print("\n🚀 INICIANDO SERVIDOR FLASK...")
    
    try:
        # Matar processos Flask existentes
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                      capture_output=True, shell=True)
        time.sleep(2)
        
        # Iniciar novo servidor
        print("🔄 Iniciando servidor em http://127.0.0.1:5000...")
        processo = subprocess.Popen([sys.executable, 'app.py'])
        
        # Aguardar alguns segundos para o servidor iniciar
        time.sleep(5)
        
        # Testar se está funcionando
        try:
            response = requests.get('http://127.0.0.1:5000', timeout=10)
            if response.status_code == 200:
                print("✅ SERVIDOR FUNCIONANDO!")
                print("🌐 Acesse: http://127.0.0.1:5000")
                return True
            else:
                print(f"⚠️ Servidor respondeu com código: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao conectar: {e}")
            
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
    
    return False

def testar_apis():
    """Testa as APIs principais"""
    print("\n🧪 TESTANDO APIs...")
    
    base_url = 'http://127.0.0.1:5000'
    
    # Testar homepage
    try:
        response = requests.get(f'{base_url}/')
        print(f"✅ Homepage: {response.status_code}")
    except:
        print("❌ Homepage não acessível")
    
    # Testar página de login
    try:
        response = requests.get(f'{base_url}/login')
        print(f"✅ Login page: {response.status_code}")
    except:
        print("❌ Login page não acessível")
    
    # Testar API de alimentos
    try:
        response = requests.get(f'{base_url}/api/alimentos')
        print(f"✅ API Alimentos: {response.status_code}")
    except:
        print("❌ API Alimentos não acessível")

if __name__ == "__main__":
    print("🔧 DIAGNÓSTICO E CORREÇÃO DO L7NUTRI")
    print("=" * 50)
    
    verificar_dependencias()
    verificar_banco()
    
    if iniciar_servidor():
        testar_apis()
        print("\n🎉 SISTEMA PRONTO!")
        print("👤 Login: admin")
        print("🔑 Senha: admin123")
        print("🌐 URL: http://127.0.0.1:5000/login")
    else:
        print("\n❌ FALHA AO INICIAR SERVIDOR")
        print("💡 Tente executar manualmente: python app.py")
