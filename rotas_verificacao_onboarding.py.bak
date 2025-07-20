#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ROTAS FLASK PARA VERIFICAÇÃO DE EMAIL E ONBOARDING
Integra sistema de segurança e questionário obrigatório
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import os

# Importar sistema de verificação
from sistema_verificacao_onboarding import (
    validar_email_real, 
    enviar_email_verificacao, 
    gerar_token_verificacao,
    QUESTIONARIO_L7CHEF,
    analisar_questionario_l7chef
)

app = Flask(__name__)
db = SQLAlchemy(app)

# Modelo de usuário atualizado
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    
    # Campos de verificação
    email_verificado = db.Column(db.Boolean, default=False)
    token_verificacao = db.Column(db.String(100), nullable=True)
    token_expira = db.Column(db.DateTime, nullable=True)
    
    # Campos de onboarding
    onboarding_completo = db.Column(db.Boolean, default=False)
    respostas_questionario = db.Column(db.Text, nullable=True)  # JSON das respostas
    plano_nutricional = db.Column(db.Text, nullable=True)  # JSON do plano
    
    # Dados pessoais (do questionário)
    idade = db.Column(db.Integer, nullable=True)
    sexo = db.Column(db.String(10), nullable=True)
    peso = db.Column(db.Float, nullable=True)
    altura = db.Column(db.Float, nullable=True)
    
    # Status da conta
    status = db.Column(db.String(20), default='pendente_verificacao')  # ativo, bloqueado, pendente
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime, nullable=True)

@app.route('/api/usuario/registro-seguro', methods=['POST'])
def registro_seguro():
    """Registro com verificação de email obrigatória"""
    
    try:
        dados = request.get_json()
        
        # Validações básicas
        campos_obrigatorios = ['nome', 'email', 'senha']
        for campo in campos_obrigatorios:
            if not dados.get(campo):
                return jsonify({
                    'sucesso': False,
                    'erro': f'Campo {campo} é obrigatório'
                }), 400
        
        # Validar email real
        email_valido, mensagem = validar_email_real(dados['email'])
        if not email_valido:
            return jsonify({
                'sucesso': False,
                'erro': mensagem
            }), 400
        
        # Verificar se email já existe
        usuario_existente = Usuario.query.filter_by(email=dados['email']).first()
        if usuario_existente:
            if usuario_existente.email_verificado:
                return jsonify({
                    'sucesso': False,
                    'erro': 'Email já cadastrado e verificado'
                }), 400
            else:
                # Reenviar email de verificação para conta não verificada
                novo_token = gerar_token_verificacao()
                usuario_existente.token_verificacao = novo_token
                usuario_existente.token_expira = datetime.utcnow() + timedelta(hours=24)
                db.session.commit()
                
                enviar_email_verificacao(dados['email'], dados['nome'], novo_token)
                return jsonify({
                    'sucesso': True,
                    'mensagem': 'Email de verificação reenviado. Verifique sua caixa de entrada.'
                })
        
        # Criar novo usuário
        token_verificacao = gerar_token_verificacao()
        
        novo_usuario = Usuario(
            nome=dados['nome'],
            email=dados['email'],
            senha_hash=generate_password_hash(dados['senha']),
            token_verificacao=token_verificacao,
            token_expira=datetime.utcnow() + timedelta(hours=24),
            status='pendente_verificacao'
        )
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        # Enviar email de verificação
        sucesso_email = enviar_email_verificacao(
            dados['email'], 
            dados['nome'], 
            token_verificacao
        )
        
        if sucesso_email:
            return jsonify({
                'sucesso': True,
                'mensagem': 'Conta criada! Verifique seu email para ativar.',
                'proxima_etapa': 'verificar_email'
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': 'Erro ao enviar email de verificação'
            }), 500
            
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro interno: {str(e)}'
        }), 500

@app.route('/verificar-email')
def verificar_email():
    """Verifica email através do token"""
    
    token = request.args.get('token')
    if not token:
        flash('Token de verificação inválido', 'error')
        return redirect(url_for('login'))
    
    # Buscar usuário pelo token
    usuario = Usuario.query.filter_by(token_verificacao=token).first()
    
    if not usuario:
        flash('Token de verificação inválido', 'error')
        return redirect(url_for('login'))
    
    # Verificar se token não expirou
    if usuario.token_expira < datetime.utcnow():
        flash('Token de verificação expirado. Solicite um novo.', 'error')
        return redirect(url_for('login'))
    
    # Ativar conta
    usuario.email_verificado = True
    usuario.status = 'ativo'
    usuario.token_verificacao = None
    usuario.token_expira = None
    db.session.commit()
    
    # Redirecionar para onboarding obrigatório
    session['usuario_id'] = usuario.id
    session['email_verificado'] = True
    
    flash('Email verificado com sucesso! Complete seu perfil.', 'success')
    return redirect(url_for('onboarding_obrigatorio'))

@app.route('/onboarding')
def onboarding_obrigatorio():
    """Onboarding obrigatório - questionário L7Chef"""
    
    # Verificar se usuário está logado e verificado
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get(session['usuario_id'])
    if not usuario or not usuario.email_verificado:
        return redirect(url_for('login'))
    
    # Se já completou onboarding, redirecionar
    if usuario.onboarding_completo:
        return redirect(url_for('dashboard'))
    
    return render_template('onboarding_l7chef.html', 
                         questionario=QUESTIONARIO_L7CHEF,
                         usuario=usuario)

