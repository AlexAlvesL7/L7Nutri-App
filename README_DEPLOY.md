# 🚀 DEPLOY L7NUTRI NA HOSTINGER

Guia completo para fazer deploy da aplicação L7Nutri na hospedagem Hostinger.

## 📋 PRÉ-REQUISITOS

### 1. Conta Hostinger
- Plano com suporte a Python (Premium ou Business)
- Banco de dados MySQL disponível
- Acesso ao painel de controle

### 2. Chave da API Google Gemini
- Acesse: https://makersuite.google.com/app/apikey
- Gere sua chave da API
- Guarde a chave para configuração

## 🗄️ CONFIGURAÇÃO DO BANCO DE DADOS

### 1. Criar Banco MySQL na Hostinger
1. Acesse o painel da Hostinger
2. Vá em **Bancos de Dados MySQL**
3. Clique em **Criar Novo Banco**
4. Configure:
   - **Nome do banco**: `l7nutri_db`
   - **Usuário**: `l7nutri_user`
   - **Senha**: Gere uma senha forte
5. **Anote os dados**: host, porta, nome do banco, usuário e senha

### 2. Exemplo de Dados do Banco
```
Host: srv1234.hstgr.io
Porta: 3306
Banco: u123456789_l7nutri
Usuário: u123456789_l7nutri
Senha: MinhaSenh@123
```

## ⚙️ CONFIGURAÇÃO DA APLICAÇÃO

### 1. Instalar Driver MySQL
Primeiro, instale o "tradutor" para MySQL:

```bash
pip install PyMySQL
```

### 2. Configurar Conexão Diretamente no app.py
**OPÇÃO A: Configuração Direta (Mais Simples)**

Abra o arquivo `app.py` e encontre a linha de configuração do banco. Substitua por:

```python
# === CONFIGURAÇÃO DO BANCO DE DADOS ===
# Suas credenciais REAIS da Hostinger
db_user = 'u419790683_l7nutri_user'
db_pass = 'Duda@1401'
db_host = 'localhost'  # Para Hostinger, geralmente é localhost
db_name = 'u419790683_l7nutri_db'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}'
```

**OPÇÃO B: Usando Variáveis de Ambiente (.env)**

1. Copie o arquivo `env_template.txt` para `.env`
2. Configure as variáveis:

```env
# === CONFIGURAÇÃO DE PRODUÇÃO ===
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=SuaChaveSecretaSuperForteMais32Caracteres

# === BANCO DE DADOS ===
DATABASE_URL=mysql+pymysql://u419790683_l7nutri_user:Duda@1401@localhost/u419790683_l7nutri_db

# === GOOGLE GEMINI AI ===
GEMINI_API_KEY=sua_chave_gemini_aqui

# === JWT ===
JWT_SECRET_KEY=SuaChaveJWTSuperSecretaMais32Caracteres
JWT_ACCESS_TOKEN_EXPIRES=86400
```

### 3. Criar Tabelas no Banco MySQL
Após configurar a conexão, execute:

```bash
flask db upgrade
```

Se não funcionar, use o script de inicialização:

```bash
python init_producao.py
```

### 4. Instalar Dependências
```bash
pip install -r requirements.txt
```

## 📁 ESTRUTURA DE ARQUIVOS PARA UPLOAD

Organize seus arquivos assim antes do upload:

```
l7nutri/
├── app.py                 # Aplicação principal
├── requirements.txt       # Dependências
├── gunicorn.conf.py      # Configuração do servidor
├── .env                  # Variáveis de ambiente (configurar)
├── init_producao.py      # Script de inicialização
├── templates/            # Templates HTML
│   ├── home.html
│   ├── login.html
│   ├── cadastro.html
│   ├── logout.html
│   ├── diario_alimentar.html
│   └── dashboard_insights.html
└── static/              # Arquivos estáticos (se houver)
```

