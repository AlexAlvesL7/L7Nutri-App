#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sqlite3
import os

def migrar_dados_para_render():
    """Migra dados do SQLite local para PostgreSQL do Render"""
    
    print("🚀 MIGRANDO DADOS PARA RENDER")
    print("=" * 50)
    
    # URL da aplicação no Render
    base_url = "https://l7nutri-app.onrender.com"
    
    # 1. Verificar se o banco local existe
    if not os.path.exists('nutricao.db'):
        print("❌ Banco local nutricao.db não encontrado!")
        return
    
    # 2. Conectar ao SQLite local
    conn = sqlite3.connect('nutricao.db')
    cursor = conn.cursor()
    
    # 3. Buscar todos os alimentos
    cursor.execute("""
        SELECT nome, categoria, energia, proteina, lipidios, carboidrato, 
               fibras, sodio, acucar, calcio, ferro, magnesio, fosforo, 
               potassio, zinco, colesterol, porcao_referencia, fonte_dados
        FROM alimento
    """)
    
    alimentos_locais = cursor.fetchall()
    conn.close()
    
    print(f"📊 Encontrados {len(alimentos_locais)} alimentos no banco local")
    
    # 4. Aguardar a aplicação acordar
    print("⏳ Aguardando aplicação acordar...")
    try:
        response = requests.get(f"{base_url}/", timeout=60)
        print(f"✅ Aplicação respondeu: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Erro ao conectar: {e}")
        print("💡 Aguarde mais alguns segundos...")
    
    # 5. Criar usuário admin
    print("\n👤 Criando usuário administrador...")
    admin_data = {
        "nome": "Administrador",
        "email": "admin@l7nutri.com",
        "senha": "admin123",
        "peso": 70,
        "altura": 175,
        "idade": 30,
        "sexo": "M",
        "nivel_atividade": "Moderadamente ativo",
        "objetivo": "Manter peso"
    }
    
    try:
        response = requests.post(f"{base_url}/api/usuario/registro", 
                                json=admin_data, 
                                timeout=30)
        if response.status_code in [200, 201]:
            print("✅ Usuário admin criado com sucesso!")
        else:
            print(f"⚠️ Admin já existe ou erro: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Erro ao criar admin: {e}")
    
    # 6. Fazer login e obter token
    print("\n🔐 Fazendo login...")
    login_data = {
        "email": "admin@l7nutri.com",
        "senha": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/usuario/login", 
                                json=login_data, 
                                timeout=30)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print("✅ Login realizado com sucesso!")
        else:
            print(f"❌ Erro no login: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return
    
    # 7. Headers com autorização
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 8. Migrar alimentos
    print(f"\n🍎 Migrando {len(alimentos_locais)} alimentos...")
    sucesso = 0
    erros = 0
    
    for alimento in alimentos_locais:
        alimento_data = {
            "nome": alimento[0],
            "categoria": alimento[1] or "Outros",
            "energia": float(alimento[2] or 0),
            "proteina": float(alimento[3] or 0),
            "lipidios": float(alimento[4] or 0),
            "carboidrato": float(alimento[5] or 0),
            "fibras": float(alimento[6] or 0),
            "sodio": float(alimento[7] or 0),
            "acucar": float(alimento[8] or 0),
            "calcio": float(alimento[9] or 0),
            "ferro": float(alimento[10] or 0),
            "magnesio": float(alimento[11] or 0),
            "fosforo": float(alimento[12] or 0),
            "potassio": float(alimento[13] or 0),
            "zinco": float(alimento[14] or 0),
            "colesterol": float(alimento[15] or 0),
            "porcao_referencia": alimento[16] or "100g",
            "fonte_dados": alimento[17] or "TACO"
        }
        
        try:
            response = requests.post(f"{base_url}/api/alimentos", 
                                    json=alimento_data, 
                                    headers=headers,
                                    timeout=10)
            if response.status_code in [200, 201]:
                sucesso += 1
                print(f"✅ {alimento[0]}")
            else:
                erros += 1
                print(f"❌ {alimento[0]} - Erro: {response.status_code}")
        except Exception as e:
            erros += 1
            print(f"❌ {alimento[0]} - Erro: {e}")
    
    # 9. Relatório final
    print(f"\n📊 MIGRAÇÃO CONCLUÍDA:")
    print(f"✅ Sucessos: {sucesso}")
    print(f"❌ Erros: {erros}")
    print(f"📱 Total: {len(alimentos_locais)}")
    
    print(f"\n🌐 ACESSE SUA APLICAÇÃO:")
    print(f"🔗 URL: {base_url}")
    print(f"👤 Login: admin@l7nutri.com")
    print(f"🔑 Senha: admin123")
    
    # 10. Testar API de alimentos
    print(f"\n🧪 Verificando alimentos migrados...")
    try:
        response = requests.get(f"{base_url}/api/alimentos", timeout=30)
        if response.status_code == 200:
            alimentos_render = response.json()
            print(f"✅ {len(alimentos_render)} alimentos disponíveis no Render!")
        else:
            print(f"⚠️ Erro ao verificar alimentos: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Erro ao verificar: {e}")

if __name__ == "__main__":
    migrar_dados_para_render()
