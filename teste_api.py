import requests
import json

# Fazer login
login_data = {
    "username": "admin@admin.com",
    "password": "admin123"
}

response = requests.post("http://127.0.0.1:5000/api/login", json=login_data)
print("Status:", response.status_code)
print("Response:", response.json())

if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"Token: {token}")
    
    # Testar busca de alimentos
    headers = {"Authorization": f"Bearer {token}"}
    busca_response = requests.get("http://127.0.0.1:5000/api/alimentos/buscar?q=arroz", headers=headers)
    print("Busca alimentos:", busca_response.json())
    
    # Verificar diário atual
    diario_response = requests.get("http://127.0.0.1:5000/api/diario", headers=headers)
    print("Diário atual:", diario_response.json())
