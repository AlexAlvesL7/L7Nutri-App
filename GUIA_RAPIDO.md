# 🎯 GUIA RÁPIDO - DEPLOY HOSTINGER

## ✅ CHECKLIST COMPLETO PARA DEPLOY

### 📋 ANTES DO UPLOAD (Execute no VS Code)

```bash
# 1. Instalar driver MySQL
pip install PyMySQL

# 2. Configurar banco automaticamente
python config_hostinger.py

# 3. Validar configuração
python validar_deploy.py

# 4. Compactar arquivos para upload
```

### 🚀 NA HOSTINGER (Execute no painel)

```bash
# 1. Upload dos arquivos para public_html

# 2. Configurar Aplicação Python:
#    - Versão: Python 3.9+
#    - Pasta: /public_html
#    - Arquivo: app.py
#    - WSGI: app

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Criar tabelas no banco
python setup_mysql.py

# 5. Adicionar dados iniciais
python init_producao.py
```

## 🔑 SUAS CREDENCIAIS ATUALIZADAS

```
✅ Banco MySQL Hostinger:
   • Usuário: u419790683_l7nutri_alex
   • Senha: Duda@1401
   • Host: 127.0.0.1
   • Banco: u419790683_l7nutri_novo

✅ Login Inicial da Aplicação:
   • Usuário: admin
   • Senha: admin123
```

## 🎉 APÓS DEPLOY - TESTAR

1. **Home**: `https://seudominio.com/`
2. **Login**: `https://seudominio.com/login`
3. **Dashboard IA**: `https://seudominio.com/dashboard-insights`

## 📞 PROBLEMAS COMUNS

### ❌ Erro de Conexão MySQL
```bash
# Verificar se PyMySQL está instalado
pip list | grep PyMySQL

# Testar conexão
python setup_mysql.py
```

### ❌ Erro 500 (Internal Server Error)
```bash
# Ver logs de erro no painel Hostinger
# Verificar se todas as dependências foram instaladas
pip install -r requirements.txt
```

### ❌ IA não funciona
```bash
# Configurar GEMINI_API_KEY no arquivo .env
# Ou adicionar diretamente no app.py:
# gemini_api_key = "sua_chave_aqui"
```

## 🚀 SUA APLICAÇÃO TERÁ

✅ **Sistema de Login/Cadastro Visual**
✅ **Dashboard de IA com Google Gemini**  
✅ **Diário Alimentar Completo**
✅ **Base de 15+ Alimentos Nutritivos**
✅ **Interface Responsiva e Moderna**
✅ **Suporte Multi-usuário**

**🎯 Pronto para receber usuários reais!**
