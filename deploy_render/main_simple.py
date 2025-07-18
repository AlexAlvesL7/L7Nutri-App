#!/usr/bin/env python3
"""
L7Nutri - Aplicação Nutricional
Versão Simplificada para Deploy Render
"""
import os
import sys
from datetime import datetime

print("=== L7NUTRI INICIANDO ===")

try:
    # Importar Flask
    from flask import Flask, jsonify, request
    print("✓ Flask importado")
    
    # Criar aplicação
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'l7nutri-secret-key-2025'
    print("✓ App Flask criado")
    
    # Rota principal
    @app.route('/')
    def home():
        return f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>L7Nutri - Aplicação Nutricional</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: white;
                }}
                .container {{
                    background: rgba(255,255,255,0.95);
                    padding: 40px;
                    border-radius: 15px;
                    color: #333;
                    text-align: center;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }}
                h1 {{
                    color: #28a745;
                    margin-bottom: 20px;
                    font-size: 2.5em;
                }}
                .status {{
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 8px;
                    font-weight: bold;
                }}
                .success {{
                    background: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }}
                .info {{
                    background: #d1ecf1;
                    color: #0c5460;
                    border: 1px solid #bee5eb;
                }}
                .button {{
                    display: inline-block;
                    background: #007bff;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 10px;
                    font-weight: bold;
                }}
                .button:hover {{
                    background: #0056b3;
                }}
                .env-info {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                    text-align: left;
                    font-family: monospace;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🥗 L7Nutri</h1>
                <p style="font-size: 1.2em; margin-bottom: 30px;">Sistema de Monitoramento Nutricional</p>
                
                <div class="status success">
                    ✅ Aplicação funcionando perfeitamente!
                </div>
                
                <div class="status info">
                    🚀 Deploy Render - Versão Simplificada
                </div>
                
                <div class="env-info">
                    <strong>📊 Informações do Sistema:</strong><br>
                    • Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                    • Porta: {os.getenv('PORT', 5000)}<br>
                    • Banco: {'PostgreSQL' if os.getenv('DATABASE_URL') else 'SQLite'}<br>
                    • Status: Operacional
                </div>
                
                <div>
                    <a href="/api/health" class="button">🏥 Health Check</a>
                    <a href="/api/status" class="button">📊 Status API</a>
                </div>
                
                <hr style="margin: 30px 0;">
                
                <p><strong>🎯 Próximos Passos:</strong></p>
                <ol style="text-align: left; max-width: 400px; margin: 0 auto;">
                    <li>Aplicação básica funcionando ✅</li>
                    <li>Adicionar sistema de login</li>
                    <li>Integrar banco de dados</li>
                    <li>Implementar recursos nutricionais</li>
                </ol>
                
                <hr style="margin: 30px 0;">
                
                <p><small>
                    <strong>L7Nutri</strong> - Desenvolvido por Alex Alves<br>
                    Versão 1.0 - {datetime.now().strftime('%B %Y')}
                </small></p>
            </div>
        </body>
        </html>
        """
    
    # API Health Check
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'OK',
            'message': 'L7Nutri funcionando perfeitamente',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0-simplified'
        })
    
    # API Status
    @app.route('/api/status')
    def api_status():
        return jsonify({
            'application': 'L7Nutri',
            'status': 'running',
            'environment': {{
                'port': os.getenv('PORT', 5000),
                'database': 'postgresql' if os.getenv('DATABASE_URL') else 'sqlite',
                'flask_env': os.getenv('FLASK_ENV', 'production')
            }},
            'timestamp': datetime.now().isoformat(),
            'uptime': 'Sistema operacional'
        })
    
    # Rota de teste para formulário
    @app.route('/teste')
    def teste():
        return '''
        <h2>Teste de Formulário</h2>
        <form method="POST" action="/api/teste">
            <input type="text" name="nome" placeholder="Seu nome" required>
            <button type="submit">Enviar</button>
        </form>
        '''
    
    @app.route('/api/teste', methods=['POST'])
    def api_teste():
        nome = request.form.get('nome', 'Usuário')
        return jsonify({
            'message': f'Olá, {nome}! Formulário funcionando.',
            'timestamp': datetime.now().isoformat()
        })
    
    # Handler de erro
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'erro': 'Rota não encontrada'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'erro': 'Erro interno do servidor'}), 500
    
    print("✓ Rotas configuradas")
    
    # Iniciar servidor
    if __name__ == '__main__':
        port = int(os.getenv('PORT', 5000))
        print(f"✓ Iniciando servidor na porta {port}")
        print("=== L7NUTRI PRONTO ===")
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False
        )

except Exception as e:
    print(f"❌ ERRO CRÍTICO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
