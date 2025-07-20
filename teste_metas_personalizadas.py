#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 TESTE COMPLETO DO SISTEMA DE METAS PERSONALIZADAS
Teste do endpoint /api/onboarding/metas com diferentes perfis de usuário

Comandos de Teste:
python teste_metas_personalizadas.py
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configurações da API
BASE_URL = "http://127.0.0.1:5000"
ENDPOINTS = {
    'login': f"{BASE_URL}/api/login",
    'cadastro': f"{BASE_URL}/api/cadastro",
    'metas': f"{BASE_URL}/api/onboarding/metas",
    'perfil': f"{BASE_URL}/api/onboarding/perfil",
    'atividade': f"{BASE_URL}/api/onboarding/atividade",
    'objetivo': f"{BASE_URL}/api/onboarding/objetivo",
    'preferencias': f"{BASE_URL}/api/onboarding/preferencias"
}

def criar_linha_separadora(titulo):
    """Cria uma linha separadora visual"""
    linha = "=" * 60
    print(f"\n{linha}")
    print(f"  {titulo}")
    print(linha)

def exibir_resultado_teste(teste_nome, sucesso, detalhes=""):
    """Exibe o resultado de um teste"""
    status = "✅ PASSOU" if sucesso else "❌ FALHOU"
    print(f"{status} - {teste_nome}")
    if detalhes:
        print(f"   Detalhes: {detalhes}")

def fazer_requisicao(method, url, data=None, headers=None):
    """Faz uma requisição HTTP e retorna resposta"""
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        
        return response
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def criar_usuario_completo(perfil_usuario):
    """Cria um usuário completo com onboarding"""
    print(f"\n🔄 Criando usuário: {perfil_usuario['nome']}")
    
    # 1. Cadastro
    response = fazer_requisicao('POST', ENDPOINTS['cadastro'], perfil_usuario)
    if not response or response.status_code != 201:
        print(f"❌ Falha no cadastro: {response.text if response else 'Sem resposta'}")
        return None
    
    # 2. Login
    login_data = {
        'email': perfil_usuario['email'],
        'senha': perfil_usuario['senha']
    }
    response = fazer_requisicao('POST', ENDPOINTS['login'], login_data)
    if not response or response.status_code != 200:
        print(f"❌ Falha no login: {response.text if response else 'Sem resposta'}")
        return None
    
    token = response.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # 3. Perfil
    perfil_data = {
        'idade': perfil_usuario['idade'],
        'sexo': perfil_usuario['sexo'],
        'peso': perfil_usuario['peso'],
        'altura': perfil_usuario['altura']
    }
    response = fazer_requisicao('POST', ENDPOINTS['perfil'], perfil_data, headers)
    if not response or response.status_code != 200:
        print(f"❌ Falha no perfil: {response.text if response else 'Sem resposta'}")
        return None
    
    # 4. Atividade Física
    atividade_data = {
        'fator_atividade': perfil_usuario['fator_atividade']
    }
    response = fazer_requisicao('POST', ENDPOINTS['atividade'], atividade_data, headers)
    if not response or response.status_code != 200:
        print(f"❌ Falha na atividade: {response.text if response else 'Sem resposta'}")
        return None
    
    # 5. Objetivo
    objetivo_data = {
        'objetivo': perfil_usuario['objetivo']
    }
    response = fazer_requisicao('POST', ENDPOINTS['objetivo'], objetivo_data, headers)
    if not response or response.status_code != 200:
        print(f"❌ Falha no objetivo: {response.text if response else 'Sem resposta'}")
        return None
    
    # 6. Preferências (opcional)
    if 'preferencias' in perfil_usuario:
        response = fazer_requisicao('POST', ENDPOINTS['preferencias'], perfil_usuario['preferencias'], headers)
        if response and response.status_code == 200:
            print("✅ Preferências salvas")
    
    print(f"✅ Usuário {perfil_usuario['nome']} criado com sucesso")
    return token

def testar_calculos_metas(token, perfil_esperado):
    """Testa os cálculos de metas"""
    headers = {'Authorization': f'Bearer {token}'}
    
    response = fazer_requisicao('GET', ENDPOINTS['metas'], headers=headers)
    
    if not response:
        return False, "Falha na requisição"
    
    if response.status_code != 200:
        return False, f"Status {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Verificar estrutura da resposta
    campos_obrigatorios = ['usuario_info', 'calculos', 'macronutrientes', 'resumo']
    for campo in campos_obrigatorios:
        if campo not in data:
            return False, f"Campo obrigatório ausente: {campo}"
    
    # Verificar cálculos básicos
    calculos = data['calculos']
    
    # TMB deve ser > 0
    if calculos['tmb'] <= 0:
        return False, f"TMB inválida: {calculos['tmb']}"
    
    # Gasto total deve ser > TMB
    if calculos['gasto_total'] <= calculos['tmb']:
        return False, f"Gasto total deve ser maior que TMB"
    
    # Meta calórica deve ser positiva
    if calculos['meta_calorica'] <= 0:
        return False, f"Meta calórica inválida: {calculos['meta_calorica']}"
    
    # Verificar macronutrientes
    macros = data['macronutrientes']
    total_calorias_macros = (
        macros['proteina_kcal'] + 
        macros['carboidrato_kcal'] + 
        macros['gordura_kcal']
    )
    
    # Tolerância de ±5% nas calorias totais
    diferenca = abs(total_calorias_macros - calculos['meta_calorica'])
    tolerancia = calculos['meta_calorica'] * 0.05
    
    if diferenca > tolerancia:
        return False, f"Soma de macros ({total_calorias_macros}) não bate com meta calórica ({calculos['meta_calorica']})"
    
    return True, data

