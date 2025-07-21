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
        if os.path.exists('nutricao.db'):
            shutil.copy2('nutricao.db', backup_filename)
            app.logger.info(f"Backup realizado com sucesso: {backup_filename}")
            
            # Manter apenas os últimos 7 backups
            import glob
            backups = sorted(glob.glob('backups/nutricao_backup_*.db'))
            if len(backups) > 7:
                for old_backup in backups[:-7]:
                    os.remove(old_backup)
                    app.logger.info(f"Backup antigo removido: {old_backup}")
        else:
            app.logger.warning("Arquivo nutricao.db não encontrado para backup")
    except Exception as e:
        app.logger.error(f"Erro durante backup: {str(e)}")

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
