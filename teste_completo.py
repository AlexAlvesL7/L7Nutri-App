import requests
import json

# Tentar criar usuário para teste
cadastro_data = {
    "nome": "Teste Usuario",
    "username": "teste@teste.com",
    "email": "teste@teste.com",
    "password": "teste123"
}

cadastro_response = requests.post("http://127.0.0.1:5000/api/cadastro", json=cadastro_data)
print("Cadastro:", cadastro_response.status_code, cadastro_response.json())

# Fazer login
login_data = {
    "username": "teste@teste.com",
    "password": "teste123"
}

response = requests.post("http://127.0.0.1:5000/api/login", json=login_data)
print("Login Status:", response.status_code)
print("Login Response:", response.json())

if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"Token obtido: {token[:50]}...")
    
    # Adicionar um alimento ao diário
    headers = {"Authorization": f"Bearer {token}"}
    
    # Primeiro buscar um alimento disponível
    busca_response = requests.get("http://127.0.0.1:5000/api/alimentos/buscar?q=arroz", headers=headers)
    print("Busca alimentos:", busca_response.json())
    
    if busca_response.status_code == 200 and busca_response.json():
        primeiro_alimento = busca_response.json()[0]
        print(f"Usando alimento: {primeiro_alimento['nome']} (ID: {primeiro_alimento['id']})")
        
        # Adicionar alimento ao diário
        diario_data = {
            "alimento_id": primeiro_alimento["id"],
            "quantidade": 100,
            "refeicao": "cafe-manha"
        }
        
        add_response = requests.post("http://127.0.0.1:5000/api/diario", json=diario_data, headers=headers)
        print("Adicionar ao diário:", add_response.status_code, add_response.json())
        
        # Verificar diário atual
        diario_response = requests.get("http://127.0.0.1:5000/api/diario", headers=headers)
        print("Diário atual:", diario_response.json())
        
        # Testar exclusão se tiver registros
        if diario_response.status_code == 200 and diario_response.json():
            primeiro_registro = diario_response.json()[0]
            registro_id = primeiro_registro["id"]
            print(f"Testando exclusão do registro ID: {registro_id}")
            
            delete_response = requests.delete(f"http://127.0.0.1:5000/api/diario/{registro_id}", headers=headers)
            print("Exclusão:", delete_response.status_code)
            if delete_response.status_code == 200:
                print("Exclusão realizada com sucesso!")
                
                # Verificar se foi realmente excluído
                diario_final = requests.get("http://127.0.0.1:5000/api/diario", headers=headers)
                print("Diário após exclusão:", diario_final.json())
            else:
                print("Erro na exclusão:", delete_response.json())
