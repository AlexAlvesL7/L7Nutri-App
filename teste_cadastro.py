import requests
import json

# Dados do teste
dados_teste = {
    "nome": "Usuário Teste", 
    "email": "teste@l7nutri.com",
    "username": "userteste",
    "password": "senhaforte123"
}

print("🧪 TESTE DO ENDPOINT /api/cadastro")
print("=" * 50)

try:
    # Fazer a requisição
    response = requests.post(
        "http://127.0.0.1:5000/api/cadastro",
        headers={"Content-Type": "application/json"},
        json=dados_teste
    )
    
    # Mostrar resultado
    print(f"📊 STATUS CODE: {response.status_code}")
    print(f"📄 RESPOSTA: {response.json()}")
    
    # Validação do resultado
    if response.status_code == 201:
        print("✅ TESTE PASSOU - Usuário criado com sucesso!")
    else:
        print("❌ TESTE FALHOU - Erro na criação do usuário")
        
except requests.exceptions.ConnectionError:
    print("❌ ERRO: Servidor Flask não está rodando")
except Exception as e:
    print(f"❌ ERRO INESPERADO: {e}")

print("=" * 50)
