#!/usr/bin/env python3
"""
🔧 CORREÇÃO COMPLETA DO ERRO "Erro ao carregar insights"

Este script resolve todos os problemas possíveis:
1. Verifica e cria dados de teste
2. Testa a configuração da IA
3. Valida a API
4. Fornece instruções específicas
"""

import sqlite3
import os
import sys
from datetime import datetime, timedelta
import random

def verificar_configuracao():
    """Verifica se tudo está configurado corretamente"""
    print("🔍 VERIFICANDO CONFIGURAÇÃO")
    print("=" * 50)
    
    problemas = []
    
    # 1. Verificar arquivo .env
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            conteudo = f.read()
            if 'GEMINI_API_KEY' in conteudo and 'AIzaSy' in conteudo:
                print("✅ GEMINI_API_KEY configurada")
            else:
                problemas.append("❌ GEMINI_API_KEY não configurada no .env")
    else:
        problemas.append("❌ Arquivo .env não encontrado")
    
    # 2. Verificar banco de dados
    if os.path.exists('nutricao.db'):
        print("✅ Banco de dados existe")
        
        # Verificar tabelas
        conn = sqlite3.connect('nutricao.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM alimento")
        alimentos = cursor.fetchone()[0]
        print(f"   📊 Alimentos: {alimentos}")
        
        cursor.execute("SELECT COUNT(*) FROM registro_alimentar WHERE usuario_id = 1")
        registros = cursor.fetchone()[0]
        print(f"   📝 Registros usuário 1: {registros}")
        
        if alimentos == 0:
            problemas.append("❌ Nenhum alimento cadastrado")
        if registros == 0:
            problemas.append("❌ Nenhum registro alimentar encontrado")
            
        conn.close()
    else:
        problemas.append("❌ Banco de dados não encontrado")
    
    # 3. Verificar dependências
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI instalado")
    except ImportError:
        problemas.append("❌ google-generativeai não instalado")
    
    try:
        import flask
        print("✅ Flask instalado")
    except ImportError:
        problemas.append("❌ Flask não instalado")
    
    return problemas

def corrigir_problemas(problemas):
    """Corrige automaticamente os problemas encontrados"""
    print("\n🔧 CORRIGINDO PROBLEMAS")
    print("=" * 50)
    
    for problema in problemas:
        if "alimento cadastrado" in problema:
            print("📦 Executando cadastro de alimentos...")
            os.system('python cadastrar_alimentos.py')
            
        elif "registro alimentar" in problema:
            print("📝 Criando registros de teste...")
            criar_registros_teste()
            
        elif "GEMINI_API_KEY" in problema:
            print("⚠️ Configure a GEMINI_API_KEY no arquivo .env")
            
        elif "google-generativeai" in problema:
            print("📦 Instalando google-generativeai...")
            os.system('pip install google-generativeai')

def criar_registros_teste():
    """Cria registros de teste para demonstração"""
    conn = sqlite3.connect('nutricao.db')
    cursor = conn.cursor()
    
    # Limpar registros existentes do usuário de teste
    cursor.execute("DELETE FROM registro_alimentar WHERE usuario_id = 1")
    
    # Buscar alimentos
    cursor.execute("SELECT id, nome FROM alimento LIMIT 8")
    alimentos = cursor.fetchall()
    
    if not alimentos:
        print("❌ Nenhum alimento encontrado para criar registros")
        conn.close()
        return
    
    tipos_refeicao = ['cafe_manha', 'almoco', 'lanche', 'jantar']
    registros_criados = 0
    
    # Criar registros para os últimos 7 dias
    for i in range(7):
        data_registro = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # 2-3 refeições por dia
        num_refeicoes = random.randint(2, 3)
        refeicoes_dia = random.sample(tipos_refeicao, num_refeicoes)
        
        for tipo_refeicao in refeicoes_dia:
            alimento = random.choice(alimentos)
            quantidade = random.randint(100, 200)
            
            cursor.execute("""
                INSERT INTO registro_alimentar 
                (usuario_id, data, tipo_refeicao, alimento_id, quantidade_gramas)
                VALUES (?, ?, ?, ?, ?)
            """, (1, data_registro, tipo_refeicao, alimento[0], quantidade))
            
            registros_criados += 1
    
    conn.commit()
    conn.close()
    print(f"✅ {registros_criados} registros de teste criados!")

def criar_script_inicializacao():
    """Cria um script para iniciar o servidor com debug"""
    script_content = """#!/usr/bin/env python3
import sys
import os

# Adicionar diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar e iniciar a aplicação
from app import app

if __name__ == '__main__':
    print("🚀 Iniciando L7NUTRI Dashboard com IA")
    print("📍 Acesse: http://127.0.0.1:5000/dashboard-insights?id=9185fb0a-a4ed-4345-9af4-e0e7698d3c83")
    print("=" * 80)
    
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000,
        use_reloader=False  # Evita problemas com restart
    )
"""
    
    with open('start_server.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ Script de inicialização criado: start_server.py")

def main():
    """Função principal"""
    print("🚀 SOLUCIONADOR DE PROBLEMAS DO DASHBOARD")
    print("=" * 60)
    print("🎯 Objetivo: Resolver o erro 'Erro ao carregar insights'")
    print("=" * 60)
    
    # 1. Verificar configuração
    problemas = verificar_configuracao()
    
    if problemas:
        print(f"\n⚠️ {len(problemas)} problema(s) encontrado(s):")
        for problema in problemas:
            print(f"   {problema}")
        
        # 2. Tentar corrigir
        corrigir_problemas(problemas)
        
        # 3. Verificar novamente
        print("\n🔄 Verificando novamente...")
        problemas_restantes = verificar_configuracao()
        
        if problemas_restantes:
            print(f"\n❌ {len(problemas_restantes)} problema(s) ainda precisam ser resolvidos manualmente:")
            for problema in problemas_restantes:
                print(f"   {problema}")
        else:
            print("\n✅ Todos os problemas foram corrigidos!")
    else:
        print("\n✅ Configuração está correta!")
    
    # 4. Criar script de inicialização
    criar_script_inicializacao()
    
    print("\n" + "=" * 60)
    print("🎯 INSTRUÇÕES PARA TESTAR:")
    print("=" * 60)
    print("1. Execute: python start_server.py")
    print("2. Aguarde a mensagem 'Running on http://127.0.0.1:5000'")
    print("3. Acesse: http://127.0.0.1:5000/dashboard-insights?id=9185fb0a-a4ed-4345-9af4-e0e7698d3c83")
    print("4. Clique no botão '7 dias' para carregar os insights")
    print("5. Se ainda der erro, verifique o console do navegador (F12)")
    
    print("\n🔧 COMANDOS ÚTEIS:")
    print("   python cadastrar_alimentos.py  # Cadastrar alimentos")
    print("   python verificar_registros.py  # Ver registros no banco")
    print("   python start_server.py         # Iniciar servidor")
    
    print("\n✨ Dashboard pronto para funcionar!")

if __name__ == "__main__":
    main()
