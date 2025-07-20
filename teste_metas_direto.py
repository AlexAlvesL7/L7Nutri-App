#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 TESTE DIRETO DO ENDPOINT DE METAS
Teste direto com usuário existente
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def testar_login_e_metas():
    """Testa login e cálculo de metas"""
    print("🔐 Testando login...")
    
    # Login com usuário de teste
    login_data = {
        'username': 'alexalves',
        'password': 'teste123'
    }
    
    response = requests.post(f"{BASE_URL}/api/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Falha no login: {response.status_code} - {response.text}")
        return
    
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    print("✅ Login realizado com sucesso")
    print(f"🎫 Token: {token[:20]}...")
    
    # Testar endpoint de metas
    print("\n📊 Testando cálculo de metas...")
    
    response = requests.get(f"{BASE_URL}/api/onboarding/metas", headers=headers)
    
    print(f"📡 Status: {response.status_code}")
    print(f"📄 Resposta: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ METAS CALCULADAS COM SUCESSO!")
        print(f"🔥 TMB: {data['calculos']['tmb']} kcal")
        print(f"⚡ Gasto Total: {data['calculos']['gasto_total']} kcal")
        print(f"🎯 Meta Calórica: {data['calculos']['meta_calorica']} kcal")
        
        macros = data['macronutrientes']
        print(f"\n🥗 MACRONUTRIENTES:")
        print(f"🥩 Proteína: {macros['proteina_g']}g ({macros['proteina_perc']}%)")
        print(f"🍞 Carboidrato: {macros['carboidrato_g']}g ({macros['carboidrato_perc']}%)")
        print(f"🥑 Gordura: {macros['gordura_g']}g ({macros['gordura_perc']}%)")
        
        # Verificar se soma dá 100%
        total_perc = macros['proteina_perc'] + macros['carboidrato_perc'] + macros['gordura_perc']
        print(f"📋 Total percentual: {total_perc}%")
        
        # Verificar se calorias batem
        total_calorias = macros['proteina_kcal'] + macros['carboidrato_kcal'] + macros['gordura_kcal']
        print(f"🔢 Total calorias macros: {total_calorias} kcal")
        print(f"🎯 Meta calórica: {data['calculos']['meta_calorica']} kcal")
        
        diferenca = abs(total_calorias - data['calculos']['meta_calorica'])
        print(f"📐 Diferença: {diferenca} kcal")
        
        if diferenca <= 5:
            print("✅ Cálculos CORRETOS!")
        else:
            print("⚠️ Diferença alta nos cálculos")
    
    else:
        print("❌ Falha no cálculo de metas")

if __name__ == "__main__":
    testar_login_e_metas()
