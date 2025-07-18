#!/usr/bin/env python3
"""
L7Nutri - Versão Ultra Simples para Diagnóstico
"""
import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    logger.info("=== INICIANDO L7NUTRI - VERSÃO DIAGNÓSTICO ===")
    
    # Importar Flask
    from flask import Flask, jsonify, render_template_string
    logger.info("✓ Flask importado com sucesso")
    
    # Criar app Flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'l7nutri-secret-key-2025'
    logger.info("✓ App Flask criado")
    
    # Template HTML inline
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>L7Nutri - Diagnóstico</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                background: rgba(255,255,255,0.95);
                padding: 40px;
                border-radius: 15px;
                color: #333;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            h1 {
                color: #28a745;
                margin-bottom: 20px;
            }
            .status {
                padding: 15px;
                margin: 15px 0;
                border-radius: 8px;
                font-weight: bold;
            }
            .success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .info {
                background: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }
            .button {
                display: inline-block;
                background: #007bff;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 6px;
                margin: 10px;
                font-weight: bold;
            }
            .env-vars {
                text-align: left;
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                font-family: monospace;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🥗 L7Nutri - Diagnóstico</h1>
            
            <div class="status success">
                ✅ Aplicação Flask funcionando!
            </div>
            
            <div class="status info">
                🚀 Deploy Render - Versão de Diagnóstico
            </div>
            
            <p><strong>Timestamp:</strong> {{ timestamp }}</p>
            
            <div class="env-vars">
                <strong>🔧 Variáveis de Ambiente:</strong><br>
                • DATABASE_URL: {{ 'Configurada' if database_url else 'Não configurada' }}<br>
                • GEMINI_API_KEY: {{ 'Configurada' if gemini_key else 'Não configurada' }}<br>
                • PORT: {{ port }}<br>
                • FLASK_ENV: {{ flask_env }}
            </div>
            
            <div>
                <a href="/health" class="button">🏥 Health Check</a>
                <a href="/test-db" class="button">🗄️ Teste DB</a>
            </div>
            
            <hr style="margin: 30px 0;">
            
            <p><small>
                <strong>L7Nutri</strong> - Sistema de Monitoramento Nutricional<br>
                Versão de Diagnóstico para Render
            </small></p>
        </div>
    </body>
    </html>
    """
    
    # Rotas
    @app.route('/')
    def index():
        logger.info("Rota / acessada")
        return render_template_string(HTML_TEMPLATE, 
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            database_url=bool(os.getenv('DATABASE_URL')),
            gemini_key=bool(os.getenv('GEMINI_API_KEY')),
            port=os.getenv('PORT', 5000),
            flask_env=os.getenv('FLASK_ENV', 'development')
        )
    
    @app.route('/health')
    def health():
        logger.info("Health check acessado")
        return jsonify({
            'status': 'OK',
            'app': 'L7Nutri',
            'version': 'diagnosis',
            'timestamp': datetime.now().isoformat(),
            'environment': {
                'database_url': 'configured' if os.getenv('DATABASE_URL') else 'not_configured',
                'gemini_api_key': 'configured' if os.getenv('GEMINI_API_KEY') else 'not_configured',
                'port': os.getenv('PORT', 5000),
                'flask_env': os.getenv('FLASK_ENV', 'development')
            }
        })
    
    @app.route('/test-db')
    def test_db():
        logger.info("Teste de banco acessado")
        
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            return jsonify({
                'status': 'ERROR',
                'message': 'DATABASE_URL não configurada'
            })
        
        try:
            # Importar psycopg2 apenas quando necessário
            import psycopg2
            from urllib.parse import urlparse
            
            # Corrigir URL se necessário
            if DATABASE_URL.startswith('postgres://'):
                DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
            
            parsed = urlparse(DATABASE_URL)
            
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password
            )
            
            cursor = conn.cursor()
            cursor.execute('SELECT version();')
            version = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'status': 'SUCCESS',
                'message': 'Conexão com banco bem-sucedida',
                'database_version': version[0][:100] + '...' if version else 'N/A'
            })
            
        except Exception as e:
            logger.error(f"Erro ao conectar com banco: {e}")
            return jsonify({
                'status': 'ERROR',
                'message': f'Erro ao conectar com banco: {str(e)}'
            })
    
    # Handler de erro global
    @app.errorhandler(Exception)
    def handle_error(error):
        logger.error(f"Erro: {error}")
        return jsonify({
            'status': 'ERROR',
            'message': str(error)
        }), 500
    
    logger.info("✓ Rotas configuradas")
    logger.info("=== L7NUTRI DIAGNÓSTICO PRONTO ===")
    
    if __name__ == '__main__':
        port = int(os.getenv('PORT', 5000))
        logger.info(f"Iniciando servidor na porta {port}")
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False
        )

except Exception as e:
    logger.error(f"ERRO CRÍTICO: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)
