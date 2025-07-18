from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from functools import wraps
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
    print("✅ Google Gemini AI configurado com sucesso!")
else:
    modelo_ia = None
    print("⚠️ GEMINI_API_KEY não configurada. Recursos de IA estarão desabilitados.")

# --- Configuração do Aplicativo Flask ---
app = Flask(__name__)
bcrypt = Bcrypt(app)

@app.context_processor
def inject_datetime():
    """
    Injeta a funcionalidade do datetime em todos os templates
    para que possamos usar coisas como o ano atual no rodapé.
    """
    return {'datetime': datetime}

app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Troque por uma chave forte em produção
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=365)  # Token válido por 1 ano para testes
jwt = JWTManager(app)

# Configura a chave secreta para a aplicação
app.config['SECRET_KEY'] = os.urandom(24)

# Configura o caminho para o arquivo do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.getcwd()), 'nutricao.db')
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
    return render_template('index.html')

# --- Rota do Diário Alimentar ---
@app.route('/diario')
# Futuramente, esta rota será protegida com @jwt_required()
def diario_usuario():
    # Por enquanto, vamos usar dados fixos (mockados) para as metas.
    # No futuro, buscaremos isso do perfil do usuário logado no banco de dados.
    metas = {
        'calorias': 2200,
        'proteinas': 150,
        'carboidratos': 250,
        'gorduras': 60
    }
    return render_template('diario.html', metas=metas)

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
        objetivo = data['objetivo'].lower()

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
        elif objetivo == 'ganhar':
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

# --- Rota de busca de alimentos ---
@app.route('/api/alimentos/buscar', methods=['GET'])
# Futuramente, protegeremos esta rota com @jwt_required(), mas por enquanto,
# deixaremos aberta para facilitar a construção e os testes.
def buscar_alimentos():
    # Pega o termo de busca da URL (ex: /api/alimentos/buscar?q=arroz)
    termo_busca = request.args.get('q', '').strip()

    # Se o termo de busca for muito curto, não fazemos a busca para não sobrecarregar o sistema
    if len(termo_busca) < 2:
        return jsonify({'erro': 'Termo de busca muito curto (mínimo 2 caracteres).'}), 400

    try:
        # Usamos '.ilike()' para fazer a busca sem diferenciar maiúsculas de minúsculas.
        # O '%{termo_busca}%' é um coringa que busca a palavra em qualquer parte do nome.
        # '.limit(20)' evita que a busca retorne resultados demais, mantendo-a rápida.
        alimentos_encontrados = Alimento.query.filter(Alimento.nome.ilike(f'%{termo_busca}%')).limit(20).all()

        resultado = []
        for alimento in alimentos_encontrados:
            resultado.append({
                'id': alimento.id,
                'nome': alimento.nome,
                'calorias': alimento.calorias,
                'proteinas': alimento.proteinas,
                'carboidratos': alimento.carboidratos,
                'gorduras': alimento.gorduras
            })

        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({'erro': f'Ocorreu um erro na busca: {str(e)}'}), 500

# --- ROTA PARA REGISTRAR ALIMENTOS NO DIÁRIO ---
@app.route('/api/diario/registrar', methods=['POST'])
# No futuro, esta rota será protegida com @jwt_required() para aceitar registros apenas de usuários logados.
def registrar_refeicao():
    data = request.get_json()

    # Validação para garantir que os dados essenciais foram enviados
    if not data or not all(k in data for k in ['alimento_id', 'tipo_refeicao']):
        return jsonify({'erro': 'Dados incompletos. ID do alimento e tipo de refeição são obrigatórios.'}), 400

    try:
        alimento_id = data.get('alimento_id')
        tipo_refeicao = data.get('tipo_refeicao')
        
        # Futuramente, o user_id virá do token JWT do usuário logado.
        # Por agora, vamos usar um ID fixo para teste (o usuário de id=1).
        user_id_teste = 1 

        novo_registro = RegistroAlimentar(
            usuario_id=user_id_teste,
            data=date.today(), # Usa a data de hoje para o registro
            tipo_refeicao=tipo_refeicao,
            alimento_id=alimento_id,
            # A quantidade (em gramas) será um campo que adicionaremos no futuro. Por enquanto, 100g é o padrão.
            quantidade_gramas=100 
        )

        db.session.add(novo_registro)
        db.session.commit()

        # Retorna o registro criado, incluindo seu novo ID, para confirmação.
        return jsonify({
            'mensagem': 'Alimento registrado com sucesso!',
            'registro_id': novo_registro.id,
            'alimento_id': novo_registro.alimento_id
        }), 201 # HTTP Status 201 significa "Created"

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Ocorreu um erro ao salvar o registro: {str(e)}'}), 500

