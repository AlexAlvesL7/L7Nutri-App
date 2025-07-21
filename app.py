from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import func
import os
import json
import unicodedata
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai
import secrets
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
import subprocess
import schedule
import threading
import time

# Importar sistema ecossistema L7
from sistema_ecossistema_l7 import ecossistema_l7

# Importar sistema de análise nutricional IA
from analise_nutricional_ia import inicializar_analise_ia, analise_ia, criar_analise_personalizada

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

# --- Configuração do Google Gemini AI ---
gemini_api_key = os.getenv('GEMINI_API_KEY')
if gemini_api_key and gemini_api_key != 'SUA_CHAVE_AQUI':
    genai.configure(api_key=gemini_api_key)
    modelo_ia = genai.GenerativeModel('gemini-1.5-flash')
    print("Google Gemini AI configurado com sucesso!")
else:
    modelo_ia = None
    print("GEMINI_API_KEY nao configurada. Recursos de IA estarao desabilitados.")

# Inicializar sistema de análise nutricional
inicializar_analise_ia(modelo_ia)

# --- Configuração do Aplicativo Flask ---
app = Flask(__name__)
bcrypt = Bcrypt(app)

# === CONFIGURAÇÃO DE LOGGING ESTRUTURADO ===
def configurar_logging():
    """Configura sistema de logging com rotação de arquivos"""
    # Criar diretório de logs se não existir
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configurar logging principal
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Arquivo com rotação (10MB, 5 arquivos)
            RotatingFileHandler('logs/l7nutri.log', maxBytes=10*1024*1024, backupCount=5),
            # Console para desenvolvimento
            logging.StreamHandler()
        ]
    )
    
    # Logger específico para IA
    ia_logger = logging.getLogger('ia')
    ia_handler = RotatingFileHandler('logs/ia.log', maxBytes=5*1024*1024, backupCount=3)
    ia_handler.setFormatter(logging.Formatter('%(asctime)s - IA - %(levelname)s - %(message)s'))
    ia_logger.addHandler(ia_handler)
    
    # Logger para análises
    analise_logger = logging.getLogger('analise')
    analise_handler = RotatingFileHandler('logs/analises.log', maxBytes=5*1024*1024, backupCount=3)
    analise_handler.setFormatter(logging.Formatter('%(asctime)s - ANALISE - %(levelname)s - %(message)s'))
    analise_logger.addHandler(analise_handler)
    
    app.logger.info("Sistema de logging configurado com sucesso")

# Configurar logging
configurar_logging()

# === SISTEMA DE BACKUP AUTOMÁTICO ===
def realizar_backup_banco():
    """Realiza backup do banco de dados SQLite"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backups/nutricao_backup_{timestamp}.db'
        
        # Criar diretório de backup se não existir
        if not os.path.exists('backups'):
            os.makedirs('backups')
        
        # Copiar banco de dados
        import shutil
        shutil.copy2('nutricao.db', backup_filename)
        
        app.logger.info(f"Backup realizado com sucesso: {backup_filename}")
        
        # Limpar backups antigos (manter apenas 7 dias)
        limpar_backups_antigos()
        
        return True
    except Exception as e:
        app.logger.error(f"Erro ao realizar backup: {str(e)}")
        enviar_alerta_erro(f"Falha no backup: {str(e)}")
        return False

def limpar_backups_antigos():
    """Remove backups com mais de 7 dias"""
    try:
        import glob
        backups = glob.glob('backups/nutricao_backup_*.db')
        cutoff_time = datetime.now() - timedelta(days=7)
        
        for backup in backups:
            backup_time = datetime.fromtimestamp(os.path.getmtime(backup))
            if backup_time < cutoff_time:
                os.remove(backup)
                app.logger.info(f"Backup antigo removido: {backup}")
    except Exception as e:
        app.logger.error(f"Erro ao limpar backups antigos: {str(e)}")

def enviar_alerta_erro(mensagem):
    """Envia alerta de erro por email"""
    try:
        email_admin = os.getenv('ADMIN_EMAIL', 'admin@l7nutri.com')
        enviar_email(
            email_admin,
            'ALERTA L7Nutri - Erro do Sistema',
            f"""
            🚨 ALERTA DO SISTEMA L7NUTRI 🚨
            
            Mensagem: {mensagem}
            Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Servidor: {os.getenv('RENDER_SERVICE_NAME', 'Local')}
            
            Verifique os logs para mais detalhes.
            """,
            tipo='alerta'
        )
    except Exception as e:
        app.logger.error(f"Erro ao enviar alerta: {str(e)}")

def executar_backup_agendado():
    """Executa backup em thread separada"""
    def job():
        schedule.every().day.at("03:00").do(realizar_backup_banco)
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto
    
    # Executar em thread separada para não bloquear a aplicação
    backup_thread = threading.Thread(target=job, daemon=True)
    backup_thread.start()
    app.logger.info("Sistema de backup automático iniciado (03:00 diariamente)")

# Iniciar sistema de backup
executar_backup_agendado()

# === CONFIGURAÇÃO DE AMBIENTE ===
# Detecta se estamos em produção ou desenvolvimento
# Force rebuild cache 21/07/2025 - Fix tabela órfã ConquistaUsuario
is_production = os.getenv('FLASK_ENV') == 'production'

# Configuração do JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
    seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 31536000))  # 1 ano padrão
)
jwt = JWTManager(app)

# Configura a chave secreta para a aplicação
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))

# === CONFIGURAÇÃO DO BANCO DE DADOS (VERSÃO FINAL E CORRIGIDA) ===
DATABASE_URL = os.getenv('DATABASE_URL')

# A nova lógica: Se a variável DATABASE_URL existir no ambiente, use-a.
if DATABASE_URL:
    # Garante a compatibilidade com SQLAlchemy trocando 'postgres://' por 'postgresql://' se necessário
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    print("✅ MODO PRODUÇÃO: Conectando ao banco de dados PostgreSQL do Render...")
else:
    # Fallback para desenvolvimento local se a variável não existir
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.getcwd()), 'nutricao.db')
    print("⚠️ MODO DESENVOLVIMENTO: Usando banco de dados SQLite local.")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o SQLAlchemy com o aplicativo Flask
db = SQLAlchemy(app)

# Inicializa o Flask-Migrate
migrate = Migrate(app, db)

# === CONFIGURAÇÃO DE EMAIL ===
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# === FUNÇÕES DE SISTEMA DE VERIFICAÇÃO ===

def validar_email_real(email):
    """Valida se o email tem formato correto e não é temporário"""
    # Padrão básico de email
    padrao_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(padrao_email, email):
        return False, "Formato de email inválido"
    
    # Lista de domínios temporários conhecidos
    dominios_temporarios = [
        '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
        'mailinator.com', 'yopmail.com', 'temp-mail.org',
        'sharklasers.com', 'grr.la', 'throwaway.email'
    ]
    
    dominio = email.split('@')[1].lower()
    if dominio in dominios_temporarios:
        return False, "Emails temporários não são permitidos"
    
    return True, "Email válido"

def gerar_token_verificacao():
    """Gera um token seguro para verificação de email"""
    return secrets.token_urlsafe(32)

def enviar_email_verificacao(email, nome, token):
    """Envia email de verificação para o usuário"""
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        print("⚠️ Configurações de email não encontradas")
        return False
    
    try:
        # Configurar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🥗 L7Nutri - Confirme sua conta"
        msg['From'] = EMAIL_USERNAME
        msg['To'] = email
        
        # Criar URL de verificação
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        link_verificacao = f"{base_url}/verificar-email?token={token}"
        
        # HTML do email
        html_email = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirme sua conta L7Nutri</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">🥗 L7Nutri</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">Bem-vindo à sua jornada nutricional!</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                <h2 style="color: #28a745; margin-top: 0;">Olá, {nome}! 👋</h2>
                
                <p>Você está quase lá! Para ativar sua conta L7Nutri e começar sua jornada de transformação nutricional, você precisa confirmar seu email.</p>
                
                <div style="background: white; padding: 25px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #28a745;">
                    <h3 style="color: #333; margin-top: 0;">🚀 Próximos passos:</h3>
                    <ol style="color: #666;">
                        <li>Clique no botão abaixo para verificar seu email</li>
                        <li>Complete o questionário L7Chef personalizado</li>
                        <li>Receba suas recomendações nutricionais exclusivas</li>
                        <li>Comece a usar seu diário alimentar inteligente</li>
                    </ol>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link_verificacao}" style="background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; display: inline-block;">
                        ✅ Confirmar Minha Conta
                    </a>
                </div>
                
                <div style="background: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="color: #0066cc; margin-top: 0;">🔒 Segurança Garantida</h4>
                    <p style="margin-bottom: 0; color: #004499; font-size: 14px;">
                        Verificamos todos os emails para garantir que apenas pessoas reais acessem a plataforma. 
                        Isso garante uma comunidade mais segura e recomendações mais precisas.
                    </p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #e9ecef; margin: 30px 0;">
                
                <p style="color: #666; font-size: 14px; text-align: center;">
                    Se você não se cadastrou na L7Nutri, pode ignorar este email.<br>
                    Este link expira em 24 horas por segurança.
                </p>
                
                <div style="text-align: center; margin-top: 20px;">
                    <p style="color: #999; font-size: 12px;">
                        L7Nutri - Sua jornada nutricional personalizada<br>
                        Email enviado automaticamente, não responda este email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Versão texto
        texto_email = f"""
        L7Nutri - Confirme sua conta
        
        Olá, {nome}!
        
        Bem-vindo à L7Nutri! Para ativar sua conta, confirme seu email clicando no link abaixo:
        
        {link_verificacao}
        
        Após a confirmação, você poderá:
        - Completar o questionário L7Chef
        - Receber recomendações personalizadas
        - Acessar seu diário alimentar
        
        Este link expira em 24 horas.
        
        Se você não se cadastrou na L7Nutri, ignore este email.
        
        L7Nutri - Sua jornada nutricional personalizada
        """
        
        # Anexar partes da mensagem
        parte_texto = MIMEText(texto_email, 'plain', 'utf-8')
        parte_html = MIMEText(html_email, 'html', 'utf-8')
        
        msg.attach(parte_texto)
        msg.attach(parte_html)
        
        # Enviar email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email de verificação enviado para {email}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {str(e)}")
        return False

def requer_verificacao_email(f):
    """Decorator para rotas que requerem email verificado"""
    @wraps(f)
    def verificar_email_decorator(*args, **kwargs):
        if 'usuario_id' not in session:
            return jsonify({'erro': 'Login necessário'}), 401
        
        usuario = Usuario.query.get(session['usuario_id'])
        if not usuario or not usuario.email_verificado:
            return jsonify({
                'erro': 'Email não verificado',
                'acao_necessaria': 'verificar_email'
            }), 403
        
        return f(*args, **kwargs)
    return verificar_email_decorator

def requer_onboarding_completo(f):
    """Decorator para rotas que requerem onboarding completo"""
    @wraps(f)
    def verificar_onboarding_decorator(*args, **kwargs):
        if 'usuario_id' not in session:
            return jsonify({'erro': 'Login necessário'}), 401
        
        usuario = Usuario.query.get(session['usuario_id'])
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        if not usuario.email_verificado:
            return jsonify({
                'erro': 'Email não verificado',
                'acao_necessaria': 'verificar_email'
            }), 403
        
        if not usuario.onboarding_completo:
            return jsonify({
                'erro': 'Onboarding não completado',
                'acao_necessaria': 'completar_onboarding'
            }), 403
        
        return f(*args, **kwargs)
    return verificar_onboarding_decorator

def obter_ip_cliente(request):
    """Obtém o IP real do cliente considerando proxies"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

# --- Modelos do Banco de Dados (Tabelas) ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    idade = db.Column(db.Integer)
    sexo = db.Column(db.String(10))
    peso = db.Column(db.Float)
    altura = db.Column(db.Float)
    nivel_atividade = db.Column(db.String(50))
    fator_atividade = db.Column(db.Float)
    objetivo = db.Column(db.String(100))

    # Campos de verificação de email
    email_verificado = db.Column(db.Boolean, default=False, nullable=False)
    token_verificacao = db.Column(db.String(255), nullable=True)
    token_expiracao = db.Column(db.DateTime, nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime, nullable=True)

    # Campos de onboarding
    onboarding_completo = db.Column(db.Boolean, default=False, nullable=False)
    dados_questionario = db.Column(db.JSON, nullable=True)
    plano_personalizado = db.Column(db.JSON, nullable=True)
    dicas_l7chef = db.Column(db.JSON, nullable=True)
    analise_nutricional = db.Column(db.JSON, nullable=True)  # Análise IA personalizada

    # Campos de segurança
    tentativas_login = db.Column(db.Integer, default=0)
    bloqueado_ate = db.Column(db.DateTime, nullable=True)
    ip_cadastro = db.Column(db.String(45), nullable=True)

    alergias = db.relationship('AlergiaUsuario', backref='usuario', lazy=True)
    preferencias = db.relationship('PreferenciaUsuario', backref='usuario', lazy=True)
    registros_alimentares = db.relationship('RegistroAlimentar', backref='usuario', lazy=True)
    planos_sugeridos = db.relationship('PlanoSugestao', backref='usuario', lazy=True)
    # Relacionamento conquistas removido temporariamente para correção de bugs

    def __repr__(self):
        return f'<Usuario {self.username}>'

    def esta_verificado(self):
        """Verifica se o email foi confirmado"""
        return self.email_verificado

    def esta_onboarding_completo(self):
        """Verifica se o onboarding foi completado"""
        return self.onboarding_completo

    def pode_acessar_diario(self):
        """Verifica se pode acessar o diário alimentar"""
        return self.email_verificado and self.onboarding_completo

    def token_valido(self):
        """Verifica se o token de verificação ainda é válido"""
        if not self.token_expiracao:
            return False
        return datetime.utcnow() < self.token_expiracao

    def esta_bloqueado(self):
        """Verifica se o usuário está temporariamente bloqueado"""
        if not self.bloqueado_ate:
            return False
        return datetime.utcnow() < self.bloqueado_ate

class Alimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    categoria = db.Column(db.String(50))  # Ex: frutas, legumes, carnes, etc
    calorias = db.Column(db.Float)
    proteinas = db.Column(db.Float)
    carboidratos = db.Column(db.Float)
    gorduras = db.Column(db.Float)
    fibras = db.Column(db.Float)
    sodio = db.Column(db.Float)  # em mg
    acucar = db.Column(db.Float)  # em g
    colesterol = db.Column(db.Float)  # em mg
    porcao_referencia = db.Column(db.String(20), default='100g')  # Ex: 100g, 1 unidade
    fonte_dados = db.Column(db.String(50), default='TACO')  # TACO, ANVISA, etc

    def __repr__(self):
        return f'<Alimento {self.nome}>'

class Receita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text)
    tipo_refeicao = db.Column(db.String(50))
    alimentos = db.relationship('ReceitaAlimento', backref='receita', lazy=True)

    def __repr__(self):
        return f'<Receita {self.nome}>'

# Modelo para associar ingredientes (alimentos) às receitas
class ReceitaAlimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=False)
    alimento_id = db.Column(db.Integer, db.ForeignKey('alimento.id'), nullable=False)
    quantidade_gramas = db.Column(db.Float)

    def __repr__(self):
        return f'<ReceitaAlimento Receita:{self.receita_id} Alimento:{self.alimento_id}>'

class Alergia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f'<Alergia {self.nome}>'

class AlergiaUsuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    alergia_id = db.Column(db.Integer, db.ForeignKey('alergia.id'), nullable=False)

    def __repr__(self):
        return f'<AlergiaUsuario Usuario:{self.usuario_id} Alergia:{self.alergia_id}>'

class Preferencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f'<Preferencia {self.nome}>'

class PreferenciaUsuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    preferencia_id = db.Column(db.Integer, db.ForeignKey('preferencia.id'), nullable=False)

    def __repr__(self):
        return f'<PreferenciaUsuario Usuario:{self.usuario_id} Preferencia:{self.preferencia_id}>'

