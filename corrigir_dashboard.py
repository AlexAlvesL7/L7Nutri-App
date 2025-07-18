#!/usr/bin/env python3
"""
Script para verificar e criar dados de teste para o dashboard
"""

import sqlite3
from datetime import datetime, timedelta
import random

def verificar_dados():
    """Verifica se há dados no banco"""
    conn = sqlite3.connect('nutricao.db')
    cursor = conn.cursor()
    
    print("🔍 VERIFICANDO DADOS DO BANCO")
    print("=" * 50)
    
    # Verificar usuários
    cursor.execute("SELECT COUNT(*) FROM usuario")
    usuarios = cursor.fetchone()[0]
    print(f"👥 Usuários cadastrados: {usuarios}")
    
    # Verificar alimentos
    cursor.execute("SELECT COUNT(*) FROM alimento")
    alimentos = cursor.fetchone()[0]
    print(f"🍎 Alimentos cadastrados: {alimentos}")
    
    # Verificar registros alimentares
    cursor.execute("SELECT COUNT(*) FROM registro_alimentar")
    registros = cursor.fetchone()[0]
    print(f"📝 Registros alimentares: {registros}")
    
    # Verificar registros dos últimos 7 dias
    data_limite = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    cursor.execute("""
        SELECT COUNT(*) FROM registro_alimentar 
        WHERE data >= ? AND usuario_id = 1
    """, (data_limite,))
    registros_recentes = cursor.fetchone()[0]
    print(f"📊 Registros últimos 7 dias (usuário 1): {registros_recentes}")
    
    conn.close()
    return registros_recentes > 0

def criar_dados_teste():
    """Cria dados de teste para demonstração"""
    conn = sqlite3.connect('nutricao.db')
    cursor = conn.cursor()
    
    print("\n🧪 CRIANDO DADOS DE TESTE")
    print("=" * 50)
    
    # Buscar alguns alimentos para usar nos registros
    cursor.execute("SELECT id, nome FROM alimento LIMIT 10")
    alimentos = cursor.fetchall()
    
    if not alimentos:
        print("❌ Nenhum alimento encontrado! Execute cadastrar_alimentos.py primeiro")
        conn.close()
        return False
    
    # Criar registros para os últimos 7 dias
    tipos_refeicao = ['cafe_manha', 'almoco', 'lanche', 'jantar']
    registros_criados = 0
    
    for i in range(7):
        data_registro = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # 2-4 refeições por dia
        num_refeicoes = random.randint(2, 4)
        refeicoes_dia = random.sample(tipos_refeicao, num_refeicoes)
        
        for tipo_refeicao in refeicoes_dia:
            # Escolher alimento aleatório
            alimento = random.choice(alimentos)
            quantidade = random.randint(80, 200)  # 80g a 200g
            
            try:
                cursor.execute("""
                    INSERT INTO registro_alimentar 
                    (usuario_id, data, tipo_refeicao, alimento_id, quantidade_gramas)
                    VALUES (?, ?, ?, ?, ?)
                """, (1, data_registro, tipo_refeicao, alimento[0], quantidade))
                
                registros_criados += 1
                print(f"✅ Registro criado: {data_registro} - {tipo_refeicao} - {alimento[1]} ({quantidade}g)")
                
            except sqlite3.IntegrityError:
                print(f"⚠️ Registro já existe: {data_registro} - {tipo_refeicao}")
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 {registros_criados} novos registros criados!")
    return True

def testar_api():
    """Testa a API do dashboard"""
    import requests
    import json
    
    print("\n🧪 TESTANDO API DO DASHBOARD")
    print("=" * 50)
    
    url = "http://127.0.0.1:5000/api/ia/dashboard-insights"
    payload = {"periodo": 7}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API funcionando!")
            print(f"📊 Estatísticas: {data.get('estatisticas', {})}")
            if 'insights_ia' in data:
                print("🧠 IA respondeu com sucesso!")
            else:
                print("⚠️ Resposta sem insights da IA")
        else:
            print(f"❌ Erro: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando. Execute: python app.py")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO E CORREÇÃO DO DASHBOARD")
    print("=" * 60)
    
    # Verificar dados existentes
    tem_dados = verificar_dados()
    
    if not tem_dados:
        print("\n⚠️ Poucos dados encontrados. Criando dados de teste...")
        criar_dados_teste()
    else:
        print("\n✅ Dados suficientes encontrados!")
    
    print("\n🌐 Para testar o dashboard:")
    print("1. Execute: python app.py")
    print("2. Acesse: http://127.0.0.1:5000/dashboard-insights?id=9185fb0a-a4ed-4345-9af4-e0e7698d3c83")
    print("3. Clique em '7 dias' para ver a análise")
    
    # Tentar testar a API (se o servidor estiver rodando)
    testar_api()