# --- ROTA PARA REMOVER ALIMENTOS DO DIÁRIO ---
@app.route('/api/diario/remover', methods=['POST'])
# @jwt_required() # Também será protegida no futuro
def remover_refeicao():
    data = request.get_json()
    if not data or 'registro_id' not in data:
        return jsonify({'erro': 'ID do registro é obrigatório.'}), 400

    try:
        registro_id = data.get('registro_id')
        
        # Futuramente, vamos verificar se este registro pertence ao usuário logado.
        # Por enquanto, buscamos o registro diretamente pelo ID.
        registro = RegistroAlimentar.query.get(registro_id)

        if registro:
            db.session.delete(registro)
            db.session.commit()
            return jsonify({'mensagem': f'Registro {registro_id} removido com sucesso!'}), 200
        else:
            return jsonify({'erro': 'Registro não encontrado.'}), 404 # Not Found

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Ocorreu um erro ao remover o registro: {str(e)}'}), 500

# --- ROTA DE TESTE DO GEMINI AI ---
@app.route('/api/ia/teste-conexao', methods=['GET'])
def teste_gemini():
    """
    Rota de teste para verificar se a conexão com o Google Gemini AI está funcionando
    """
    try:
        # Verifica se a API key está configurada e modelo inicializado
        if not modelo_ia:
            return jsonify({
                'erro': 'Chave da API Gemini não configurada. Configure GEMINI_API_KEY no arquivo .env'
            }), 400

        # Faz uma pergunta simples de teste
        prompt = """
        Você é um assistente de nutrição especializado. 
        Responda em português brasileiro de forma breve:
        
        O que é uma alimentação balanceada?
        """
        
        response = modelo_ia.generate_content(prompt)
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Conexão com Gemini AI funcionando!',
            'resposta_ia': response.text,
            'modelo': 'gemini-1.5-flash'
        }), 200

    except Exception as e:
        return jsonify({
            'erro': f'Erro ao conectar com Gemini AI: {str(e)}',
            'dica': 'Verifique se a GEMINI_API_KEY está correta no arquivo .env'
        }), 500

