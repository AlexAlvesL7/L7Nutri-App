# =================================
# L7NUTRI - VERSÃO CORRIGIDA E FINAL
# MESTRE SAAS - DIRETRIZ ESTRATÉGICA
# =================================

import os
from datetime import datetime, date, timedelta
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
# Removido temporariamente para garantir o deploy inicial
# import google.generativeai as genai

# --- 1. INICIALIZAÇÃO DA APLICAÇÃO ---
app = Flask(__name__)

# --- 2. CONFIGURAÇÃO ESSENCIAL ---
# NOTA: Configure estas variáveis no ambiente do Render!
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

# --- 3. INICIALIZAÇÃO DAS EXTENSÕES ---
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# --- 4. MODELOS DO BANCO DE DADOS (MODELS) ---
# O modelo 'Usuario' estava faltando no arquivo sabotado. Ele foi reconstruído.
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)

class Alimento(db.Model):
    __tablename__ = 'alimentos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    calorias = db.Column(db.Numeric(10, 2), nullable=False)
    proteinas = db.Column(db.Numeric(10, 2), nullable=False)
    carboidratos = db.Column(db.Numeric(10, 2), nullable=False)
    gorduras = db.Column(db.Numeric(10, 2), nullable=False)

class Diario(db.Model):
    __tablename__ = 'diarios'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_entrada = db.Column(db.Date, nullable=False)
    alimento_id = db.Column(db.Integer, db.ForeignKey('alimentos.id'), nullable=False)
    quantidade = db.Column(db.Numeric(10, 2), nullable=False)
    usuario = db.relationship('Usuario', backref='diarios')
    alimento = db.relationship('Alimento', backref='diarios')

# --- 5. ROTAS DA APLICAÇÃO (VIEWS/CONTROLLERS) ---
# Esta é a rota principal correta
@app.route('/')
def index():
    return "<h1>L7Nutri - Servidor Principal Online</h1><p>A aplicação está funcionando. Use as rotas de API ou acesse /login.</p>"

# ... (O restante das suas rotas de /login, /cadastro, /diario, /api/*, etc., viriam aqui)
# Cole o restante das suas rotas (do arquivo antigo) a partir deste ponto.
# Certifique-se de que não haja rotas duplicadas.

# --- Bloco para inicializar o banco de dados (executado uma vez no deploy) ---
with app.app_context():
    db.create_all()
    # Adicionar alimentos se não existirem
    if Alimento.query.count() == 0:
        # (Seu código para adicionar alimentos base)
        pass # Adicione seu loop de alimentos aqui para popular a base

# Este bloco só é usado para testes locais, o Gunicorn não o utiliza.
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)