def main():
    """Função principal de teste"""
    criar_linha_separadora("🎯 TESTE SISTEMA DE METAS PERSONALIZADAS")
    print(f"⏰ Início dos testes: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Perfis de teste diversos
    perfis_teste = [
        {
            'nome': 'Ana Silva',
            'email': f'ana.teste.{int(time.time())}@teste.com',
            'senha': 'teste123',
            'idade': 28,
            'sexo': 'feminino',
            'peso': 65.0,
            'altura': 165.0,
            'fator_atividade': 1.375,  # Leve atividade
            'objetivo': 'perder_peso',
            'preferencias': {
                'estilo_alimentar': 'vegetariano',
                'restricoes': ['lactose', 'gluten'],
                'alimentos_evitar': 'frituras, doces'
            }
        },
        {
            'nome': 'Carlos Santos',
            'email': f'carlos.teste.{int(time.time())+1}@teste.com',
            'senha': 'teste123',
            'idade': 35,
            'sexo': 'masculino',
            'peso': 80.0,
            'altura': 180.0,
            'fator_atividade': 1.725,  # Atividade intensa
            'objetivo': 'ganhar_massa',
            'preferencias': {
                'estilo_alimentar': 'onivoro',
                'restricoes': [],
                'alimentos_evitar': ''
            }
        },
        {
            'nome': 'Maria Costa',
            'email': f'maria.teste.{int(time.time())+2}@teste.com',
            'senha': 'teste123',
            'idade': 42,
            'sexo': 'feminino',
            'peso': 70.0,
            'altura': 160.0,
            'fator_atividade': 1.55,   # Atividade moderada
            'objetivo': 'manter_peso'
        },
        {
            'nome': 'João Oliveira',
            'email': f'joao.teste.{int(time.time())+3}@teste.com',
            'senha': 'teste123',
            'idade': 50,
            'sexo': 'masculino',
            'peso': 90.0,
            'altura': 175.0,
            'fator_atividade': 1.2,    # Sedentário
            'objetivo': 'vida_saudavel'
        }
    ]
    
    resultados_testes = []
    
    for i, perfil in enumerate(perfis_teste, 1):
        criar_linha_separadora(f"TESTE {i}/4: {perfil['nome']}")
        
        # Criar usuário completo
        token = criar_usuario_completo(perfil)
        if not token:
            resultados_testes.append(False)
            print(f"❌ Falha na criação do usuário {perfil['nome']}")
            continue
        
        # Testar cálculo de metas
        sucesso, resultado = testar_calculos_metas(token, perfil)
        resultados_testes.append(sucesso)
        
        if sucesso:
            print(f"✅ Metas calculadas com sucesso para {perfil['nome']}")
            
            # Exibir resumo dos resultados
            data = resultado
            calculos = data['calculos']
            macros = data['macronutrientes']
            
            print(f"📊 Resumo:")
            print(f"   • TMB: {calculos['tmb']} kcal")
            print(f"   • Gasto Total: {calculos['gasto_total']} kcal")
            print(f"   • Meta Calórica: {calculos['meta_calorica']} kcal")
            print(f"   • Proteína: {macros['proteina_g']}g ({macros['proteina_perc']}%)")
            print(f"   • Carboidrato: {macros['carboidrato_g']}g ({macros['carboidrato_perc']}%)")
            print(f"   • Gordura: {macros['gordura_g']}g ({macros['gordura_perc']}%)")
            
            # Verificar se tem preferências
            if data.get('preferencias'):
                prefs = data['preferencias']
                print(f"   • Estilo: {prefs.get('estilo_alimentar', 'Não definido')}")
                if prefs.get('restricoes'):
                    print(f"   • Restrições: {', '.join(prefs['restricoes'])}")
            
        else:
            print(f"❌ Falha no teste de metas: {resultado}")
        
        print()  # Linha em branco
        time.sleep(1)  # Pausa entre testes
    
    # Resumo final
    criar_linha_separadora("📋 RESUMO DOS TESTES")
    
    total_testes = len(resultados_testes)
    testes_passou = sum(resultados_testes)
    testes_falhou = total_testes - testes_passou
    
    print(f"Total de testes: {total_testes}")
    print(f"✅ Passou: {testes_passou}")
    print(f"❌ Falhou: {testes_falhou}")
    print(f"📈 Taxa de sucesso: {(testes_passou/total_testes)*100:.1f}%")
    
    if testes_passou == total_testes:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema de metas funcionando perfeitamente.")
        return 0
    else:
        print(f"\n⚠️ {testes_falhou} teste(s) falharam. Verifique os logs acima.")
        return 1

if __name__ == "__main__":
    try:
        codigo_saida = main()
        sys.exit(codigo_saida)
    except KeyboardInterrupt:
        print("\n\n⏹️ Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Erro inesperado: {e}")
        sys.exit(1)
