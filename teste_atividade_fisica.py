import requests
import json

def testar_formulario_atividade_fisica():
    print("🏃‍♂️ Testando Formulário de Atividade Física\n")
    
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
    
    # 2. Testar envio de cada nível de atividade
    niveis_atividade = [
        {"nome": "Sedentário", "valor": 1.2},
        {"nome": "Levemente Ativo", "valor": 1.375},
        {"nome": "Moderadamente Ativo", "valor": 1.55},
        {"nome": "Muito Ativo", "valor": 1.725},
        {"nome": "Extremamente Ativo", "valor": 1.9}
    ]
    
    for nivel in niveis_atividade:
        print(f"\n2. Testando nível: {nivel['nome']} ({nivel['valor']})")
        
        atividade_data = {
            "nivel_atividade": nivel["valor"]
        }
        
        response = requests.put(
            "http://127.0.0.1:5000/api/usuario/atividade-fisica", 
            json=atividade_data, 
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ {nivel['nome']}: {response.json()['mensagem']}")
        else:
            print(f"❌ Erro para {nivel['nome']}: {response.json()}")
        
        # Pequena pausa entre testes
        import time
        time.sleep(0.5)
    
    # 3. Testar valores inválidos
    print("\n3. Testando valores inválidos...")
    
    valores_invalidos = [
        {"nome": "Valor muito baixo", "valor": 0.5},
        {"nome": "Valor muito alto", "valor": 2.5},
        {"nome": "Valor string", "valor": "invalid"},
        {"nome": "Valor null", "valor": None}
    ]
    
    for teste in valores_invalidos:
        atividade_data = {
            "nivel_atividade": teste["valor"]
        }
        
        response = requests.put(
            "http://127.0.0.1:5000/api/usuario/atividade-fisica", 
            json=atividade_data, 
            headers=headers
        )
        
        if response.status_code == 400:
            print(f"✅ {teste['nome']}: Validação funcionando - {response.json()['erro']}")
        else:
            print(f"❌ {teste['nome']}: Deveria retornar erro 400")
    
    # 4. Testar sem token
    print("\n4. Testando sem token de autenticação...")
    response = requests.put(
        "http://127.0.0.1:5000/api/usuario/atividade-fisica", 
        json={"nivel_atividade": 1.55}
    )
    
    if response.status_code == 401:
        print("✅ Autenticação funcionando: Acesso negado sem token")
    else:
        print("❌ Problema na autenticação")
    
    print("\n🎯 Teste completo finalizado!")

if __name__ == "__main__":
    testar_formulario_atividade_fisica()