@app.route('/api/onboarding/salvar', methods=['POST'])
def salvar_onboarding():
    """Salva respostas do questionário e gera plano nutricional"""
    
    try:
        if 'usuario_id' not in session:
            return jsonify({'erro': 'Usuário não autenticado'}), 401
        
        usuario = Usuario.query.get(session['usuario_id'])
        if not usuario or not usuario.email_verificado:
            return jsonify({'erro': 'Email não verificado'}), 401
        
        respostas = request.get_json()
        
        # Analisar respostas e gerar plano
        plano_personalizado = analisar_questionario_l7chef(respostas)
        
        # Salvar no banco
        import json
        usuario.respostas_questionario = json.dumps(respostas)
        usuario.plano_nutricional = json.dumps(plano_personalizado)
        usuario.onboarding_completo = True
        
        # Salvar dados pessoais
        usuario.idade = int(respostas.get('idade', 0))
        usuario.sexo = respostas.get('sexo', '')
        usuario.peso = float(respostas.get('peso_atual', 0))
        usuario.altura = float(respostas.get('altura', 0))
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Perfil completo! Bem-vindo ao L7Nutri!',
            'plano': plano_personalizado,
            'proxima_etapa': 'dashboard'
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao salvar: {str(e)}'}), 500

@app.route('/api/usuario/login-verificado', methods=['POST'])
def login_verificado():
    """Login que verifica se conta está ativada e onboarding completo"""
    
    try:
        dados = request.get_json()
        email = dados.get('email')
        senha = dados.get('senha')
        
        if not email or not senha:
            return jsonify({
                'sucesso': False,
                'erro': 'Email e senha são obrigatórios'
            }), 400
        
        # Buscar usuário
        usuario = Usuario.query.filter_by(email=email).first()
        
        if not usuario or not check_password_hash(usuario.senha_hash, senha):
            return jsonify({
                'sucesso': False,
                'erro': 'Email ou senha inválidos'
            }), 401
        
        # Verificar se email foi confirmado
        if not usuario.email_verificado:
            return jsonify({
                'sucesso': False,
                'erro': 'Email não verificado. Verifique sua caixa de entrada.',
                'requer_verificacao': True
            }), 401
        
        # Verificar se onboarding foi completo
        if not usuario.onboarding_completo:
            session['usuario_id'] = usuario.id
            return jsonify({
                'sucesso': True,
                'mensagem': 'Login realizado. Complete seu perfil.',
                'requer_onboarding': True,
                'redirect_url': '/onboarding'
            })
        
        # Login completo
        session['usuario_id'] = usuario.id
        usuario.ultimo_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Login realizado com sucesso!',
            'usuario': {
                'id': usuario.id,
                'nome': usuario.nome,
                'email': usuario.email
            },
            'redirect_url': '/dashboard'
        })
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro no login: {str(e)}'
        }), 500

# Middleware para proteger rotas
def requer_onboarding_completo(f):
    """Decorator que bloqueia acesso se onboarding não foi completo"""
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        
        usuario = Usuario.query.get(session['usuario_id'])
        if not usuario or not usuario.email_verificado:
            return redirect(url_for('login'))
        
        if not usuario.onboarding_completo:
            flash('Complete seu perfil antes de continuar', 'warning')
            return redirect(url_for('onboarding_obrigatorio'))
        
        return f(*args, **kwargs)
    return wrapper

@app.route('/diario')
@requer_onboarding_completo
def diario_alimentar():
    """Diário alimentar - só acessível após onboarding"""
    usuario = Usuario.query.get(session['usuario_id'])
    return render_template('diario.html', usuario=usuario)

@app.route('/dashboard')
@requer_onboarding_completo
def dashboard():
    """Dashboard - só acessível após onboarding"""
    usuario = Usuario.query.get(session['usuario_id'])
    
    # Carregar plano nutricional
    import json
    plano = json.loads(usuario.plano_nutricional) if usuario.plano_nutricional else None
    
    return render_template('dashboard.html', 
                         usuario=usuario, 
                         plano=plano)

@app.route('/api/reenviar-verificacao', methods=['POST'])
def reenviar_verificacao():
    """Reenvia email de verificação"""
    
    try:
        dados = request.get_json()
        email = dados.get('email')
        
        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario:
            return jsonify({'erro': 'Email não encontrado'}), 404
        
        if usuario.email_verificado:
            return jsonify({'erro': 'Email já verificado'}), 400
        
        # Gerar novo token
        novo_token = gerar_token_verificacao()
        usuario.token_verificacao = novo_token
        usuario.token_expira = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()
        
        # Enviar email
        sucesso = enviar_email_verificacao(email, usuario.nome, novo_token)
        
        if sucesso:
            return jsonify({
                'sucesso': True,
                'mensagem': 'Email de verificação reenviado!'
            })
        else:
            return jsonify({'erro': 'Erro ao enviar email'}), 500
            
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == "__main__":
    print("🔐 Sistema de Verificação e Onboarding configurado!")
    print("📧 Verificação de email obrigatória")
    print("📋 Questionário L7Chef obrigatório")
    print("🛡️ Proteção contra acesso não autorizado")
