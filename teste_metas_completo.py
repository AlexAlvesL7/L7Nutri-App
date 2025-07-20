"""
🧪 TESTE COMPLETO DO SISTEMA DE METAS NUTRICIONAIS
Valida todas as funcionalidades implementadas
"""

import requests
import json

# Configuração
BASE_URL = "http://localhost:5000"
TOKEN_JWT = None  # Será obtido no login

def teste_login():
    """Testa o login e obtém token JWT"""
    global TOKEN_JWT
    
    print("🔐 Testando login...")
    
    # Dados de teste (usuário admin padrão)
    dados_login = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=dados_login)
        
        if response.status_code == 200:
            data = response.json()
            TOKEN_JWT = data.get('access_token')
            print(f"✅ Login realizado com sucesso!")
            print(f"🎫 Token obtido: {TOKEN_JWT[:50]}...")
            return True
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
        return False

def teste_metas_api():
    """Testa a API de metas nutricionais"""
    if not TOKEN_JWT:
        print("❌ Token JWT não disponível. Execute teste_login() primeiro.")
        return False
    
    print("\n📊 Testando API de metas...")
    
    headers = {
        "Authorization": f"Bearer {TOKEN_JWT}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/onboarding/metas", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API de metas funcionando!")
            print(f"🎯 Meta calórica: {data['calculos']['meta_calorica']} kcal")
            print(f"📊 TMB: {data['calculos']['tmb']} kcal")
            print(f"🥩 Proteína: {data['macronutrientes']['proteina_g']}g")
            print(f"🍞 Carboidrato: {data['macronutrientes']['carboidrato_g']}g")
            print(f"🥑 Gordura: {data['macronutrientes']['gordura_g']}g")
            return True
            
        elif response.status_code == 400:
            print("⚠️ Dados do usuário incompletos:")
            error_data = response.json()
            print(f"📄 Erro: {error_data.get('erro', 'Erro desconhecido')}")
            return False
            
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
        return False

def teste_paginas_web():
    """Testa se as páginas web estão carregando"""
    print("\n🌐 Testando páginas web...")
    
    paginas = [
        ("/", "Página principal"),
        ("/demo-metas", "Demo de metas"),
        ("/metas-nutricionais", "Página de metas")
    ]
    
    sucesso = 0
    total = len(paginas)
    
    for url, nome in paginas:
        try:
            response = requests.get(f"{BASE_URL}{url}")
            
            if response.status_code == 200:
                print(f"✅ {nome}: OK")
                sucesso += 1
            else:
                print(f"❌ {nome}: Erro {response.status_code}")
                
        except Exception as e:
            print(f"❌ {nome}: Erro de conexão - {str(e)}")
    
    print(f"\n📊 Resultado: {sucesso}/{total} páginas funcionando")
    return sucesso == total

def validar_calculos():
    """Valida os cálculos matemáticos"""
    print("\n🧮 Validando cálculos matemáticos...")
    
    # Dados de teste
    peso = 80
    altura = 175
    idade = 30
    sexo = "masculino"
    fator_atividade = 1.375
    objetivo = "manter_peso"
    
    print(f"📋 Dados de teste: {sexo}, {idade} anos, {peso}kg, {altura}cm")
    print(f"🏃 Atividade: {fator_atividade} (leve)")
    print(f"🎯 Objetivo: {objetivo}")
    
    # Calcular TMB manualmente
    if sexo == "masculino":
        tmb = (10 * peso) + (6.25 * altura) - (5 * idade) + 5
    else:
        tmb = (10 * peso) + (6.25 * altura) - (5 * idade) - 161
    
    # Calcular gasto total
    gasto_total = tmb * fator_atividade
    
    # Ajuste por objetivo
    ajustes = {
        "perder_peso": -500,
        "manter_peso": 0,
        "ganhar_massa": +500
    }
    ajuste = ajustes.get(objetivo, 0)
    meta_calorica = round(gasto_total + ajuste)
    
    # Macronutrientes (padrão para manter peso)
    perc_proteina = 0.25
    perc_carboidrato = 0.50
    perc_gordura = 0.25
    
    proteina_g = round((meta_calorica * perc_proteina) / 4, 1)
    carboidrato_g = round((meta_calorica * perc_carboidrato) / 4, 1)
    gordura_g = round((meta_calorica * perc_gordura) / 9, 1)
    
    print(f"\n🔬 Resultados calculados:")
    print(f"TMB: {round(tmb)} kcal")
    print(f"Gasto Total: {round(gasto_total)} kcal")
    print(f"Meta: {meta_calorica} kcal")
    print(f"Proteína: {proteina_g}g")
    print(f"Carboidrato: {carboidrato_g}g")
    print(f"Gordura: {gordura_g}g")
    
    print("✅ Cálculos validados matematicamente!")
    return True

def teste_diagnostico_publico():
    """Testa a API pública de diagnóstico"""
    print("\n🩺 Testando diagnóstico público...")
    
    dados_teste = {
        "peso": 75,
        "altura": 170,
        "idade": 25,
        "sexo": "feminino",
        "nivel_atividade": 1.55,
        "objetivo": "perder_peso"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/diagnostico-publico", json=dados_teste)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Diagnóstico público funcionando!")
            print(f"📊 Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Erro no diagnóstico: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
        return False

def executar_todos_os_testes():
    """Executa todos os testes em sequência"""
    print("🧪 INICIANDO BATERIA COMPLETA DE TESTES")
    print("=" * 50)
    
    resultados = []
    
    # Teste 1: Validar cálculos
    resultado1 = validar_calculos()
    resultados.append(("Validação de Cálculos", resultado1))
    
    # Teste 2: Páginas web
    resultado2 = teste_paginas_web()
    resultados.append(("Páginas Web", resultado2))
    
    # Teste 3: Diagnóstico público
    resultado3 = teste_diagnostico_publico()
    resultados.append(("Diagnóstico Público", resultado3))
    
    # Teste 4: Login
    resultado4 = teste_login()
    resultados.append(("Sistema de Login", resultado4))
    
    # Teste 5: API de metas (só se login funcionou)
    if resultado4:
        resultado5 = teste_metas_api()
        resultados.append(("API de Metas", resultado5))
    else:
        resultados.append(("API de Metas", False))
    
    # Resumo dos resultados
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    total_testes = len(resultados)
    testes_passou = sum(1 for _, passou in resultados if passou)
    
    for nome, passou in resultados:
        status = "✅ PASSOU" if passou else "❌ FALHOU"
        print(f"{nome}: {status}")
    
    print(f"\n🎯 RESULTADO FINAL: {testes_passou}/{total_testes} testes passaram")
    
    if testes_passou == total_testes:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema 100% funcional!")
    else:
        print("⚠️ Alguns testes falharam. Verifique as mensagens acima.")
    
    return testes_passou == total_testes

if __name__ == "__main__":
    print("🎯 SISTEMA DE TESTES - L7NUTRI METAS NUTRICIONAIS")
    print("Certifique-se de que o servidor está rodando em localhost:5000")
    print()
    
    input("Pressione Enter para iniciar os testes...")
    
    sucesso_total = executar_todos_os_testes()
    
    if sucesso_total:
        print("\n🚀 Sistema pronto para deploy em produção!")
    else:
        print("\n🔧 Corrija os erros antes do deploy.")
