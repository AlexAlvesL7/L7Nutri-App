from app import app, db
from sqlalchemy import text

# Script para adicionar coluna fator_atividade
print("🔧 Adicionando coluna fator_atividade ao banco de dados...")

with app.app_context():
    try:
        # Executar comando SQL direto para adicionar a coluna
        with db.engine.connect() as connection:
            connection.execute(text("ALTER TABLE usuario ADD COLUMN fator_atividade FLOAT"))
            connection.commit()
        
        print("✅ Coluna fator_atividade adicionada com sucesso!")
        
        # Verificar se a coluna foi adicionada
        with db.engine.connect() as connection:
            result = connection.execute(text("PRAGMA table_info(usuario)"))
            colunas = [row[1] for row in result]
        
        if 'fator_atividade' in colunas:
            print("✅ Verificação: Coluna fator_atividade existe na tabela")
        else:
            print("❌ Erro: Coluna não foi criada")
            
        print("\n📋 Colunas da tabela usuario:")
        for coluna in colunas:
            print(f"   - {coluna}")
            
    except Exception as e:
        print(f"❌ Erro ao adicionar coluna: {e}")
        
        # Verificar se é PostgreSQL (produção)
        if "postgresql" in str(db.engine.url):
            print("🔄 Detectado PostgreSQL, tentando comando específico...")
            try:
                with db.engine.connect() as connection:
                    connection.execute(text("ALTER TABLE usuario ADD COLUMN IF NOT EXISTS fator_atividade FLOAT"))
                    connection.commit()
                print("✅ Coluna adicionada no PostgreSQL!")
            except Exception as e2:
                print(f"❌ Erro no PostgreSQL: {e2}")
        else:
            print("ℹ️ Se a coluna já existe, isso é normal.")
