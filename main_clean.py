from flask import Flask, jsonify, render_template_string
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>L7Nutri - Sistema Online!</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: 'Arial', sans-serif; 
                text-align: center; 
                padding: 50px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin: 0;
                min-height: 100vh;
            }
            .container { 
                max-width: 600px; 
                margin: 0 auto; 
                background: rgba(255,255,255,0.95); 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                color: #333;
            }
            h1 { 
                color: #28a745; 
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }
            .success { 
                color: #28a745; 
                font-size: 20px; 
                font-weight: bold;
                margin: 20px 0;
                padding: 15px;
                background: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 8px;
            }
            .info { 
                color: #666; 
                margin: 20px 0; 
                font-size: 16px;
                line-height: 1.6;
            }
            .button { 
                display: inline-block; 
                background: #28a745; 
                color: white; 
                padding: 15px 30px; 
                text-decoration: none; 
                border-radius: 25px; 
                margin: 10px; 
                font-weight: bold;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(40,167,69,0.3);
            }
            .button:hover { 
                background: #218838; 
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(40,167,69,0.4);
            }
            .timestamp { 
                font-size: 12px; 
                color: #999; 
                margin-top: 30px;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 5px;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin: 30px 0;
                text-align: left;
            }
            .feature {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #28a745;
            }
            .feature h3 {
                color: #28a745;
                margin-top: 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🥗 L7Nutri App</h1>
            <div class="success">✅ Sistema Online e Funcionando!</div>
            <div class="info">
                <strong>Parabéns!</strong> Seu aplicativo de nutrição está online e operacional no Render!
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🚀 Deploy Realizado</h3>
                    <p>Aplicação hospedada no Render com sucesso</p>
                </div>
                <div class="feature">
                    <h3>🔗 APIs Funcionando</h3>
                    <p>Sistema de rotas e endpoints operacionais</p>
                </div>
                <div class="feature">
                    <h3>📱 Interface Responsiva</h3>
                    <p>Design adaptável para todos os dispositivos</p>
                </div>
                <div class="feature">
                    <h3>⚡ Performance Otimizada</h3>
                    <p>Código limpo e eficiente</p>
                </div>
            </div>
            
            <a href="/api/test" class="button">🧪 Testar API</a>
            <a href="/status" class="button">📊 Ver Status</a>
            
            <div class="timestamp">
                🕒 Deployed: {{ timestamp }}<br>
                🌐 URL: {{ url }}<br>
                ⚡ Status: Online
            </div>
        </div>
    </body>
    </html>
    """, 
    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    url='https://l7nutri-app.onrender.com'
    )

@app.route('/api/test')
def api_test():
    return jsonify({
        'status': 'success',
        'message': 'API funcionando perfeitamente!',
        'timestamp': datetime.now().isoformat(),
        'app': 'L7Nutri',
        'version': '1.0.0',
        'platform': 'Render',
        'endpoints': {
            'home': '/',
            'api_test': '/api/test',
            'status': '/status'
        }
    })

@app.route('/status')
def status():
    return jsonify({
        'status': 'online',
        'app': 'L7Nutri - Sistema de Nutrição',
        'platform': 'Render',
        'python_version': '3.x',
        'flask_version': '3.0.0',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'Active',
        'health': 'OK',
        'endpoints': [
            {'path': '/', 'method': 'GET', 'description': 'Homepage'},
            {'path': '/api/test', 'method': 'GET', 'description': 'API Test'},
            {'path': '/status', 'method': 'GET', 'description': 'System Status'}
        ]
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint não encontrado',
        'message': 'Verifique a URL e tente novamente',
        'available_endpoints': ['/', '/api/test', '/status']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Erro interno do servidor',
        'message': 'Tente novamente em alguns instantes',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
