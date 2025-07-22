"""
🔧 MODELO USUARIO TEMPORÁRIO - APENAS COLUNAS EXISTENTES
Arquivo para substituir temporariamente o modelo Usuario no app.py

USAR APENAS ATÉ ADICIONAR AS COLUNAS NO BANCO!
"""

# MODELO TEMPORÁRIO - APENAS COLUNAS QUE EXISTEM NO BANCO
class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    # COLUNAS QUE EXISTEM NO BANCO (11 colunas básicas)
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
    
    # CAMPOS TEMPORARIAMENTE REMOVIDOS (até adicionar no banco):
    # email_verificado = db.Column(db.Boolean, default=False, nullable=False)
    # token_verificacao = db.Column(db.String(255), nullable=True)
    # token_expiracao = db.Column(db.DateTime, nullable=True)
    # data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    # ultimo_login = db.Column(db.DateTime, nullable=True)
    # onboarding_completo = db.Column(db.Boolean, default=False, nullable=False)
    # dados_questionario = db.Column(db.JSON, nullable=True)
    # plano_personalizado = db.Column(db.JSON, nullable=True)
    # dicas_l7chef = db.Column(db.JSON, nullable=True)
    # analise_nutricional = db.Column(db.JSON, nullable=True)
    # tentativas_login = db.Column(db.Integer, default=0, nullable=False)
    # bloqueado_ate = db.Column(db.DateTime, nullable=True)
    # ip_cadastro = db.Column(db.String(45), nullable=True)

    def __repr__(self):
        return f'<Usuario {self.username}>'

    def to_dict(self):
        """Converte o usuário para dicionário (compatibilidade)"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'username': self.username,
            'idade': self.idade,
            'sexo': self.sexo,
            'peso': self.peso,
            'altura': self.altura,
            'nivel_atividade': self.nivel_atividade,
            'objetivo': self.objetivo,
            # Campos avançados com valores padrão para compatibilidade
            'email_verificado': False,
            'token_verificacao': None,
            'token_expiracao': None,
            'data_criacao': None,
            'ultimo_login': None,
            'onboarding_completo': False,
            'dados_questionario': None,
            'plano_personalizado': None,
            'dicas_l7chef': None,
            'analise_nutricional': None,
            'tentativas_login': 0,
            'bloqueado_ate': None,
            'ip_cadastro': None
        }

print("📋 INSTRUÇÕES PARA USO:")
print("1. Substitua o modelo Usuario no app.py pelo código acima")
print("2. Faça deploy da aplicação")
print("3. Teste o cadastro (deve funcionar)")
print("4. Adicione as colunas no banco usando adicionar_colunas.sql")
print("5. Restaure o modelo completo")
print()
print("⚠️  TEMPORÁRIO: Este modelo só tem as 11 colunas básicas")
print("✅ FUNCIONAL: Cadastro e login vão funcionar normalmente")