# --- ROTA DE SUGESTÕES INTELIGENTES ---
@app.route('/api/ia/sugestoes-inteligentes', methods=['POST'])
def sugestoes_inteligentes():
    """
    IA que analisa o histórico do usuário e dá sugestões personalizadas
    """
    try:
        # Verifica se a IA está configurada
        if not modelo_ia:
            return jsonify({
                'erro': 'IA não configurada. Configure GEMINI_API_KEY no arquivo .env'
            }), 400

        data = request.get_json()
        
        # Dados do usuário (futuramente virão do banco)
        user_id_teste = 1
        objetivo = data.get('objetivo', 'emagrecimento')
        horario_atual = datetime.now().hour
        
        # Busca histórico recente do usuário
        registros_recentes = RegistroAlimentar.query.filter_by(
            usuario_id=user_id_teste
        ).join(Alimento).add_columns(
            Alimento.nome, Alimento.calorias, Alimento.proteinas
        ).order_by(RegistroAlimentar.data.desc()).limit(10).all()
        
        # Constrói contexto para a IA
        historico_texto = ""
        if registros_recentes:
            for registro, nome, calorias, proteinas in registros_recentes:
                historico_texto += f"- {nome} ({registro.tipo_refeicao}) - {calorias}kcal, {proteinas}g proteína\n"
        else:
            historico_texto = "Usuário ainda não tem histórico registrado."

        # Determina contexto do horário
        contexto_horario = ""
        if 6 <= horario_atual < 10:
            contexto_horario = "café da manhã"
        elif 11 <= horario_atual < 15:
            contexto_horario = "almoço"
        elif 15 <= horario_atual < 18:
            contexto_horario = "lanche da tarde"
        elif 18 <= horario_atual <= 22:
            contexto_horario = "jantar"
        else:
            contexto_horario = "lanche noturno"

        # Prompt inteligente para o Gemini
        prompt = f"""
        Você é um nutricionista especializado em IA. Analise o perfil do usuário e dê sugestões personalizadas.

        PERFIL DO USUÁRIO:
        - Objetivo: {objetivo}
        - Horário atual: {horario_atual}h (contexto: {contexto_horario})
        
        HISTÓRICO ALIMENTAR RECENTE:
        {historico_texto}
        
        TAREFA:
        Baseado no histórico e horário atual, sugira:
        1. Um alimento específico adequado para agora
        2. Uma explicação nutricional breve (máximo 2 frases)
        3. Uma dica personalizada baseada no padrão alimentar dele
        
        FORMATO DA RESPOSTA (responda EXATAMENTE neste formato JSON):
        {{
            "alimento_sugerido": "nome do alimento",
            "explicacao": "explicação nutricional breve",
            "dica_personalizada": "dica baseada no histórico",
            "contexto": "{contexto_horario}"
        }}
        
        Seja específico e prático. Use alimentos comuns no Brasil.
        """

        # Chama o Gemini
        response = modelo_ia.generate_content(prompt)
        
        # Tenta extrair JSON da resposta
        import json
        try:
            # Remove possíveis marcações de código
            resposta_limpa = response.text.strip()
            if resposta_limpa.startswith('```json'):
                resposta_limpa = resposta_limpa[7:]
            if resposta_limpa.endswith('```'):
                resposta_limpa = resposta_limpa[:-3]
            
            sugestao = json.loads(resposta_limpa)
            
            return jsonify({
                'sucesso': True,
                'sugestao': sugestao,
                'horario_contexto': f"{horario_atual}h - {contexto_horario}",
                'historico_analisado': len(registros_recentes)
            }), 200
            
        except json.JSONDecodeError:
            # Fallback se não conseguir fazer parse do JSON
            return jsonify({
                'sucesso': True,
                'sugestao': {
                    'alimento_sugerido': 'Não foi possível processar sugestão específica',
                    'explicacao': response.text[:200] + '...',
                    'dica_personalizada': 'Continue registrando seus alimentos para receber sugestões mais precisas!',
                    'contexto': contexto_horario
                }
            }), 200

    except Exception as e:
        return jsonify({
            'erro': f'Erro ao gerar sugestões: {str(e)}',
            'dica': 'Tente novamente em alguns segundos'
        }), 500

# === ROTAS DE IA ===

@app.route('/dashboard-insights')
def dashboard_insights():
    """
    Dashboard de Insights com IA - Análise inteligente dos padrões alimentares
    """
    # Para demo, usando dados simulados - em produção viria do login do usuário
    user_id = request.args.get('id', '9185fb0a-a4ed-4345-9af4-e0e7698d3c83')
    
    # Buscar dados dos últimos 30 dias
    from datetime import datetime, timedelta
    data_limite = datetime.now() - timedelta(days=30)
    
    registros = db.session.query(RegistroAlimentar).join(Alimento).filter(
        RegistroAlimentar.usuario_id == 1,  # Demo user
        RegistroAlimentar.data >= data_limite
    ).all()
    
    # Estatísticas básicas
    total_registros = len(registros)
    dias_ativos = len(set(r.data.date() for r in registros)) if registros else 0
    
    return render_template('dashboard_insights.html', 
                         total_registros=total_registros,
                         dias_ativos=dias_ativos,
                         user_id=user_id)

