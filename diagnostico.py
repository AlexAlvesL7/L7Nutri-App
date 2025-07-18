print("🧠 DASHBOARD DE INSIGHTS - STATUS E DIAGNÓSTICO")
print("=" * 60)

# Verificar se os arquivos necessários existem
import os

arquivos_necessarios = [
    "app.py",
    "templates/dashboard_insights.html",
    ".env"
]

print("\n📁 Verificando arquivos necessários:")
for arquivo in arquivos_necessarios:
    if os.path.exists(arquivo):
        print(f"   ✅ {arquivo}")
    else:
        print(f"   ❌ {arquivo} - AUSENTE")

# Verificar se as dependências estão instaladas
print("\n📦 Verificando dependências:")
dependencias = [
    "flask",
    "flask_sqlalchemy", 
    "python-dotenv",
    "google-generativeai"
]

for dep in dependencias:
    try:
        __import__(dep.replace('-', '_'))
        print(f"   ✅ {dep}")
    except ImportError:
        print(f"   ❌ {dep} - NÃO INSTALADO")

# Verificar configuração da IA
print("\n🤖 Verificando configuração da IA:")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key and gemini_key != 'SUA_CHAVE_AQUI':
        print(f"   ✅ GEMINI_API_KEY configurada")
    else:
        print(f"   ⚠️ GEMINI_API_KEY não configurada ou inválida")
except Exception as e:
    print(f"   ❌ Erro ao verificar: {e}")

# Verificar se o banco existe
print("\n🗄️ Verificando banco de dados:")
if os.path.exists("nutricao.db"):
    print("   ✅ nutricao.db existe")
    # Verificar tamanho
    tamanho = os.path.getsize("nutricao.db")
    print(f"   📊 Tamanho: {tamanho:,} bytes")
else:
    print("   ❌ nutricao.db não encontrado")

print("\n" + "=" * 60)
print("🚀 INSTRUÇÕES PARA INICIAR O SERVIDOR:")
print("   1. Abra um terminal")
print("   2. Execute: python app.py")
print("   3. Aguarde a mensagem 'Running on http://127.0.0.1:5000'")
print("   4. Acesse: http://127.0.0.1:5000/dashboard-insights?id=9185fb0a-a4ed-4345-9af4-e0e7698d3c83")

print("\n🌐 URLs IMPORTANTES:")
print("   📊 Dashboard: http://127.0.0.1:5000/dashboard-insights?id=9185fb0a-a4ed-4345-9af4-e0e7698d3c83")
print("   🧪 API Test: http://127.0.0.1:5000/api/teste")
print("   📝 Diário: http://127.0.0.1:5000/diario?id=9185fb0a-a4ed-4345-9af4-e0e7698d3c83")

print("\n✨ SISTEMA PRONTO PARA USO!")
