#!/usr/bin/env python3
"""
L7Nutri - Versão Minimalista para Diagnóstico
"""
import os
import sys

print("=== L7NUTRI - DIAGNÓSTICO MINIMALISTA ===")
print(f"Python: {sys.version}")
print(f"Diretório: {os.getcwd()}")
print(f"PORT: {os.getenv('PORT', 'Não configurada')}")
print(f"DATABASE_URL: {'Configurada' if os.getenv('DATABASE_URL') else 'Não configurada'}")

try:
    print("1. Importando Flask...")
    from flask import Flask, jsonify
    print("   ✓ Flask importado")
    
    print("2. Criando app Flask...")
    app = Flask(__name__)
    print("   ✓ App criado")
    
    print("3. Configurando rotas...")
    
    @app.route('/')
    def home():
        return """
        <html>
        <head><title>L7Nutri - Diagnóstico</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: green;">✅ L7Nutri Funcionando!</h1>
            <p>Aplicação Flask iniciada com sucesso</p>
            <p>Timestamp: """ + str(__import__('datetime').datetime.now()) + """</p>
            <hr>
            <a href="/health">Health Check</a>
        </body>
        </html>
        """
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'OK',
            'message': 'Aplicação funcionando',
            'timestamp': str(__import__('datetime').datetime.now())
        })
    
    print("   ✓ Rotas configuradas")
    
    print("4. Iniciando servidor...")
    port = int(os.getenv('PORT', 5000))
    print(f"   Porta: {port}")
    
    if __name__ == '__main__':
        print("=== SERVIDOR INICIANDO ===")
        app.run(host='0.0.0.0', port=port, debug=False)
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
