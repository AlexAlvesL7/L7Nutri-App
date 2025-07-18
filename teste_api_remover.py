#!/usr/bin/env python3
import urllib.request
import json

# Teste da API de remoção usando urllib
url = 'http://localhost:5000/api/diario/remover'
data = {'registro_id': 2}

# Converte para JSON e codifica
json_data = json.dumps(data).encode('utf-8')

# Cria a requisição
req = urllib.request.Request(url, data=json_data)
req.add_header('Content-Type', 'application/json')

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print(f"Status: {response.status}")
        print(f"Resposta: {result}")
except Exception as e:
    print(f"Erro: {e}")