@app.route('/api/ia/dashboard-insights', methods=['POST'])
def api_dashboard_insights():
    """
    API para gerar insights inteligentes sobre padrões alimentares
    """
    try:
        if not modelo_ia:
            return jsonify({
                'erro': 'IA não configurada. Configure GEMINI_API_KEY no arquivo .env'
            }), 400
            
        data = request.get_json()
        periodo = data.get('periodo', 7)  # Últimos 7 dias por padrão
        
        # Buscar dados do período
        from datetime import datetime, timedelta
        data_limite = datetime.now() - timedelta(days=periodo)
        
        registros = db.session.query(RegistroAlimentar, Alimento).join(Alimento).filter(
            RegistroAlimentar.usuario_id == 1,  # Demo user
            RegistroAlimentar.data >= data_limite
        ).all()
        
        # Calcular estatísticas
        total_calorias = sum(r.RegistroAlimentar.quantidade * r.Alimento.calorias / 100 for r in registros)
        total_proteinas = sum(r.RegistroAlimentar.quantidade * r.Alimento.proteinas / 100 for r in registros)
        total_carboidratos = sum(r.RegistroAlimentar.quantidade * r.Alimento.carboidratos / 100 for r in registros)
        total_gorduras = sum(r.RegistroAlimentar.quantidade * r.Alimento.gorduras / 100 for r in registros)
        
        dias_com_registros = len(set(r.RegistroAlimentar.data.date() for r in registros))
        
        # Alimentos mais consumidos
        alimentos_freq = {}
        for r in registros:
            nome = r.Alimento.nome
            alimentos_freq[nome] = alimentos_freq.get(nome, 0) + 1
        
        alimentos_top = sorted(alimentos_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Preparar contexto para a IA
        contexto_nutricional = f"""
        ANÁLISE NUTRICIONAL DOS ÚLTIMOS {periodo} DIAS:
        
        Dados Gerais:
        - Total de calorias: {total_calorias:.0f} kcal
        - Média diária: {total_calorias/max(dias_com_registros, 1):.0f} kcal/dia
        - Proteínas totais: {total_proteinas:.1f}g
        - Carboidratos totais: {total_carboidratos:.1f}g  
        - Gorduras totais: {total_gorduras:.1f}g
        - Dias com registros: {dias_com_registros} de {periodo}
        
        Alimentos mais consumidos:
        {', '.join([f"{nome} ({freq}x)" for nome, freq in alimentos_top[:3]])}
        
        Como especialista em nutrição, forneça uma análise detalhada em formato JSON com:
        1. Resumo geral da alimentação
        2. Pontos positivos identificados
        3. Áreas que precisam melhorar
        4. Recomendações específicas e práticas
        5. Meta para a próxima semana
        
        Seja específico, motivacional e use dados brasileiros de alimentação.
        Responda APENAS em JSON válido com as chaves: resumo, pontos_positivos, areas_melhorar, recomendacoes, meta_proxima_semana.
        """
        
        response = modelo_ia.generate_content(contexto_nutricional)
        
        # Processar resposta da IA
        import json
        try:
            resposta_limpa = response.text.strip()
            if resposta_limpa.startswith('```json'):
                resposta_limpa = resposta_limpa[7:]
            if resposta_limpa.endswith('```'):
                resposta_limpa = resposta_limpa[:-3]
            
            insights_ia = json.loads(resposta_limpa)
            
            return jsonify({
                'sucesso': True,
                'periodo_analisado': periodo,
                'estatisticas': {
                    'total_calorias': round(total_calorias),
                    'media_diaria_calorias': round(total_calorias/max(dias_com_registros, 1)),
                    'total_proteinas': round(total_proteinas, 1),
                    'total_carboidratos': round(total_carboidratos, 1),
                    'total_gorduras': round(total_gorduras, 1),
                    'dias_ativos': dias_com_registros,
                    'alimentos_top': alimentos_top[:5]
                },
                'insights_ia': insights_ia
            })
            
        except json.JSONDecodeError:
            # Fallback se a IA não retornar JSON válido
            return jsonify({
                'sucesso': True,
                'periodo_analisado': periodo,
                'estatisticas': {
                    'total_calorias': round(total_calorias),
                    'media_diaria_calorias': round(total_calorias/max(dias_com_registros, 1)),
                    'total_proteinas': round(total_proteinas, 1),
                    'total_carboidratos': round(total_carboidratos, 1),
                    'total_gorduras': round(total_gorduras, 1),
                    'dias_ativos': dias_com_registros,
                    'alimentos_top': alimentos_top[:5]
                },
                'insights_ia': {
                    'resumo': 'Análise em processamento. Tente novamente em alguns segundos.',
                    'pontos_positivos': ['Dados coletados com sucesso'],
                    'areas_melhorar': ['Aguardando processamento da IA'],
                    'recomendacoes': ['Consulte novamente em alguns instantes'],
                    'meta_proxima_semana': 'Manter consistência no registro alimentar'
                },
                'resposta_bruta_ia': response.text
            })
        
    except Exception as e:
        return jsonify({
            'erro': f'Erro ao gerar insights: {str(e)}',
            'dica': 'Verifique se há dados suficientes no período selecionado'
        }), 500

# === DASHBOARD DE INSIGHTS ===

@app.route('/dashboard-insights')
def dashboard_insights():
    """
    Dashboard de Insights com IA - Análise inteligente dos padrões alimentares
    """
    user_id = request.args.get('id', '9185fb0a-a4ed-4345-9af4-e0e7698d3c83')
    return render_template('dashboard_insights.html', user_id=user_id)

@app.route('/api/ia/dashboard-insights', methods=['POST'])
def api_dashboard_insights():
    """
    API para gerar insights inteligentes sobre padrões alimentares
    """
    try:
        if not modelo_ia:
            return jsonify({
                'erro': 'IA não configurada. Configure GEMINI_API_KEY no arquivo .env'
            }), 400
            
        data = request.get_json()
        periodo = data.get('periodo', 7)  # Últimos 7 dias por padrão
        
        # Buscar dados do período
        from datetime import datetime, timedelta
        data_limite = datetime.now() - timedelta(days=periodo)
        
        registros = db.session.query(RegistroAlimentar, Alimento).join(Alimento).filter(
            RegistroAlimentar.usuario_id == 1,  # Demo user
            RegistroAlimentar.data >= data_limite
        ).all()
        
        if not registros:
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
        total_calorias = sum(r.RegistroAlimentar.quantidade * r.Alimento.calorias / 100 for r in registros)
        total_proteinas = sum(r.RegistroAlimentar.quantidade * r.Alimento.proteinas / 100 for r in registros)
        total_carboidratos = sum(r.RegistroAlimentar.quantidade * r.Alimento.carboidratos / 100 for r in registros)
        total_gorduras = sum(r.RegistroAlimentar.quantidade * r.Alimento.gorduras / 100 for r in registros)
        
        dias_com_registros = len(set(r.RegistroAlimentar.data.date() for r in registros))
        
        # Alimentos mais consumidos
        alimentos_freq = {}
        for r in registros:
            nome = r.Alimento.nome
            alimentos_freq[nome] = alimentos_freq.get(nome, 0) + 1
        
        alimentos_top = sorted(alimentos_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Preparar contexto para a IA
        contexto_nutricional = f"""
        ANÁLISE NUTRICIONAL DOS ÚLTIMOS {periodo} DIAS:
        
        Dados Gerais:
        - Total de calorias: {total_calorias:.0f} kcal
        - Média diária: {total_calorias/max(dias_com_registros, 1):.0f} kcal/dia
        - Proteínas totais: {total_proteinas:.1f}g
        - Carboidratos totais: {total_carboidratos:.1f}g  
        - Gorduras totais: {total_gorduras:.1f}g
        - Dias com registros: {dias_com_registros} de {periodo}
        
        Alimentos mais consumidos:
        {', '.join([f"{nome} ({freq}x)" for nome, freq in alimentos_top[:3]])}
        
        Como especialista em nutrição, forneça uma análise detalhada em formato JSON com:
        1. Resumo geral da alimentação
        2. Pontos positivos identificados
        3. Áreas que precisam melhorar
        4. Recomendações específicas e práticas
        5. Meta para a próxima semana
        
        Seja específico, motivacional e use dados brasileiros de alimentação.
        Responda APENAS em JSON válido com as chaves: resumo, pontos_positivos, areas_melhorar, recomendacoes, meta_proxima_semana.
        """
        
        response = modelo_ia.generate_content(contexto_nutricional)
        
        # Processar resposta da IA
        import json
        try:
            resposta_limpa = response.text.strip()
            if resposta_limpa.startswith('```json'):
                resposta_limpa = resposta_limpa[7:]
            if resposta_limpa.endswith('```'):
                resposta_limpa = resposta_limpa[:-3]
            
            insights_ia = json.loads(resposta_limpa)
            
            return jsonify({
                'sucesso': True,
                'periodo_analisado': periodo,
                'estatisticas': {
                    'total_calorias': round(total_calorias),
                    'media_diaria_calorias': round(total_calorias/max(dias_com_registros, 1)),
                    'total_proteinas': round(total_proteinas, 1),
                    'total_carboidratos': round(total_carboidratos, 1),
                    'total_gorduras': round(total_gorduras, 1),
                    'dias_ativos': dias_com_registros,
                    'total_registros': len(registros),
                    'alimentos_top': alimentos_top[:5]
                },
                'insights_ia': insights_ia
            })
            
        except json.JSONDecodeError:
            # Fallback se a IA não retornar JSON válido
            return jsonify({
                'sucesso': True,
                'periodo_analisado': periodo,
                'estatisticas': {
                    'total_calorias': round(total_calorias),
                    'media_diaria_calorias': round(total_calorias/max(dias_com_registros, 1)),
                    'total_proteinas': round(total_proteinas, 1),
                    'total_carboidratos': round(total_carboidratos, 1),
                    'total_gorduras': round(total_gorduras, 1),
                    'dias_ativos': dias_com_registros,
                    'total_registros': len(registros),
                    'alimentos_top': alimentos_top[:5]
                },
                'insights_ia': {
                    'resumo': f'Análise de {periodo} dias com {dias_com_registros} dias ativos e {len(registros)} registros.',
                    'pontos_positivos': [f'Você manteve registros em {dias_com_registros} dias', f'Total de {len(registros)} alimentos registrados'],
                    'areas_melhorar': ['Continue mantendo a consistência nos registros'],
                    'recomendacoes': ['Mantenha o foco em alimentos naturais e integrais'],
                    'meta_proxima_semana': 'Manter ou aumentar a frequência de registros alimentares'
                }
            })
        
    except Exception as e:
        return jsonify({
            'erro': f'Erro ao gerar insights: {str(e)}',
            'dica': 'Verifique se há dados suficientes no período selecionado'
        }), 500

# --- Rota de teste para verificação ---
@app.route('/api/teste', methods=['GET'])
def teste():
    return jsonify({'status': 'ok', 'mensagem': 'API está rodando!', 'arquivo': __file__}), 200

# --- Rota de teste simples para debug ---
@app.route('/teste')
def teste_simples():
    return "Servidor Flask está funcionando! 🎉"

if __name__ == '__main__':
    app.run(debug=True)
        
        # Alimentos favoritos baseados no histórico
        alimentos_favoritos = {}
        for registro in registros_recentes:
            alimento = registro.nome
            alimentos_favoritos[alimento] = alimentos_favoritos.get(alimento, 0) + 1
        
        favoritos_top = sorted(alimentos_favoritos.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Preparar prompt para IA
        restricoes_texto = ", ".join(restricoes) if restricoes else "Nenhuma restrição"
        favoritos_texto = ", ".join([f[0] for f in favoritos_top]) if favoritos_top else "Não identificados"
        
        prompt = f"""
        Você é um nutricionista especialista em planejamento de refeições.
        Crie um plano alimentar inteligente e personalizado para {dias_plano} dias.
        
        PARÂMETROS DO USUÁRIO:
        - Objetivo: {objetivo}
        - Restrições alimentares: {restricoes_texto}
        - Orçamento: {orcamento}
        - Tempo de preparo: {tempo_preparo}
        - Alimentos favoritos (baseado no histórico): {favoritos_texto}
        
        INSTRUÇÕES:
        1. Crie um plano variado e equilibrado
        2. Considere alimentos brasileiros e facilmente encontrados
        3. Ajuste as porções conforme o objetivo
        4. Inclua 5 refeições diárias: café da manhã, lanche manhã, almoço, lanche tarde, jantar
        5. Forneça dicas de preparo e substituições
        
        FORMATO DE RESPOSTA (JSON):
        {{
            "titulo_plano": "Plano para [objetivo] - [dias] dias",
            "resumo_nutricional": {{
                "calorias_media_dia": 0000,
                "proteinas_media_dia": 00,
                "carboidratos_media_dia": 000,
                "gorduras_media_dia": 00
            }},
            "dias": [
                {{
                    "dia": 1,
                    "data_sugerida": "Segunda-feira",
                    "refeicoes": {{
                        "cafe_da_manha": {{
                            "titulo": "Nome da refeição",
                            "ingredientes": ["ingrediente 1", "ingrediente 2"],
                            "modo_preparo": "Instruções rápidas",
                            "tempo_preparo": "X minutos",
                            "calorias_estimadas": 000
                        }},
                        "lanche_manha": {{ "titulo": "...", "ingredientes": [], "calorias_estimadas": 000 }},
                        "almoco": {{ "titulo": "...", "ingredientes": [], "modo_preparo": "...", "calorias_estimadas": 000 }},
                        "lanche_tarde": {{ "titulo": "...", "ingredientes": [], "calorias_estimadas": 000 }},
                        "jantar": {{ "titulo": "...", "ingredientes": [], "modo_preparo": "...", "calorias_estimadas": 000 }}
                    }}
                }}
            ],
            "lista_compras": {{
                "proteinas": ["item 1", "item 2"],
                "carboidratos": ["item 1", "item 2"],
                "vegetais": ["item 1", "item 2"],
                "frutas": ["item 1", "item 2"],
                "laticínios": ["item 1", "item 2"],
                "outros": ["item 1", "item 2"]
            }},
            "dicas_especiais": [
                "Dica 1 para otimizar o plano",
                "Dica 2 sobre preparo"
            ],
            "substituicoes_inteligentes": {{
                "se_nao_gostar_de_X": "pode_substituir_por_Y",
                "opcao_economica": "sugestão_mais_barata"
            }}
        }}
        
        Seja criativo, prático e considere a realidade brasileira. Inclua apenas alimentos da nossa base de dados quando possível.
        """
        
        # Chamar IA
        response = modelo_ia.generate_content(prompt)
        
        # Processar resposta
        import json
        try:
            resposta_limpa = response.text.strip()
            if resposta_limpa.startswith('```json'):
                resposta_limpa = resposta_limpa[7:]
            if resposta_limpa.endswith('```'):
                resposta_limpa = resposta_limpa[:-3]