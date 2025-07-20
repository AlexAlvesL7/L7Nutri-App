import requests
import json

# === TESTE SIMPLES DE PREFERÊNCIAS ALIMENTARES ===

def testar_preferencias():
    """Teste direto do endpoint de preferências"""
    
    print("🧪 === TESTE DE PREFERÊNCIAS ALIMENTARES ===\n")
    
    BASE_URL = "http://127.0.0.1:5000"
    
    # Usar usuário existente do teste anterior
    dados_login = {
        "username": "testecompleto77261@gmail.com",
        "password": "123456"
    }
    
    print("🔐 Fazendo login...")
    response = requests.post(f"{BASE_URL}/api/login", json=dados_login)
    
    if response.status_code != 200:
        print("❌ Erro no login. Execute primeiro o teste_final_sistema.py")
        return False
    
    token = response.json()["access_token"]
    print("✅ Login realizado com sucesso!")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    # Dados de teste das preferências
    dados_preferencias = {
        "alimentos_evitar": "brócolis, peixe, leite integral",
        "restricoes": ["lactose", "gluten"],
        "estilo_alimentar": "vegetariano"
    }
    
    print(f"\n📝 Enviando preferências: {dados_preferencias}")
    
    # Enviar preferências
    response = requests.post(f"{BASE_URL}/api/onboarding/preferencias",
                           json=dados_preferencias,
                           headers=headers)
    
    print(f"📊 Status da resposta: {response.status_code}")
    
    if response.status_code == 200:
        resultado = response.json()
        print("✅ Preferências salvas com sucesso!")
        print(f"📋 Resposta: {resultado}")
        return True
    else:
        print(f"❌ Erro ao salvar preferências: {response.text}")
        return False

def testar_pagina_preferencias():
    """Testar se a página de preferências carrega"""
    
    print("\n🌐 Testando página de preferências...")
    
    try:
        response = requests.get("http://127.0.0.1:5000/preferencias-alimentares")
        
        if response.status_code == 200:
            print("✅ Página de preferências carrega corretamente!")
            return True
        else:
            print(f"❌ Erro ao carregar página: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando teste de preferências alimentares...\n")
    
    # Teste da página
    pagina_ok = testar_pagina_preferencias()
    
    # Teste do endpoint
    endpoint_ok = testar_preferencias()
    
    print(f"\n📈 === RESUMO ===")
    print(f"🌐 Página: {'✅ OK' if pagina_ok else '❌ FALHOU'}")
    print(f"🔗 Endpoint: {'✅ OK' if endpoint_ok else '❌ FALHOU'}")
    
    if pagina_ok and endpoint_ok:
        print("🎉 SISTEMA DE PREFERÊNCIAS FUNCIONANDO!")
    else:
        print("⚠️  Alguns componentes falharam")
