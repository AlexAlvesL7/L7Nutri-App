import requests
import time
import subprocess
import os

def iniciar_servidor():
    """Inicia o servidor Flask"""
    print("🚀 Iniciando servidor Flask...")
    
    # Muda para o diretório do projeto
    os.chdir(r"c:\Users\ALEX\OneDrive\Área de Trabalho\L7Nutri\app_nutricional")
    
    # Inicia o servidor em background
    processo = subprocess.Popen(['python', 'app.py'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
    
    # Aguarda o servidor inicializar
    print("⏳ Aguardando servidor inicializar...")
    time.sleep(5)
    
    return processo

def testar_endpoints():
    """Testa os endpoints principais"""
    base_url = "http://127.0.0.1:5000"
    
    endpoints = [
        ("/api/teste", "GET", None),
        ("/dashboard-insights?id=9185fb0a-a4ed-4345-9af4-e0e7698d3c83", "GET", None),
        ("/api/ia/dashboard-insights", "POST", {"periodo": 7})
    ]
    
    print("\n🔍 Testando endpoints...")
    
    for endpoint, method, data in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n📡 Testando: {method} {endpoint}")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json=data, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                if 'application/json' in response.headers.get('content-type', ''):
                    print(f"   Resposta: {response.json()}")
                else:
                    print(f"   HTML carregado: {len(response.text)} caracteres")
                print("   ✅ SUCESSO!")
            else:
                print(f"   ❌ ERRO: {response.text[:100]}...")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ ERRO: Não foi possível conectar ao servidor")
        except requests.exceptions.Timeout:
            print("   ❌ ERRO: Timeout na conexão")
        except Exception as e:
            print(f"   ❌ ERRO: {e}")

if __name__ == "__main__":
    print("🧠 TESTE COMPLETO DO DASHBOARD DE INSIGHTS")
    print("=" * 50)
    
    # Inicia o servidor
    processo_servidor = iniciar_servidor()
    
    try:
        # Testa os endpoints
        testar_endpoints()
        
        print("\n" + "=" * 50)
        print("✨ TESTE CONCLUÍDO!")
        print("\n🌐 URLs para teste manual:")
        print("   Dashboard: http://127.0.0.1:5000/dashboard-insights?id=9185fb0a-a4ed-4345-9af4-e0e7698d3c83")
        print("   API Test: http://127.0.0.1:5000/api/teste")
        
        print("\n⏸️ Pressione Ctrl+C para parar o servidor...")
        processo_servidor.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Parando servidor...")
        processo_servidor.terminate()
        print("✅ Servidor parado!")
