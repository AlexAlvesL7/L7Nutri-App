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
        <title>L7Nutri - Funcionando!</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f0f0; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #28a745; }
            .success { color: #28a745; font-size: 18px; }
            .info { color: #666; margin: 20px 0; }
            .button { display: inline-block; background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px; }
            .button:hover { background: #218838; }
            .timestamp { font-size: 12px; color: #999; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🥗 L7Nutri App</h1>
            <div class="success">✅ Sistema funcionando perfeitamente!</div>
            <div class="info">
                Seu aplicativo de nutrição está online e operacional no Render!
            </div>
            <a href="/api/test" class="button">Testar API</a>
            <a href="/status" class="button">Ver Status</a>
            <div class="timestamp">
                Deployed: {{ timestamp }}
            </div>
        </div>
    </body>
    </html>
    """, timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/api/test')
def api_test():
    return jsonify({
        'status': 'success',
        'message': 'API funcionando!',
        'timestamp': datetime.now().isoformat(),
        'app': 'L7Nutri',
        'version': '1.0.0'
    })

@app.route('/status')
def status():
    return jsonify({
        'status': 'online',
        'app': 'L7Nutri',
        'platform': 'Render',
        'python_version': '3.x',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