class RegistroAlimentar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    data = db.Column(db.Date, nullable=False, default=date.today)
    tipo_refeicao = db.Column(db.String(50), nullable=False)
    alimento_id = db.Column(db.Integer, db.ForeignKey('alimento.id'), nullable=True)
    receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=True)
    quantidade_gramas = db.Column(db.Float)

    alimento = db.relationship('Alimento', backref='registros_alimentares_alimento', lazy=True)
    receita = db.relationship('Receita', backref='registros_alimentares_receita', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'data': self.data.isoformat() if self.data else None,
            'tipo_refeicao': self.tipo_refeicao,
            'alimento_id': self.alimento_id,
            'receita_id': self.receita_id,
            'quantidade_gramas': self.quantidade_gramas,
            'alimento': {
                'id': self.alimento.id,
                'nome': self.alimento.nome,
                'calorias': self.alimento.calorias,
                'proteinas': self.alimento.proteinas,
                'carboidratos': self.alimento.carboidratos,
                'gorduras': self.alimento.gorduras
            } if self.alimento else None,
            'receita': {
                'id': self.receita.id,
                'nome': self.receita.nome,
                'descricao': self.receita.descricao,
                'tipo_refeicao': self.receita.tipo_refeicao
            } if self.receita else None
        }

    def __repr__(self):
        return f'<RegistroAlimentar Usuario:{self.usuario_id} Data:{self.data} Refeicao:{self.tipo_refeicao}>'

class PlanoSugestao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    data_sugestao = db.Column(db.Date, nullable=False)
    cafe_manha_receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=True)
    almoco_receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=True)
    jantar_receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=True)
    lanche_receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=True)

    cafe_manha_receita = db.relationship('Receita', foreign_keys=[cafe_manha_receita_id], backref='plano_cafe_manha', lazy=True)
    almoco_receita = db.relationship('Receita', foreign_keys=[almoco_receita_id], backref='plano_almoco', lazy=True)
    jantar_receita = db.relationship('Receita', foreign_keys=[jantar_receita_id], backref='plano_jantar', lazy=True)
    lanche_receita = db.relationship('Receita', foreign_keys=[lanche_receita_id], backref='plano_lanche', lazy=True)

    def __repr__(self):
        return f'<PlanoSugestao Usuario:{self.usuario_id} Data:{self.data_sugestao}>'

# Modelo Suplementos
class Suplementos(db.Model):
    __tablename__ = 'suplementos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    objetivo = db.Column(db.String(30))
    link_loja = db.Column(db.String(255))
    imagem_url = db.Column(db.String(255))

    def __repr__(self):
        return f'<Suplemento {self.nome}>'

# --- Modelo PerfisNutricionais ---
class PerfisNutricionais(db.Model):
    __tablename__ = 'perfis_nutricionais'
    id = db.Column(db.Integer, primary_key=True)
    peso = db.Column(db.Float)
    altura = db.Column(db.Integer)
    idade = db.Column(db.Integer)
    genero = db.Column(db.String(20))
    nivel_atividade = db.Column(db.String(30))
    objetivo = db.Column(db.String(30))
    aceita_suplementos = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    created_at = db.Column(db.DateTime, default=date.today)

# --- Modelo PreferenciasUsuario ---
class PreferenciasUsuario(db.Model):
    __tablename__ = 'preferencias_usuario'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    alimentos_evitar = db.Column(db.Text)  # Lista de alimentos separados por vírgula
    restricoes = db.Column(db.JSON)  # Array JSON com restrições
    estilo_alimentar = db.Column(db.String(50))  # Estilo alimentar escolhido
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com Usuario (sem conflito)
    # usuario = db.relationship('Usuario') # Relacionamento direto sem backref
    
    def __repr__(self):
        return f'<PreferenciasUsuario {self.usuario_id}>'

# === MODELOS PARA SISTEMA DE BADGES E GAMIFICAÇÃO ===

class Badge(db.Model):
    """Modelo para badges/medalhas do sistema"""
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    icone = db.Column(db.String(50), nullable=False)  # Emoji ou classe CSS
    cor = db.Column(db.String(20), default='#667eea')  # Cor da badge
    tipo = db.Column(db.String(50), nullable=False)  # streak, meta, primeiro_registro, etc.
    criterio = db.Column(db.Integer, nullable=False)  # Valor necessário (ex: 7 dias)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Badge {self.nome}>'

# ConquistaUsuario modelo removido temporariamente para correção de bugs

class StreakUsuario(db.Model):
    """Modelo para tracking de sequências de usuários"""
    __tablename__ = 'streaks_usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo_streak = db.Column(db.String(50), nullable=False)  # diario_preenchido, meta_proteina, etc.
    streak_atual = db.Column(db.Integer, default=0)
    melhor_streak = db.Column(db.Integer, default=0)
    ultima_atividade = db.Column(db.Date)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    usuario = db.relationship('Usuario', backref='streaks')

# === MODELO PARA SISTEMA DE LEADS ===
class Lead(db.Model):
    """Modelo para captura de leads antes do cadastro completo"""
    __tablename__ = 'leads'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    objetivo = db.Column(db.String(50), nullable=True)  # emagrecer, ganhar_massa, etc.
    fonte = db.Column(db.String(50), default='modal_captura')  # modal_captura, landing_page, etc.
    ip_address = db.Column(db.String(45), nullable=True)  # Para analytics
    user_agent = db.Column(db.Text, nullable=True)  # Para analytics
    utm_source = db.Column(db.String(100), nullable=True)  # Tracking de origem
    utm_medium = db.Column(db.String(100), nullable=True)
    utm_campaign = db.Column(db.String(100), nullable=True)
    converteu_cadastro = db.Column(db.Boolean, default=False)  # Se virou usuário completo
    data_conversao = db.Column(db.DateTime, nullable=True)  # Quando se cadastrou completamente
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'nome': self.nome,
            'objetivo': self.objetivo,
            'fonte': self.fonte,
            'converteu_cadastro': self.converteu_cadastro,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<StreakUsuario {self.usuario_id}:{self.tipo_streak}>'

# --- ROTAS DA APLICAÇÃO ---

@app.route('/')
def home():
    return render_template('home.html')

# Rota para landing page de leads
@app.route('/landing')
def landing_page_leads():
    """Landing page otimizada para captura de leads"""
    return render_template('landing_page_leads.html')

# --- Rota para página de metas nutricionais ---
@app.route('/metas-nutricionais')
def metas_nutricionais():
    """Página para exibir as metas nutricionais personalizadas do usuário"""
    return render_template('metas_nutricionais.html')

# --- Rota para demo do sistema de metas ---
@app.route('/demo-metas')
def demo_metas():
    """Página de demonstração do cálculo de metas nutricionais"""
    return render_template('demo_metas.html')

# --- Rota pública para diagnóstico nutricional ---
@app.route('/api/diagnostico-publico', methods=['POST'])
def diagnostico_publico():
    data = request.get_json()
    if not data:
        return jsonify({'erro': 'Dados são obrigatórios!'}), 400
    
    try:
        # 2. Coletar os dados
        peso = float(data['peso'])
        altura_cm = float(data['altura'])
        idade = int(data['idade'])
        sexo = data['sexo'].lower()
        fator_atividade = float(data['nivel_atividade']) # Supondo que o valor já vem (ex: 1.2, 1.375)
        objetivo = data['objetivo'].lower().replace(' ', '_')  # Normaliza objetivo: "Ganho de Massa" -> "ganho_de_massa"

        # 3. Realizar os Cálculos (A INTELIGÊNCIA)
        altura_m = altura_cm / 100
        imc = round(peso / (altura_m ** 2), 2)

        # TMB (Taxa Metabólica Basal)
        if sexo == 'masculino':
            tmb = 88.362 + (13.397 * peso) + (4.799 * altura_cm) - (5.677 * idade)
        elif sexo == 'feminino':
            tmb = 447.593 + (9.247 * peso) + (3.098 * altura_cm) - (4.330 * idade)
        else:
            return jsonify({'erro': 'Sexo deve ser "masculino" ou "feminino"'}), 400
        
        # GET (Gasto Energético Total)
        get = tmb * fator_atividade

        # Meta Calórica por Objetivo
        if objetivo == 'emagrecimento':
            meta_calorica = get - 500
        elif objetivo == 'ganhar':  # Atualizado para aceitar 'ganhar' do frontend
            meta_calorica = get + 400
        else: # Manter
            meta_calorica = get

        # 4. Montar a Resposta JSON
        resposta = {
            'diagnostico': {
                'imc': imc,
                'gasto_calorico_diario_estimado': round(get),
                'meta_calorica_sugerida': round(meta_calorica)
            },
            'plano_exemplo_1_dia': {
                'cafe_da_manha': 'Ex: 2 ovos mexidos com 1 fatia de pão integral.',
                'almoco': 'Ex: 150g de frango grelhado, arroz integral e salada.',
                'jantar': 'Ex: 1 posta de salmão com legumes no vapor.'
            },
            'call_to_action': 'Gostou? Crie sua conta gratuitamente em nossa plataforma para salvar seu progresso e receber planos completos e personalizados!'
        }

        # --- LÓGICA DE RECOMENDAÇÃO - VERSÃO COMPLETA E FINAL ---
        
        suplemento_query = None

        if objetivo == 'emagrecimento':
            suplemento_query = Suplementos.query.filter(Suplementos.objetivo.contains('emagrecimento')).first()
        elif objetivo == 'ganhar':
            suplemento_query = Suplementos.query.filter(Suplementos.objetivo.contains('ganho_massa')).first()
        elif objetivo == 'manter': # <-- A NOVA CONDIÇÃO QUE FALTAVA
            # O termo de busca no BD será 'manter'
            suplemento_query = Suplementos.query.filter(Suplementos.objetivo.contains('manter')).first()
        elif objetivo == 'energia':
            suplemento_query = Suplementos.query.filter(Suplementos.objetivo.contains('energia')).first()
        
        # O resto do código permanece o mesmo
        if suplemento_query:
            resposta['suplemento_recomendado'] = {
                'nome': suplemento_query.nome,
                'link_loja': suplemento_query.link_loja,
                'imagem_url': suplemento_query.imagem_url
            }

        return jsonify(resposta), 200

    except (ValueError, TypeError) as e:
        return jsonify({'erro': f'Dado inválido fornecido: {e}'}), 400
    except Exception as e:
        return jsonify({'erro': f'Ocorreu um erro inesperado: {e}'}), 500

# --- ROTA DE DEBUG TEMPORÁRIA ---
# Adiciona uma rota para listar todos os suplementos cadastrados
@app.route('/api/debug/suplementos', methods=['GET'])
def listar_todos_os_suplementos():
    try:
        # Busca todos os registros da tabela Suplementos
        todos_suplementos = Suplementos.query.all()
        # Se não houver suplementos, retorna uma lista vazia
        if not todos_suplementos:
            return jsonify([]), 200
        # Transforma os objetos em uma lista de dicionários para o JSON
        resultado = []
        for suplemento in todos_suplementos:
            resultado.append({
                'id': suplemento.id,
                'nome': suplemento.nome,
                'objetivo': suplemento.objetivo
            })
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': f'Ocorreu um erro ao buscar os suplementos: {str(e)}'}), 500

# --- Rota temporária para listar suplementos cadastrados ---
@app.route('/api/suplementos', methods=['GET'])
def listar_suplementos():
    suplementos = Suplementos.query.all()
    resultado = []
    for sup in suplementos:
        resultado.append({
            'id': sup.id,
            'nome': sup.nome,
            'objetivo': sup.objetivo
        })
    return jsonify(resultado), 200

# --- Rota protegida para dicas nutricionais ---
@app.route('/api/nutri/dicas', methods=['GET'])
@jwt_required()
def dicas_nutricionais():
    user_id = get_jwt_identity()
    perfil = PerfisNutricionais.query.filter_by(user_id=user_id).order_by(PerfisNutricionais.created_at.desc()).first()
    if not perfil:
        return jsonify({'erro': 'Preencha seu perfil nutricional primeiro!'}), 400

    dicas = []
    # Geração de dicas básicas
    if perfil.objetivo == 'emagrecimento':
        dicas.append('Mantenha uma alimentação rica em fibras e proteínas para maior saciedade.')
        dicas.append('Evite açúcares simples e priorize alimentos naturais.')
        if perfil.nivel_atividade == 'sedentario':
            dicas.append('Inclua caminhadas leves diariamente para acelerar o metabolismo.')
        else:
            dicas.append('Continue praticando atividades físicas para potencializar o emagrecimento.')
    elif perfil.objetivo == 'ganho_massa':
        dicas.append('Consuma proteínas magras em todas as refeições.')
        dicas.append('Inclua carboidratos complexos para fornecer energia ao treino.')
        dicas.append('Durma bem para otimizar a recuperação muscular.')
    else:
        dicas.append('Mantenha uma alimentação equilibrada e variada.')
        dicas.append('Beba bastante água ao longo do dia.')

    suplemento = None
    if perfil.objetivo == 'emagrecimento' and perfil.aceita_suplementos:
        suplemento = Suplementos.query.filter_by(objetivo='emagrecimento').first()

    resposta = {'dicas': dicas}
    if suplemento:
        resposta['suplemento_recomendado'] = {
            'nome': suplemento.nome,
            'link_loja': suplemento.link_loja,
            'imagem_url': suplemento.imagem_url
        }
    return jsonify(resposta), 200

