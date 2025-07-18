#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar tabelas no MySQL Hostinger
Execute este script para configurar o banco de dados
"""

import os
import sys

def criar_tabelas_mysql():
    """
    Cria todas as tabelas no banco MySQL da Hostinger
    """
    print("🗄️ CRIANDO TABELAS NO MYSQL HOSTINGER")
    print("=" * 50)
    
    # Forçar modo produção
    os.environ['FLASK_ENV'] = 'production'
    
    try:
        from app import app, db, Alimento, Usuario, Suplementos
        
        with app.app_context():
            print("📦 Criando tabelas...")
            
            # Criar todas as tabelas
            db.create_all()
            
            print("✅ Tabelas criadas com sucesso!")
            
            # Verificar se foram criadas
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tabelas = inspector.get_table_names()
            
            print(f"📋 Tabelas encontradas ({len(tabelas)}):")
            for tabela in tabelas:
                print(f"   • {tabela}")
            
            # Verificar se há dados
            total_alimentos = Alimento.query.count()
            total_usuarios = Usuario.query.count()
            
            print(f"\n📊 Status do banco:")
            print(f"   • Alimentos: {total_alimentos}")
            print(f"   • Usuários: {total_usuarios}")
            
            if total_alimentos == 0:
                print("\n💡 Dica: Execute 'python init_producao.py' para adicionar dados iniciais")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {str(e)}")
        print("\n🔧 Possíveis soluções:")
        print("1. Verifique se PyMySQL está instalado: pip install PyMySQL")
        print("2. Confirme as credenciais do banco no app.py")
        print("3. Verifique se o banco existe na Hostinger")
        return False

def testar_conexao():
    """
    Testa a conexão com o banco MySQL
    """
    print("🔌 TESTANDO CONEXÃO COM MYSQL")
    print("=" * 30)
    
    os.environ['FLASK_ENV'] = 'production'
    
    try:
        from app import app, db
        
        with app.app_context():
            # Testar conexão
            db.engine.execute('SELECT 1')
            print("✅ Conexão com MySQL funcionando!")
            
            # Mostrar informações do banco
            result = db.engine.execute('SELECT DATABASE(), USER(), VERSION()')
            for row in result:
                print(f"📋 Banco: {row[0]}")
                print(f"👤 Usuário: {row[1]}")
                print(f"🔢 Versão MySQL: {row[2]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
        return False

if __name__ == '__main__':
    print("CONFIGURACAO BANCO MYSQL HOSTINGER")
    print("Credenciais atualizadas:")
    print("  • Usuario: u419790683_l7nutri_alex")
    print("  • Host: 127.0.0.1")
    print("  • Banco: u419790683_l7nutri_novo")
    print()
    
    # Testar conexao primeiro
    if testar_conexao():
        print("\n" + "="*50)
        print("Conexao OK! Criando tabelas automaticamente...")
        
        if criar_tabelas_mysql():
            print("\nBANCO CONFIGURADO COM SUCESSO!")
            print("Proximos passos:")
            print("1. python init_producao.py (para dados iniciais)")
            print("2. python app.py (para testar aplicacao)")
        else:
            print("\nFalha na criacao das tabelas")
    else:
        print("\nFalha na conexao. Verifique as configuracoes.")
