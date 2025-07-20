import requests

# Login existente
login_data = {
    "username": "teste@teste.com",
    "password": "teste123"
}

response = requests.post("http://127.0.0.1:5000/api/login", json=login_data)
if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Verificar se existem alimentos na base
    alimentos_response = requests.get("http://127.0.0.1:5000/alimentos", headers=headers)
    print("Todos os alimentos:", alimentos_response.status_code)
    if alimentos_response.status_code == 200:
        alimentos = alimentos_response.json()
        print(f"Total de alimentos: {len(alimentos)}")
        if alimentos:
            for i, alimento in enumerate(alimentos[:5]):
                print(f"{i+1}. {alimento['nome']} - {alimento['calorias']} kcal")
        
        # Usar o primeiro alimento disponível para teste
        if alimentos:
            primeiro_alimento = alimentos[0]
            print(f"\nUsando {primeiro_alimento['nome']} para teste...")
            
            # Adicionar ao diário
            diario_data = {
                "alimento_id": primeiro_alimento["id"],
                "quantidade": 100,
                "refeicao": "cafe-manha"
            }
            
            add_response = requests.post("http://127.0.0.1:5000/api/diario", json=diario_data, headers=headers)
            print("Adicionar ao diário:", add_response.status_code)
            
            if add_response.status_code == 201:
                registro_criado = add_response.json()["registro"]
                print(f"Registro criado com ID: {registro_criado['id']}")
                
                # Verificar diário
                diario_response = requests.get("http://127.0.0.1:5000/api/diario", headers=headers)
                print("Registros no diário:", len(diario_response.json()))
                
                # Testar exclusão
                registro_id = registro_criado['id']
                print(f"Testando exclusão do registro {registro_id}...")
                
                delete_response = requests.delete(f"http://127.0.0.1:5000/api/diario/{registro_id}", headers=headers)
                print("Status da exclusão:", delete_response.status_code)
                
                if delete_response.status_code == 200:
                    print("✅ EXCLUSÃO FUNCIONOU PERFEITAMENTE!")
                    
                    # Verificar se foi excluído
                    diario_final = requests.get("http://127.0.0.1:5000/api/diario", headers=headers)
                    print(f"Registros após exclusão: {len(diario_final.json())}")
                else:
                    print("❌ Erro na exclusão:", delete_response.json())
            else:
                print("Erro ao adicionar:", add_response.json())
        else:
            print("Nenhum alimento disponível para teste")
