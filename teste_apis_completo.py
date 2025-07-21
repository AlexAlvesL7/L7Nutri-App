import requests
import json

def teste_apis():
    """Testa as APIs principais do L7Nutri"""
    base_url = "https://l7nutri-app.onrender.com"
    
    print("🔍 TESTANDO APIS DO L7NUTRI")
    print("=" * 50)
    
    # 1. Teste básico da API
    try:
        response = requests.get(f"{base_url}/api/teste")
        print(f"✅ API Base: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ API Base: Erro - {e}")
    
    # 2. Teste diagnóstico do banco
    try:
        response = requests.get(f"{base_url}/api/diagnostico-db")
        print(f"🗄️ Banco: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - Status: {data.get('status')}")
            print(f"   - Banco: {data.get('database_url')}")
            print(f"   - Usuários: {data.get('total_usuarios')}")
            print(f"   - Tabelas: {data.get('tabelas')}")
        else:
            print(f"   - Erro: {response.text}")
    except Exception as e:
        print(f"❌ Diagnóstico Banco: Erro - {e}")
    
    # 3. Teste registro (dados simulados)
    dados_teste = {
        "nome": "Usuario Teste",
        "email": "teste123@gmail.com",
        "senha": "senhaforte123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/usuario/registro-seguro",
            json=dados_teste,
            headers={"Content-Type": "application/json"}
        )
        print(f"📝 Registro: {response.status_code}")
        if response.status_code in [200, 201, 409]:  # 409 = já existe
            data = response.json()
            print(f"   - Sucesso: {data.get('sucesso')}")
            print(f"   - Mensagem: {data.get('mensagem')}")
            if not data.get('sucesso'):
                print(f"   - Erro: {data.get('erro')}")
        else:
            print(f"   - Erro HTTP: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Registro: Erro - {e}")
    
    # 4. Teste login (dados simulados)
    dados_login = {
        "email": "teste123@gmail.com",
        "senha": "senhaforte123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/login",
            json=dados_login,
            headers={"Content-Type": "application/json"}
        )
        print(f"🔑 Login: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - Sucesso: {data.get('sucesso')}")
            print(f"   - Mensagem: {data.get('mensagem')}")
        else:
            print(f"   - Erro: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Login: Erro - {e}")

if __name__ == "__main__":
    teste_apis()
