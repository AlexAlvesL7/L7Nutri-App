import os
import sys
import traceback
from datetime import timedelta

# Configurar logging primeiro
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

try:
    logger.info("=== INICIANDO L7NUTRI APP ===")
    
    # Importações básicas
    from flask import Flask, request, jsonify, render_template, redirect, url_for, session
    from flask_sqlalchemy import SQLAlchemy
    from flask_bcrypt import Bcrypt
    from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
    from datetime import date, datetime, timedelta
    
    logger.info("✓ Importações básicas realizadas")
    
    # Importação opcional do Google AI
    try:
        import google.generativeai as genai
        logger.info("✓ Google Generative AI importado")
    except ImportError:
        genai = None
        logger.warning("⚠ Google Generative AI não disponível")
    
    # Configuração do Flask
    app = Flask(__name__)
    bcrypt = Bcrypt(app)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'l7nutri-secret-key-2025')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=365)
    
    jwt = JWTManager(app)
    logger.info("✓ Configurações básicas do Flask aplicadas")
    
    # Configuração do banco
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        # Corrigir URL do PostgreSQL se necessário
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        logger.info("✓ Configurado para PostgreSQL (Render)")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nutricao.db'
        logger.info("✓ Configurado para SQLite (local)")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar banco
    db = SQLAlchemy(app)
    logger.info("✓ SQLAlchemy inicializado")
    
    # Configurar Google AI se disponível
    modelo_ia = None
    if genai:
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key and gemini_api_key != 'SUA_CHAVE_AQUI':
            try:
                genai.configure(api_key=gemini_api_key)
                modelo_ia = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✓ Google Gemini AI configurado")
            except Exception as e:
                logger.error(f"✗ Erro ao configurar Gemini AI: {e}")
        else:
            logger.warning("⚠ GEMINI_API_KEY não configurada")
    
    # === MODELOS DO BANCO ===
    class Usuario(db.Model):
        __tablename__ = 'usuario'
        
        id = db.Column(db.Integer, primary_key=True)
        nome_usuario = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        senha_hash = db.Column(db.String(255), nullable=False)
        data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())
        
        def __repr__(self):
            return f'<Usuario {self.nome_usuario}>'
    
    class Alimento(db.Model):
        __tablename__ = 'alimento'
        
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(200), nullable=False)
        calorias = db.Column(db.Float, nullable=False)
        proteinas = db.Column(db.Float, nullable=False)
        carboidratos = db.Column(db.Float, nullable=False)
        gorduras = db.Column(db.Float, nullable=False)
        
        def __repr__(self):
            return f'<Alimento {self.nome}>'
    
    class RegistroAlimentar(db.Model):
        __tablename__ = 'registro_alimentar'
        
        id = db.Column(db.Integer, primary_key=True)
        usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
        alimento_id = db.Column(db.Integer, db.ForeignKey('alimento.id'), nullable=False)
        quantidade = db.Column(db.Float, nullable=False)
        data_registro = db.Column(db.Date, nullable=False)
        data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())
        
        # Relacionamentos
        usuario = db.relationship('Usuario', backref='registros')
        alimento = db.relationship('Alimento', backref='registros')
        
        def __repr__(self):
            return f'<RegistroAlimentar {self.usuario_id}-{self.alimento_id}>'
    
    logger.info("✓ Modelos do banco definidos")
    
    # === ROTAS ===
    @app.route('/')
    def index():
        try:
            logger.info("Rota / acessada")
            return render_template('index.html')
        except Exception as e:
            logger.error(f"Erro na rota /: {e}")
            return f"Erro: {str(e)}", 500
    
    @app.route('/health')
    def health_check():
        try:
            # Testar conexão com banco
            with app.app_context():
                db.engine.execute('SELECT 1')
            
            return jsonify({
                'status': 'OK',
                'database': 'Connected',
                'ai_model': 'Available' if modelo_ia else 'Not Available',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Health check falhou: {e}")
            return jsonify({
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        try:
            if request.method == 'POST':
                data = request.get_json()
                nome_usuario = data.get('nome_usuario')
                senha = data.get('senha')
                
                if not nome_usuario or not senha:
                    return jsonify({'erro': 'Nome de usuário e senha são obrigatórios'}), 400
                
                usuario = Usuario.query.filter_by(nome_usuario=nome_usuario).first()
                
                if usuario and bcrypt.check_password_hash(usuario.senha_hash, senha):
                    access_token = create_access_token(identity=usuario.id)
                    session['user_id'] = usuario.id
                    session['nome_usuario'] = usuario.nome_usuario
                    return jsonify({
                        'mensagem': 'Login realizado com sucesso',
                        'token': access_token,
                        'usuario': {
                            'id': usuario.id,
                            'nome_usuario': usuario.nome_usuario,
                            'email': usuario.email
                        }
                    })
                else:
                    return jsonify({'erro': 'Credenciais inválidas'}), 401
            
            return render_template('login.html')
        except Exception as e:
            logger.error(f"Erro na rota /login: {e}")
            return jsonify({'erro': 'Erro interno do servidor'}), 500
    
    # Handler de erro global
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Erro não tratado: {e}")
        logger.error(traceback.format_exc())
        
        # Não retornar detalhes em produção
        if app.debug:
            return jsonify({'erro': 'Erro interno do servidor', 'detalhes': str(e)}), 500
        else:
            return jsonify({'erro': 'Erro interno do servidor'}), 500
    
    # Criar tabelas se não existirem
    with app.app_context():
        try:
            db.create_all()
            logger.info("✓ Tabelas do banco criadas/verificadas")
        except Exception as e:
            logger.error(f"✗ Erro ao criar tabelas: {e}")
    
    logger.info("=== L7NUTRI APP CONFIGURADO COM SUCESSO ===")
    
    if __name__ == '__main__':
        port = int(os.getenv('PORT', 5000))
        logger.info(f"Iniciando servidor na porta {port}")
        
        app.run(host='0.0.0.0', port=port, debug=False)

except Exception as e:
    logger.error(f"ERRO CRÍTICO: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)
