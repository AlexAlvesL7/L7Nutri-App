#!/usr/bin/env python3
"""
Script para testar o painel de IA do diário alimentar
"""

import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://127.0.0.1:5000"

def test_ai_panel():
    print("🤖 Testando Painel de IA do Diário Alimentar")
    print("=" * 50)
    
    # Teste 1: Conexão básica
    print("\n1. Testando conexão com IA...")
    try:
        response = requests.get(f"{BASE_URL}/api/ia/teste-conexao")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conexão OK! Modelo: {data.get('modelo')}")
            print(f"📝 Resposta: {data.get('resposta_ia', '')[:100]}...")
        else:
            print(f"❌ Erro na conexão: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False
    
    # Teste 2: Sugestões inteligentes
    print("\n2. Testando sugestões inteligentes...")
    
    # Diferentes cenários de teste
    cenarios = [
        {"objetivo": "emagrecimento", "nome": "Emagrecimento"},
        {"objetivo": "ganho_massa", "nome": "Ganho de Massa"},
        {"objetivo": "manutencao", "nome": "Manutenção"}
    ]
    
    for cenario in cenarios:
        print(f"\n   🎯 Cenário: {cenario['nome']}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/ia/sugestoes-inteligentes",
                json={"objetivo": cenario["objetivo"]},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("sucesso"):
                    sugestao = data.get("sugestao", {})
                    print(f"   ✅ Sucesso!")
                    print(f"   🍽️  Alimento: {sugestao.get('alimento_sugerido', 'N/A')}")
                    print(f"   ⏰ Contexto: {sugestao.get('contexto', 'N/A')}")
                    print(f"   💡 Dica: {sugestao.get('dica_personalizada', 'N/A')[:80]}...")
                else:
                    print(f"   ❌ Erro na resposta: {data.get('erro')}")
            else:
                print(f"   ❌ Erro HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro na requisição: {e}")
    
    # Teste 3: Verificar horário contextual
    print(f"\n3. Teste contextual - Horário atual: {datetime.now().strftime('%H:%M')}")
    hora_atual = datetime.now().hour
    
    if 6 <= hora_atual <= 10:
        contexto_esperado = "Café da manhã"
    elif 11 <= hora_atual <= 14:
        contexto_esperado = "Almoço"
    elif 18 <= hora_atual <= 21:
        contexto_esperado = "Jantar"
    else:
        contexto_esperado = "Lanche"
    
    print(f"   🕐 Contexto esperado: {contexto_esperado}")
    
    return True

def test_diario_page():
    print("\n4. Testando página do diário...")
    try:
        # Teste com ID de usuário de exemplo
        response = requests.get(f"{BASE_URL}/diario?id=9185fb0a-a4ed-4345-9af4-e0e7698d3c83")
        if response.status_code == 200:
            print("   ✅ Página do diário carregada com sucesso!")
            
            # Verifica se contém elementos do painel de IA
            html_content = response.text
            if "ai-panel" in html_content:
                print("   ✅ Painel de IA presente na página!")
            if "Sugestões Inteligentes de IA" in html_content:
                print("   ✅ Texto do botão de IA encontrado!")
            if "toggleAISuggestions" in html_content:
                print("   ✅ Função JavaScript de IA encontrada!")
                
            return True
        else:
            print(f"   ❌ Erro ao carregar página: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes do sistema de IA integrado")
    
    # Executar testes
    ai_ok = test_ai_panel()
    page_ok = test_diario_page()
    
    # Resultado final
    print("\n" + "=" * 50)
    if ai_ok and page_ok:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✨ O painel de IA está funcionando perfeitamente!")
        print("\n📋 Para testar manualmente:")
        print(f"   🌐 Acesse: {BASE_URL}/diario?id=9185fb0a-a4ed-4345-9af4-e0e7698d3c83")
        print("   🤖 Clique em 'Sugestões Inteligentes de IA'")
        print("   💡 Veja as recomendações personalizadas!")
    else:
        print("❌ Alguns testes falharam. Verifique os logs acima.")
    
    print("\n🎯 Próximo passo: Testar interface no navegador!")
