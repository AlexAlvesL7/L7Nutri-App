import requests

try:
    r = requests.get('https://l7nutri-app.onrender.com/api/diagnostico-db')
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Erro: {e}")
