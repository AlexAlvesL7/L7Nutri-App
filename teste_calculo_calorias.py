import requests
import json

# === TESTE COMPLETO DO ENDPOINT DE CÁLCULO DE CALORIAS ===

print("🧮 === TESTE DE CÁLCULO DE CALORIAS ===\n")

# Configuração base
BASE_URL = "http://127.0.0.1:5000"

# Dados de teste para login
dados_login = {
    "username": "alex.teste@gmail.com",
    "password": "123456"
}

def fazer_login():
    """Fazer login e obter token JWT"""
    print("🔐 Fazendo login...")
    
    response = requests.post(f"{BASE_URL}/api/login", json=dados_login)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"✅ Login realizado com sucesso!")
        print(f"🎫 Token obtido: {token[:50]}...\n")
        return token
    else:
        print(f"❌ Erro no login: {response.status_code}")
        print(f"📝 Resposta: {response.text}")
        return None

def testar_calculo_calorias(token, objetivo):
    """Testar o endpoint de cálculo de calorias"""
    print(f"🧮 Testando cálculo para objetivo: {objetivo}")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    dados = {
        "objetivo": objetivo
    }
    
    response = requests.post(f"{BASE_URL}/api/calcular-calorias", 
                           json=dados, 
                           headers=headers)
    
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        dados_resposta = response.json()
        print("✅ Cálculo realizado com sucesso!")
        print(f"🔥 TMB: {dados_resposta.get('tmb')} kcal")
        print(f"⚡ GET: {dados_resposta.get('get')} kcal") 
        print(f"🎯 Calorias Objetivo: {dados_resposta.get('calorias_objetivo')} kcal")
        print(f"📈 Fator Atividade: {dados_resposta.get('fator_atividade')}")
        print(f"🎪 Fator Objetivo: {dados_resposta.get('fator_objetivo')}")
        print(f"👤 Dados Usuário: {dados_resposta.get('dados_usuario')}")
        print()
        return True
    else:
        print(f"❌ Erro no cálculo: {response.text}")
        print()
        return False

def main():
    """Função principal do teste"""
    
    # Fazer login
    token = fazer_login()
    if not token:
        print("❌ Não foi possível obter token. Encerrando teste.")
        return
    
    # Lista de objetivos para testar
    objetivos_teste = [
        'perder_peso',
        'manter_peso', 
        'ganhar_peso',
        'ganhar_massa',
        'vida_saudavel',
        'performance'
    ]
    
    sucessos = 0
    total = len(objetivos_teste)
    
    print("🧪 === INICIANDO TESTES DE CÁLCULO ===\n")
    
    # Testar cada objetivo
    for objetivo in objetivos_teste:
        if testar_calculo_calorias(token, objetivo):
            sucessos += 1
    
    # Testar objetivo inválido
    print("🚫 Testando objetivo inválido...")
    testar_calculo_calorias(token, "objetivo_inexistente")
    
    # Resumo dos testes
    print(f"📈 === RESUMO DOS TESTES ===")
    print(f"✅ Sucessos: {sucessos}/{total}")
    print(f"📊 Taxa de sucesso: {(sucessos/total)*100:.1f}%")
    
    if sucessos == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("⚠️  Alguns testes falharam.")

if __name__ == "__main__":
    main()
