import requests
import json
import random

# === TESTE FINAL COMPLETO DO SISTEMA ===

def testar_sistema_completo():
    """Teste final do sistema completo de onboarding com cálculo de calorias"""
    
    print("🎯 === TESTE SISTEMA COMPLETO L7 NUTRI ===\n")
    
    BASE_URL = "http://127.0.0.1:5000"
    
    # Gerar usuário único
    user_id = random.randint(10000, 99999)
    
    # === PASSO 1: CADASTRO ===
    print("📝 Passo 1: Cadastrando usuário...")
    
    dados_cadastro = {
        "nome": f"Teste Completo {user_id}",
        "username": f"testecompleto{user_id}@gmail.com",
        "email": f"testecompleto{user_id}@gmail.com",
        "password": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/api/cadastro", json=dados_cadastro)
    
    if response.status_code == 201:
        print("✅ Usuário cadastrado com sucesso!")
    else:
        print(f"❌ Erro no cadastro: {response.text}")
        return
    
    # === PASSO 2: LOGIN ===
    print("\n🔐 Passo 2: Fazendo login...")
    
    dados_login = {
        "username": dados_cadastro["username"],
        "password": dados_cadastro["password"]
    }
    
    response = requests.post(f"{BASE_URL}/api/login", json=dados_login)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login realizado com sucesso!")
        print(f"🎫 Token: {token[:30]}...")
    else:
        print(f"❌ Erro no login: {response.text}")
        return
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    # === PASSO 3: PERFIL ===
    print("\n👤 Passo 3: Atualizando perfil...")
    
    dados_perfil = {
        "idade": 28,
        "genero": "masculino",
        "peso": 78.0,
        "altura": 180
    }
    
    response = requests.put(f"{BASE_URL}/api/usuario/perfil", 
                           json=dados_perfil, headers=headers)
    
    if response.status_code == 200:
        print("✅ Perfil atualizado com sucesso!")
        print(f"📊 Dados: {dados_perfil}")
    else:
        print(f"❌ Erro no perfil: {response.text}")
        return
    
    # === PASSO 4: ATIVIDADE FÍSICA ===
    print("\n🏃 Passo 4: Definindo atividade física...")
    
    dados_atividade = {
        "fator_atividade": 1.725  # Muito ativo
    }
    
    response = requests.post(f"{BASE_URL}/api/onboarding/atividade",
                           json=dados_atividade, headers=headers)
    
    if response.status_code == 200:
        print("✅ Atividade física salva com sucesso!")
        print(f"🏃 Fator: {dados_atividade['fator_atividade']} (Muito Ativo)")
    else:
        print(f"❌ Erro na atividade: {response.text}")
        return
    
    # === PASSO 5: OBJETIVO ===
    print("\n🎯 Passo 5: Definindo objetivo...")
    
    dados_objetivo = {
        "objetivo": "ganhar_massa"
    }
    
    response = requests.put(f"{BASE_URL}/api/usuario/objetivo",
                           json=dados_objetivo, headers=headers)
    
    if response.status_code == 200:
        print("✅ Objetivo salvo com sucesso!")
        print(f"🎯 Objetivo: {dados_objetivo['objetivo']}")
    else:
        print(f"❌ Erro no objetivo: {response.text}")
        return
    
    # === PASSO 6: CÁLCULO DE CALORIAS ===
    print("\n🧮 Passo 6: Calculando necessidades calóricas...")
    
    dados_calculo = {
        "objetivo": "ganhar_massa"
    }
    
    response = requests.post(f"{BASE_URL}/api/calcular-calorias",
                           json=dados_calculo, headers=headers)
    
    if response.status_code == 200:
        calculos = response.json()
        print("✅ Cálculo de calorias realizado com sucesso!")
        print(f"🔥 TMB (Taxa Metabólica Basal): {calculos['tmb']} kcal")
        print(f"⚡ GET (Gasto Energético Total): {calculos['get']} kcal")
        print(f"🎯 Calorias para Objetivo: {calculos['calorias_objetivo']} kcal")
        print(f"📈 Fator Atividade: {calculos['fator_atividade']}")
        print(f"🎪 Fator Objetivo: {calculos['fator_objetivo']}")
    else:
        print(f"❌ Erro no cálculo: {response.text}")
        return
    
    # === PASSO 7: VERIFICAÇÃO FINAL ===
    print("\n📋 Passo 7: Verificando perfil completo...")
    
    response = requests.get(f"{BASE_URL}/api/usuario/perfil", headers=headers)
    
    if response.status_code == 200:
        perfil = response.json()
        print("✅ Perfil recuperado com sucesso!")
        print(f"👤 Nome: {perfil.get('nome')}")
        print(f"📊 Idade: {perfil.get('idade')} anos")
        print(f"⚖️  Peso: {perfil.get('peso')} kg")
        print(f"📏 Altura: {perfil.get('altura')} cm")
        print(f"🏃 Atividade: {perfil.get('fator_atividade')}")
        print(f"🎯 Objetivo: {perfil.get('objetivo')}")
    else:
        print(f"❌ Erro ao recuperar perfil: {response.text}")
        return
    
    # === RESULTADO FINAL ===
    print(f"\n🎉 === ONBOARDING COMPLETO! ===")
    print(f"✅ Usuário: {dados_cadastro['username']}")
    print(f"✅ Perfil: Completo")
    print(f"✅ Atividade: Definida")
    print(f"✅ Objetivo: Configurado")
    print(f"✅ Calorias: Calculadas")
    print(f"\n🌐 Acesso ao dashboard: {BASE_URL}/dashboard-onboarding")
    print(f"🔑 Token para testes: {token}")
    
    return True

if __name__ == "__main__":
    sucesso = testar_sistema_completo()
    if sucesso:
        print("\n🚀 SISTEMA COMPLETO FUNCIONANDO PERFEITAMENTE!")
    else:
        print("\n❌ Houve problemas no teste.")
