from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>L7Nutri - FUNCIONANDO!</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px; 
                background: linear-gradient(135deg, #28a745, #20c997);
                color: white;
                margin: 0;
                min-height: 100vh;
            }
            .container { 
                background: white; 
                color: #333; 
                padding: 50px; 
                border-radius: 15px; 
                max-width: 600px; 
                margin: 0 auto;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            h1 { 
                color: #28a745; 
                font-size: 4em; 
                margin-bottom: 20px;
            }
            .success { 
                color: #28a745; 
                font-size: 28px; 
                font-weight: bold; 
                margin: 30px 0;
                padding: 20px;
                background: #d4edda;
                border: 3px solid #c3e6cb;
                border-radius: 10px;
            }
            .info {
                font-size: 18px;
                margin: 20px 0;
                line-height: 1.6;
            }
            .button { 
                background: #28a745; 
                color: white; 
                padding: 15px 30px; 
                text-decoration: none; 
                border-radius: 25px; 
                margin: 15px; 
                display: inline-block;
                font-size: 16px;
                font-weight: bold;
                transition: all 0.3s;
            }
            .button:hover {
                background: #218838;
                transform: translateY(-2px);
            }
            .footer {
                margin-top: 30px;
                font-size: 14px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🥗 L7Nutri</h1>
            <div class="success">✅ FUNCIONANDO 100%!</div>
            <div class="info">
                <strong>🎉 PARABÉNS!</strong><br><br>
                Seu aplicativo de nutrição está <strong>online e funcionando</strong> no Render!<br>
                Deploy realizado com sucesso!
            </div>
            <a href="/test" class="button">🧪 Testar API</a>
            <a href="/status" class="button">📊 Ver Status</a>
            <div class="footer">
                Platform: Render | Status: Online | L7Nutri v1.0
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.route('/test')
def test_api():
    return jsonify({
        'status': 'success',
        'message': 'L7Nutri API funcionando perfeitamente!',
        'app': 'L7Nutri',
        'version': '1.0.0',
        'platform': 'Render',
        'timestamp': '2025-07-18'
    })

@app.route('/status')
def status():
    return jsonify({
        'status': 'online',
        'app': 'L7Nutri - Sistema de Nutrição',
        'platform': 'Render',
        'health': 'OK',
        'message': 'Sistema funcionando perfeitamente!'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
