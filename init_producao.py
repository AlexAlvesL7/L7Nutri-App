#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicialização do banco de dados para produção (Hostinger)
Execute este script APENAS na primeira vez após o deploy
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Alimento, Usuario, Suplementos
from flask_bcrypt import Bcrypt

def criar_banco_producao():
    """
    Cria todas as tabelas no banco de dados de produção
    """
    print("🚀 INICIALIZANDO BANCO DE DADOS DE PRODUÇÃO")
    print("=" * 50)
    
    with app.app_context():
        try:
            # 1. Criar todas as tabelas
            print("📦 Criando tabelas...")
            db.create_all()
            print("✅ Tabelas criadas com sucesso!")
            
            # 2. Verificar se já existem dados
            total_alimentos = Alimento.query.count()
            total_usuarios = Usuario.query.count()
            
            print(f"📊 Status atual:")
            print(f"   • Alimentos: {total_alimentos}")
            print(f"   • Usuários: {total_usuarios}")
            
            # 3. Inserir dados básicos se necessário
            if total_alimentos == 0:
                print("🥗 Adicionando alimentos básicos...")
                adicionar_alimentos_basicos()
                
            if total_usuarios == 0:
                print("👤 Criando usuário administrador...")
                criar_usuario_admin()
                
            # 4. Adicionar suplementos se necessário
            total_suplementos = Suplementos.query.count()
            if total_suplementos == 0:
                print("💊 Adicionando suplementos...")
                adicionar_suplementos_basicos()
                
            print("\n🎉 BANCO DE DADOS INICIALIZADO COM SUCESSO!")
            print("✅ Sua aplicação está pronta para produção!")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar banco: {str(e)}")
            return False
            
    return True

def adicionar_alimentos_basicos():
    """Adiciona alimentos essenciais ao banco"""
    alimentos_basicos = [
        # Proteínas
        ("Peito de Frango, grelhado", 165, 31.0, 0.0, 3.6),
        ("Ovo, cozido", 155, 13.0, 1.1, 11.0),
        ("Salmão, grelhado", 208, 22.0, 0.0, 12.0),
        
        # Carboidratos
        ("Arroz Branco, cozido", 130, 2.7, 28.0, 0.3),
        ("Batata Doce, cozida", 86, 1.6, 20.0, 0.1),
        ("Aveia", 389, 16.9, 66.3, 6.9),
        
        # Verduras e Legumes
        ("Brócolis, cozido", 34, 2.8, 7.0, 0.4),
        ("Espinafre, cru", 23, 2.9, 3.6, 0.4),
        ("Tomate", 18, 0.9, 3.9, 0.2),
        
        # Frutas
        ("Banana", 89, 1.1, 23.0, 0.3),
        ("Maçã", 52, 0.3, 14.0, 0.2),
        ("Laranja", 47, 0.9, 12.0, 0.1),
    ]
    
    for nome, cal, prot, carb, gord in alimentos_basicos:
        if not Alimento.query.filter_by(nome=nome).first():
            alimento = Alimento(
                nome=nome,
                calorias=cal,
                proteinas=prot,
                carboidratos=carb,
                gorduras=gord
            )
            db.session.add(alimento)
    
    db.session.commit()
    print(f"✅ {len(alimentos_basicos)} alimentos adicionados!")

def criar_usuario_admin():
    """Cria usuário administrador"""
    bcrypt = Bcrypt(app)
    senha_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
    
    admin = Usuario(
        nome='Administrador',
        email='admin@l7nutri.com',
        username='admin',
        password=senha_hash
    )
    
    db.session.add(admin)
    db.session.commit()
    print("✅ Usuário admin criado (username: admin, senha: admin123)")

def adicionar_suplementos_basicos():
    """Adiciona suplementos básicos"""
    suplementos = [
        ("Whey Protein", "ganho_massa", "https://exemplo.com/whey", ""),
        ("Termogênico", "emagrecimento", "https://exemplo.com/termo", ""),
        ("Multivitamínico", "manter", "https://exemplo.com/multi", ""),
    ]
    
    for nome, objetivo, link, img in suplementos:
        suplemento = Suplementos(
            nome=nome,
            objetivo=objetivo,
            link_loja=link,
            imagem_url=img
        )
        db.session.add(suplemento)
    
    db.session.commit()
    print(f"✅ {len(suplementos)} suplementos adicionados!")

if __name__ == '__main__':
    # Verificar se estamos em produção
    if os.getenv('FLASK_ENV') != 'production':
        print("⚠️  AVISO: Este script deve ser executado apenas em produção!")
        print("⚠️  Configure FLASK_ENV=production no arquivo .env")
        sys.exit(1)
    
    # Confirmar execução
    resposta = input("🚨 ATENÇÃO: Deseja realmente inicializar o banco de PRODUÇÃO? (sim/não): ")
    if resposta.lower() in ['sim', 's', 'yes', 'y']:
        criar_banco_producao()
    else:
        print("❌ Operação cancelada.")
