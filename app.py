from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai

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

# --- Configuração do Aplicativo Flask ---
app = Flask(__name__)
bcrypt = Bcrypt(app)

# === CONFIGURAÇÃO DE AMBIENTE ===
# Detecta se estamos em produção ou desenvolvimento
is_production = os.getenv('FLASK_ENV') == 'production'

# Configuração do JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
    seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 31536000))  # 1 ano padrão
)
jwt = JWTManager(app)

# Configura a chave secreta para a aplicação
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))

# === CONFIGURAÇÃO DO BANCO DE DADOS (VERSÃO CORRIGIDA E SEGURA) ===
# Lê a URL do banco de dados diretamente do ambiente do Render.
DATABASE_URL = os.getenv('DATABASE_URL')

# Verifica se a DATABASE_URL foi encontrada e se é de um PostgreSQL
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    # O Render fornece 'postgres://' mas o SQLAlchemy prefere 'postgresql://'
    # Esta linha faz a correção necessária para garantir a compatibilidade.
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    print("✅ MODO PRODUÇÃO: Conectando ao banco de dados PostgreSQL do Render...")
else:
    # Se a DATABASE_URL não for encontrada, usa o SQLite para desenvolvimento local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.getcwd()), 'nutricao.db')
    print("⚠️ MODO DESENVOLVIMENTO: Usando banco de dados SQLite local.")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o SQLAlchemy com o aplicativo Flask
db = SQLAlchemy(app)

# Inicializa o Flask-Migrate
migrate = Migrate(app, db)

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
    objetivo = db.Column(db.String(100))

    alergias = db.relationship('AlergiaUsuario', backref='usuario', lazy=True)
    preferencias = db.relationship('PreferenciaUsuario', backref='usuario', lazy=True)
    registros_alimentares = db.relationship('RegistroAlimentar', backref='usuario', lazy=True)
    planos_sugeridos = db.relationship('PlanoSugestao', backref='usuario', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.username}>'

class Alimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    calorias = db.Column(db.Float)
    proteinas = db.Column(db.Float)
    carboidratos = db.Column(db.Float)
    gorduras = db.Column(db.Float)

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
    data = db.Column(db.Date, nullable=False)
    tipo_refeicao = db.Column(db.String(50), nullable=False)
    alimento_id = db.Column(db.Integer, db.ForeignKey('alimento.id'), nullable=True)
    receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=True)
    quantidade_gramas = db.Column(db.Float)

    alimento = db.relationship('Alimento', backref='registros_alimentares_alimento', lazy=True)
    receita = db.relationship('Receita', backref='registros_alimentares_receita', lazy=True)

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

# --- ROTAS DA APLICAÇÃO ---

@app.route('/')
def home():
    return render_template('home.html')

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
        access_token = create_access_token(identity=str(usuario.id))
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Nome de usuário ou senha incorretos!'}), 401

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
        return jsonify({'message': 'Todos os campos de alimento (nome, calorias, proteinas, carboidratos, gorduras) são obrigatórios!'}), 400

    nome = data['nome']
    calorias = data['calorias']
    proteinas = data['proteinas']
    carboidratos = data['carboidratos']
    gorduras = data['gorduras']

    if Alimento.query.filter_by(nome=nome).first():
        return jsonify({'message': 'Alimento com este nome já existe!'}), 409

    novo_alimento = Alimento(
        nome=nome,
        calorias=calorias,
        proteinas=proteinas,
        carboidratos=carboidratos,
        gorduras=gorduras
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
    Página de cadastro visual
    """
    return render_template('cadastro.html')

@app.route('/logout')
def logout():
    """
    Rota de logout - limpa sessão e redireciona
    """
    return render_template('logout.html')

# ROTA DE DIAGNÓSTICO TEMPORÁRIA - REMOVER APÓS O TESTE
@app.route('/api/debug/inspect-users/<secret_key>')
def inspect_users(secret_key):
    # Medida de segurança simples para não deixar o endpoint aberto ao público
    if secret_key != 'NOSSA_CHAVE_SECRETA_123':
        return jsonify({"erro": "Acesso negado"}), 403

    try:
        # Acessa o modelo Usuario e busca por todos os registros
        usuarios = Usuario.query.all()
        resultado = []
        for usuario in usuarios:
            resultado.append({
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "username": usuario.username
                # Propositalmente não exibimos o hash da senha
            })
        # Retorna a lista de usuários como uma resposta JSON
        return jsonify(resultado)
    except Exception as e:
        # Se algo der errado, retorna o erro
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
