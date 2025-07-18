import requests
import json

# Teste da API de registro
url = 'http://localhost:5000/api/diario/registrar'
data = {
    'alimento_id': 1,
    'tipo_refeicao': 'almoco'
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
except Exception as e:
    print(f"Erro: {e}")