## 🚀 PROCESSO DE DEPLOY

### 1. Preparação Local (Execute ANTES do upload)

**Passo 1: Instalar Driver MySQL**
```bash
pip install PyMySQL
```

**Passo 2: Configurar para Produção**
Execute o script automático:
```bash
python config_hostinger.py
```

OU configure manualmente editando `app.py` conforme mostrado na seção anterior.

**Passo 3: Testar Configuração MySQL** (Opcional - se estiver testando localmente)
```bash
python setup_mysql.py
```

### 2. Upload dos Arquivos
1. Comprima todos os arquivos em um ZIP
2. Acesse o **File Manager** da Hostinger
3. Navegue até a pasta `public_html`
4. Faça upload e extraia os arquivos

### 3. Configurar Aplicação Python na Hostinger
1. No painel Hostinger, vá em **Aplicação Python**
2. Clique em **Criar Aplicação**
3. Configure:
   - **Versão Python**: 3.9 ou superior
   - **Pasta da aplicação**: `/public_html`
   - **Arquivo principal**: `app.py`
   - **Variável WSGI**: `app`

### 4. Instalar Dependências na Hostinger
No terminal da Hostinger (ou via painel):
```bash
cd public_html
pip install -r requirements.txt
```

### 5. Criar Tabelas no Banco MySQL
Execute um dos scripts:
```bash
# Opção 1: Script específico para MySQL
python setup_mysql.py

# Opção 2: Script completo de inicialização
python init_producao.py

# Opção 3: Usando Flask-Migrate (se disponível)
flask db upgrade
```

## 🔧 CONFIGURAÇÃO FINAL

### 1. Arquivo WSGI (se necessário)
Crie um arquivo `wsgi.py`:
```python
from app import app

if __name__ == "__main__":
    app.run()
```

### 2. Verificar Funcionamento
1. Acesse sua URL da Hostinger
2. Teste o login com: `admin` / `admin123`
3. Verifique se o dashboard de IA funciona
4. Teste o registro de alimentos

## 🎯 FUNCIONALIDADES DISPONÍVEIS

Após o deploy, sua aplicação terá:

✅ **Sistema de Autenticação**
- Login e cadastro de usuários
- Sistema de logout
- Autenticação JWT

✅ **Diário Alimentar**
- Registro de refeições
- Busca de alimentos
- Histórico de consumo

✅ **Dashboard de IA**
- Análise inteligente com Google Gemini
- Insights nutricionais personalizados
- Recomendações baseadas em dados

✅ **Base de Alimentos**
- Verduras e legumes
- Proteínas e carboidratos
- Oleaginosas e industrializados

## 🔍 SOLUÇÃO DE PROBLEMAS

### Erro de Conexão com Banco
- Verifique `DATABASE_URL` no arquivo `.env`
- Confirme credenciais do MySQL na Hostinger
- Teste conexão no painel de banco de dados

### Erro 500 (Internal Server Error)
- Verifique logs de erro na Hostinger
- Confirme que todas as dependências foram instaladas
- Verifique se `GEMINI_API_KEY` está configurada

### IA não funciona
- Verifique se `GEMINI_API_KEY` está correta
- Teste a chave em: https://makersuite.google.com/
- Confirme que a API está ativada

## 📞 SUPORTE

Se encontrar problemas:
1. Verifique os logs de erro da Hostinger
2. Confirme todas as configurações
3. Teste cada funcionalidade separadamente

## 🎉 PRONTO!

Sua aplicação L7Nutri está agora rodando em produção na Hostinger!

**URLs importantes:**
- **Home**: `https://seudominio.com/`
- **Login**: `https://seudominio.com/login`
- **Dashboard**: `https://seudominio.com/dashboard-insights`

**Credenciais iniciais:**
- **Usuário**: `admin`
- **Senha**: `admin123`

**🔒 Importante**: Altere a senha do admin após o primeiro login!
