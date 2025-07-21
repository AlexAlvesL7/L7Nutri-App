import requests
import time

def testar_sistema():
    print("🔍 TESTANDO SISTEMA APÓS FORCE REBUILD...")
    print("=" * 50)
    
    base_url = "https://l7nutri-app.onrender.com"
    
    # Teste 1: API básica
    print("1. Testando API básica...")
    try:
        r = requests.get(f"{base_url}/api/teste", timeout=10)
        print(f"   ✅ Status: {r.status_code}")
        if r.status_code == 200:
            print(f"   ✅ Response: {r.json()}")
        else:
            print(f"   ❌ Error: {r.text[:200]}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print()
    
    # Teste 2: Diagnóstico do banco
    print("2. Testando diagnóstico do banco...")
    try:
        r = requests.get(f"{base_url}/api/diagnostico-db", timeout=15)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   ✅ SUCESSO! Banco conectado: {data.get('banco_conectado')}")
            print(f"   ✅ Database: {data.get('database_url')}")
            print(f"   ✅ Usuários: {data.get('total_usuarios')}")
            print(f"   ✅ Tabelas: {data.get('tabelas')}")
        else:
            data = r.json()
            print(f"   ❌ Erro: {data.get('erro', 'Erro desconhecido')}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print()
    
    # Teste 3: Cadastro de teste
    print("3. Testando cadastro...")
    dados_teste = {
        "nome": "Usuario Teste Rebuild",
        "email": f"teste_rebuild_{int(time.time())}@gmail.com",
        "senha": "senhaforte123"
    }
    
    try:
        r = requests.post(
            f"{base_url}/api/usuario/registro-seguro",
            json=dados_teste,
            timeout=15
        )
        print(f"   Status: {r.status_code}")
        if r.status_code in [200, 201]:
            data = r.json()
            print(f"   ✅ SUCESSO! Cadastro funcionando!")
            print(f"   ✅ Mensagem: {data.get('mensagem')}")
        elif r.status_code == 409:
            print(f"   ✅ Email já existe (normal)")
        else:
            try:
                data = r.json()
                print(f"   ❌ Erro: {data.get('erro', 'Erro desconhecido')}")
            except:
                print(f"   ❌ Erro HTTP: {r.text[:200]}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    testar_sistema()