# --- Rota protegida para criar/atualizar perfil nutricional ---
@app.route('/api/nutri/perfil', methods=['POST'])
@jwt_required()
def criar_ou_atualizar_perfil():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({'mensagem': 'Dados do perfil são obrigatórios!'}), 400

    perfil = PerfisNutricionais.query.filter_by(user_id=user_id).first()
    if perfil:
        # Atualiza perfil existente
        perfil.peso = data.get('peso', perfil.peso)
        perfil.altura = data.get('altura', perfil.altura)
        perfil.idade = data.get('idade', perfil.idade)
        perfil.genero = data.get('genero', perfil.genero)
        perfil.nivel_atividade = data.get('nivel_atividade', perfil.nivel_atividade)
        perfil.objetivo = data.get('objetivo', perfil.objetivo)
        perfil.aceita_suplementos = data.get('aceita_suplementos', perfil.aceita_suplementos)
    else:
        perfil = PerfisNutricionais(
            peso=data.get('peso'),
            altura=data.get('altura'),
            idade=data.get('idade'),
            genero=data.get('genero'),
            nivel_atividade=data.get('nivel_atividade'),
            objetivo=data.get('objetivo'),
            aceita_suplementos=data.get('aceita_suplementos'),
            user_id=user_id
        )
        db.session.add(perfil)
    try:
        db.session.commit()
        return jsonify({'mensagem': 'Perfil salvo com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'mensagem': f'Erro ao salvar perfil: {str(e)}'}), 500

# Rota para Cadastro de Novo Usuário
@app.route('/cadastro', methods=['POST'])
def cadastro_usuario():
    data = request.get_json()

    if not data or not 'username' in data or not 'password' in data:
        return jsonify({'message': 'Dados de usuário e senha são obrigatórios!'}), 400

    username = data['username']
    password = data['password']

    if Usuario.query.filter_by(username=username).first():
        return jsonify({'message': 'Nome de usuário já existe. Escolha outro!'}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    novo_usuario = Usuario(
        username=username,
        password=hashed_password,
        idade=data.get('idade'),
        sexo=data.get('sexo'),
        peso=data.get('peso'),
        altura=data.get('altura'),
        nivel_atividade=data.get('nivel_atividade'),
        objetivo=data.get('objetivo')
    )

    try:
        db.session.add(novo_usuario)
        db.session.commit()

        if 'alergias' in data and isinstance(data['alergias'], list):
            for alergia_nome in data['alergias']:
                alergia = Alergia.query.filter_by(nome=alergia_nome).first()
                if not alergia:
                    alergia = Alergia(nome=alergia_nome)
                    db.session.add(alergia)
                    db.session.commit()

                alergia_usuario = AlergiaUsuario(usuario_id=novo_usuario.id, alergia_id=alergia.id)
                db.session.add(alergia_usuario)
            db.session.commit()

        if 'preferencias' in data and isinstance(data['preferencias'], list):
            for preferencia_nome in data['preferencias']:
                preferencia = Preferencia.query.filter_by(nome=preferencia_nome).first()
                if not preferencia:
                    preferencia = Preferencia(nome=preferencia_nome)
                    db.session.add(preferencia)
                    db.session.commit()

                preferencia_usuario = PreferenciaUsuario(usuario_id=novo_usuario.id, preferencia_id=preferencia.id)
                db.session.add(preferencia_usuario)
            db.session.commit()

        return jsonify({'message': 'Usuário cadastrado com sucesso!', 'user_id': novo_usuario.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao cadastrar usuário: {str(e)}'}), 500

# --- Rota para Cadastro de Usuário ---
@app.route('/api/cadastro', methods=['POST'])
def cadastro_novo_usuario():
    """
    Endpoint para cadastro de novos usuários
    Aceita: nome, email, username, password
    Retorna: JSON com mensagem de sucesso ou erro
    """
    data = request.get_json()
    
    # Validação de dados obrigatórios
    if not data:
        return jsonify({'erro': 'Dados são obrigatórios!'}), 400
    
    if not 'nome' in data or not 'email' in data or not 'username' in data or not 'password' in data:
        return jsonify({'erro': 'Campos nome, email, username e password são obrigatórios!'}), 400
    
    nome = data['nome']
    email = data['email']
    username = data['username']
    password = data['password']
    
    # Validação de duplicidade - verifica se email ou username já existem
    usuario_existente = Usuario.query.filter(
        (Usuario.email == email) | (Usuario.username == username)
    ).first()
    
    if usuario_existente:
        if usuario_existente.email == email:
            return jsonify({'erro': 'E-mail já cadastrado'}), 409
        else:
            return jsonify({'erro': 'Username já cadastrado'}), 409
    
    try:
        # Segurança da senha - gera hash usando bcrypt
        senha_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Criação do novo usuário
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            username=username,
            password=senha_hash
        )
        
        # Persistência no banco de dados
        db.session.add(novo_usuario)
        db.session.commit()
        
        return jsonify({'mensagem': 'Usuário criado com sucesso'}), 201
        
    except Exception as e:
        # Em caso de erro, desfaz a transação
        db.session.rollback()
        return jsonify({'erro': f'Erro ao criar usuário: {str(e)}'}), 500

# Rota para Login de Usuário usando JWT
@app.route('/api/login', methods=['POST'])
def login_usuario():
    data = request.get_json()
    if not data or not 'username' in data or not 'password' in data:
        return jsonify({'message': 'Usuário e senha são obrigatórios!'}), 400
    
    username = data['username']
    password = data['password']
    usuario = Usuario.query.filter_by(username=username).first()
    
    if usuario and bcrypt.check_password_hash(usuario.password, password):
        # Atualizar último login
        usuario.ultimo_login = datetime.utcnow()
        db.session.commit()
        
        access_token = create_access_token(identity=str(usuario.id))
        
        # Verificar status do usuário para redirecionamento
        response_data = {
            'access_token': access_token,
            'user_id': usuario.id,
            'nome': usuario.nome
        }
        
        # Verificar se email foi verificado
        if not usuario.email_verificado:
            response_data['redirect'] = '/verificar-email'
            response_data['acao_necessaria'] = 'verificar_email'
            response_data['mensagem'] = 'Verifique seu email antes de continuar'
        # Verificar se onboarding foi completado
        elif not usuario.onboarding_completo:
            response_data['redirect'] = '/onboarding'
            response_data['acao_necessaria'] = 'completar_onboarding'
            response_data['mensagem'] = 'Complete seu perfil para personalizar sua experiência'
        # Verificar se tem análise nutricional
        elif not usuario.analise_nutricional:
            response_data['redirect'] = '/analise-nutricional'
            response_data['acao_necessaria'] = 'ver_analise'
            response_data['mensagem'] = 'Veja sua análise nutricional personalizada!'
        else:
            response_data['redirect'] = '/dashboard'
            response_data['mensagem'] = f'Bem-vindo de volta, {usuario.nome}!'
        
        return jsonify(response_data), 200
    else:
        return jsonify({'message': 'Nome de usuário ou senha incorretos!'}), 401

# === ROTAS DO SISTEMA DE VERIFICAÇÃO E ONBOARDING ===

@app.route('/api/usuario/registro-seguro', methods=['POST'])
def registro_seguro():
    """Registro com verificação de email obrigatória"""
    data = request.get_json()
    
    if not data:
        return jsonify({'sucesso': False, 'erro': 'Dados são obrigatórios'}), 400
    
    nome = data.get('nome', '').strip()
    email = data.get('email', '').strip().lower()
    senha = data.get('senha', '')
    
    # Validações básicas
    if not nome or len(nome) < 3:
        return jsonify({'sucesso': False, 'erro': 'Nome deve ter pelo menos 3 caracteres'}), 400
    
    if not email or not senha:
        return jsonify({'sucesso': False, 'erro': 'Email e senha são obrigatórios'}), 400
    
    if len(senha) < 8:
        return jsonify({'sucesso': False, 'erro': 'Senha deve ter pelo menos 8 caracteres'}), 400
    
    # Validar email
    email_valido, mensagem_email = validar_email_real(email)
    if not email_valido:
        return jsonify({'sucesso': False, 'erro': mensagem_email}), 400
    
    # Verificar se email já existe
    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        if usuario_existente.email_verificado:
            return jsonify({'sucesso': False, 'erro': 'Este email já está cadastrado e verificado'}), 409
        else:
            # Reenviar verificação para email não verificado
            token = gerar_token_verificacao()
            usuario_existente.token_verificacao = token
            usuario_existente.token_expiracao = datetime.utcnow() + timedelta(hours=24)
            db.session.commit()
            
            if enviar_email_verificacao(email, nome, token):
                return jsonify({
                    'sucesso': True,
                    'mensagem': 'Email de verificação reenviado. Verifique sua caixa de entrada.'
                }), 200
            else:
                return jsonify({'sucesso': False, 'erro': 'Erro ao enviar email'}), 500
    
    try:
        # Criar novo usuário
        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')
        token = gerar_token_verificacao()
        
        # Gerar username único baseado no email
        username_base = email.split('@')[0]
        username = username_base
        contador = 1
        while Usuario.query.filter_by(username=username).first():
            username = f"{username_base}{contador}"
            contador += 1
        
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            username=username,
            password=senha_hash,
            token_verificacao=token,
            token_expiracao=datetime.utcnow() + timedelta(hours=24),
            ip_cadastro=obter_ip_cliente(request)
        )
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        # Enviar email de verificação
        if enviar_email_verificacao(email, nome, token):
            return jsonify({
                'sucesso': True,
                'mensagem': 'Conta criada! Verifique seu email para ativar.'
            }), 201
        else:
            return jsonify({
                'sucesso': False,
                'erro': 'Conta criada, mas erro ao enviar email. Tente reenviar.'
            }), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': f'Erro ao criar conta: {str(e)}'}), 500

@app.route('/api/verificar-email', methods=['POST'])
def verificar_email():
    """Verifica o email do usuário através do token"""
    data = request.get_json()
    token = data.get('token') if data else None
    
    if not token:
        return jsonify({'sucesso': False, 'erro': 'Token não fornecido'}), 400
    
    usuario = Usuario.query.filter_by(token_verificacao=token).first()
    
    if not usuario:
        return jsonify({'sucesso': False, 'erro': 'Token de verificação inválido'}), 400
    
    if not usuario.token_valido():
        return jsonify({'sucesso': False, 'erro': 'Token de verificação expirado'}), 400
    
    if usuario.email_verificado:
        return jsonify({'sucesso': False, 'erro': 'Email já verificado anteriormente'}), 400
    
    try:
        # Marcar email como verificado
        usuario.email_verificado = True
        usuario.token_verificacao = None
        usuario.token_expiracao = None
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Email verificado com sucesso! Você pode fazer login agora.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': f'Erro ao verificar email: {str(e)}'}), 500

@app.route('/api/reenviar-verificacao', methods=['POST'])
def reenviar_verificacao():
    """Reenvia email de verificação"""
    data = request.get_json()
    email = data.get('email') if data else None
    
    if not email:
        return jsonify({'sucesso': False, 'erro': 'Email é obrigatório'}), 400
    
    usuario = Usuario.query.filter_by(email=email).first()
    
    if not usuario:
        return jsonify({'sucesso': False, 'erro': 'Email não encontrado'}), 404
    
    if usuario.email_verificado:
        return jsonify({'sucesso': False, 'erro': 'Email já verificado'}), 400
    
    try:
        # Gerar novo token
        token = gerar_token_verificacao()
        usuario.token_verificacao = token
        usuario.token_expiracao = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()
        
        if enviar_email_verificacao(email, usuario.nome, token):
            return jsonify({
                'sucesso': True,
                'mensagem': 'Email de verificação reenviado com sucesso'
            }), 200
        else:
            return jsonify({'sucesso': False, 'erro': 'Erro ao enviar email'}), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': f'Erro ao reenviar verificação: {str(e)}'}), 500

@app.route('/verificar-email')
def pagina_verificacao_email():
    """Página de verificação de email"""
    return render_template('verificacao_email.html')

@app.route('/cadastro-seguro')
@app.route('/cadastro_seguro')  # Rota alternativa para compatibilidade
def pagina_cadastro_seguro():
    """Página de cadastro com verificação"""
    return render_template('cadastro_seguro.html')

@app.route('/onboarding')
def pagina_onboarding():
    """Página do questionário L7Chef"""
    return render_template('onboarding_l7chef.html')

# --- Rota para Atualizar Perfil do Usuário (Passo 2 do Onboarding) ---
@app.route('/api/usuario/perfil', methods=['PUT'])
@jwt_required()
def atualizar_perfil_usuario():
    """
    Endpoint para atualização do perfil do usuário
    Aceita: idade, genero, peso, altura
    Retorna: JSON com mensagem de sucesso ou erro
    """
    # Obter ID do usuário logado através do token JWT
    user_id = get_jwt_identity()
    
    # Extrair dados do JSON da requisição
    data = request.get_json()
    if not data:
        return jsonify({'erro': 'Dados são obrigatórios!'}), 400
    
    # Validação dos dados de entrada
    try:
        idade = data.get('idade')
        genero = data.get('genero')
        peso = data.get('peso')
        altura = data.get('altura')
        
        # Validação de dados numéricos positivos
        if idade is not None:
            idade = int(idade)
            if idade <= 0 or idade > 120:
                return jsonify({'erro': 'Idade deve ser um número positivo entre 1 e 120'}), 400
        
        if peso is not None:
            peso = float(peso)
            if peso <= 0 or peso > 500:
                return jsonify({'erro': 'Peso deve ser um número positivo até 500kg'}), 400
        
        if altura is not None:
            altura = float(altura)
            if altura <= 0 or altura > 300:
                return jsonify({'erro': 'Altura deve ser um número positivo até 300cm'}), 400
        
        if genero is not None and genero not in ['masculino', 'feminino']:
            return jsonify({'erro': 'Gênero deve ser "masculino" ou "feminino"'}), 400
            
    except (ValueError, TypeError):
        return jsonify({'erro': 'Dados de perfil inválidos'}), 400
    
    try:
        # Buscar usuário no banco de dados
        usuario = Usuario.query.get(int(user_id))
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        # Atualizar campos do perfil
        if idade is not None:
            usuario.idade = idade
        if genero is not None:
            usuario.sexo = genero
        if peso is not None:
            usuario.peso = peso
        if altura is not None:
            usuario.altura = altura
        
        # Persistir alterações no banco de dados
        db.session.commit()
        
        return jsonify({'mensagem': 'Perfil atualizado com sucesso'}), 200
        
    except Exception as e:
        # Em caso de erro, desfaz a transação
        db.session.rollback()
        return jsonify({'erro': f'Erro ao atualizar perfil: {str(e)}'}), 500

# --- Rota para Recuperar Perfil do Usuário ---
@app.route('/api/usuario/perfil', methods=['GET'])
@jwt_required()
def obter_perfil_usuario():
    """
    Endpoint para recuperar os dados completos do perfil do usuário
    Retorna: JSON com todos os dados do perfil
    """
    try:
        # Obter ID do usuário do token JWT
        user_id = get_jwt_identity()
        
        # Buscar usuário no banco de dados
        usuario = Usuario.query.get(int(user_id))
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        # Retornar dados do perfil
        perfil_dados = {
            'id': usuario.id,
            'nome': usuario.nome,
            'username': usuario.username,
            'email': usuario.email,
            'idade': usuario.idade,
            'sexo': usuario.sexo,
            'peso': usuario.peso,
            'altura': usuario.altura,
            'fator_atividade': usuario.fator_atividade,
            'objetivo': usuario.objetivo
        }
        
        return jsonify(perfil_dados), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao recuperar perfil: {str(e)}'}), 500

# --- Rota para Salvar Nível de Atividade Física (Passo 3 do Onboarding) ---
@app.route('/api/usuario/atividade-fisica', methods=['PUT'])
@jwt_required()
def salvar_atividade_fisica():
    """
    Endpoint para salvar o nível de atividade física do usuário no onboarding
    Aceita: nivel_atividade (float)
    Retorna: JSON com mensagem de sucesso ou erro
    """
    try:
        # Obter ID do usuário do token JWT
        user_id = get_jwt_identity()
        
        # Buscar usuário no banco de dados
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        # Obter dados da requisição
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados não fornecidos'}), 400
        
        nivel_atividade = data.get('nivel_atividade')
        
        # Validar nível de atividade
        if nivel_atividade is None:
            return jsonify({'erro': 'Nível de atividade é obrigatório'}), 400
        
        # Converter para float e validar valores permitidos
        try:
            nivel_atividade = float(nivel_atividade)
        except (ValueError, TypeError):
            return jsonify({'erro': 'Nível de atividade deve ser um número'}), 400
        
        # Validar se é um dos valores permitidos
        valores_permitidos = [1.2, 1.375, 1.55, 1.725, 1.9]
        if nivel_atividade not in valores_permitidos:
            return jsonify({'erro': 'Nível de atividade inválido'}), 400
        
        # Atualizar nível de atividade do usuário
        usuario.nivel_atividade = str(nivel_atividade)
        
        # Persistir alterações no banco de dados
        db.session.commit()
        
        return jsonify({'mensagem': 'Nível de atividade salvo com sucesso'}), 200
        
    except Exception as e:
        # Em caso de erro, desfaz a transação
        db.session.rollback()
        return jsonify({'erro': f'Erro ao salvar nível de atividade: {str(e)}'}), 500

# --- Rota POST para Salvar Fator de Atividade Física (Onboarding) ---
@app.route('/api/onboarding/atividade', methods=['POST'])
@jwt_required()
def salvar_fator_atividade():
    """
    Endpoint POST para salvar o fator de atividade física do usuário
    Aceita: fator_atividade (float)
    Retorna: JSON com mensagem de sucesso ou erro
    """
    try:
        # Obter ID do usuário do token JWT
        user_id = get_jwt_identity()
        
        # Buscar usuário no banco de dados
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        # Obter dados da requisição
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados não fornecidos'}), 400
        
        fator_atividade = data.get('fator_atividade')
        
        # Validar fator de atividade
        if fator_atividade is None:
            return jsonify({'erro': 'Fator de atividade é obrigatório'}), 400
        
        # Converter para float e validar valores permitidos
        try:
            fator_atividade = float(fator_atividade)
        except (ValueError, TypeError):
            return jsonify({'erro': 'Fator de atividade deve ser um número'}), 400
        
        # Validar se é um dos valores permitidos
        valores_permitidos = [1.2, 1.375, 1.55, 1.725, 1.9]
        if fator_atividade not in valores_permitidos:
            return jsonify({'erro': 'Fator de atividade inválido'}), 400
        
        # Salvar ou atualizar fator de atividade do usuário
        usuario.fator_atividade = fator_atividade
        
        # Persistir alterações no banco de dados
        db.session.commit()
        
        return jsonify({'mensagem': 'Atividade salva com sucesso'}), 200
        
    except Exception as e:
        # Em caso de erro, desfaz a transação
        db.session.rollback()
        return jsonify({'erro': f'Erro ao salvar fator de atividade: {str(e)}'}), 500

# === ROTAS DO SISTEMA DE ANÁLISE NUTRICIONAL INTELIGENTE ===

@app.route('/api/finalizar-onboarding', methods=['POST'])
@jwt_required()
@requer_verificacao_email
def finalizar_onboarding():
    """
    Finaliza o onboarding, gera análise nutricional personalizada e marca como completo
    """
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        # Verificar se já completou o onboarding
        if usuario.onboarding_completo:
            return jsonify({
                'mensagem': 'Onboarding já foi completado',
                'redirect': '/analise-nutricional'
            }), 200
        
        # Obter dados do questionário da requisição
        dados_questionario = request.get_json() or {}
        
        # Preparar dados completos do usuário para análise
        dados_usuario_completos = {
            'nome': usuario.nome,
            'idade': usuario.idade,
            'peso': usuario.peso,
            'altura': usuario.altura,
            'sexo': usuario.sexo,
            'objetivo': usuario.objetivo,
            'fator_atividade': usuario.fator_atividade,
            # Adicionar dados do questionário
            **dados_questionario
        }
        
        # Criar instância personalizada da análise IA
        print(f"Criando análise personalizada para usuário: {usuario.nome}")
        analise_personalizada = criar_analise_personalizada(dados_usuario_completos, modelo_ia)
        
        # Gerar análise completa usando a nova classe modular
        analise_resultado = analise_personalizada.gerar_resultado_completo()
        
        # Salvar dados do questionário no usuário
        if dados_questionario:
            usuario.dados_questionario = json.dumps(dados_questionario)
        
        # Salvar análise no campo correspondente (ou criar tabela específica se necessário)
        usuario.analise_nutricional = json.dumps(analise_resultado)
        
        # Marcar onboarding como completo
        usuario.onboarding_completo = True
        
        # Salvar no banco
        db.session.commit()
        
        print(f"Onboarding finalizado para usuário: {usuario.nome}")
        
        return jsonify({
            'mensagem': 'Onboarding finalizado com sucesso!',
            'analise_gerada': True,
            'redirect': '/analise-nutricional'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao finalizar onboarding: {str(e)}")
        return jsonify({'erro': f'Erro ao finalizar onboarding: {str(e)}'}), 500

@app.route('/analise-nutricional')
@requer_verificacao_email
@requer_onboarding_completo
def pagina_analise_nutricional():
    """
    Página para exibir análise nutricional personalizada
    """
    return render_template('analise_nutricional.html')

@app.route('/api/analise-nutricional')
@jwt_required()
@requer_onboarding_completo
def api_analise_nutricional():
    """
    API que retorna a análise nutricional do usuário
    """
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        # Verificar se tem análise salva
        if not usuario.analise_nutricional:
            # Se não tem análise, gerar uma nova usando a classe modular
            dados_usuario_completos = {
                'nome': usuario.nome,
                'idade': usuario.idade,
                'peso': usuario.peso,
                'altura': usuario.altura,
                'sexo': usuario.sexo,
                'objetivo': usuario.objetivo,
                'fator_atividade': usuario.fator_atividade
            }
            
            # Adicionar dados do questionário se existir
            if usuario.dados_questionario:
                dados_questionario = json.loads(usuario.dados_questionario)
                dados_usuario_completos.update(dados_questionario)
            
            # Criar análise personalizada
            analise_personalizada = criar_analise_personalizada(dados_usuario_completos, modelo_ia)
            analise_resultado = analise_personalizada.gerar_resultado_completo()
            
            # Salvar nova análise
            usuario.analise_nutricional = json.dumps(analise_resultado)
            db.session.commit()
            
            return jsonify(analise_resultado)
        
        # Retornar análise existente
        analise = json.loads(usuario.analise_nutricional)
        return jsonify(analise)
        
    except Exception as e:
        print(f"Erro ao carregar análise: {str(e)}")
        return jsonify({'erro': 'Erro ao carregar análise'}), 500

@app.route('/api/regenerar-analise', methods=['POST'])
@jwt_required()
@requer_onboarding_completo
def regenerar_analise_nutricional():
    """
    Regenera a análise nutricional com novos dados
    """
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        # Obter novos dados do questionário (se fornecidos)
        novos_dados = request.get_json() or {}
        
        # Atualizar dados do questionário se fornecidos
        if novos_dados:
            dados_atuais = {}
            if usuario.dados_questionario:
                dados_atuais = json.loads(usuario.dados_questionario)
            
            dados_atuais.update(novos_dados)
            usuario.dados_questionario = json.dumps(dados_atuais)
        
        # Preparar dados completos para nova análise
        dados_usuario_completos = {
            'nome': usuario.nome,
            'idade': usuario.idade,
            'peso': usuario.peso,
            'altura': usuario.altura,
            'sexo': usuario.sexo,
            'objetivo': usuario.objetivo,
            'fator_atividade': usuario.fator_atividade
        }
        
        # Adicionar dados do questionário atualizado
        if usuario.dados_questionario:
            dados_questionario = json.loads(usuario.dados_questionario)
            dados_usuario_completos.update(dados_questionario)
        
        # Criar nova análise personalizada
        analise_personalizada = criar_analise_personalizada(dados_usuario_completos, modelo_ia)
        nova_analise = analise_personalizada.gerar_resultado_completo()
        
        # Salvar nova análise
        usuario.analise_nutricional = json.dumps(nova_analise)
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Análise regenerada com sucesso!',
            'analise': nova_analise
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao regenerar análise: {str(e)}")
        return jsonify({'erro': 'Erro ao regenerar análise'}), 500

# --- Rota para Calcular Calorias Baseado nos Dados do Usuário ---
@app.route('/api/calcular-calorias', methods=['POST'])
@jwt_required()
def calcular_calorias_usuario():
    """
    Endpoint para calcular calorias baseado nos dados do usuário e objetivo
    Aceita: objetivo (string)
    Retorna: JSON com TMB, GET e calorias objetivo
    """
    try:
        # Obter ID do usuário do token JWT
        user_id = get_jwt_identity()
        
        # Buscar usuário no banco de dados
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        # Obter dados da requisição
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados não fornecidos'}), 400
        
        objetivo = data.get('objetivo')
        if not objetivo:
            return jsonify({'erro': 'Objetivo é obrigatório'}), 400
        
        # Verificar se o usuário tem dados suficientes para cálculo
        if not all([usuario.idade, usuario.sexo, usuario.peso, usuario.altura]):
            return jsonify({'erro': 'Dados do perfil incompletos. Complete seu perfil primeiro.'}), 400
        
        # Calcular TMB (Taxa Metabólica Basal) usando fórmula de Harris-Benedict
        if usuario.sexo.lower() == 'masculino':
            # TMB homens = 88.362 + (13.397 × peso) + (4.799 × altura) - (5.677 × idade)
            tmb = 88.362 + (13.397 * usuario.peso) + (4.799 * usuario.altura) - (5.677 * usuario.idade)
        else:
            # TMB mulheres = 447.593 + (9.247 × peso) + (3.098 × altura) - (4.330 × idade)
            tmb = 447.593 + (9.247 * usuario.peso) + (3.098 * usuario.altura) - (4.330 * usuario.idade)
        
        # Aplicar fator de atividade física
        fator_atividade = usuario.fator_atividade or 1.55  # Padrão moderadamente ativo
        get = tmb * float(fator_atividade)  # Gasto Energético Total
        
        # Aplicar fator baseado no objetivo
        fatores_objetivo = {
            'perder_peso': 0.8,      # Déficit de 20%
            'manter_peso': 1.0,      # Manutenção
            'ganhar_peso': 1.15,     # Superávit de 15%
            'ganhar_massa': 1.2,     # Superávit de 20%
            'vida_saudavel': 1.0,    # Manutenção
            'performance': 1.1       # Superávit de 10%
        }
        
        fator_objetivo = fatores_objetivo.get(objetivo, 1.0)
        calorias_objetivo = round(get * fator_objetivo)
        
        # Retornar dados calculados
        return jsonify({
            'tmb': round(tmb),
            'get': round(get),
            'fator_atividade': float(fator_atividade),
            'objetivo': objetivo,
            'fator_objetivo': fator_objetivo,
            'calorias_objetivo': calorias_objetivo,
            'dados_usuario': {
                'idade': usuario.idade,
                'sexo': usuario.sexo,
                'peso': usuario.peso,
                'altura': usuario.altura
            }
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao calcular calorias: {str(e)}'}), 500

# --- Rota para Salvar Objetivo do Usuário (Passo 3 do Onboarding) ---
@app.route('/api/usuario/objetivo', methods=['PUT'])
@jwt_required()
def salvar_objetivo_usuario():
    """
    Endpoint para salvar o objetivo do usuário no onboarding
    Aceita: objetivo
    Retorna: JSON com mensagem de sucesso ou erro
    """
    # Obter ID do usuário logado através do token JWT
    user_id = get_jwt_identity()
    
    # Extrair dados do JSON da requisição
    data = request.get_json()
    if not data:
        return jsonify({'erro': 'Dados são obrigatórios!'}), 400
    
    # Extrair objetivo do JSON
    objetivo = data.get('objetivo')
    if not objetivo:
        return jsonify({'erro': 'Campo objetivo é obrigatório!'}), 400
    
    # Validação dos objetivos permitidos
    objetivos_validos = [
        'perder_peso',
        'manter_peso',
        'ganhar_peso',
        'ganhar_massa',
        'vida_saudavel',
        'performance'
    ]
    
    if objetivo not in objetivos_validos:
        return jsonify({'erro': 'Objetivo inválido'}), 400
    
    try:
        # Buscar usuário no banco de dados
        usuario = Usuario.query.get(int(user_id))
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        # Atualizar campo objetivo
        usuario.objetivo = objetivo
        
        # Persistir alterações no banco de dados
        db.session.commit()
        
        return jsonify({'mensagem': 'Objetivo salvo com sucesso'}), 200
        
    except Exception as e:
        # Em caso de erro, desfaz a transação
        db.session.rollback()
        return jsonify({'erro': 'Ocorreu um erro interno ao salvar o objetivo'}), 500

# --- Rota para Salvar Preferências Alimentares (Passo 4 do Onboarding) ---
@app.route('/api/onboarding/preferencias', methods=['POST'])
@jwt_required()
def salvar_preferencias_usuario():
    """
    Endpoint para salvar as preferências alimentares do usuário no onboarding
    Aceita: alimentos_evitar, restricoes, estilo_alimentar
    Retorna: JSON com mensagem de sucesso ou erro
    """
    try:
        # Obter ID do usuário logado através do token JWT
        user_id = get_jwt_identity()
        
        # Extrair dados do JSON da requisição
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados são obrigatórios!'}), 400
        
        # Extrair campos do JSON
        alimentos_evitar = data.get('alimentos_evitar', '').strip()
        restricoes = data.get('restricoes', [])
        estilo_alimentar = data.get('estilo_alimentar', '').strip()
        
        # Validação dos dados
        if not isinstance(restricoes, list):
            return jsonify({'erro': 'Restrições devem ser uma lista'}), 400
        
        if not estilo_alimentar:
            return jsonify({'erro': 'Estilo alimentar é obrigatório'}), 400
        
        # Validar restrições permitidas
        restricoes_validas = [
            'lactose', 'gluten', 'diabetes', 'hipertensao', 'alergia_nozes', 'nenhuma'
        ]
        
        for restricao in restricoes:
            if restricao not in restricoes_validas:
                return jsonify({'erro': f'Restrição inválida: {restricao}'}), 400
        
        # Validar estilos alimentares permitidos
        estilos_validos = [
            'tradicional', 'vegetariano', 'vegano', 'low_carb', 
            'jejum_intermitente', 'mediterranea'
        ]
        
        if estilo_alimentar not in estilos_validos:
            return jsonify({'erro': 'Estilo alimentar inválido'}), 400
        
        # Buscar usuário no banco de dados
        usuario = Usuario.query.get(int(user_id))
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        # Verificar se já existem preferências para este usuário
        preferencias_existentes = PreferenciasUsuario.query.filter_by(usuario_id=int(user_id)).first()
        
        if preferencias_existentes:
            # Atualizar preferências existentes
            preferencias_existentes.alimentos_evitar = alimentos_evitar
            preferencias_existentes.restricoes = restricoes
            preferencias_existentes.estilo_alimentar = estilo_alimentar
            preferencias_existentes.updated_at = datetime.utcnow()
            
            print(f"🔄 Atualizando preferências existentes do usuário {user_id}")
        else:
            # Criar novas preferências
            novas_preferencias = PreferenciasUsuario(
                usuario_id=int(user_id),
                alimentos_evitar=alimentos_evitar,
                restricoes=restricoes,
                estilo_alimentar=estilo_alimentar
            )
            
            db.session.add(novas_preferencias)
            print(f"✨ Criando novas preferências para usuário {user_id}")
        
        # Persistir alterações no banco de dados
        db.session.commit()
        
        print(f"✅ Preferências salvas: Usuário {user_id} - Estilo: {estilo_alimentar} - Restrições: {restricoes}")
        
        return jsonify({
            'mensagem': 'Preferências salvas com sucesso',
            'dados': {
                'alimentos_evitar': alimentos_evitar,
                'restricoes': restricoes,
                'estilo_alimentar': estilo_alimentar
            }
        }), 200
        
    except Exception as e:
        # Em caso de erro, desfaz a transação
        db.session.rollback()
        print(f"❌ Erro ao salvar preferências: {str(e)}")
        return jsonify({'erro': f'Erro interno ao salvar preferências: {str(e)}'}), 500

# --- Rota para Calcular Metas Personalizadas (Passo 5 do Onboarding) ---
@app.route('/api/onboarding/metas', methods=['GET'])
@jwt_required()
def calcular_metas_personalizadas():
    """
    Endpoint para calcular metas personalizadas baseado no perfil completo do usuário
    Retorna: TMB, gasto total, meta calórica e distribuição de macronutrientes
    """
    try:
        # Obter ID do usuário logado através do token JWT
        user_id = get_jwt_identity()
        
        # Buscar usuário no banco de dados
        usuario = Usuario.query.get(int(user_id))
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        # Verificar se o usuário tem dados suficientes
        if not all([usuario.idade, usuario.sexo, usuario.peso, usuario.altura]):
            return jsonify({'erro': 'Dados do perfil incompletos. Complete seu perfil primeiro.'}), 400
        
        if not usuario.fator_atividade:
            return jsonify({'erro': 'Nível de atividade física não definido. Complete o onboarding.'}), 400
        
        if not usuario.objetivo:
            return jsonify({'erro': 'Objetivo nutricional não definido. Complete o onboarding.'}), 400
        
        # === CÁLCULO DA TMB (Taxa Metabólica Basal) ===
        # Fórmula de Mifflin-St Jeor (mais precisa que Harris-Benedict)
        peso = float(usuario.peso)
        altura = float(usuario.altura)
        idade = int(usuario.idade)
        sexo = usuario.sexo.lower()
        
        if sexo == 'masculino':
            # TMB homens = (10 × peso) + (6.25 × altura) - (5 × idade) + 5
            tmb = (10 * peso) + (6.25 * altura) - (5 * idade) + 5
        else:
            # TMB mulheres = (10 × peso) + (6.25 × altura) - (5 × idade) - 161
            tmb = (10 * peso) + (6.25 * altura) - (5 * idade) - 161
        
        # === GASTO ENERGÉTICO TOTAL ===
        fator_atividade = float(usuario.fator_atividade)
        gasto_total = tmb * fator_atividade
        
        # === AJUSTE POR OBJETIVO ===
        objetivo = usuario.objetivo.lower()
        
        # Mapear objetivos para ajustes calóricos
        ajustes_caloricos = {
            'perder_peso': -500,      # Déficit de 500 kcal
            'emagrecer': -500,        # Alias para perder_peso
            'manter_peso': 0,         # Manutenção
            'manter': 0,              # Alias para manter_peso
            'vida_saudavel': 0,       # Manutenção
            'ganhar_peso': +400,      # Superávit de 400 kcal
            'ganhar_massa': +500,     # Superávit de 500 kcal
            'performance': +300       # Superávit leve de 300 kcal
        }
        
        ajuste = ajustes_caloricos.get(objetivo, 0)
        meta_calorica = round(gasto_total + ajuste)
        
        # === DISTRIBUIÇÃO DE MACRONUTRIENTES ===
        # Percentuais padrão recomendados
        perc_proteina = 0.25    # 25% das calorias
        perc_carboidrato = 0.50 # 50% das calorias
        perc_gordura = 0.25     # 25% das calorias
        
        # Ajustes baseados no objetivo
        if objetivo in ['ganhar_massa', 'performance']:
            # Mais proteína para ganho de massa
            perc_proteina = 0.30
            perc_carboidrato = 0.45
            perc_gordura = 0.25
        elif objetivo in ['perder_peso', 'emagrecer']:
            # Mais proteína para preservar massa muscular
            perc_proteina = 0.35
            perc_carboidrato = 0.40
            perc_gordura = 0.25
        
        # Calcular gramas de macronutrientes
        # Proteína e carboidrato: 4 kcal/g
        # Gordura: 9 kcal/g
        calorias_proteina = meta_calorica * perc_proteina
        calorias_carboidrato = meta_calorica * perc_carboidrato
        calorias_gordura = meta_calorica * perc_gordura
        
        proteina_g = round(calorias_proteina / 4, 1)
        carboidrato_g = round(calorias_carboidrato / 4, 1)
        gordura_g = round(calorias_gordura / 9, 1)
        
        # === BUSCAR PREFERÊNCIAS ALIMENTARES ===
        preferencias = None
        try:
            preferencias = PreferenciasUsuario.query.filter_by(usuario_id=int(user_id)).first()
        except:
            pass  # Preferências são opcionais
        
        # === MONTAR RESPOSTA ===
        resultado = {
            'usuario_info': {
                'nome': usuario.nome,
                'idade': usuario.idade,
                'sexo': usuario.sexo,
                'peso': usuario.peso,
                'altura': usuario.altura,
                'objetivo': usuario.objetivo,
                'fator_atividade': usuario.fator_atividade
            },
            'calculos': {
                'tmb': round(tmb),
                'gasto_total': round(gasto_total),
                'ajuste_calorico': ajuste,
                'meta_calorica': meta_calorica
            },
            'macronutrientes': {
                'proteina_g': proteina_g,
                'proteina_kcal': round(calorias_proteina),
                'proteina_perc': round(perc_proteina * 100),
                'carboidrato_g': carboidrato_g,
                'carboidrato_kcal': round(calorias_carboidrato),
                'carboidrato_perc': round(perc_carboidrato * 100),
                'gordura_g': gordura_g,
                'gordura_kcal': round(calorias_gordura),
                'gordura_perc': round(perc_gordura * 100)
            },
            'resumo': {
                'total_calorias': meta_calorica,
                'total_proteina': proteina_g,
                'total_carboidrato': carboidrato_g,
                'total_gordura': gordura_g
            },
            'preferencias': {
                'estilo_alimentar': preferencias.estilo_alimentar if preferencias else None,
                'restricoes': preferencias.restricoes if preferencias else [],
                'alimentos_evitar': preferencias.alimentos_evitar if preferencias else None
            } if preferencias else None
        }
        
        print(f"✅ Metas calculadas para usuário {user_id}: {meta_calorica} kcal")
        print(f"📊 Macros: P:{proteina_g}g C:{carboidrato_g}g G:{gordura_g}g")
        
        return jsonify(resultado), 200
        
    except Exception as e:
        print(f"❌ Erro ao calcular metas: {str(e)}")
        return jsonify({'erro': f'Erro interno ao calcular metas: {str(e)}'}), 500

# Rota para registrar um novo usuário (exemplo)
@app.route('/api/usuarios/registrar', methods=['POST'])
def registrar_usuario_api():
    data = request.get_json()

    if not data or not 'nome' in data or not 'email' in data or not 'senha' in data:
        return jsonify({'message': 'Campos nome, email e senha são obrigatórios!'}), 400

    nome = data['nome']
    email = data['email']
    senha = data['senha']

    # Verifica se o email ou username já existem
    if Usuario.query.filter((Usuario.email == email) | (Usuario.username == email)).first():
        return jsonify({'message': 'Este email já está em uso.'}), 409

    try:
        # Gera o hash da senha
        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

        # Cria o novo usuário usando o ORM
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            username=email,  # Usando email como username
            password=senha_hash
        )

        # Adiciona e salva no banco de dados
        db.session.add(novo_usuario)
        db.session.commit()

        return jsonify({'message': f'Usuário {nome} registrado com sucesso!'}), 201

    except Exception as e:
        # Em caso de erro, desfaz a transação
        db.session.rollback()
        return jsonify({'message': f'Erro ao registrar usuário: {str(e)}'}), 500

# --- Rotas para Alimentos ---

# Rota para Adicionar um Novo Alimento
@app.route('/alimentos', methods=['POST'])
def adicionar_alimento():
    data = request.get_json()

    if not data or not 'nome' in data or not 'calorias' in data or \
       not 'proteinas' in data or not 'carboidratos' in data or not 'gorduras' in data:
        return jsonify({'message': 'Todos os campos obrigatórios (nome, calorias, proteinas, carboidratos, gorduras) são necessários!'}), 400

    nome = data['nome']
    categoria = data.get('categoria', 'Outros')
    calorias = data['calorias']
    proteinas = data['proteinas']
    carboidratos = data['carboidratos']
    gorduras = data['gorduras']
    fibras = data.get('fibras', 0)
    sodio = data.get('sodio', 0)
    acucar = data.get('acucar', 0)
    colesterol = data.get('colesterol', 0)
    porcao_referencia = data.get('porcao_referencia', '100g')
    fonte_dados = data.get('fonte_dados', 'TACO')

    if Alimento.query.filter_by(nome=nome).first():
        return jsonify({'message': 'Alimento com este nome já existe!'}), 409

    novo_alimento = Alimento(
        nome=nome,
        categoria=categoria,
        calorias=calorias,
        proteinas=proteinas,
        carboidratos=carboidratos,
        gorduras=gorduras,
        fibras=fibras,
        sodio=sodio,
        acucar=acucar,
        colesterol=colesterol,
        porcao_referencia=porcao_referencia,
        fonte_dados=fonte_dados
    )

    try:
        db.session.add(novo_alimento)
        db.session.commit()
        return jsonify({
            'message': 'Alimento adicionado com sucesso!',
            'alimento': {
                'id': novo_alimento.id,
                'nome': novo_alimento.nome,
                'calorias': novo_alimento.calorias,
                'proteinas': novo_alimento.proteinas,
                'carboidratos': novo_alimento.carboidratos,
                'gorduras': novo_alimento.gorduras
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao adicionar alimento: {str(e)}'}), 500

# Rota para Listar Todos os Alimentos
@app.route('/alimentos', methods=['GET'])
def listar_alimentos():
    alimentos = Alimento.query.all()
    resultado = []
    for alimento in alimentos:
        resultado.append({
            'id': alimento.id,
            'nome': alimento.nome,
            'calorias': alimento.calorias,
            'proteinas': alimento.proteinas,
            'carboidratos': alimento.carboidratos,
            'gorduras': alimento.gorduras
        })
    return jsonify(resultado), 200

# Rota para Busca Inteligente de Alimentos
@app.route('/api/alimentos/buscar', methods=['GET'])
def buscar_alimentos():
    # Obter termo de busca do query parameter
    termo_busca = request.args.get('q', '').strip()
    
    # Validação: se termo não existe ou tem menos de 2 caracteres, retorna lista vazia
    if not termo_busca or len(termo_busca) < 2:
        return jsonify([])
    
    # Função para remover acentos manualmente
    def remover_acentos(texto):
        return unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('ascii')
    
    # Normalizar termo de busca (converter para minúsculas e remover acentos)
    termo_normalizado = remover_acentos(termo_busca.lower())
    
    try:
        # Primeira tentativa: busca com unaccent (PostgreSQL)
        alimentos = Alimento.query.filter(
            func.unaccent(func.lower(Alimento.nome)).ilike(f'%{termo_normalizado}%')
        ).order_by(
            # Prioridade 1: nomes que começam com o termo de busca
            func.unaccent(func.lower(Alimento.nome)).ilike(f'{termo_normalizado}%').desc(),
            # Prioridade 2: ordem alfabética
            Alimento.nome.asc()
        ).all()
        
    except Exception as e:
        # Fallback: busca manual com remoção de acentos em Python
        todos_alimentos = Alimento.query.all()
        alimentos_filtrados = []
        alimentos_iniciados = []
        
        for alimento in todos_alimentos:
            nome_sem_acento = remover_acentos(alimento.nome.lower())
            if termo_normalizado in nome_sem_acento:
                if nome_sem_acento.startswith(termo_normalizado):
                    alimentos_iniciados.append(alimento)
                else:
                    alimentos_filtrados.append(alimento)
        
        # Ordenar por relevância: que começam com o termo primeiro
        alimentos = alimentos_iniciados + alimentos_filtrados
    
    # Construir lista de resultados
    resultado = []
    for alimento in alimentos:
        resultado.append({
            'id': alimento.id,
            'nome': alimento.nome,
            'calorias': alimento.calorias,
            'proteinas': alimento.proteinas,
            'carboidratos': alimento.carboidratos,
            'gorduras': alimento.gorduras
        })
    
    return jsonify(resultado), 200

# --- Rotas para Receitas ---

# Rota para Adicionar uma Nova Receita
@app.route('/receitas', methods=['POST'])
def adicionar_receita():
    data = request.get_json()

    if not data or not 'nome' in data or not 'tipo_refeicao' in data or not 'ingredientes' in data:
        return jsonify({'message': 'Nome da receita, tipo de refeição e ingredientes são obrigatórios!'}), 400

    nome_receita = data['nome']
    descricao_receita = data.get('descricao', '')
    tipo_refeicao = data['tipo_refeicao']
    ingredientes_json = data['ingredientes']

    if Receita.query.filter_by(nome=nome_receita).first():
        return jsonify({'message': 'Receita com este nome já existe!'}), 409

    nova_receita = Receita(
        nome=nome_receita,
        descricao=descricao_receita,
        tipo_refeicao=tipo_refeicao
    )

    try:
        db.session.add(nova_receita)
        db.session.commit()

        for item in ingredientes_json:
            alimento_id = item.get('alimento_id')
            quantidade = item.get('quantidade_gramas')

            if not alimento_id or not quantidade:
                db.session.rollback()
                return jsonify({'message': 'Ingredientes devem ter alimento_id e quantidade_gramas!'}), 400

            alimento_existente = Alimento.query.get(alimento_id)
            if not alimento_existente:
                db.session.rollback()
                return jsonify({'message': f'Alimento com ID {alimento_id} não encontrado!'}), 404

            receita_alimento = ReceitaAlimento(
                receita_id=nova_receita.id,
                alimento_id=alimento_id,
                quantidade_gramas=quantidade
            )
            db.session.add(receita_alimento)
        db.session.commit()

        return jsonify({
            'message': 'Receita adicionada com sucesso!',
            'receita_id': nova_receita.id,
            'nome': nova_receita.nome,
            'tipo_refeicao': nova_receita.tipo_refeicao
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao adicionar receita: {str(e)}'}), 500

# Rota para Listar Todas as Receitas (com seus ingredientes)
@app.route('/receitas', methods=['GET'])
def listar_receitas():
    receitas = Receita.query.all()
    resultado = []
    for receita in receitas:
        ingredientes_da_receita = []
        for ra in receita.alimentos:
            alimento = Alimento.query.get(ra.alimento_id)
            if alimento:
                ingredientes_da_receita.append({
                    'alimento_id': alimento.id,
                    'nome_alimento': alimento.nome,
                    'quantidade_gramas': ra.quantidade_gramas,
                    'calorias_por_porcao': (alimento.calorias / 100) * ra.quantidade_gramas if alimento.calorias else 0
                })

        resultado.append({
            'id': receita.id,
            'nome': receita.nome,
            'descricao': receita.descricao,
            'tipo_refeicao': receita.tipo_refeicao,
            'ingredientes': ingredientes_da_receita
        })
    return jsonify(resultado), 200

# --- Rotas para Registros Alimentares ---

# Rota para adicionar um registro alimentar para um usuário
@app.route('/usuarios/<int:usuario_id>/registros', methods=['POST'])
def adicionar_registro_alimentar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    data = request.get_json()

    if not data or not 'data' in data or not 'tipo_refeicao' in data:
        return jsonify({'message': 'Data e tipo de refeição são obrigatórios!'}), 400

    # Validação para garantir que ou alimento ou receita foi fornecido, mas não ambos
    alimento_id = data.get('alimento_id')
    receita_id = data.get('receita_id')

    if (alimento_id and receita_id) or (not alimento_id and not receita_id):
        return jsonify({'message': 'Forneça um alimento_id OU uma receita_id, mas não ambos.'}), 400

    try:
        data_registro = date.fromisoformat(data['data'])
    except (ValueError, TypeError):
        return jsonify({'message': 'Formato de data inválido. Use AAAA-MM-DD.'}), 400

    novo_registro = RegistroAlimentar(
        usuario_id=usuario.id,
        data=data_registro,
        tipo_refeicao=data['tipo_refeicao']
    )

    if alimento_id:
        alimento = Alimento.query.get(alimento_id)
        if not alimento:
            return jsonify({'message': f'Alimento com ID {alimento_id} não encontrado!'}), 404
        if not 'quantidade_gramas' in data:
            return jsonify({'message': 'Quantidade em gramas é obrigatória para alimentos.'}), 400
        
        novo_registro.alimento_id = alimento_id
        novo_registro.quantidade_gramas = data['quantidade_gramas']
    
    if receita_id:
        receita = Receita.query.get(receita_id)
        if not receita:
            return jsonify({'message': f'Receita com ID {receita_id} não encontrada!'}), 404
        
        novo_registro.receita_id = receita_id

    try:
        db.session.add(novo_registro)
        db.session.commit()
        return jsonify({'message': 'Registro alimentar adicionado com sucesso!', 'registro_id': novo_registro.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao adicionar registro: {str(e)}'}), 500

# Rota para listar os registros alimentares de um usuário
@app.route('/usuarios/<int:usuario_id>/registros', methods=['GET'])
def listar_registros_alimentares(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    registros = RegistroAlimentar.query.filter_by(usuario_id=usuario.id).order_by(RegistroAlimentar.data.desc()).all()
    
    resultado = []
    for registro in registros:
        detalhe = {
            'id': registro.id,
            'data': registro.data.isoformat(),
            'tipo_refeicao': registro.tipo_refeicao,
        }
        if registro.alimento_id:
            detalhe['alimento_id'] = registro.alimento_id
            detalhe['nome_alimento'] = registro.alimento.nome
            detalhe['quantidade_gramas'] = registro.quantidade_gramas
        if registro.receita_id:
            detalhe['receita_id'] = registro.receita_id
            detalhe['nome_receita'] = registro.receita.nome

        resultado.append(detalhe)
        
    return jsonify(resultado), 200

# --- Rota de teste para verificação ---
@app.route('/api/teste', methods=['GET'])
def teste():
    return jsonify({'status': 'ok', 'mensagem': 'API está rodando!', 'arquivo': __file__}), 200

@app.route('/api/diagnostico-db', methods=['GET'])
def diagnostico_banco():
    """Diagnóstico do banco de dados"""
    try:
        # Testa conexão com banco
        total_usuarios = Usuario.query.count()
        
        # Verifica se as tabelas existem
        tabelas_info = {}
        try:
            tabelas_info['usuarios'] = Usuario.query.count()
        except Exception as e:
            tabelas_info['usuarios'] = f"Erro: {str(e)}"
            
        try:
            from app import Lead
            tabelas_info['leads'] = Lead.query.count()
        except Exception as e:
            tabelas_info['leads'] = f"Erro: {str(e)}"
        
        return jsonify({
            'status': 'ok',
            'banco_conectado': True,
            'total_usuarios': total_usuarios,
            'tabelas': tabelas_info,
            'database_url': 'PostgreSQL' if os.getenv('DATABASE_URL') else 'SQLite Local'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'erro',
            'banco_conectado': False,
            'erro': str(e),
            'database_url': 'PostgreSQL' if os.getenv('DATABASE_URL') else 'SQLite Local'
        }), 500

# === DEMO SISTEMA DE USUÁRIOS ===

@app.route('/demo-usuarios')
def demo_usuarios():
    """
    Página de demonstração do sistema de usuários
    Mostra como cada usuário tem acesso isolado aos seus dados
    """
    return render_template('demo_usuarios.html')

@app.route('/diario-alimentar')
def diario_alimentar():
    """
    Diário Alimentar - Interface para registrar refeições diárias
    """
    return render_template('diario_alimentar.html')

# === ENDPOINT API DIÁRIO ALIMENTAR ===

@app.route('/api/diario', methods=['POST'])
@jwt_required()
def adicionar_ao_diario():
    """
    Endpoint para adicionar alimento ao diário do usuário
    Requer autenticação JWT
    Aceita campo opcional 'data' no formato YYYY-MM-DD
    """
    try:
        # Obter user_id do token JWT
        user_id = get_jwt_identity()
        
        # Extrair dados do JSON
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados JSON são obrigatórios'}), 400
        
        # Validar campos obrigatórios
        alimento_id = data.get('alimento_id')
        quantidade = data.get('quantidade')
        refeicao = data.get('refeicao')
        data_registro = data.get('data')  # Campo opcional
        
        if not alimento_id:
            return jsonify({'erro': 'Campo alimento_id é obrigatório'}), 400
        
        if not quantidade or quantidade <= 0:
            return jsonify({'erro': 'Campo quantidade deve ser maior que zero'}), 400
        
        if not refeicao:
            return jsonify({'erro': 'Campo refeicao é obrigatório'}), 400
        
        # Validar se alimento existe
        alimento = Alimento.query.get(alimento_id)
        if not alimento:
            return jsonify({'erro': 'Alimento não encontrado'}), 404
        
        # Processar data do registro
        from datetime import datetime
        if data_registro:
            try:
                # Converter string YYYY-MM-DD para objeto date
                data_final = datetime.strptime(data_registro, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        else:
            # Usar data atual se não fornecida
            data_final = date.today()
        
        # Criar novo registro no diário
        novo_registro = RegistroAlimentar(
            usuario_id=user_id,
            alimento_id=alimento_id,
            quantidade_gramas=quantidade,
            tipo_refeicao=refeicao,
            data=data_final
        )
        
        # Persistir no banco de dados
        db.session.add(novo_registro)
        db.session.commit()
        
        # Retornar resposta de sucesso com dados do registro
        return jsonify({
            'mensagem': 'Alimento adicionado ao diário com sucesso',
            'registro': {
                'id': novo_registro.id,
                'usuario_id': novo_registro.usuario_id,
                'alimento_id': novo_registro.alimento_id,
                'alimento_nome': alimento.nome,
                'quantidade': novo_registro.quantidade_gramas,
                'refeicao': novo_registro.tipo_refeicao,
                'data_entrada': novo_registro.data.strftime('%Y-%m-%d'),
                'calorias_calculadas': round((alimento.calorias * quantidade / 100), 2),
                'proteinas_calculadas': round((alimento.proteinas * quantidade / 100), 2),
                'carboidratos_calculados': round((alimento.carboidratos * quantidade / 100), 2),
                'gorduras_calculadas': round((alimento.gorduras * quantidade / 100), 2)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

# === ENDPOINT API DIÁRIO ALIMENTAR - LISTAR REGISTROS ===

@app.route('/api/diario', methods=['GET'])
@jwt_required()
def obter_diario():
    """
    Endpoint para obter registros do diário do usuário autenticado
    Aceita parâmetro opcional 'data' no formato YYYY-MM-DD
    Se não fornecida, retorna registros do dia atual
    """
    try:
        # Obter user_id do token JWT
        user_id = get_jwt_identity()
        
        # Obter parâmetro de data da query string
        data_param = request.args.get('data')
        
        # Processar data do filtro
        from datetime import datetime
        if data_param:
            try:
                # Converter string YYYY-MM-DD para objeto date
                data_filtro = datetime.strptime(data_param, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        else:
            # Usar data atual se não fornecida
            data_filtro = date.today()
        
        # Buscar registros do usuário para a data especificada
        registros = RegistroAlimentar.query.filter_by(
            usuario_id=user_id,
            data=data_filtro
        ).all()
        
        # Converter registros para lista de dicionários usando to_dict()
        registros_json = []
        for registro in registros:
            # Usar o método to_dict() que criamos
            registro_dict = registro.to_dict()
            
            # Adicionar cálculos nutricionais
            if registro.alimento:
                quantidade = registro.quantidade_gramas
                alimento = registro.alimento
                registro_dict['calorias_calculadas'] = round((alimento.calorias * quantidade / 100), 2)
                registro_dict['proteinas_calculadas'] = round((alimento.proteinas * quantidade / 100), 2)
                registro_dict['carboidratos_calculados'] = round((alimento.carboidratos * quantidade / 100), 2)
                registro_dict['gorduras_calculadas'] = round((alimento.gorduras * quantidade / 100), 2)
            else:
                registro_dict['calorias_calculadas'] = 0
                registro_dict['proteinas_calculadas'] = 0
                registro_dict['carboidratos_calculados'] = 0
                registro_dict['gorduras_calculadas'] = 0
            
            registros_json.append(registro_dict)
        
        # Organizar registros por tipo de refeição
        diario_organizado = {
            'data': data_filtro.strftime('%Y-%m-%d'),
            'total_registros': len(registros),
            'refeicoes': {
                'cafe_manha': [],
                'almoco': [],
                'lanche': [],
                'jantar': []
            },
            'totais_dia': {
                'calorias': 0,
                'proteinas': 0,
                'carboidratos': 0,
                'gorduras': 0
            }
        }
        
        # Distribuir registros por refeição e calcular totais
        for registro in registros_json:
            tipo_refeicao = registro['tipo_refeicao'].lower()
            
            # Mapear tipos de refeição
            if tipo_refeicao in ['cafe_manha', 'café_manhã', 'cafe da manha']:
                diario_organizado['refeicoes']['cafe_manha'].append(registro)
            elif tipo_refeicao in ['almoco', 'almoço']:
                diario_organizado['refeicoes']['almoco'].append(registro)
            elif tipo_refeicao in ['lanche', 'lanche_tarde', 'lanche da tarde']:
                diario_organizado['refeicoes']['lanche'].append(registro)
            elif tipo_refeicao in ['jantar', 'janta']:
                diario_organizado['refeicoes']['jantar'].append(registro)
            else:
                # Se não mapear, adiciona ao lanche por padrão
                diario_organizado['refeicoes']['lanche'].append(registro)
            
            # Somar totais do dia
            diario_organizado['totais_dia']['calorias'] += registro.get('calorias_calculadas', 0)
            diario_organizado['totais_dia']['proteinas'] += registro.get('proteinas_calculadas', 0)
            diario_organizado['totais_dia']['carboidratos'] += registro.get('carboidratos_calculados', 0)
            diario_organizado['totais_dia']['gorduras'] += registro.get('gorduras_calculadas', 0)
        
        # Arredondar totais
        for nutriente in diario_organizado['totais_dia']:
            diario_organizado['totais_dia'][nutriente] = round(diario_organizado['totais_dia'][nutriente], 2)
        
        return jsonify(diario_organizado), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

# === ENDPOINT API DIÁRIO ALIMENTAR - DELETAR REGISTRO ===

@app.route('/api/diario/<int:registro_id>', methods=['DELETE'])
@jwt_required()
def deletar_registro_diario(registro_id):
    """
    Endpoint para deletar um registro específico do diário alimentar
    Requer autenticação JWT e valida se o registro pertence ao usuário
    
    Args:
        registro_id (int): ID do registro a ser deletado
    
    Returns:
        JSON: Mensagem de sucesso ou erro
    """
    try:
        # Obter user_id do token JWT
        user_id = get_jwt_identity()
        
        # Buscar o registro no banco de dados
        registro = RegistroAlimentar.query.filter_by(
            id=registro_id,
            usuario_id=user_id
        ).first()
        
        # Verificar se o registro existe e pertence ao usuário
        if not registro:
            return jsonify({
                'erro': 'Registro não encontrado ou você não tem permissão para deletá-lo'
            }), 404
        
        # Obter informações do registro antes de deletar (para resposta)
        registro_info = {
            'id': registro_id,
            'alimento_nome': registro.alimento.nome if registro.alimento else 'N/A',
            'quantidade': registro.quantidade_gramas,
            'tipo_refeicao': registro.tipo_refeicao
        }
        
        # Deletar o registro
        db.session.delete(registro)
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Registro deletado com sucesso',
            'registro_deletado': registro_info
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

# === ENDPOINT API DIÁRIO ALIMENTAR - EDITAR REGISTRO ===

@app.route('/api/diario/<int:registro_id>', methods=['PUT'])
@jwt_required()
def editar_registro_diario(registro_id):
    """
    Endpoint para editar um registro específico do diário alimentar
    Permite alterar quantidade e/ou alimento
    
    Args:
        registro_id (int): ID do registro a ser editado
    
    Body JSON:
        alimento_id (int, opcional): Novo ID do alimento
        quantidade_gramas (float, opcional): Nova quantidade em gramas
        tipo_refeicao (str, opcional): Novo tipo de refeição
    
    Returns:
        JSON: Registro atualizado ou erro
    """
    try:
        # Obter user_id do token JWT
        user_id = get_jwt_identity()
        
        # Obter dados do request
        data = request.get_json()
        if not data:
            return jsonify({'erro': 'Dados são obrigatórios para edição'}), 400
        
        # Buscar o registro no banco de dados
        registro = RegistroAlimentar.query.filter_by(
            id=registro_id,
            usuario_id=user_id
        ).first()
        
        # Verificar se o registro existe e pertence ao usuário
        if not registro:
            return jsonify({
                'erro': 'Registro não encontrado ou você não tem permissão para editá-lo'
            }), 404
        
        # Validar e atualizar campos
        campos_atualizados = []
        
        # Atualizar alimento se fornecido
        if 'alimento_id' in data:
            novo_alimento_id = data['alimento_id']
            alimento = Alimento.query.get(novo_alimento_id)
            if not alimento:
                return jsonify({'erro': 'Alimento não encontrado'}), 404
            registro.alimento_id = novo_alimento_id
            campos_atualizados.append('alimento')
        
        # Atualizar quantidade se fornecida
        if 'quantidade_gramas' in data:
            nova_quantidade = data['quantidade_gramas']
            if not isinstance(nova_quantidade, (int, float)) or nova_quantidade <= 0:
                return jsonify({'erro': 'Quantidade deve ser um número positivo'}), 400
            registro.quantidade_gramas = nova_quantidade
            campos_atualizados.append('quantidade')
        
        # Atualizar tipo de refeição se fornecido
        if 'tipo_refeicao' in data:
            novo_tipo = data['tipo_refeicao']
            tipos_validos = ['cafe_manha', 'almoco', 'lanche', 'jantar']
            if novo_tipo not in tipos_validos:
                return jsonify({'erro': f'Tipo de refeição deve ser um de: {tipos_validos}'}), 400
            registro.tipo_refeicao = novo_tipo
            campos_atualizados.append('tipo_refeicao')
        
        # Verificar se pelo menos um campo foi atualizado
        if not campos_atualizados:
            return jsonify({'erro': 'Nenhum campo válido fornecido para atualização'}), 400
        
        # Salvar alterações
        db.session.commit()
        
        # Preparar resposta com dados atualizados
        registro_atualizado = {
            'id': registro.id,
            'alimento_id': registro.alimento_id,
            'alimento_nome': registro.alimento.nome if registro.alimento else 'N/A',
            'quantidade_gramas': registro.quantidade_gramas,
            'tipo_refeicao': registro.tipo_refeicao,
            'data': registro.data.isoformat(),
            'calorias_calculadas': (registro.alimento.calorias * registro.quantidade_gramas / 100) if registro.alimento else 0,
            'proteinas_calculadas': (registro.alimento.proteinas * registro.quantidade_gramas / 100) if registro.alimento and registro.alimento.proteinas else 0,
            'carboidratos_calculados': (registro.alimento.carboidratos * registro.quantidade_gramas / 100) if registro.alimento and registro.alimento.carboidratos else 0,
            'gorduras_calculadas': (registro.alimento.gorduras * registro.quantidade_gramas / 100) if registro.alimento and registro.alimento.gorduras else 0
        }
        
        return jsonify({
            'mensagem': 'Registro atualizado com sucesso',
            'registro': registro_atualizado,
            'campos_atualizados': campos_atualizados
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

# === ENDPOINT API DIÁRIO ALIMENTAR - DIAS PREENCHIDOS ===

@app.route('/api/diario/dias-preenchidos', methods=['GET'])
@jwt_required()
def dias_preenchidos_mes():
    """
    Endpoint para obter os dias do mês em que o usuário tem registros no diário
    
    Query Parameters:
        mes (str): Mês no formato YYYY-MM (ex: 2025-07)
    
    Returns:
        JSON: Lista de dias (números) com registros no mês
    """
    try:
        # Obter user_id do token JWT
        user_id = get_jwt_identity()
        
        # Obter parâmetro do mês
        mes_param = request.args.get('mes')
        if not mes_param:
            return jsonify({'erro': 'Parâmetro "mes" é obrigatório (formato: YYYY-MM)'}), 400
        
        # Validar formato do mês
        try:
            ano, mes = mes_param.split('-')
            ano = int(ano)
            mes = int(mes)
            if mes < 1 or mes > 12:
                raise ValueError("Mês inválido")
        except (ValueError, IndexError):
            return jsonify({'erro': 'Formato de mês inválido. Use YYYY-MM (ex: 2025-07)'}), 400
        
        # Criar data de início e fim do mês
        from datetime import datetime, timedelta
        import calendar
        
        data_inicio = datetime(ano, mes, 1)
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        data_fim = datetime(ano, mes, ultimo_dia, 23, 59, 59)
        
        # Buscar registros do usuário no mês
        registros = RegistroAlimentar.query.filter(
            RegistroAlimentar.usuario_id == user_id,
            RegistroAlimentar.data >= data_inicio.date(),
            RegistroAlimentar.data <= data_fim.date()
        ).all()
        
        # Extrair dias únicos
        dias_com_registros = set()
        for registro in registros:
            dias_com_registros.add(registro.data.day)
        
        # Converter para lista ordenada
        dias_lista = sorted(list(dias_com_registros))
        
        return jsonify({
            'mes': mes_param,
            'dias_preenchidos': dias_lista,
            'total_dias': len(dias_lista)
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

# === ENDPOINT API DIÁRIO ALIMENTAR - MACROS DIÁRIOS ===

@app.route('/api/diario/macros', methods=['GET'])
@jwt_required()
def macros_diarios():
    """
    Endpoint para obter macronutrientes consumidos vs metas para uma data específica
    
    Query Parameters:
        data (str): Data no formato YYYY-MM-DD (ex: 2025-07-20)
    
    Returns:
        JSON: Macros consumidos e metas do usuário
    """
    try:
        # Obter user_id do token JWT
        user_id = get_jwt_identity()
        
        # Obter parâmetro da data
        data_param = request.args.get('data')
        if not data_param:
            return jsonify({'erro': 'Parâmetro "data" é obrigatório (formato: YYYY-MM-DD)'}), 400
        
        # Validar formato da data
        try:
            from datetime import datetime
            data_obj = datetime.strptime(data_param, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD (ex: 2025-07-20)'}), 400
        
        # Buscar registros do usuário na data específica
        registros = RegistroAlimentar.query.filter(
            RegistroAlimentar.usuario_id == user_id,
            RegistroAlimentar.data == data_obj
        ).all()
        
        # Calcular totais consumidos
        consumido = {
            'proteina': 0.0,
            'carboidrato': 0.0,
            'gordura': 0.0,
            'calorias': 0.0
        }
        
        for registro in registros:
            if registro.alimento:
                # Calcular valores por grama
                fator_calculo = registro.quantidade_gramas / 100.0
                
                consumido['proteina'] += (registro.alimento.proteinas or 0) * fator_calculo
                consumido['carboidrato'] += (registro.alimento.carboidratos or 0) * fator_calculo
                consumido['gordura'] += (registro.alimento.gorduras or 0) * fator_calculo
                consumido['calorias'] += (registro.alimento.calorias or 0) * fator_calculo
        
        # Arredondar valores consumidos
        for nutriente in consumido:
            consumido[nutriente] = round(consumido[nutriente], 2)
        
        # Buscar metas do usuário (do perfil nutricional)
        perfil = PerfisNutricionais.query.filter_by(user_id=user_id).first()
        
        if perfil:
            # Calcular metas baseadas no perfil
            if perfil.genero == 'masculino':
                tmb = (10 * perfil.peso) + (6.25 * perfil.altura) - (5 * perfil.idade) + 5
            else:
                tmb = (10 * perfil.peso) + (6.25 * perfil.altura) - (5 * perfil.idade) - 161
            
            # Fator de atividade
            fatores_atividade = {
                'sedentario': 1.2,
                'leve': 1.375,
                'moderado': 1.55,
                'intenso': 1.725,
                'muito_intenso': 1.9
            }
            fator = fatores_atividade.get(perfil.nivel_atividade, 1.2)
            gasto_total = tmb * fator
            
            # Ajuste por objetivo
            if perfil.objetivo == 'emagrecimento':
                calorias_meta = gasto_total - 500
                perc_proteina = 0.30
                perc_carboidrato = 0.45
            elif perfil.objetivo == 'ganho_massa':
                calorias_meta = gasto_total + 500
                perc_proteina = 0.25
                perc_carboidrato = 0.50
            else:  # manter peso
                calorias_meta = gasto_total
                perc_proteina = 0.25
                perc_carboidrato = 0.50
            
            # Calcular gramas de macros
            proteina_meta = (calorias_meta * perc_proteina) / 4  # 4 kcal/g
            carboidrato_meta = (calorias_meta * perc_carboidrato) / 4  # 4 kcal/g
            gordura_meta = (calorias_meta * 0.25) / 9  # 9 kcal/g
            
            meta = {
                'proteina': round(proteina_meta, 2),
                'carboidrato': round(carboidrato_meta, 2),
                'gordura': round(gordura_meta, 2),
                'calorias': round(calorias_meta, 2)
            }
        else:
            # Metas padrão se não houver perfil
            meta = {
                'proteina': 100.0,
                'carboidrato': 200.0,
                'gordura': 60.0,
                'calorias': 2000.0
            }
        
        # Calcular percentuais alcançados
        percentuais = {}
        for nutriente in ['proteina', 'carboidrato', 'gordura', 'calorias']:
            if meta[nutriente] > 0:
                percentuais[nutriente] = round((consumido[nutriente] / meta[nutriente]) * 100, 1)
            else:
                percentuais[nutriente] = 0.0
        
        return jsonify({
            'data': data_param,
            'consumido': consumido,
            'meta': meta,
            'percentuais': percentuais,
            'resumo': {
                'total_registros': len(registros),
                'tem_perfil': perfil is not None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

# === ENDPOINTS DO SISTEMA DE BADGES E GAMIFICAÇÃO ===

@app.route('/api/badges/verificar', methods=['POST'])
@jwt_required()
def verificar_badges():
    """
    Verifica e concede badges baseadas na atividade do usuário
    
    Body JSON:
        acao (str): Tipo de ação realizada (registro_diario, meta_atingida, etc.)
        data (str): Data da ação no formato YYYY-MM-DD
    
    Returns:
        JSON: Badges conquistadas (se houver)
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        acao = data.get('acao', 'registro_diario')
        data_acao = datetime.strptime(data.get('data', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        
        badges_conquistadas = []
        
        # Verificar streak de diário preenchido
        if acao == 'registro_diario':
            badges_conquistadas.extend(verificar_streak_diario(user_id, data_acao))
        
        # Verificar metas atingidas
        elif acao == 'meta_atingida':
            badges_conquistadas.extend(verificar_badges_metas(user_id, data_acao))
        
        return jsonify({
            'badges_conquistadas': badges_conquistadas,
            'total': len(badges_conquistadas)
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

@app.route('/api/badges/usuario', methods=['GET'])
@jwt_required()
def badges_usuario():
    """
    Retorna todas as badges do usuário - TEMPORARIAMENTE DESABILITADO
    """
    return jsonify({
        'sucesso': True,
        'badges': [],
        'mensagem': 'Sistema de badges temporariamente em manutenção'
    }), 200
        
        # Buscar streaks atuais
        streaks = StreakUsuario.query.filter_by(usuario_id=user_id).all()
        streaks_info = {}
        for streak in streaks:
            streaks_info[streak.tipo_streak] = {
                'atual': streak.streak_atual,
                'melhor': streak.melhor_streak,
                'ultima_atividade': streak.ultima_atividade.isoformat() if streak.ultima_atividade else None
            }
        
        return jsonify({
            'badges': badges_usuario,
            'total_badges': len(badges_usuario),
            'streaks': streaks_info
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

@app.route('/api/badges/marcar-visualizada/<int:conquista_id>', methods=['PUT'])
@jwt_required()
def marcar_badge_visualizada(conquista_id):
    """
    Marca uma badge como visualizada - TEMPORARIAMENTE DESABILITADO
    """
    return jsonify({'mensagem': 'Sistema de badges temporariamente em manutenção'}), 200

# === FUNÇÕES AUXILIARES PARA BADGES === 
# TEMPORARIAMENTE DESABILITADAS PARA CORREÇÃO DE BUGS

# def verificar_streak_diario(user_id, data_acao):
#     """Verifica e atualiza streak de diário preenchido"""
#     return []

# def verificar_badges_metas(user_id, data_acao):
#     """Verifica badges relacionadas ao cumprimento de metas"""
#     return []
    """Verifica e atualiza streak de diário preenchido"""
    badges_conquistadas = []
    
    # Buscar ou criar streak
    streak = StreakUsuario.query.filter_by(
        usuario_id=user_id,
        tipo_streak='diario_preenchido'
    ).first()
    
    if not streak:
        streak = StreakUsuario(
            usuario_id=user_id,
            tipo_streak='diario_preenchido',
            streak_atual=1,
            melhor_streak=1,
            ultima_atividade=data_acao
        )
        db.session.add(streak)
    else:
        # Verificar se é consecutivo
        if streak.ultima_atividade and (data_acao - streak.ultima_atividade).days == 1:
            streak.streak_atual += 1
        elif streak.ultima_atividade != data_acao:
            streak.streak_atual = 1
        
        streak.ultima_atividade = data_acao
        if streak.streak_atual > streak.melhor_streak:
            streak.melhor_streak = streak.streak_atual
    
    db.session.commit()
    
    # Verificar badges de streak
    badges_streak = [
        (3, 'Iniciante Consistente', '🔥 3 dias seguidos registrando!', '🔥'),
        (7, 'Uma Semana Forte', '💪 7 dias seguidos! Você está no caminho certo!', '💪'),
        (14, 'Duas Semanas de Foco', '🎯 14 dias seguidos! Incrível dedicação!', '🎯'),
        (30, 'Um Mês de Excelência', '👑 30 dias seguidos! Você é um campeão!', '👑'),
        (60, 'Mestre da Consistência', '🏆 60 dias seguidos! Lendário!', '🏆'),
        (100, 'Centurião Nutricional', '⭐ 100 dias seguidos! Extraordinário!', '⭐')
    ]
    
    for dias, nome, descricao, icone in badges_streak:
        if streak.streak_atual == dias:
            # Verificar se já tem essa badge
            badge_existente = Badge.query.filter_by(nome=nome).first()
            if not badge_existente:
                badge_existente = Badge(
                    nome=nome,
                    descricao=descricao,
                    icone=icone,
                    tipo='streak',
                    criterio=dias
                )
                db.session.add(badge_existente)
                db.session.commit()
            
            # conquista_existente = ConquistaUsuario.query.filter_by(
            #     usuario_id=user_id,
            #     badge_id=badge_existente.id
            # ).first()
            
            # if not conquista_existente:
            #     nova_conquista = ConquistaUsuario(
            #         usuario_id=user_id,
            #         badge_id=badge_existente.id
            #     )
            #     db.session.add(nova_conquista)
            #     db.session.commit()
                
            badges_conquistadas.append({
                'id': badge_existente.id,
                'nome': badge_existente.nome,
                    'descricao': badge_existente.descricao,
                    'icone': badge_existente.icone,
                    'cor': badge_existente.cor
                })
    
    return badges_conquistadas

def verificar_badges_metas(user_id, data_acao):
    """Verifica badges relacionadas ao cumprimento de metas"""
    badges_conquistadas = []
    
    # Buscar dados de macros do dia
    from datetime import datetime
    try:
        registros = RegistroAlimentar.query.filter(
            RegistroAlimentar.usuario_id == user_id,
            RegistroAlimentar.data == data_acao
        ).all()
        
        # Calcular totais consumidos
        consumido = {'proteina': 0.0, 'carboidrato': 0.0, 'gordura': 0.0, 'calorias': 0.0}
        
        for registro in registros:
            if registro.alimento:
                fator_calculo = registro.quantidade_gramas / 100.0
                consumido['proteina'] += (registro.alimento.proteinas or 0) * fator_calculo
                consumido['carboidrato'] += (registro.alimento.carboidratos or 0) * fator_calculo
                consumido['gordura'] += (registro.alimento.gorduras or 0) * fator_calculo
                consumido['calorias'] += (registro.alimento.calorias or 0) * fator_calculo
        
        # Buscar metas do usuário
        perfil = PerfisNutricionais.query.filter_by(user_id=user_id).first()
        
        if perfil:
            # Calcular metas (mesmo cálculo do endpoint de macros)
            if perfil.genero == 'masculino':
                tmb = (10 * perfil.peso) + (6.25 * perfil.altura) - (5 * perfil.idade) + 5
            else:
                tmb = (10 * perfil.peso) + (6.25 * perfil.altura) - (5 * perfil.idade) - 161
            
            fatores_atividade = {
                'sedentario': 1.2, 'leve': 1.375, 'moderado': 1.55,
                'intenso': 1.725, 'muito_intenso': 1.9
            }
            fator = fatores_atividade.get(perfil.nivel_atividade, 1.2)
            gasto_total = tmb * fator
            
            if perfil.objetivo == 'emagrecimento':
                calorias_meta = gasto_total - 500
                perc_proteina = 0.30
            elif perfil.objetivo == 'ganho_massa':
                calorias_meta = gasto_total + 500
                perc_proteina = 0.25
            else:
                calorias_meta = gasto_total
                perc_proteina = 0.25
            
            proteina_meta = (calorias_meta * perc_proteina) / 4
            
            # Verificar se atingiu meta de proteína
            if consumido['proteina'] >= proteina_meta:
                badge_proteina = Badge.query.filter_by(nome='Meta de Proteína Atingida').first()
                if not badge_proteina:
                    badge_proteina = Badge(
                        nome='Meta de Proteína Atingida',
                        descricao='🥩 Parabéns! Você bateu a meta de proteínas hoje!',
                        icone='🥩',
                        tipo='meta_diaria',
                        criterio=1
                    )
                    db.session.add(badge_proteina)
                    db.session.commit()
                
                # Não criar conquista duplicada para meta diária
                # (badges diárias são mais para notificação imediata)
                badges_conquistadas.append({
                    'id': badge_proteina.id,
                    'nome': badge_proteina.nome,
                    'descricao': badge_proteina.descricao,
                    'icone': badge_proteina.icone,
                    'cor': badge_proteina.cor,
                    'tipo': 'notificacao_diaria'
                })
    
    except Exception as e:
        print(f"Erro ao verificar badges de metas: {e}")
    
    return badges_conquistadas

# === DASHBOARD DE ONBOARDING COMPLETO ===

@app.route('/dashboard-onboarding')
def dashboard_onboarding():
    """
    Dashboard de conclusão do onboarding - Mostra resumo completo do perfil e cálculos nutricionais
    """
    return render_template('dashboard_onboarding.html')

@app.route('/dashboard')
def dashboard_principal():
    """
    Dashboard principal do sistema (redirecionamento)
    """
    return render_template('dashboard_insights.html')

@app.route('/teste-analise-modular')
def teste_analise_modular():
    """
    🧠 Página de teste para a nova classe de análise nutricional modular
    Permite testar cada módulo individualmente com prompts específicos
    """
    return render_template('teste_analise_modular.html')

# === DASHBOARD DE INSIGHTS ===

@app.route('/dashboard-insights')
@jwt_required(optional=True)  # JWT opcional para demonstração
def dashboard_insights():
    """
    Dashboard de Insights com IA - Análise inteligente dos padrões alimentares
    ACESSO: Somente usuários autenticados veem seus próprios dados
    """
    # Verifica se usuário está autenticado
    current_user_id = get_jwt_identity()
    
    if current_user_id:
        # Usuário logado - usa seu ID real
        user_id = current_user_id
        print(f"👤 Usuário logado acessando dashboard: ID {user_id}")
    else:
        # Demo público - permite visualização com dados de exemplo
        user_id = request.args.get('id', '1')  # ID demo
        print(f"🔓 Acesso demo ao dashboard: ID {user_id}")
    
    return render_template('dashboard_insights.html', user_id=user_id)

@app.route('/api/ia/dashboard-insights', methods=['POST'])
def api_dashboard_insights():
    """
    API para gerar insights inteligentes sobre padrões alimentares
    """
    try:
        print("🧠 Iniciando análise de insights...")
        
        if not modelo_ia:
            print("❌ Modelo IA não configurado")
            return jsonify({
                'sucesso': False,
                'erro': 'IA não configurada. Configure GEMINI_API_KEY no arquivo .env'
            }), 400
            
        data = request.get_json()
        if not data:
            return jsonify({
                'sucesso': False,
                'erro': 'Dados não fornecidos'
            }), 400
            
        periodo = data.get('periodo', 7)  # Últimos 7 dias por padrão
        print(f"📅 Analisando período de {periodo} dias")
        
        # Buscar dados do período
        data_limite = datetime.now() - timedelta(days=periodo)
        
        print(f"🔍 Buscando registros desde {data_limite.strftime('%Y-%m-%d')}")
        
        registros = db.session.query(RegistroAlimentar, Alimento).join(Alimento).filter(
            RegistroAlimentar.usuario_id == int(data.get('user_id', 1)),  # Usa o ID do usuário específico
            RegistroAlimentar.data >= data_limite.date()
        ).all()
        
        print(f"📊 Encontrados {len(registros)} registros")
        
        if not registros:
            print("⚠️ Nenhum registro encontrado, retornando dados padrão")
            return jsonify({
                'sucesso': True,
                'periodo_analisado': periodo,
                'estatisticas': {
                    'total_calorias': 0,
                    'media_diaria_calorias': 0,
                    'dias_ativos': 0,
                    'total_registros': 0
                },
                'insights_ia': {
                    'resumo': 'Nenhum registro encontrado para o período selecionado.',
                    'pontos_positivos': ['Você está começando sua jornada nutricional!'],
                    'areas_melhorar': ['Comece registrando suas refeições diariamente'],
                    'recomendacoes': ['Registre pelo menos 3 refeições por dia'],
                    'meta_proxima_semana': 'Estabelecer o hábito de registrar todas as refeições'
                }
            })
        
        # Calcular estatísticas
        print("🧮 Calculando estatísticas...")
        total_calorias = 0
        for r in registros:
            if r.RegistroAlimentar.quantidade_gramas and r.Alimento.calorias:
                calorias_item = r.RegistroAlimentar.quantidade_gramas * r.Alimento.calorias / 100
                total_calorias += calorias_item
        
        dias_com_registros = len(set(r.RegistroAlimentar.data for r in registros))
        media_diaria = total_calorias / max(dias_com_registros, 1)
        
        print(f"📈 Estatísticas: {total_calorias:.0f} kcal em {dias_com_registros} dias")
        
        # Preparar contexto para a IA
        contexto_nutricional = f"""
        ANÁLISE NUTRICIONAL DOS ÚLTIMOS {periodo} DIAS:
        
        Total de calorias: {total_calorias:.0f} kcal
        Média diária: {media_diaria:.0f} kcal/dia
        Dias com registros: {dias_com_registros} de {periodo}
        Total de refeições: {len(registros)}
        
        Como especialista em nutrição, forneça uma análise em formato JSON com exatamente estas chaves:
        {{
            "resumo": "texto do resumo",
            "pontos_positivos": ["item1", "item2"],
            "areas_melhorar": ["item1", "item2"], 
            "recomendacoes": ["item1", "item2"],
            "meta_proxima_semana": "texto da meta"
        }}
        """
        
        print("🤖 Enviando para IA...")
        response = modelo_ia.generate_content(contexto_nutricional)
        
        # Processar resposta da IA
        import json
        try:
            resposta_limpa = response.text.strip()
            print(f"📝 Resposta IA: {resposta_limpa[:100]}...")
            
            if resposta_limpa.startswith('```json'):
                resposta_limpa = resposta_limpa[7:]
            if resposta_limpa.endswith('```'):
                resposta_limpa = resposta_limpa[:-3]
            
            insights_ia = json.loads(resposta_limpa)
            print("✅ JSON da IA processado com sucesso")
            
            return jsonify({
                'sucesso': True,
                'periodo_analisado': periodo,
                'estatisticas': {
                    'total_calorias': round(total_calorias, 1),
                    'media_diaria_calorias': round(media_diaria, 1),
                    'dias_ativos': dias_com_registros,
                    'total_registros': len(registros)
                },
                'insights_ia': insights_ia
            })
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Erro ao processar JSON da IA: {e}")
            return jsonify({
                'sucesso': True,
                'periodo_analisado': periodo,
                'estatisticas': {
                    'total_calorias': round(total_calorias, 1),
                    'media_diaria_calorias': round(media_diaria, 1),
                    'dias_ativos': dias_com_registros,
                    'total_registros': len(registros)
                },
                'insights_ia': {
                    'resumo': f'Análise dos últimos {periodo} dias com {total_calorias:.0f} kcal totais.',
                    'pontos_positivos': ['Registros consistentes de alimentação'],
                    'areas_melhorar': ['Continue mantendo os registros diários'],
                    'recomendacoes': ['Mantenha uma alimentação equilibrada'],
                    'meta_proxima_semana': 'Continuar os bons hábitos alimentares'
                }
            })
        
    except Exception as e:
        print(f"❌ Erro na API: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao processar análise: {str(e)}'
        }), 500

# === SISTEMA DE AUTENTICAÇÃO VISUAL ===

@app.route('/login')
def login_page():
    """
    Página de login visual
    """
    return render_template('login.html')

@app.route('/cadastro')
def cadastro_page():
    """
    Página de cadastro seguro com verificação de email
    """
    return render_template('cadastro_seguro.html')

@app.route('/logout')
def logout():
    """
    Rota de logout - limpa sessão e redireciona
    """
    return render_template('logout.html')

@app.route('/atividade-fisica')
def atividade_fisica_page():
    """
    Página para definir nível de atividade física (Etapa 3 do onboarding)
    """
    return render_template('atividade_fisica.html')

@app.route('/objetivo')
def objetivo_page():
    """
    Página para definir objetivo nutricional (Etapa 4 do onboarding)
    """
    return render_template('objetivo.html')

@app.route('/preferencias-alimentares')
def preferencias_alimentares_page():
    """
    Página para definir preferências e restrições alimentares (Etapa 5 do onboarding)
    """
    return render_template('preferencias_alimentares.html')

@app.route('/metas-personalizadas')
def metas_personalizadas():
    """Tela para exibir metas personalizadas calculadas"""
    return render_template('metas_personalizadas.html')

# === ROTAS DO ECOSSISTEMA L7 INTELIGENTE ===

@app.route('/resultado-completo')
@requer_verificacao_email
@requer_onboarding_completo
def resultado_completo():
    """
    Página principal com todo o ecossistema L7 personalizado
    Exibe recomendações completas: nutricional, treino, receitas, suplementos
    """
    return render_template('resultado_ecossistema.html')

@app.route('/api/ecossistema/recomendacoes')
@jwt_required()
def api_recomendacoes_ecossistema():
    """
    API que retorna todas as recomendações personalizadas do ecossistema L7
    """
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        # Verificar se onboarding está completo
        if not usuario.onboarding_completo:
            return jsonify({'erro': 'Complete o onboarding primeiro'}), 400
        
        # Preparar dados do usuário para análise
        dados_usuario = {
            'nome': usuario.nome,
            'idade': usuario.idade,
            'peso': usuario.peso,
            'altura': usuario.altura,
            'sexo': usuario.sexo,
            'objetivo': usuario.objetivo,
            'fator_atividade': usuario.fator_atividade,
            'estilo_alimentar': 'tradicional',  # Padrão se não tiver
            'experiencia_suplementos': 'iniciante',  # Padrão se não tiver
            'tempo_treino_meses': 0,  # Padrão se não tiver
            'ja_usou_termogenico': False  # Padrão se não tiver
        }
        
        # Se tiver dados do questionário, incluir
        if usuario.dados_questionario:
            import json
            questionario = json.loads(usuario.dados_questionario)
            dados_usuario.update({
                'estilo_alimentar': questionario.get('estilo_alimentar', 'tradicional'),
                'experiencia_suplementos': questionario.get('experiencia_suplementos', 'iniciante'),
                'tempo_treino_meses': questionario.get('tempo_treino_meses', 0),
                'ja_usou_termogenico': questionario.get('ja_usou_termogenico', False)
            })
        
        # Gerar recomendações completas do ecossistema
        recomendacoes = ecossistema_l7.analisar_perfil_completo(dados_usuario)
        
        return jsonify(recomendacoes)
        
    except Exception as e:
        print(f"Erro ao gerar recomendações: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/api/ecossistema/atualizar-experiencia', methods=['POST'])
@jwt_required()
def api_atualizar_experiencia():
    """
    API para atualizar experiência do usuário e recalcular recomendações
    """
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        dados = request.get_json()
        
        # Atualizar dados de experiência
        if usuario.dados_questionario:
            import json
            questionario = json.loads(usuario.dados_questionario)
        else:
            questionario = {}
        
        # Atualizar campos de experiência
        questionario.update({
            'experiencia_suplementos': dados.get('experiencia_suplementos'),
            'tempo_treino_meses': dados.get('tempo_treino_meses'),
            'ja_usou_termogenico': dados.get('ja_usou_termogenico'),
            'resultado_l7ultra': dados.get('resultado_l7ultra'),
            'satisfacao_atual': dados.get('satisfacao_atual')
        })
        
        usuario.dados_questionario = json.dumps(questionario)
        db.session.commit()
        
        return jsonify({'mensagem': 'Experiência atualizada com sucesso'})
        
    except Exception as e:
        print(f"Erro ao atualizar experiência: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/api/ecossistema/proximos-produtos')
@jwt_required()
def api_proximos_produtos():
    """
    API que sugere próximos produtos baseado na evolução do usuário
    """
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        # Simular análise de evolução (pode ser expandido)
        tempo_uso = 30  # dias - pode vir do banco
        satisfacao = 4  # escala 1-5 - pode vir do questionário
        
        if tempo_uso >= 30 and satisfacao >= 4:
            sugestao = {
                'produto_atual': 'L7Ultra',
                'proximo_produto': 'L7Turbo',
                'motivo': 'Você está pronto para o próximo nível! Seus resultados com L7Ultra foram excelentes.',
                'desconto': '20% OFF na sua evolução',
                'link': 'https://l7shop.com/l7turbo?upgrade=true',
                'urgencia': 'Oferta de upgrade por 48h!'
            }
        else:
            sugestao = {
                'produto_atual': 'L7Ultra',
                'recomendacao': 'Continue com L7Ultra',
                'motivo': 'Mantenha a consistência para maximizar seus resultados.',
                'dica': 'Complete pelo menos 60 dias para avaliar evolução',
                'link': 'https://l7shop.com/l7ultra?recompra=true'
            }
        
        return jsonify(sugestao)
        
    except Exception as e:
        print(f"Erro ao buscar próximos produtos: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/api/ecossistema/analytics', methods=['POST'])
def api_analytics_ecossistema():
    """
    API para capturar analytics do ecossistema (cliques, conversões, etc.)
    """
    try:
        dados = request.get_json()
        
        # Aqui você pode integrar com Google Analytics, Facebook Pixel, etc.
        evento = dados.get('evento')
        categoria = dados.get('categoria')
        produto = dados.get('produto')
        valor = dados.get('valor')
        
        # Log para análise (pode ser salvo no banco)
        print(f"Analytics: {evento} - {categoria} - {produto} - {valor}")
        
        # Salvar no banco para análise posterior
        # analytics_event = AnalyticsEvent(
        #     evento=evento,
        #     categoria=categoria,
        #     produto=produto,
        #     valor=valor,
        #     timestamp=datetime.utcnow()
        # )
        # db.session.add(analytics_event)
        # db.session.commit()
        
        return jsonify({'status': 'registrado'})
        
    except Exception as e:
        print(f"Erro no analytics: {str(e)}")
        return jsonify({'erro': 'Erro interno'}), 500

# === SISTEMA DE CAPTURA DE LEADS ===

@app.route('/api/leads/capturar', methods=['POST'])
def capturar_lead():
    """Captura lead antes do cadastro completo"""
    try:
        dados = request.get_json()
        
        # Validar dados obrigatórios
        email = dados.get('email', '').strip().lower()
        if not email or '@' not in email:
            return jsonify({'erro': 'Email válido é obrigatório'}), 400
        
        # Verificar se lead já existe
        lead_existente = Lead.query.filter_by(email=email).first()
        if lead_existente:
            # Atualizar informações se necessário
            if dados.get('nome'):
                lead_existente.nome = dados.get('nome')
            if dados.get('objetivo'):
                lead_existente.objetivo = dados.get('objetivo')
            lead_existente.updated_at = datetime.utcnow()
            
            db.session.commit()
            app.logger.info(f"Lead atualizado: {email}")
            
            return jsonify({
                'sucesso': True,
                'mensagem': 'Lead atualizado com sucesso',
                'lead': lead_existente.to_dict()
            })
        
        # Capturar dados adicionais para analytics
        user_agent = request.headers.get('User-Agent', '')
        ip_address = request.remote_addr
        
        # Criar novo lead
        novo_lead = Lead(
            email=email,
            nome=dados.get('nome', ''),
            telefone=dados.get('telefone', ''),
            objetivo=dados.get('objetivo', ''),
            fonte=dados.get('fonte', 'modal_captura'),
            ip_address=ip_address,
            user_agent=user_agent,
            utm_source=dados.get('utm_source'),
            utm_medium=dados.get('utm_medium'),
            utm_campaign=dados.get('utm_campaign')
        )
        
        db.session.add(novo_lead)
        db.session.commit()
        
        # Log da captura
        app.logger.info(f"Novo lead capturado: {email} - Objetivo: {dados.get('objetivo')} - Fonte: {dados.get('fonte')}")
        
        # Enviar email de boas-vindas ao lead (opcional)
        try:
            enviar_email_boas_vindas_lead(email, dados.get('nome', ''))
        except Exception as e:
            app.logger.warning(f"Erro ao enviar email para lead {email}: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Lead capturado com sucesso',
            'lead_id': novo_lead.id
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao capturar lead: {str(e)}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

def enviar_email_boas_vindas_lead(email, nome):
    """Enviar email de boas-vindas para lead capturado"""
    try:
        # Implementar aqui integração com serviço de email
        # Exemplo: MailChimp, SendGrid, etc.
        app.logger.info(f"Email de boas-vindas enviado para {email}")
        return True
    except Exception as e:
        app.logger.error(f"Erro ao enviar email de boas-vindas: {str(e)}")
        return False

@app.route('/api/leads/verificar', methods=['POST'])
def verificar_lead():
    """Verifica se email já é lead ou usuário"""
    try:
        dados = request.get_json()
        email = dados.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'erro': 'Email é obrigatório'}), 400
        
        # Verificar se é usuário cadastrado
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            return jsonify({
                'tipo': 'usuario',
                'cadastrado': True,
                'onboarding_completo': usuario.onboarding_completo
            })
        
        # Verificar se é lead
        lead = Lead.query.filter_by(email=email).first()
        if lead:
            return jsonify({
                'tipo': 'lead',
                'cadastrado': False,
                'lead': lead.to_dict()
            })
        
        # Email não encontrado
        return jsonify({
            'tipo': 'novo',
            'cadastrado': False
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao verificar lead: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/api/admin/leads', methods=['GET'])
@jwt_required()
def listar_leads():
    """Lista todos os leads para dashboard admin"""
    try:
        # Verificar se usuário é admin
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario or usuario.email != 'admin@l7nutri.com':
            return jsonify({'erro': 'Acesso negado'}), 403
        
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Filtros
        convertidos = request.args.get('convertidos')  # 'true', 'false', ou None
        fonte = request.args.get('fonte')
        
        # Query base
        query = Lead.query
        
        # Aplicar filtros
        if convertidos == 'true':
            query = query.filter(Lead.converteu_cadastro == True)
        elif convertidos == 'false':
            query = query.filter(Lead.converteu_cadastro == False)
        
        if fonte:
            query = query.filter(Lead.fonte == fonte)
        
        # Ordenar por data de criação (mais recentes primeiro)
        query = query.order_by(Lead.created_at.desc())
        
        # Paginar resultados
        leads_paginated = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'leads': [lead.to_dict() for lead in leads_paginated.items],
            'total': leads_paginated.total,
            'pages': leads_paginated.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao listar leads: {str(e)}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500

def enviar_email_boas_vindas_lead(email, nome):
    """Envia email de boas-vindas para lead capturado"""
    subject = "🎯 Bem-vindo ao L7Nutri! Sua jornada para uma vida mais saudável começou"
    
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #f8f9fa; padding: 20px;">
        <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #e74c3c; margin: 0;">🧠 L7Nutri</h1>
                <p style="color: #666; margin: 5px 0;">Inteligência Artificial para sua Nutrição</p>
            </div>
            
            <h2 style="color: #2c3e50;">Olá{', ' + nome if nome else ''}! 👋</h2>
            
            <p>Que ótimo ter você conosco! Você acaba de dar o primeiro passo para transformar sua alimentação e alcançar seus objetivos.</p>
            
            <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #27ae60; margin-top: 0;">🎯 O que você vai ganhar:</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Análise nutricional personalizada com IA</li>
                    <li>Plano alimentar 100% adaptado para você</li>
                    <li>Receitas exclusivas do L7Chef</li>
                    <li>Treinos personalizados do L7Personal</li>
                    <li>Recomendações de suplementos L7Shop</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://l7nutri-app.onrender.com/cadastro" 
                   style="background: #e74c3c; color: white; text-decoration: none; padding: 15px 30px; border-radius: 25px; font-weight: bold; display: inline-block;">
                    🚀 Completar Cadastro Agora
                </a>
            </div>
            
            <p style="font-size: 14px; color: #666; border-top: 1px solid #eee; padding-top: 15px; margin-top: 30px;">
                Este email foi enviado porque você demonstrou interesse no L7Nutri. Se não foi você, pode ignorar este email.
            </p>
        </div>
    </div>
    """
    
    enviar_email(email, subject, html_body, tipo='lead')

if __name__ == '__main__':
    app.run(debug=True)
