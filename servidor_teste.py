#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template_string
import sqlite3
import os

app = Flask(__name__)

# Template HTML simples
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>L7Nutri - Sistema de Nutrição</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c5530; border-bottom: 3px solid #4a7c59; padding-bottom: 10px; }
        .status { padding: 15px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .info { background: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }
        .login-link { display: inline-block; background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 10px 5px; }
        .login-link:hover { background: #218838; }
        .stats { display: flex; gap: 20px; margin: 20px 0; }
        .stat-card { background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; flex: 1; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🥗 L7Nutri - Sistema de Nutrição</h1>
        
        <div class="status success">
            ✅ <strong>Sistema Funcionando!</strong>
        </div>
        
        <div class="status info">
            📊 <strong>Status do Banco de Dados:</strong><br>
            {{ db_status }}
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>{{ total_alimentos }}</h3>
                <p>Alimentos Cadastrados</p>
            </div>
            <div class="stat-card">
                <h3>{{ total_usuarios }}</h3>
                <p>Usuários Registrados</p>
            </div>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="/login" class="login-link">🔐 Fazer Login</a>
            <a href="/registro" class="login-link">📝 Criar Conta</a>
            <a href="/alimentos" class="login-link">🍎 Ver Alimentos</a>
        </div>
        
        <div class="status info">
            <strong>Credenciais de Teste:</strong><br>
            👤 Usuário: <code>admin</code><br>
            🔑 Senha: <code>admin123</code>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    # Verificar banco de dados
    if os.path.exists('nutricao.db'):
        try:
            conn = sqlite3.connect('nutricao.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM alimento")
            total_alimentos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM usuario")
            total_usuarios = cursor.fetchone()[0]
            
            conn.close()
            
            db_status = f"✅ Banco conectado ({total_alimentos} alimentos, {total_usuarios} usuários)"
            
        except Exception as e:
            total_alimentos = 0
            total_usuarios = 0
            db_status = f"❌ Erro no banco: {str(e)}"
    else:
        total_alimentos = 0
        total_usuarios = 0
        db_status = "❌ Banco nutricao.db não encontrado"
    
    return render_template_string(HOME_TEMPLATE, 
                                  db_status=db_status,
                                  total_alimentos=total_alimentos,
                                  total_usuarios=total_usuarios)

@app.route('/login')
def login():
    return """
    <h1>🔐 Login L7Nutri</h1>
    <p>Sistema de login em desenvolvimento...</p>
    <p><a href="/">← Voltar</a></p>
    """

@app.route('/registro')
def registro():
    return """
    <h1>📝 Registro L7Nutri</h1>
    <p>Sistema de registro em desenvolvimento...</p>
    <p><a href="/">← Voltar</a></p>
    """

@app.route('/alimentos')
def alimentos():
    if os.path.exists('nutricao.db'):
        try:
            conn = sqlite3.connect('nutricao.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT nome, categoria, energia, proteina FROM alimento LIMIT 10")
            alimentos = cursor.fetchall()
            
            conn.close()
            
            html = "<h1>🍎 Alimentos Cadastrados</h1>"
            html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
            html += "<tr><th>Nome</th><th>Categoria</th><th>Energia (kcal)</th><th>Proteína (g)</th></tr>"
            
            for alimento in alimentos:
                html += f"<tr><td>{alimento[0]}</td><td>{alimento[1]}</td><td>{alimento[2]}</td><td>{alimento[3]}</td></tr>"
            
            html += "</table>"
            html += "<p><a href='/'>← Voltar</a></p>"
            
            return html
            
        except Exception as e:
            return f"<h1>❌ Erro ao acessar alimentos</h1><p>{str(e)}</p><p><a href='/'>← Voltar</a></p>"
    else:
        return "<h1>❌ Banco não encontrado</h1><p><a href='/'>← Voltar</a></p>"

if __name__ == '__main__':
    print("🚀 Iniciando L7Nutri...")
    print("🌐 Acesse: http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
