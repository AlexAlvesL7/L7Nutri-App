#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuração rápida para banco MySQL Hostinger
Configura automaticamente com as credenciais fornecidas
"""

import os
import sys

def configurar_banco_hostinger():
    """
    Configura o app.py com as credenciais do banco MySQL da Hostinger
    """
    print("🔧 CONFIGURANDO BANCO MYSQL HOSTINGER")
    print("=" * 50)
    
    # Credenciais fornecidas
    db_user = 'u419790683_l7nutri_user'
    db_pass = 'Duda@1401'
    db_host = 'localhost'
    db_name = 'u419790683_l7nutri_db'
    
    print(f"📋 Configurando com:")
    print(f"   • Usuário: {db_user}")
    print(f"   • Host: {db_host}")
    print(f"   • Banco: {db_name}")
    
    # Ler arquivo app.py
    if not os.path.exists('app.py'):
        print("❌ Arquivo app.py não encontrado!")
        return False
    
    with open('app.py', 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Configuração para adicionar
    nova_config = f"""# === CONFIGURAÇÃO DO BANCO DE DADOS ===
if is_production:
    # Produção: MySQL Hostinger com credenciais específicas
    db_user = '{db_user}'
    db_pass = '{db_pass}'
    db_host = '{db_host}'
    db_name = '{db_name}'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{{db_user}}:{{db_pass}}@{{db_host}}/{{db_name}}'
    print("🔥 MODO PRODUÇÃO: Usando MySQL Hostinger")
else:
    # Desenvolvimento: usa SQLite local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.getcwd()), 'nutricao.db')
    print("🔧 MODO DESENVOLVIMENTO: Usando SQLite local")"""
    
    # Procurar e substituir a configuração existente
    if "# === CONFIGURAÇÃO DO BANCO DE DADOS ===" in conteudo:
        print("✅ Configuração existente encontrada, atualizando...")
        
        # Encontrar início e fim da seção
        inicio = conteudo.find("# === CONFIGURAÇÃO DO BANCO DE DADOS ===")
        fim = conteudo.find("app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False")
        
        if inicio != -1 and fim != -1:
            # Substituir a seção
            antes = conteudo[:inicio]
            depois = conteudo[fim:]
            novo_conteudo = antes + nova_config + "\n\n" + depois
        else:
            print("⚠️ Não foi possível localizar seção completa, adicionando no final...")
            novo_conteudo = conteudo + "\n\n" + nova_config
    else:
        print("⚠️ Configuração não encontrada, adicionando no final...")
        novo_conteudo = conteudo + "\n\n" + nova_config
    
    # Salvar arquivo modificado
    try:
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)
        print("✅ Arquivo app.py configurado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar: {str(e)}")
        return False

def criar_script_migracao():
    """
    Cria script para executar migração do banco
    """
    script_migracao = """#!/usr/bin/env python3
# Script para migrar/criar tabelas no MySQL Hostinger

import os
from app import app, db

# Forçar modo produção
os.environ['FLASK_ENV'] = 'production'

with app.app_context():
    print("🗄️ Criando tabelas no MySQL...")
    try:
        db.create_all()
        print("✅ Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
"""
    
    with open('migrar_mysql.py', 'w', encoding='utf-8') as f:
        f.write(script_migracao)
    
    print("📝 Script migrar_mysql.py criado!")

def instalar_dependencias():
    """
    Instala PyMySQL se necessário
    """
    try:
        import pymysql
        print("✅ PyMySQL já instalado")
    except ImportError:
        print("📦 Instalando PyMySQL...")
        os.system("pip install PyMySQL")
        print("✅ PyMySQL instalado!")

if __name__ == '__main__':
    print("🚀 CONFIGURAÇÃO AUTOMÁTICA HOSTINGER")
    print("Suas credenciais:")
    print("  • u419790683_l7nutri_user")
    print("  • Banco: u419790683_l7nutri_db")
    print()
    
    resposta = input("Deseja configurar automaticamente? (s/n): ")
    
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        print("\n🔧 Iniciando configuração...")
        
        # 1. Instalar dependências
        instalar_dependencias()
        
        # 2. Configurar app.py
        if configurar_banco_hostinger():
            print("✅ Configuração concluída!")
            
            # 3. Criar script de migração
            criar_script_migracao()
            
            print("\n📋 Próximos passos:")
            print("1. Execute: python migrar_mysql.py")
            print("2. Execute: python init_producao.py")
            print("3. Teste a aplicação!")
        else:
            print("❌ Falha na configuração")
    else:
        print("❌ Configuração cancelada")
