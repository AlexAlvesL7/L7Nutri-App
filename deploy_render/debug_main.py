import os
import sys
import traceback
import logging

# Configurar logging para debug
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('debug.log')
    ]
)

logger = logging.getLogger(__name__)

try:
    logger.info("Iniciando importação do Flask...")
    from flask import Flask, request, jsonify, render_template, redirect, url_for, session
    logger.info("Flask importado com sucesso")
    
    logger.info("Iniciando importação do SQLAlchemy...")
    from flask_sqlalchemy import SQLAlchemy
    logger.info("SQLAlchemy importado com sucesso")
    
    logger.info("Iniciando importação do Bcrypt...")
    from flask_bcrypt import Bcrypt
    logger.info("Bcrypt importado com sucesso")
    
    logger.info("Iniciando importação do JWT...")
    from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
    logger.info("JWT importado com sucesso")
    
    logger.info("Iniciando importação das bibliotecas padrão...")
    from datetime import date, datetime, timedelta
    logger.info("Bibliotecas datetime importadas com sucesso")
    
    logger.info("Tentando importar Google Generative AI...")
    try:
        import google.generativeai as genai
        logger.info("Google Generative AI importado com sucesso")
    except ImportError as e:
        logger.error(f"Erro ao importar Google Generative AI: {e}")
        genai = None
    
    # Configuração do Google Gemini AI
    logger.info("Configurando Google Gemini AI...")
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if gemini_api_key and gemini_api_key != 'SUA_CHAVE_AQUI' and genai:
        try:
            genai.configure(api_key=gemini_api_key)
            modelo_ia = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Google Gemini AI configurado com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao configurar Google Gemini AI: {e}")
            modelo_ia = None
    else:
        modelo_ia = None
        logger.warning("GEMINI_API_KEY não configurada. Recursos de IA estarão desabilitados.")
    
    # Configuração do Flask
    logger.info("Criando aplicação Flask...")
    app = Flask(__name__)
    logger.info("Aplicação Flask criada com sucesso")
    
    logger.info("Configurando Bcrypt...")
    bcrypt = Bcrypt(app)
    logger.info("Bcrypt configurado com sucesso")
    
    # Configuração do JWT
    logger.info("Configurando JWT...")
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=365)
    jwt = JWTManager(app)
    logger.info("JWT configurado com sucesso")
    
    # Chave secreta
    logger.info("Configurando chave secreta...")
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'l7nutri-secret-key-2025')
    logger.info("Chave secreta configurada com sucesso")
    
    # Configuração do banco de dados
    logger.info("Configurando banco de dados...")
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        logger.info(f"DATABASE_URL encontrada: {DATABASE_URL[:50]}...")
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
            logger.info("URL do banco corrigida para PostgreSQL")
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        logger.info("MODO PRODUÇÃO: Usando PostgreSQL Render")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nutricao.db'
        logger.info("MODO DESENVOLVIMENTO: Usando SQLite local")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar SQLAlchemy
    logger.info("Inicializando SQLAlchemy...")
    db = SQLAlchemy(app)
    logger.info("SQLAlchemy inicializado com sucesso")
    
    # Verificar se consegue conectar ao banco
    logger.info("Testando conexão com banco de dados...")
    with app.app_context():
        try:
            db.engine.execute('SELECT 1')
            logger.info("Conexão com banco de dados testada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar com banco de dados: {e}")
    
    # Criar uma rota de teste simples
    @app.route('/')
    def index():
        logger.info("Rota / acessada")
        return "L7Nutri - Aplicação funcionando! Debug Mode"
    
    @app.route('/debug/status')
    def debug_status():
        logger.info("Rota /debug/status acessada")
        return jsonify({
            'status': 'OK',
            'database_url': 'configurada' if DATABASE_URL else 'não configurada',
            'gemini_ai': 'configurada' if modelo_ia else 'não configurada',
            'flask_env': os.getenv('FLASK_ENV', 'development')
        })
    
    # Adicionar handler de erro global
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Erro não tratado: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'erro': 'Erro interno do servidor', 'detalhes': str(e)}), 500
    
    if __name__ == '__main__':
        logger.info("Iniciando servidor Flask...")
        port = int(os.getenv('PORT', 5000))
        logger.info(f"Porta configurada: {port}")
        
        try:
            app.run(host='0.0.0.0', port=port, debug=False)
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor: {e}")
            logger.error(traceback.format_exc())
            sys.exit(1)

except Exception as e:
    logger.error(f"Erro crítico durante inicialização: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)
