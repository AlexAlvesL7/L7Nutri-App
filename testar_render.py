#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

def testar_render():
    """Testa se a aplicação no Render está funcionando"""
    
    print("🔍 TESTANDO L7NUTRI NO RENDER")
    print("=" * 40)
    
    url = "https://l7nutri-app.onrender.com"
    
    print(f"🌐 Testando: {url}")
    print("⏳ Aguardando aplicação acordar...")
    
    # Tentar múltiplas vezes
    for tentativa in range(1, 6):
        try:
            print(f"\n🔄 Tentativa {tentativa}/5...")
            response = requests.get(url, timeout=60)
            
            if response.status_code == 200:
                print(f"✅ SUCESSO! Status: {response.status_code}")
                print(f"📄 Conteúdo: {len(response.text)} caracteres")
                
                # Verificar se é página HTML ou loading
                if "L7Nutri" in response.text or "html" in response.text.lower():
                    print("🎉 APLICAÇÃO CARREGOU CORRETAMENTE!")
                    return True
                else:
                    print("⚠️ Ainda carregando...")
                    
            else:
                print(f"⚠️ Status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout - aplicação ainda acordando...")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        if tentativa < 5:
            print("⏳ Aguardando 30 segundos...")
            time.sleep(30)
    
    print("❌ Aplicação não respondeu adequadamente")
    return False

def testar_login():
    """Testa sistema de login"""
    
    print("\n🔐 TESTANDO SISTEMA DE LOGIN")
    print("=" * 40)
    
    url = "https://l7nutri-app.onrender.com"
    
    # Testar página de login
    try:
        response = requests.get(f"{url}/login", timeout=30)
        if response.status_code == 200:
            print("✅ Página de login acessível")
        else:
            print(f"⚠️ Login page status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar login: {e}")
    
    # Testar API de alimentos
    try:
        response = requests.get(f"{url}/api/alimentos", timeout=30)
        if response.status_code == 200:
            alimentos = response.json()
            print(f"✅ API alimentos: {len(alimentos)} alimentos")
        else:
            print(f"⚠️ API alimentos status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na API: {e}")

if __name__ == "__main__":
    if testar_render():
        testar_login()
        
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print(f"1. Acesse: https://l7nutri-app.onrender.com")
        print(f"2. Aguarde carregar completamente")
        print(f"3. Teste login (se houver usuário cadastrado)")
        print(f"4. Se não houver dados, execute migração manual")
    else:
        print(f"\n💡 AGUARDE MAIS ALGUNS MINUTOS")
        print(f"A aplicação pode demorar para acordar no primeiro acesso")
