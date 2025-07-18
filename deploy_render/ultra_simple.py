#!/usr/bin/env python3
"""
L7Nutri - Versão Ultra Minimalista
Garantida para funcionar no Render
"""
import os
import sys
from datetime import datetime

# Importar apenas o essencial
try:
    from flask import Flask
    print("✓ Flask importado")
except ImportError as e:
    print(f"✗ Erro ao importar Flask: {e}")
    sys.exit(1)

# Criar app Flask mais simples possível
app = Flask(__name__)

# Rota principal simples
@app.route('/')
def home():
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>L7Nutri - Funcionando!</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background-color: #f0f0f0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #28a745;
                margin-bottom: 20px;
            }}
            .success {{
                background: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🥗 L7Nutri</h1>
            <div class="success">
                ✅ Aplicação Flask funcionando perfeitamente!
            </div>
            <p><strong>Data/Hora:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            <p><strong>Versão:</strong> Ultra Minimalista</p>
            <p><strong>Status:</strong> Operacional</p>
            <hr>
            <p>🎉 <strong>Parabéns!</strong> Sua aplicação está rodando no Render!</p>
        </div>
    </body>
    </html>
    '''

# Rota de teste simples
@app.route('/test')
def test():
    return 'L7Nutri - Teste OK!'

# Verificar se é o arquivo principal
if __name__ == '__main__':
    # Obter porta do ambiente
    port = int(os.getenv('PORT', 5000))
    
    print(f"=== L7NUTRI INICIANDO ===")
    print(f"Porta: {port}")
    print(f"Hora: {datetime.now()}")
    
    # Iniciar servidor Flask
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
