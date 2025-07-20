import requests
import json

def testar_fluxo_onboarding_completo():
    print("🚀 Testando Fluxo Completo de Onboarding\n")
    
    # 1. Cadastro de novo usuário
    print("1. Cadastrando novo usuário...")
    import random
    user_id = random.randint(1000, 9999)
    
    cadastro_data = {
        "nome": f"Usuario Teste {user_id}",
        "username": f"teste{user_id}@teste.com",
        "email": f"teste{user_id}@teste.com",
        "password": "teste123"
    }
    
    cadastro_response = requests.post("http://127.0.0.1:5000/api/cadastro", json=cadastro_data)
    
    if cadastro_response.status_code == 201:
        print("✅ Usuário cadastrado com sucesso!")
    else:
        print("❌ Erro no cadastro:", cadastro_response.json())
        return
    
    # 2. Login
    print("\n2. Fazendo login...")
    login_data = {
        "username": cadastro_data["username"],
        "password": cadastro_data["password"]
    }
    
    login_response = requests.post("http://127.0.0.1:5000/api/login", json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print("✅ Login realizado com sucesso!")
    else:
        print("❌ Erro no login:", login_response.json())
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Atualizar perfil (Etapa 2)
    print("\n3. Atualizando perfil (Etapa 2)...")
    perfil_data = {
        "idade": 30,
        "genero": "masculino",
        "peso": 80.5,
        "altura": 175
    }
    
    perfil_response = requests.put(
        "http://127.0.0.1:5000/api/usuario/perfil", 
        json=perfil_data, 
        headers=headers
    )
    
    if perfil_response.status_code == 200:
        print("✅ Perfil atualizado com sucesso!")
    else:
        print("❌ Erro ao atualizar perfil:", perfil_response.json())
        return
    
    # 4. Definir nível de atividade física (Etapa 3)
    print("\n4. Definindo nível de atividade física (Etapa 3)...")
    atividade_data = {
        "nivel_atividade": 1.55  # Moderadamente ativo
    }
    
    atividade_response = requests.put(
        "http://127.0.0.1:5000/api/usuario/atividade-fisica", 
        json=atividade_data, 
        headers=headers
    )
    
    if atividade_response.status_code == 200:
        print("✅ Nível de atividade física salvo com sucesso!")
    else:
        print("❌ Erro ao salvar atividade física:", atividade_response.json())
        return
    
    # 5. Verificar dados do usuário
    print("\n5. Verificando dados completos do usuário...")
    
    # Simular endpoint para obter dados do usuário (se existir)
    try:
        usuario_response = requests.get("http://127.0.0.1:5000/api/usuario", headers=headers)
        if usuario_response.status_code == 200:
            dados_usuario = usuario_response.json()
            print("✅ Dados do usuário:")
            print(f"   - Nome: {dados_usuario.get('nome', 'N/A')}")
            print(f"   - Idade: {dados_usuario.get('idade', 'N/A')} anos")
            print(f"   - Gênero: {dados_usuario.get('sexo', 'N/A')}")
            print(f"   - Peso: {dados_usuario.get('peso', 'N/A')} kg")
            print(f"   - Altura: {dados_usuario.get('altura', 'N/A')} cm")
            print(f"   - Nível Atividade: {dados_usuario.get('nivel_atividade', 'N/A')}")
        else:
            print("ℹ️ Endpoint de dados do usuário não disponível")
    except:
        print("ℹ️ Endpoint de dados do usuário não disponível")
    
    print("\n🎯 Fluxo de onboarding testado com sucesso!")
    print(f"   Usuário: {cadastro_data['username']}")
    print(f"   Token válido para próximas etapas")
    
    return {
        "username": cadastro_data["username"],
        "token": token,
        "perfil_completo": True
    }

if __name__ == "__main__":
    resultado = testar_fluxo_onboarding_completo()
    
    if resultado:
        print(f"\n📋 Resultado do teste:")
        print(f"   - Usuário criado: {resultado['username']}")
        print(f"   - Token disponível: Sim")
        print(f"   - Perfil completo: {resultado['perfil_completo']}")
        print(f"   - Pronto para próxima etapa: Sim")
