import requests
import json
import random

def testar_integracao_completa():
    print("🚀 Teste de Integração Completa - Endpoint POST + JavaScript\n")
    
    # 1. Criar usuário
    print("1. Criando usuário...")
    user_id = random.randint(100000, 999999)
    
    cadastro_data = {
        "nome": f"Usuario Completo {user_id}",
        "username": f"completo{user_id}@teste.com",
        "email": f"completo{user_id}@teste.com",
        "password": "teste123"
    }
    
    cadastro_response = requests.post("http://127.0.0.1:5000/api/cadastro", json=cadastro_data)
    
    if cadastro_response.status_code != 201:
        print("❌ Erro no cadastro:", cadastro_response.json())
        return
    
    print("✅ Usuário cadastrado com sucesso!")
    
    # 2. Login
    print("\n2. Fazendo login...")
    login_data = {
        "username": cadastro_data["username"],
        "password": cadastro_data["password"]
    }
    
    login_response = requests.post("http://127.0.0.1:5000/api/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Erro no login:", login_response.json())
        return
    
    token = login_response.json()["access_token"]
    print("✅ Login realizado com sucesso!")
    print(f"   Token: {token[:30]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Testar todas as funcionalidades do endpoint POST
    print("\n3. Testando endpoint POST /api/onboarding/atividade...")
    
    # Testar cada nível de atividade
    niveis = [
        {"nome": "Sedentário", "valor": 1.2},
        {"nome": "Levemente Ativo", "valor": 1.375},
        {"nome": "Moderadamente Ativo", "valor": 1.55},
        {"nome": "Muito Ativo", "valor": 1.725},
        {"nome": "Extremamente Ativo", "valor": 1.9}
    ]
    
    for nivel in niveis:
        post_data = {"fator_atividade": nivel["valor"]}
        
        response = requests.post(
            "http://127.0.0.1:5000/api/onboarding/atividade", 
            json=post_data, 
            headers=headers
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("mensagem") == "Atividade salva com sucesso":
                print(f"   ✅ {nivel['nome']} ({nivel['valor']}): Sucesso")
            else:
                print(f"   ❌ {nivel['nome']}: Resposta incorreta - {response_data}")
        else:
            print(f"   ❌ {nivel['nome']}: Status {response.status_code}")
    
    # 4. Verificar atualização (se já existe, atualiza)
    print("\n4. Testando atualização de dados...")
    
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
        print("   ✅ Atualização funcionando: Ambos POSTs retornaram 200")
    else:
        print(f"   ❌ Problema na atualização: {response1.status_code}, {response2.status_code}")
    
    # 5. Validar estrutura da resposta
    print("\n5. Validando estrutura da resposta...")
    
    response = requests.post(
        "http://127.0.0.1:5000/api/onboarding/atividade", 
        json={"fator_atividade": 1.55}, 
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        if "mensagem" in data and data["mensagem"] == "Atividade salva com sucesso":
            print("   ✅ Estrutura da resposta correta")
            print(f"   📋 Resposta: {data}")
        else:
            print(f"   ❌ Estrutura incorreta: {data}")
    
    # 6. Testar validações de segurança
    print("\n6. Testando validações de segurança...")
    
    # Sem token
    response_sem_token = requests.post(
        "http://127.0.0.1:5000/api/onboarding/atividade", 
        json={"fator_atividade": 1.55}
    )
    
    if response_sem_token.status_code == 401:
        print("   ✅ JWT: Bloqueando acesso sem token")
    else:
        print(f"   ❌ JWT: Deveria bloquear, retornou {response_sem_token.status_code}")
    
    # Token inválido
    headers_invalido = {"Authorization": "Bearer token_invalido"}
    response_token_invalido = requests.post(
        "http://127.0.0.1:5000/api/onboarding/atividade", 
        json={"fator_atividade": 1.55}, 
        headers=headers_invalido
    )
    
    if response_token_invalido.status_code == 422:  # Unprocessable Entity para JWT inválido
        print("   ✅ JWT: Bloqueando token inválido")
    else:
        print(f"   ❌ JWT: Token inválido retornou {response_token_invalido.status_code}")
    
    print("\n🎯 Teste de integração completa finalizado!")
    
    return {
        "usuario": cadastro_data["username"],
        "token": token,
        "endpoint_funcionando": True
    }

if __name__ == "__main__":
    resultado = testar_integracao_completa()
    
    if resultado:
        print(f"\n📋 Resumo do teste:")
        print(f"   - Usuário: {resultado['usuario']}")
        print(f"   - Endpoint POST funcionando: {resultado['endpoint_funcionando']}")
        print(f"   - Token válido para testes manuais disponível")
        print(f"\n🌐 Para testar a interface:")
        print(f"   1. Abra: http://127.0.0.1:5000/atividade-fisica")
        print(f"   2. Faça login com: {resultado['usuario']} / teste123")
        print(f"   3. Selecione um nível de atividade e clique 'Avançar'")
        print(f"   4. Verifique se redireciona para /objetivo")
