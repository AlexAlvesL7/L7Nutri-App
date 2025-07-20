import requests
import json
import random

def testar_novo_endpoint_post_completo():
    print("🚀 Testando Novo Endpoint POST /api/onboarding/atividade (Completo)\n")
    
    # 1. Criar usuário para teste
    print("1. Criando usuário para teste...")
    user_id = random.randint(10000, 99999)
    
    cadastro_data = {
        "nome": f"Usuario Teste {user_id}",
        "username": f"teste{user_id}@teste.com",
        "email": f"teste{user_id}@teste.com",
        "password": "teste123"
    }
    
    cadastro_response = requests.post("http://127.0.0.1:5000/api/cadastro", json=cadastro_data)
    
    if cadastro_response.status_code != 201:
        print("❌ Erro no cadastro:")
        try:
            print(cadastro_response.json())
        except:
            print(f"Status: {cadastro_response.status_code}, Text: {cadastro_response.text}")
        return
    
    print("✅ Usuário cadastrado com sucesso!")
    
    # 2. Fazer login
    print("\n2. Fazendo login...")
    login_data = {
        "username": cadastro_data["username"],
        "password": cadastro_data["password"]
    }
    
    login_response = requests.post("http://127.0.0.1:5000/api/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Erro no login:")
        try:
            print(login_response.json())
        except:
            print(f"Status: {login_response.status_code}, Text: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    print("✅ Login realizado com sucesso!")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Testar POST com dados válidos
    print("\n3. Testando POST /api/onboarding/atividade...")
    
    fatores_atividade = [
        {"nome": "Sedentário", "valor": 1.2},
        {"nome": "Moderadamente Ativo", "valor": 1.55},
        {"nome": "Extremamente Ativo", "valor": 1.9}
    ]
    
    for fator in fatores_atividade:
        print(f"\n   Testando: {fator['nome']} ({fator['valor']})")
        
        post_data = {
            "fator_atividade": fator["valor"]
        }
        
        response = requests.post(
            "http://127.0.0.1:5000/api/onboarding/atividade", 
            json=post_data, 
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"   Response: {response_data}")
            
            if response.status_code == 200 and response_data.get("mensagem") == "Atividade salva com sucesso":
                print(f"   ✅ {fator['nome']}: Sucesso!")
            else:
                print(f"   ❌ {fator['nome']}: Falhou")
        except:
            print(f"   Erro ao decodificar JSON: {response.text}")
        
        # Pequena pausa
        import time
        time.sleep(0.5)
    
    # 4. Testar dados inválidos
    print("\n4. Testando dados inválidos...")
    
    testes_invalidos = [
        {"nome": "Fator muito baixo", "dados": {"fator_atividade": 0.5}},
        {"nome": "Campo ausente", "dados": {}},
        {"nome": "Fator null", "dados": {"fator_atividade": None}}
    ]
    
    for teste in testes_invalidos:
        response = requests.post(
            "http://127.0.0.1:5000/api/onboarding/atividade", 
            json=teste["dados"], 
            headers=headers
        )
        
        print(f"   {teste['nome']}: Status {response.status_code}")
        
        if response.status_code == 400:
            print(f"   ✅ Validação funcionando")
        else:
            print(f"   ❌ Deveria retornar erro 400")
    
    # 5. Testar sem autenticação
    print("\n5. Testando sem token...")
    response = requests.post(
        "http://127.0.0.1:5000/api/onboarding/atividade", 
        json={"fator_atividade": 1.55}
    )
    
    print(f"   Status sem token: {response.status_code}")
    if response.status_code == 401:
        print("   ✅ Autenticação JWT funcionando")
    else:
        print("   ❌ Problema na autenticação")
    
    print("\n🎯 Teste completo finalizado!")
    return cadastro_data["username"]

if __name__ == "__main__":
    usuario_teste = testar_novo_endpoint_post_completo()
    if usuario_teste:
        print(f"\n📋 Usuário de teste criado: {usuario_teste}")
        print("   Pode ser usado para testes manuais no formulário")
