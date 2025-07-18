#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para migrar dados do SQLite local para MySQL de produção
Execute este script para transferir dados locais para a Hostinger
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def migrar_dados():
    """
    Migra dados do banco local SQLite para MySQL de produção
    """
    print("🔄 INICIANDO MIGRAÇÃO DE DADOS")
    print("=" * 50)
    
    # Configuração do banco local (SQLite)
    os.environ['FLASK_ENV'] = 'development'
    from app import app as app_local, db as db_local, Alimento, Usuario, Suplementos
    
    dados_coletados = {}
    
    # Coleta dados do banco local
    with app_local.app_context():
        print("📥 Coletando dados do banco local...")
        
        # Coleta alimentos
        alimentos = Alimento.query.all()
        dados_coletados['alimentos'] = [
            {
                'nome': a.nome,
                'calorias': a.calorias,
                'proteinas': a.proteinas,
                'carboidratos': a.carboidratos,
                'gorduras': a.gorduras
            } for a in alimentos
        ]
        
        # Coleta usuários
        usuarios = Usuario.query.all()
        dados_coletados['usuarios'] = [
            {
                'nome': u.nome,
                'email': u.email,
                'username': u.username,
                'password': u.password,
                'idade': u.idade,
                'sexo': u.sexo,
                'peso': u.peso,
                'altura': u.altura,
                'nivel_atividade': u.nivel_atividade,
                'objetivo': u.objetivo
            } for u in usuarios
        ]
        
        # Coleta suplementos
        suplementos = Suplementos.query.all()
        dados_coletados['suplementos'] = [
            {
                'nome': s.nome,
                'objetivo': s.objetivo,
                'link_loja': s.link_loja,
                'imagem_url': s.imagem_url
            } for s in suplementos
        ]
        
        print(f"✅ Dados coletados:")
        print(f"   • {len(dados_coletados['alimentos'])} alimentos")
        print(f"   • {len(dados_coletados['usuarios'])} usuários")
        print(f"   • {len(dados_coletados['suplementos'])} suplementos")
    
    # Configura para produção
    os.environ['FLASK_ENV'] = 'production'
    
    # Reinicia app para configuração de produção
    from importlib import reload
    import app as app_module
    reload(app_module)
    
    from app_module import app as app_prod, db as db_prod
    
    # Insere dados no banco de produção
    with app_prod.app_context():
        print("📤 Inserindo dados no banco de produção...")
        
        try:
            # Criar tabelas se não existirem
            db_prod.create_all()
            
            # Inserir alimentos
            for alimento_data in dados_coletados['alimentos']:
                if not app_module.Alimento.query.filter_by(nome=alimento_data['nome']).first():
                    alimento = app_module.Alimento(**alimento_data)
                    db_prod.session.add(alimento)
            
            # Inserir usuários
            for usuario_data in dados_coletados['usuarios']:
                if not app_module.Usuario.query.filter_by(username=usuario_data['username']).first():
                    usuario = app_module.Usuario(**usuario_data)
                    db_prod.session.add(usuario)
            
            # Inserir suplementos
            for suplemento_data in dados_coletados['suplementos']:
                if not app_module.Suplementos.query.filter_by(nome=suplemento_data['nome']).first():
                    suplemento = app_module.Suplementos(**suplemento_data)
                    db_prod.session.add(suplemento)
            
            db_prod.session.commit()
            
            print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("✅ Todos os dados foram transferidos para produção!")
            
        except Exception as e:
            db_prod.session.rollback()
            print(f"❌ Erro durante migração: {str(e)}")
            return False
    
    return True

if __name__ == '__main__':
    # Verificar se DATABASE_URL está configurada
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL não configurada!")
        print("Configure a variável DATABASE_URL no arquivo .env")
        sys.exit(1)
    
    # Confirmar migração
    resposta = input("🚨 Confirma migração de dados para PRODUÇÃO? (sim/não): ")
    if resposta.lower() in ['sim', 's', 'yes', 'y']:
        migrar_dados()
    else:
        print("❌ Migração cancelada.")
