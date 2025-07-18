from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from datetime import date, datetime, timedelta
import google.generativeai as genai

# --- Configuração do Google Gemini AI ---
gemini_api_key = os.getenv('GEMINI_API_KEY')
if gemini_api_key and gemini_api_key != 'SUA_CHAVE_AQUI':
    genai.configure(api_key=gemini_api_key)
    modelo_ia = genai.GenerativeModel('gemini-1.5-flash')
    print("Google Gemini AI configurado com sucesso!")
else:
    modelo_ia = None
    print("GEMINI_API_KEY nao configurada. Recursos de IA estarao desabilitados.")

# --- Configuração do Aplicativo Flask ---
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configuração do JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=365)  # 1 ano
jwt = JWTManager(app)

# Configura a chave secreta para a aplicação
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'l7nutri-secret-key-2025')

# === CONFIGURAÇÃO DO BANCO DE DADOS ===
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

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# === MODELOS DO BANCO DE DADOS ===
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_usuario': self.nome_usuario,
            'email': self.email,
            'data_criacao': self.data_criacao.isoformat()
        }

class Alimento(db.Model):
    __tablename__ = 'alimentos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    calorias = db.Column(db.Float, nullable=False)
    proteinas = db.Column(db.Float, nullable=False)
    carboidratos = db.Column(db.Float, nullable=False)
    gorduras = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'calorias': self.calorias,
            'proteinas': self.proteinas,
            'carboidratos': self.carboidratos,
            'gorduras': self.gorduras
        }

class Diario(db.Model):
    __tablename__ = 'diarios'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_entrada = db.Column(db.Date, nullable=False)
    alimento_id = db.Column(db.Integer, db.ForeignKey('alimentos.id'), nullable=False)
    quantidade = db.Column(db.Float, nullable=False)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref='diarios')
    alimento = db.relationship('Alimento', backref='diarios')
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'data_entrada': self.data_entrada.isoformat(),
            'alimento_id': self.alimento_id,
            'quantidade': self.quantidade,
            'alimento': self.alimento.to_dict() if self.alimento else None
        }

# === ROTAS DA APLICAÇÃO ===

@app.route('/')
def home():
    """Rota principal - redireciona para login"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template_string(LOGIN_TEMPLATE, error="Usuário e senha são obrigatórios")
        
        # Verificar credenciais
        usuario = Usuario.query.filter_by(nome_usuario=username).first()
        if usuario and bcrypt.check_password_hash(usuario.senha_hash, password):
            session['user_id'] = usuario.id
            session['username'] = usuario.nome_usuario
            return redirect(url_for('dashboard'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="Usuário ou senha inválidos")
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/dashboard')
def dashboard():
    """Dashboard principal"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get(session['user_id'])
    total_alimentos = Alimento.query.count()
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                usuario=usuario, 
                                total_alimentos=total_alimentos)

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/alimentos')
def listar_alimentos():
    """API para listar alimentos"""
    try:
        alimentos = Alimento.query.all()
        return jsonify([alimento.to_dict() for alimento in alimentos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def status():
    """Verificar status da aplicação"""
    try:
        # Verificar conexão com banco
        total_usuarios = Usuario.query.count()
        total_alimentos = Alimento.query.count()
        total_diarios = Diario.query.count()
        
        return jsonify({
            'status': 'ok',
            'usuarios': total_usuarios,
            'alimentos': total_alimentos,
            'diarios': total_diarios,
            'gemini_ai': modelo_ia is not None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === TEMPLATES HTML EMBUTIDOS ===
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>L7Nutri - Login</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 400px; margin: 100px auto; padding: 20px; background: #f0f0f0; }
        .login-form { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input, button { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { background: #28a745; color: white; cursor: pointer; border: none; }
        button:hover { background: #218838; }
        .error { color: red; margin: 10px 0; text-align: center; }
        h1 { text-align: center; color: #333; margin-bottom: 20px; }
        .info { text-align: center; color: #666; font-size: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="login-form">
        <h1>🥗 L7Nutri</h1>
        <form method="POST">
            <input type="text" name="username" placeholder="Usuário" required>
            <input type="password" name="password" placeholder="Senha" required>
            <button type="submit">Entrar</button>
        </form>
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
        <div class="info">
            <strong>Teste:</strong> admin / admin123
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>L7Nutri - Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f0f0f0; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .stat-card { background: #28a745; color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; }
        .stat-label { font-size: 0.9em; opacity: 0.9; }
        .logout-btn { background: #dc3545; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; float: right; }
        .logout-btn:hover { background: #c82333; }
        h1 { color: #333; margin: 0; }
        .welcome { color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🥗 L7Nutri Dashboard</h1>
        <div class="welcome">Bem-vindo, {{ usuario.nome_usuario }}!</div>
        <a href="{{ url_for('logout') }}">
            <button class="logout-btn">Sair</button>
        </a>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{{ total_alimentos }}</div>
            <div class="stat-label">Alimentos Cadastrados</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">✅</div>
            <div class="stat-label">Sistema Online</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">🤖</div>
            <div class="stat-label">IA Gemini Ativa</div>
        </div>
    </div>
    
    <div class="card">
        <h2>🎉 Parabéns!</h2>
        <p>Seu aplicativo L7Nutri está funcionando perfeitamente no Render!</p>
        <p><strong>Características:</strong></p>
        <ul>
            <li>✅ Banco de dados PostgreSQL configurado</li>
            <li>✅ {{ total_alimentos }} alimentos da Base de Ouro carregados</li>
            <li>✅ Sistema de autenticação funcionando</li>
            <li>✅ Integração com Google Gemini AI preparada</li>
            <li>✅ Deploy automático configurado</li>
        </ul>
    </div>
    
    <div class="card">
        <h3>🔗 Links Úteis</h3>
        <p><strong>API de Alimentos:</strong> <a href="{{ url_for('listar_alimentos') }}" target="_blank">Ver alimentos</a></p>
        <p><strong>Status da API:</strong> <a href="{{ url_for('status') }}" target="_blank">Verificar status</a></p>
    </div>
</body>
</html>
"""

# === INICIALIZAÇÃO DO BANCO ===
def init_db():
    """Inicializar banco de dados"""
    with app.app_context():
        db.create_all()
        
        # Verificar se já existe usuário admin
        admin_user = Usuario.query.filter_by(nome_usuario='admin').first()
        if not admin_user:
            # Criar usuário admin
            senha_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = Usuario(
                nome_usuario='admin',
                email='admin@l7nutri.com',
                senha_hash=senha_hash
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuário admin criado!")
        
        # Verificar se já existem alimentos
        total_alimentos = Alimento.query.count()
        if total_alimentos == 0:
            # Adicionar Base de Ouro - 26 alimentos
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

# Inicializar banco ao iniciar a aplicação
init_db()

if __name__ == '__main__':
    # Configuração do servidor
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
