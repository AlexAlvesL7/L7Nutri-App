# Atualizações para o modelo Usuario para incluir sistema de verificação
# Adicione estes campos ao modelo Usuario existente

# Campos para sistema de verificação de email
email_verificado = db.Column(db.Boolean, default=False, nullable=False)
token_verificacao = db.Column(db.String(255), nullable=True)
token_expiracao = db.Column(db.DateTime, nullable=True)
data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
ultimo_login = db.Column(db.DateTime, nullable=True)

# Campos para sistema de onboarding
onboarding_completo = db.Column(db.Boolean, default=False, nullable=False)
dados_questionario = db.Column(db.JSON, nullable=True)
plano_personalizado = db.Column(db.JSON, nullable=True)
dicas_l7chef = db.Column(db.JSON, nullable=True)

# Campos de segurança adicional
tentativas_login = db.Column(db.Integer, default=0)
bloqueado_ate = db.Column(db.DateTime, nullable=True)
ip_cadastro = db.Column(db.String(45), nullable=True)  # Suporta IPv6

# Modelo Usuario atualizado completo:

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

    # Campos de segurança
    tentativas_login = db.Column(db.Integer, default=0)
    bloqueado_ate = db.Column(db.DateTime, nullable=True)
    ip_cadastro = db.Column(db.String(45), nullable=True)

    alergias = db.relationship('AlergiaUsuario', backref='usuario', lazy=True)
    preferencias = db.relationship('PreferenciaUsuario', backref='usuario', lazy=True)
    registros_alimentares = db.relationship('RegistroAlimentar', backref='usuario', lazy=True)
    planos_sugeridos = db.relationship('PlanoSugestao', backref='usuario', lazy=True)

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
