#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validação pré-deploy
Verifica se tudo está configurado corretamente antes do upload
"""

import os
import sys
from dotenv import load_dotenv

def validar_configuracao():
    """
    Valida todas as configurações necessárias para o deploy
    """
    print("🔍 VALIDANDO CONFIGURAÇÃO PARA DEPLOY")
    print("=" * 50)
    
    erros = []
    avisos = []
    
    # 1. Verificar arquivo .env
    if not os.path.exists('.env'):
        erros.append("❌ Arquivo .env não encontrado")
        print("💡 Copie env_template.txt para .env e configure")
    else:
        load_dotenv()
        print("✅ Arquivo .env encontrado")
        
        # Verificar variáveis essenciais
        variaveis_obrigatorias = [
            'FLASK_ENV',
            'SECRET_KEY',
            'DATABASE_URL',
            'GEMINI_API_KEY',
            'JWT_SECRET_KEY'
        ]
        
        for var in variaveis_obrigatorias:
            valor = os.getenv(var)
            if not valor:
                erros.append(f"❌ Variável {var} não configurada")
            elif valor in ['sua_chave_aqui', 'SUA_CHAVE_AQUI']:
                erros.append(f"❌ Variável {var} não foi alterada do template")
            else:
                print(f"✅ {var} configurada")
        
        # Verificar se está em modo produção
        if os.getenv('FLASK_ENV') != 'production':
            avisos.append("⚠️  FLASK_ENV não está definida como 'production'")
    
    # 2. Verificar arquivos essenciais
    arquivos_obrigatorios = [
        'app.py',
        'requirements.txt',
        'gunicorn.conf.py',
        'init_producao.py',
        'templates/home.html',
        'templates/login.html',
        'templates/cadastro.html',
        'templates/logout.html',
        'templates/diario_alimentar.html',
        'templates/dashboard_insights.html'
    ]
    
    print("\n📁 Verificando arquivos essenciais...")
    for arquivo in arquivos_obrigatorios:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo}")
        else:
            erros.append(f"❌ Arquivo {arquivo} não encontrado")
    
    # 3. Verificar dependências
    print("\n📦 Verificando requirements.txt...")
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            conteudo = f.read()
            deps_essenciais = [
                'Flask',
                'Flask-SQLAlchemy',
                'Flask-JWT-Extended',
                'PyMySQL',
                'gunicorn',
                'python-dotenv',
                'google-generativeai'
            ]
            
            for dep in deps_essenciais:
                if dep in conteudo:
                    print(f"✅ {dep}")
                else:
                    erros.append(f"❌ Dependência {dep} não encontrada")
    
    # 4. Testar importação do app
    print("\n🧪 Testando importação da aplicação...")
    try:
        sys.path.insert(0, '.')
        from app import app, db
        print("✅ Aplicação importada com sucesso")
        
        # Testar configuração do banco
        if 'mysql' in str(app.config.get('SQLALCHEMY_DATABASE_URI', '')):
            print("✅ Configuração MySQL detectada")
        else:
            avisos.append("⚠️  Não detectada configuração MySQL")
            
    except Exception as e:
        erros.append(f"❌ Erro ao importar aplicação: {str(e)}")
    
    # 5. Verificar estrutura de pastas
    print("\n📂 Verificando estrutura de pastas...")
    pastas_necessarias = ['templates']
    
    for pasta in pastas_necessarias:
        if os.path.exists(pasta) and os.path.isdir(pasta):
            print(f"✅ Pasta {pasta}/")
        else:
            erros.append(f"❌ Pasta {pasta}/ não encontrada")
    
    # 6. Relatório final
    print("\n" + "=" * 50)
    print("📊 RELATÓRIO DE VALIDAÇÃO")
    print("=" * 50)
    
    if not erros and not avisos:
        print("🎉 TUDO CERTO! Pronto para deploy!")
        print("\n📋 Próximos passos:")
        print("1. Compacte todos os arquivos em um ZIP")
        print("2. Faça upload para a Hostinger")
        print("3. Configure a aplicação Python no painel")
        print("4. Execute: python init_producao.py")
        return True
        
    if avisos:
        print("⚠️  AVISOS:")
        for aviso in avisos:
            print(f"   {aviso}")
    
    if erros:
        print("\n❌ ERROS ENCONTRADOS:")
        for erro in erros:
            print(f"   {erro}")
        print("\n🔧 Corrija os erros antes de fazer o deploy!")
        return False
    
    if avisos and not erros:
        print("\n⚠️  Há avisos, mas você pode prosseguir com o deploy.")
        return True

def gerar_checklist():
    """Gera checklist de deploy"""
    checklist = """
📋 CHECKLIST DE DEPLOY HOSTINGER

□ 1. Banco de dados MySQL criado na Hostinger
□ 2. Dados de conexão anotados (host, porta, usuário, senha)
□ 3. Chave Google Gemini API obtida
□ 4. Arquivo .env configurado com dados reais
□ 5. Todos os arquivos validados (execute validar_deploy.py)
□ 6. Arquivos compactados em ZIP
□ 7. Upload feito para public_html da Hostinger
□ 8. Aplicação Python configurada no painel
□ 9. Dependências instaladas (pip install -r requirements.txt)
□ 10. Banco inicializado (python init_producao.py)
□ 11. Aplicação testada e funcionando

🎯 APÓS DEPLOY:
□ Teste login com admin/admin123
□ Altere senha do administrador
□ Teste dashboard de IA
□ Teste registro de alimentos
□ Configure domínio personalizado (opcional)
"""
    
    print(checklist)
    with open('checklist_deploy.txt', 'w', encoding='utf-8') as f:
        f.write(checklist)
    print("💾 Checklist salvo em 'checklist_deploy.txt'")

if __name__ == '__main__':
    sucesso = validar_configuracao()
    
    if sucesso:
        print("\n📋 Gerando checklist de deploy...")
        gerar_checklist()
    
    print(f"\n{'🎉 VALIDAÇÃO CONCLUÍDA!' if sucesso else '🔧 CORRIJA OS ERROS!'}")
