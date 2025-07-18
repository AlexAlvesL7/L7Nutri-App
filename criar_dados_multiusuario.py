#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 SCRIPT: Criar Dados de Teste Multi-Usuário
📅 Data: 17/07/2025
🎯 Objetivo: Demonstrar sistema de isolamento de usuários

Este script cria dados de teste para diferentes usuários
para demonstrar como cada um vê apenas seus próprios insights.
"""

import sys
import os
from datetime import datetime, timedelta, date
import random

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa os modelos da aplicação
from app import app, db, Usuario, Alimento, RegistroAlimentar
from werkzeug.security import generate_password_hash

def criar_usuarios_demo():
    """Cria usuários de demonstração"""
    print("👥 Criando usuários de demonstração...")
    
    usuarios = [
        {
            'nome': 'Maria Silva',
            'email': 'maria@demo.com',
            'username': 'maria_demo',
            'password': 'demo123',
            'idade': 28,
            'sexo': 'feminino',
            'peso': 65.0,
            'altura': 165.0,
            'objetivo': 'emagrecimento'
        },
        {
            'nome': 'João Santos',
            'email': 'joao@demo.com',
            'username': 'joao_demo',
            'password': 'demo123',
            'idade': 32,
            'sexo': 'masculino',
            'peso': 80.0,
            'altura': 175.0,
            'objetivo': 'ganho_massa'
        }
    ]
    
    for user_data in usuarios:
        # Verifica se usuário já existe
        usuario_existente = Usuario.query.filter_by(username=user_data['username']).first()
        if not usuario_existente:
            novo_usuario = Usuario(
                nome=user_data['nome'],
                email=user_data['email'],
                username=user_data['username'],
                password=generate_password_hash(user_data['password']),
                idade=user_data['idade'],
                sexo=user_data['sexo'],
                peso=user_data['peso'],
                altura=user_data['altura'],
                objetivo=user_data['objetivo']
            )
            db.session.add(novo_usuario)
            print(f"✅ Usuário criado: {user_data['nome']}")
        else:
            print(f"⚠️ Usuário já existe: {user_data['nome']}")
    
    db.session.commit()

def criar_alimentos_demo():
    """Cria alimentos de demonstração"""
    print("🍎 Criando alimentos de demonstração...")
    
    alimentos = [
        {'nome': 'Arroz Integral', 'calorias': 112, 'proteinas': 2.3, 'carboidratos': 22.9, 'gorduras': 0.9},
        {'nome': 'Frango Grelhado', 'calorias': 165, 'proteinas': 31.0, 'carboidratos': 0.0, 'gorduras': 3.6},
        {'nome': 'Brócolis', 'calorias': 34, 'proteinas': 2.8, 'carboidratos': 7.0, 'gorduras': 0.4},
        {'nome': 'Banana', 'calorias': 89, 'proteinas': 1.1, 'carboidratos': 22.8, 'gorduras': 0.3},
        {'nome': 'Aveia', 'calorias': 389, 'proteinas': 16.9, 'carboidratos': 66.3, 'gorduras': 6.9},
        {'nome': 'Ovo', 'calorias': 155, 'proteinas': 13.0, 'carboidratos': 1.1, 'gorduras': 11.0},
        {'nome': 'Batata Doce', 'calorias': 86, 'proteinas': 1.6, 'carboidratos': 20.1, 'gorduras': 0.1},
        {'nome': 'Salmão', 'calorias': 208, 'proteinas': 25.4, 'carboidratos': 0.0, 'gorduras': 12.4}
    ]
    
    for alimento_data in alimentos:
        alimento_existente = Alimento.query.filter_by(nome=alimento_data['nome']).first()
        if not alimento_existente:
            novo_alimento = Alimento(**alimento_data)
            db.session.add(novo_alimento)
            print(f"✅ Alimento criado: {alimento_data['nome']}")
        else:
            print(f"⚠️ Alimento já existe: {alimento_data['nome']}")
    
    db.session.commit()

def criar_registros_alimentares():
    """Cria registros alimentares para cada usuário"""
    print("📊 Criando registros alimentares personalizados...")
    
    # Busca usuários e alimentos
    maria = Usuario.query.filter_by(username='maria_demo').first()
    joao = Usuario.query.filter_by(username='joao_demo').first()
    alimentos = Alimento.query.all()
    
    if not maria or not joao or not alimentos:
        print("❌ Usuários ou alimentos não encontrados")
        return
    
    # Cria registros para Maria (foco em emagrecimento)
    print(f"📝 Criando registros para {maria.nome}...")
    tipos_refeicao = ['cafe_manha', 'almoco', 'jantar', 'lanche']
    
    for i in range(15):  # 15 dias de registros
        data_registro = date.today() - timedelta(days=i)
        
        # Maria come menos calorias (padrão emagrecimento)
        for tipo in tipos_refeicao:
            if random.random() > 0.2:  # 80% chance de ter a refeição
                alimento = random.choice(alimentos)
                quantidade = random.randint(50, 150)  # Porções menores
                
                registro = RegistroAlimentar(
                    usuario_id=maria.id,
                    data=data_registro,
                    tipo_refeicao=tipo,
                    alimento_id=alimento.id,
                    quantidade_gramas=quantidade
                )
                db.session.add(registro)
    
    # Cria registros para João (foco em ganho de massa)
    print(f"📝 Criando registros para {joao.nome}...")
    
    for i in range(12):  # 12 dias de registros
        data_registro = date.today() - timedelta(days=i)
        
        # João come mais calorias (padrão ganho de massa)
        for tipo in tipos_refeicao:
            if random.random() > 0.1:  # 90% chance de ter a refeição
                alimento = random.choice(alimentos)
                quantidade = random.randint(100, 250)  # Porções maiores
                
                registro = RegistroAlimentar(
                    usuario_id=joao.id,
                    data=data_registro,
                    tipo_refeicao=tipo,
                    alimento_id=alimento.id,
                    quantidade_gramas=quantidade
                )
                db.session.add(registro)
    
    db.session.commit()
    print("✅ Registros alimentares criados com sucesso!")

def verificar_dados():
    """Verifica os dados criados"""
    print("\n📊 VERIFICAÇÃO DOS DADOS CRIADOS:")
    
    usuarios = Usuario.query.all()
    print(f"👥 Total de usuários: {len(usuarios)}")
    
    for usuario in usuarios:
        registros = RegistroAlimentar.query.filter_by(usuario_id=usuario.id).count()
        print(f"   • {usuario.nome}: {registros} registros")
    
    alimentos = Alimento.query.count()
    print(f"🍎 Total de alimentos: {alimentos}")
    
    total_registros = RegistroAlimentar.query.count()
    print(f"📝 Total de registros: {total_registros}")

def main():
    """Função principal"""
    print("🚀 INICIANDO CRIAÇÃO DE DADOS DEMO MULTI-USUÁRIO")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Cria as tabelas se não existirem
            db.create_all()
            
            # Cria dados de demonstração
            criar_usuarios_demo()
            criar_alimentos_demo()
            criar_registros_alimentares()
            
            # Verifica os dados criados
            verificar_dados()
            
            print("\n" + "=" * 60)
            print("✅ DADOS DEMO CRIADOS COM SUCESSO!")
            print("\n📌 ACESSO AOS DASHBOARDS:")
            print("   • Maria Silva: http://localhost:5000/dashboard-insights?id=1")
            print("   • João Santos: http://localhost:5000/dashboard-insights?id=2")
            print("   • Demo Geral: http://localhost:5000/demo-usuarios")
            
        except Exception as e:
            print(f"❌ Erro ao criar dados: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
