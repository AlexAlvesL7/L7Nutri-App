#!/usr/bin/env python3
"""
Script para adicionar dados de teste e testar o dashboard
"""

import sqlite3
from datetime import datetime, timedelta
import random

def adicionar_dados_teste():
    """Adiciona dados de teste ao banco"""
    conn = sqlite3.connect('nutricao.db')
    cursor = conn.cursor()
    
    print("🧪 ADICIONANDO DADOS DE TESTE")
    print("=" * 50)
    
    # Primeiro, verificar se já há alimentos
    cursor.execute("SELECT COUNT(*) FROM alimento")
    total_alimentos = cursor.fetchone()[0]
    
    if total_alimentos == 0:
        print("❌ Nenhum alimento cadastrado! Execute cadastrar_alimentos.py primeiro")
        conn.close()
        return False
    
    # Limpar registros anteriores do usuário de teste
    cursor.execute("DELETE FROM registro_alimentar WHERE usuario_id = 1")
    
    # Buscar alguns alimentos
    cursor.execute("SELECT id, nome FROM alimento LIMIT 10")
    alimentos = cursor.fetchall()
    
    # Tipos de refeição
    tipos_refeicao = ['cafe_manha', 'almoco', 'lanche', 'jantar']
    
    registros_criados = 0
    
    # Criar registros para os últimos 10 dias
    for i in range(10):
        data_registro = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # 2-4 refeições por dia
        num_refeicoes = random.randint(2, 4)
        refeicoes_dia = random.sample(tipos_refeicao, num_refeicoes)
        
        for tipo_refeicao in refeicoes_dia:
            # Escolher alimento aleatório
            alimento = random.choice(alimentos)
            quantidade = random.randint(80, 250)  # 80g a 250g
            
            cursor.execute("""
                INSERT INTO registro_alimentar 
                (usuario_id, data, tipo_refeicao, alimento_id, quantidade_gramas)
                VALUES (?, ?, ?, ?, ?)
            """, (1, data_registro, tipo_refeicao, alimento[0], quantidade))
            
            registros_criados += 1
            print(f"✅ {data_registro} - {tipo_refeicao} - {alimento[1]} ({quantidade}g)")
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 {registros_criados} registros criados com sucesso!")
    return True

def testar_servidor():
    """Testa se o servidor está rodando"""
    import requests
    
    print("\n🌐 TESTANDO SERVIDOR")
    print("=" * 50)
    
    try:
        # Testar endpoint de teste
        response = requests.get("http://127.0.0.1:5000/api/teste", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando!")
            return True
        else:
            print(f"❌ Servidor retornou: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando")
        print("💡 Execute: python app.py")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_api_insights():
    """Testa a API de insights"""
    import requests
    import json
    
    print("\n🧠 TESTANDO API DE INSIGHTS")
    print("=" * 50)
    
    url = "http://127.0.0.1:5000/api/ia/dashboard-insights"
    payload = {"periodo": 7}
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API funcionando!")
            
            if data.get('sucesso'):
                print("📊 Estatísticas encontradas:")
                stats = data.get('estatisticas', {})
                for key, value in stats.items():
                    print(f"   {key}: {value}")
                
                insights = data.get('insights_ia', {})
                if insights:
                    print("🧠 Insights da IA encontrados:")
                    for key, value in insights.items():
                        if isinstance(value, list):
                            print(f"   {key}: {len(value)} itens")
                        else:
                            print(f"   {key}: {str(value)[:50]}...")
                else:
                    print("⚠️ Nenhum insight da IA encontrado")
            else:
                print(f"❌ API retornou erro: {data.get('erro')}")
        else:
            print(f"❌ Erro HTTP: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - IA pode estar processando")
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🚀 SETUP E TESTE COMPLETO DO DASHBOARD")
    print("=" * 60)
    
    # 1. Adicionar dados de teste
    if adicionar_dados_teste():
        print("\n✅ Dados de teste adicionados!")
        
        # 2. Testar servidor
        if testar_servidor():
            # 3. Testar API
            testar_api_insights()
            
            print("\n🌐 ACESSE O DASHBOARD:")
            print("URL: http://127.0.0.1:5000/dashboard-insights?id=9185fb0a-a4ed-4345-9af4-e0e7698d3c83")
        else:
            print("\n❌ Inicie o servidor primeiro com: python app.py")
    else:
        print("\n❌ Falha ao criar dados de teste")
