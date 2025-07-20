"""
Script para migrar a estrutura da tabela Alimento
Adiciona novos campos nutricionais baseados na Tabela TACO
"""

from app import app, db, Alimento
from sqlalchemy import text

def migrar_estrutura_alimentos():
    """
    Adiciona as novas colunas à tabela alimento se elas não existirem
    """
    with app.app_context():
        try:
            # Lista de comandos SQL para adicionar as novas colunas
            comandos_sql = [
                "ALTER TABLE alimento ADD COLUMN categoria VARCHAR(50)",
                "ALTER TABLE alimento ADD COLUMN fibras FLOAT DEFAULT 0",
                "ALTER TABLE alimento ADD COLUMN sodio FLOAT DEFAULT 0", 
                "ALTER TABLE alimento ADD COLUMN acucar FLOAT DEFAULT 0",
                "ALTER TABLE alimento ADD COLUMN colesterol FLOAT DEFAULT 0",
                "ALTER TABLE alimento ADD COLUMN porcao_referencia VARCHAR(20) DEFAULT '100g'",
                "ALTER TABLE alimento ADD COLUMN fonte_dados VARCHAR(50) DEFAULT 'TACO'"
            ]
            
            colunas_adicionadas = 0
            
            for comando in comandos_sql:
                try:
                    db.session.execute(text(comando))
                    db.session.commit()
                    coluna = comando.split('ADD COLUMN ')[1].split(' ')[0]
                    print(f"✅ Coluna '{coluna}' adicionada")
                    colunas_adicionadas += 1
                except Exception as e:
                    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                        coluna = comando.split('ADD COLUMN ')[1].split(' ')[0]
                        print(f"⚠️  Coluna '{coluna}' já existe")
                    else:
                        print(f"❌ Erro ao adicionar coluna: {str(e)}")
            
            if colunas_adicionadas > 0:
                print(f"🎉 Migração concluída! {colunas_adicionadas} colunas adicionadas.")
            else:
                print("✅ Estrutura já estava atualizada!")
                
        except Exception as e:
            print(f"❌ Erro geral na migração: {str(e)}")
            db.session.rollback()

def criar_tabelas():
    """Cria todas as tabelas incluindo a nova estrutura"""
    with app.app_context():
        db.create_all()
        print("✅ Todas as tabelas criadas/verificadas!")

if __name__ == "__main__":
    print("🔄 Iniciando migração da estrutura de alimentos...")
    criar_tabelas()
    migrar_estrutura_alimentos()
    print("🎉 Migração finalizada!")
