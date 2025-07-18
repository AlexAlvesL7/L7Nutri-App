#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração para deploy no Render com PostgreSQL
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import google.generativeai as genai

# Configuração do Google Gemini AI
gemini_api_key = os.getenv('GEMINI_API_KEY')
if gemini_api_key and gemini_api_key != 'SUA_CHAVE_AQUI':
    genai.configure(api_key=gemini_api_key)
    modelo_ia = genai.GenerativeModel('gemini-1.5-flash')
    print("Google Gemini AI configurado com sucesso!")
else:
    modelo_ia = None
    print("GEMINI_API_KEY não configurada. Recursos de IA estarão desabilitados.")

# Configuração do Flask
app = Flask(__name__)

# Configuração do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    # Render PostgreSQL (produção)
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    print("MODO PRODUCAO: Usando PostgreSQL Render")
else:
    # Desenvolvimento local (SQLite)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nutricao.db'
    print("MODO DESENVOLVIMENTO: Usando SQLite local")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'l7nutri-secret-key-2025')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-l7nutri')

# Inicializar extensões
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Modelos do banco de dados
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<Usuario {self.nome_usuario}>'

class Alimento(db.Model):
    __tablename__ = 'alimentos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    calorias = db.Column(db.Numeric(10, 2), nullable=False)
    proteinas = db.Column(db.Numeric(10, 2), nullable=False)
    carboidratos = db.Column(db.Numeric(10, 2), nullable=False)
    gorduras = db.Column(db.Numeric(10, 2), nullable=False)
    
    def __repr__(self):
        return f'<Alimento {self.nome}>'

class Diario(db.Model):
    __tablename__ = 'diarios'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_entrada = db.Column(db.Date, nullable=False)
    alimento_id = db.Column(db.Integer, db.ForeignKey('alimentos.id'), nullable=False)
    quantidade = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref='diarios')
    alimento = db.relationship('Alimento', backref='diarios')
    
    def __repr__(self):
        return f'<Diario {self.usuario_id} - {self.alimento_id}>'

# Resto da aplicação (rotas, etc.) permanece igual...
# [Incluir todas as rotas do app.py original]

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Criar usuário admin se não existir
        if not Usuario.query.filter_by(nome_usuario='admin').first():
            senha_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = Usuario(
                nome_usuario='admin',
                email='admin@l7nutri.com',
                senha_hash=senha_hash
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuário admin criado!")
        
        # Adicionar alimentos se não existirem
        if Alimento.query.count() == 0:
            # Lista dos 26 alimentos da Base de Ouro
            alimentos_base = [
                ("Arroz Branco, cozido", 130, 2.7, 28.2, 0.3),
                ("Feijao Preto, cozido", 132, 8.9, 23.0, 0.5),
                ("Frango, peito sem pele", 165, 31.0, 0.0, 3.6),
                ("Ovo de galinha, cozido", 155, 13.0, 1.1, 11.0),
                ("Banana, madura", 89, 1.1, 22.8, 0.3),
                ("Batata doce, cozida", 86, 1.6, 20.1, 0.1),
                ("Brocolis, cozido", 34, 2.8, 7.0, 0.4),
                ("Cenoura, crua", 41, 0.9, 9.6, 0.2),
                ("Tomate, maduro", 18, 0.9, 3.9, 0.2),
                ("Alface, crespa", 15, 1.4, 3.0, 0.1),
                ("Aveia em Flocos", 389, 16.9, 66.3, 6.9),
                ("Tapioca (Goma hidratada)", 240, 0.0, 60.0, 0.0),
                ("Pao de Queijo", 335, 5.5, 37.5, 18.0),
                ("Milho Verde, cozido", 86, 3.2, 19.0, 1.2),
                ("Carne de Porco (Bisteca), grelhada", 283, 25.8, 0.0, 19.3),
                ("Sardinha em Lata (em oleo)", 208, 24.6, 0.0, 11.5),
                ("Linguica Toscana, grelhada", 322, 16.0, 0.7, 28.0),
                ("Tofu", 76, 8.1, 1.9, 4.8),
                ("Uva Thompson", 69, 0.7, 18.1, 0.2),
                ("Manga Palmer", 60, 0.8, 15.0, 0.4),
                ("Couve Manteiga, refogada", 90, 2.7, 7.6, 6.1),
                ("Quiabo, cozido", 33, 1.9, 7.0, 0.2),
                ("Palmito Pupunha, em conserva", 28, 2.5, 4.2, 0.3),
                ("Batata Inglesa, cozida", 87, 1.9, 19.6, 0.1),
                ("Carne Bovina, alcatra", 163, 29.2, 0.0, 4.8),
                ("Leite integral", 61, 3.2, 4.6, 3.2),
            ]
            
            for nome, cal, prot, carb, gord in alimentos_base:
                alimento = Alimento(
                    nome=nome,
                    calorias=cal,
                    proteinas=prot,
                    carboidratos=carb,
                    gorduras=gord
                )
                db.session.add(alimento)
            
            db.session.commit()
            print(f"Base de Ouro adicionada: {len(alimentos_base)} alimentos!")
    
    # Configuração do servidor
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
