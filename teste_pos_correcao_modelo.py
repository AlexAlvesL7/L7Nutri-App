#!/usr/bin/env python3
"""
Teste pós-correção do modelo StreakUsuario
Verifica se o sistema está funcionando após as mudanças
"""

import requests
import time

def testar_sistema():
    """Testa se o sistema está funcionando após correções"""
    base_url = "https://l7nutri-app.onrender.com"
    
    print("🔍 TESTANDO SISTEMA APÓS CORREÇÃO MODELO STREAKUSUARIO")
    print("=" * 60)
    
    # Aguardar deploy
    print("⏱️ Aguardando deploy automático (30 segundos)...")
    time.sleep(30)
    
    tests = [
        {
            'name': 'API Básica',
            'url': f'{base_url}/api/teste',
            'expected': 200
        },
        {
            'name': 'Diagnóstico Banco',
            'url': f'{base_url}/api/diagnostico-db',
            'expected': 200
        },
        {
            'name': 'Página Principal',
            'url': f'{base_url}/',
            'expected': 200
        },
        {
            'name': 'Página Cadastro',
            'url': f'{base_url}/cadastro',
            'expected': 200
        }
    ]
    
    resultados = []
    
    for test in tests:
        print(f"\n🧪 Testando {test['name']}...")
        try:
            response = requests.get(test['url'], timeout=30)
            status = response.status_code
            
            if status == test['expected']:
                print(f"✅ {test['name']}: Status {status} - OK")
                resultados.append(True)
            else:
                print(f"❌ {test['name']}: Status {status} - ERRO")
                resultados.append(False)
                
        except Exception as e:
            print(f"❌ {test['name']}: Erro de conexão - {str(e)}")
            resultados.append(False)
    
    print("\n" + "=" * 60)
    sucessos = sum(resultados)
    total = len(resultados)
    
    if sucessos == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema funcionando corretamente após correção do modelo StreakUsuario")
        print("✅ Deploy automático bem-sucedido")
    else:
        print(f"⚠️ {sucessos}/{total} testes passaram")
        print("❌ Ainda há problemas no sistema")
    
    print("=" * 60)
    return sucessos == total

if __name__ == "__main__":
    testar_sistema()
