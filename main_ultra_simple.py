from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>L7Nutri - FUNCIONANDO!</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #28a745; color: white; }
            .container { background: white; color: #333; padding: 40px; border-radius: 10px; max-width: 500px; margin: 0 auto; }
            h1 { color: #28a745; font-size: 3em; }
            .success { color: #28a745; font-size: 24px; font-weight: bold; margin: 20px 0; }
            .button { background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🥗 L7Nutri</h1>
            <div class="success">✅ FUNCIONANDO 100%!</div>
            <p>Seu aplicativo está online no Render!</p>
            <a href="/test" class="button">Testar API</a>
            <a href="/status" class="button">Status</a>
        </div>
    </body>
    </html>
    '''

@app.route('/test')
def test():
    return jsonify({
        'status': 'success',
        'message': 'L7Nutri funcionando!',
        'app': 'L7Nutri',
        'platform': 'Render'
    })

@app.route('/status')
def status():
    return jsonify({
        'status': 'online',
        'app': 'L7Nutri',
        'platform': 'Render'
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
