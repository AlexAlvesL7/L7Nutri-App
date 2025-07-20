import requests
import json

# === TESTE DE TODOS OS OBJETIVOS E NÍVEIS DE ATIVIDADE ===

def testar_todos_objetivos():
    """Teste completo de todos os objetivos e níveis de atividade"""
    
    print("🎯 === TESTE COMPLETO DE OBJETIVOS ===\n")
    
    BASE_URL = "http://127.0.0.1:5000"
    
    # Login com usuário existente
    dados_login = {
        "username": "testecompleto77261@gmail.com",
        "password": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/api/login", json=dados_login)
    
    if response.status_code != 200:
        print("❌ Erro no login. Execute primeiro o teste_final_sistema.py")
        return
    
    token = response.json()["access_token"]
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    # Lista de objetivos para testar
    objetivos = [
        {'nome': 'perder_peso', 'descricao': 'Perder Peso'},
        {'nome': 'manter_peso', 'descricao': 'Manter Peso'},
        {'nome': 'ganhar_peso', 'descricao': 'Ganhar Peso'},
        {'nome': 'ganhar_massa', 'descricao': 'Ganhar Massa Muscular'},
        {'nome': 'vida_saudavel', 'descricao': 'Vida Saudável'},
        {'nome': 'performance', 'descricao': 'Performance Esportiva'}
    ]
    
    # Lista de níveis de atividade
    atividades = [
        {'fator': 1.2, 'descricao': 'Sedentário'},
        {'fator': 1.375, 'descricao': 'Levemente Ativo'},
        {'fator': 1.55, 'descricao': 'Moderadamente Ativo'},
        {'fator': 1.725, 'descricao': 'Muito Ativo'},
        {'fator': 1.9, 'descricao': 'Extremamente Ativo'}
    ]
    
    print("📊 Testando diferentes combinações...\n")
    
    sucessos = 0
    total_testes = 0
    
    # Testar algumas combinações importantes
    combinacoes_teste = [
        {'atividade': 1.2, 'objetivo': 'perder_peso'},
        {'atividade': 1.55, 'objetivo': 'manter_peso'},
        {'atividade': 1.725, 'objetivo': 'ganhar_massa'},
        {'atividade': 1.9, 'objetivo': 'performance'},
        {'atividade': 1.375, 'objetivo': 'vida_saudavel'},
        {'atividade': 1.55, 'objetivo': 'ganhar_peso'}
    ]
    
    for i, combo in enumerate(combinacoes_teste, 1):
        print(f"🧪 Teste {i}/6: {combo['objetivo']} + Atividade {combo['atividade']}")
        
        # Atualizar atividade
        response = requests.post(f"{BASE_URL}/api/onboarding/atividade",
                               json={'fator_atividade': combo['atividade']},
                               headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erro ao atualizar atividade: {response.text}")
            continue
        
        # Calcular calorias
        response = requests.post(f"{BASE_URL}/api/calcular-calorias",
                               json={'objetivo': combo['objetivo']},
                               headers=headers)
        
        total_testes += 1
        
        if response.status_code == 200:
            calculos = response.json()
            sucessos += 1
            
            # Encontrar descrições
            obj_desc = next((obj['descricao'] for obj in objetivos if obj['nome'] == combo['objetivo']), combo['objetivo'])
            ativ_desc = next((ativ['descricao'] for ativ in atividades if ativ['fator'] == combo['atividade']), f"Fator {combo['atividade']}")
            
            print(f"  ✅ {obj_desc} | {ativ_desc}")
            print(f"     🔥 TMB: {calculos['tmb']} kcal")
            print(f"     ⚡ GET: {calculos['get']} kcal")
            print(f"     🎯 Objetivo: {calculos['calorias_objetivo']} kcal")
            print(f"     📈 Diferença: {calculos['calorias_objetivo'] - calculos['get']:+} kcal")
        else:
            print(f"  ❌ Erro no cálculo: {response.text}")
        
        print()
    
    # Teste de objetivo inválido
    print("🚫 Testando objetivo inválido...")
    response = requests.post(f"{BASE_URL}/api/calcular-calorias",
                           json={'objetivo': 'objetivo_inexistente'},
                           headers=headers)
    
    if response.status_code != 200:
        print("✅ Validação de objetivo inválido funcionando corretamente")
    else:
        print("⚠️  Sistema deveria rejeitar objetivo inválido")
    
    # Resumo
    print(f"\n📈 === RESUMO DOS TESTES ===")
    print(f"✅ Sucessos: {sucessos}/{total_testes}")
    print(f"📊 Taxa de sucesso: {(sucessos/total_testes)*100:.1f}%")
    
    if sucessos == total_testes:
        print("🎉 TODOS OS OBJETIVOS E ATIVIDADES FUNCIONANDO!")
    else:
        print("⚠️  Alguns testes falharam")
    
    # Mostrar endpoints disponíveis
    print(f"\n🌐 === ENDPOINTS DISPONÍVEIS ===")
    print(f"📊 Dashboard: {BASE_URL}/dashboard-onboarding")
    print(f"👤 Perfil: {BASE_URL}/perfil")
    print(f"🏃 Atividade: {BASE_URL}/atividade-fisica")
    print(f"🎯 Objetivo: {BASE_URL}/objetivo")
    print(f"📖 Diário: {BASE_URL}/diario-alimentar")

if __name__ == "__main__":
    testar_todos_objetivos()
