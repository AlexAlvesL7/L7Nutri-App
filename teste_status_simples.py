import requests
import json

print("🔍 TESTANDO STATUS ATUAL DO SISTEMA L7NUTRI")
print("=" * 50)

# Teste 1: API básica
try:
    print("\n📡 Testando API básica...")
    r = requests.get('https://l7nutri-app.onrender.com/api/teste', timeout=30)
    print(f"Status: {r.status_code}")
    print(f"Resposta: {r.text[:200]}")
except Exception as e:
    print(f"Erro: {e}")

# Teste 2: Diagnóstico banco
try:
    print("\n🔍 Testando diagnóstico banco...")
    r = requests.get('https://l7nutri-app.onrender.com/api/diagnostico-db', timeout=30)
    print(f"Status: {r.status_code}")
    print(f"Resposta: {r.text[:500]}")
except Exception as e:
    print(f"Erro: {e}")

# Teste 3: Página principal
try:
    print("\n🏠 Testando página principal...")
    r = requests.get('https://l7nutri-app.onrender.com/', timeout=30)
    print(f"Status: {r.status_code}")
    print(f"Tamanho resposta: {len(r.text)} chars")
except Exception as e:
    print(f"Erro: {e}")

print("\n" + "=" * 50)
print("✅ Testes concluídos!")
