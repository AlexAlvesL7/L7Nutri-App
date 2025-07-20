import requests
import json

def testar_novo_endpoint_post():
    print("🚀 Testando Novo Endpoint POST /api/onboarding/atividade\n")
    
    # 1. Fazer login para obter token
    print("1. Fazendo login...")
    login_data = {
        "username": "teste@teste.com",
        "password": "teste123"
    }
    
    login_response = requests.post("http://127.0.0.1:5000/api/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Erro no login:", login_response.json())
        return
    
    token = login_response.json()["access_token"]
    print("✅ Login realizado com sucesso!")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Testar POST com dados válidos
    print("\n2. Testando POST com dados válidos...")
    
    fatores_atividade = [
        {"nome": "Sedentário", "valor": 1.2},
        {"nome": "Levemente Ativo", "valor": 1.375},
        {"nome": "Moderadamente Ativo", "valor": 1.55},
        {"nome": "Muito Ativo", "valor": 1.725},
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
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("mensagem") == "Atividade salva com sucesso":
                print(f"   ✅ {fator['nome']}: {response_data['mensagem']}")
            else:
                print(f"   ❌ Resposta incorreta: {response_data}")
        else:
            print(f"   ❌ Status incorreto {response.status_code}: {response.json()}")
        
        # Pequena pausa entre testes
        import time
        time.sleep(0.3)
    
    # 3. Testar dados inválidos
    print("\n3. Testando dados inválidos...")
    
    testes_invalidos = [
        {"nome": "Fator muito baixo", "dados": {"fator_atividade": 0.5}},
        {"nome": "Fator muito alto", "dados": {"fator_atividade": 2.5}},
        {"nome": "Fator string", "dados": {"fator_atividade": "invalid"}},
        {"nome": "Fator null", "dados": {"fator_atividade": None}},
        {"nome": "Campo ausente", "dados": {}},
        {"nome": "Campo errado", "dados": {"nivel_atividade": 1.55}}
    ]
    
    for teste in testes_invalidos:
        response = requests.post(
            "http://127.0.0.1:5000/api/onboarding/atividade", 
            json=teste["dados"], 
            headers=headers
        )
        
        if response.status_code == 400:
            print(f"   ✅ {teste['nome']}: Validação funcionando")
        else:
            print(f"   ❌ {teste['nome']}: Deveria retornar erro 400, retornou {response.status_code}")
    
    # 4. Testar sem autenticação
    print("\n4. Testando sem token de autenticação...")
    response = requests.post(
        "http://127.0.0.1:5000/api/onboarding/atividade", 
        json={"fator_atividade": 1.55}
    )
    
    if response.status_code == 401:
        print("   ✅ Autenticação JWT funcionando: Acesso negado sem token")
    else:
        print(f"   ❌ Problema na autenticação: Status {response.status_code}")
    
    # 5. Testar atualização (segundo POST com mesmo usuário)
    print("\n5. Testando atualização de dados...")
    
    # Primeiro POST
    response1 = requests.post(
        "http://127.0.0.1:5000/api/onboarding/atividade", 
        json={"fator_atividade": 1.2}, 
        headers=headers
    )
    
    # Segundo POST (atualização)
    response2 = requests.post(
        "http://127.0.0.1:5000/api/onboarding/atividade", 
        json={"fator_atividade": 1.9}, 
        headers=headers
    )
    
    if response1.status_code == 200 and response2.status_code == 200:
        print("   ✅ Atualização funcionando: Ambos POSTs retornaram sucesso")
    else:
        print(f"   ❌ Problema na atualização: {response1.status_code}, {response2.status_code}")
    
    print("\n🎯 Teste do endpoint POST concluído!")

if __name__ == "__main__":
    testar_novo_endpoint_post()
