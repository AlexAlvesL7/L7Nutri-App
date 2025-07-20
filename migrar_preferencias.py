from app import app, db, PreferenciasUsuario
from sqlalchemy import text
import os

def criar_tabela_preferencias():
    """Criar tabela de preferências alimentares de forma compatível"""
    
    print("🗄️  Iniciando criação da tabela preferencias_usuario...")
    
    with app.app_context():
        try:
            # Detectar tipo de banco de dados
            engine_name = db.engine.name
            print(f"🔍 Banco detectado: {engine_name}")
            
            # Verificar se a tabela já existe (compatível com SQLite e PostgreSQL)
            if engine_name == 'postgresql':
                # PostgreSQL
                resultado = db.session.execute(text("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'preferencias_usuario'
                    );
                """)).scalar()
            else:
                # SQLite
                resultado = db.session.execute(text("""
                    SELECT COUNT(*) FROM sqlite_master 
                    WHERE type='table' AND name='preferencias_usuario';
                """)).scalar()
                resultado = resultado > 0
            
            if resultado:
                print("ℹ️  Tabela preferencias_usuario já existe.")
                return True
            
            # Criar a tabela usando SQLAlchemy ORM (mais compatível)
            print("🔨 Criando tabela usando SQLAlchemy...")
            db.create_all()
            
            print("✅ Tabela preferencias_usuario criada com sucesso!")
            
            # Testar inserção básica
            print("🧪 Testando estrutura da tabela...")
            
            # Verificar se a tabela foi criada
            if engine_name == 'postgresql':
                teste = db.session.execute(text("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'preferencias_usuario'
                    ORDER BY ordinal_position;
                """)).fetchall()
            else:
                teste = db.session.execute(text("""
                    PRAGMA table_info(preferencias_usuario);
                """)).fetchall()
            
            print(f"📊 Colunas criadas: {len(teste)}")
            for coluna in teste:
                print(f"   - {coluna[0] if engine_name == 'postgresql' else coluna[1]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar tabela: {str(e)}")
            try:
                db.session.rollback()
            except:
                pass
            return False

def testar_operacoes_basicas():
    """Testar operações básicas na tabela"""
    print("\n🧪 Testando operações básicas...")
    
    with app.app_context():
        try:
            # Teste de inserção (sem commit)
            teste_pref = PreferenciasUsuario(
                usuario_id=999,  # ID de teste
                alimentos_evitar="teste",
                restricoes=["teste"],
                estilo_alimentar="tradicional"
            )
            
            db.session.add(teste_pref)
            db.session.flush()  # Apenas flush, não commit
            
            print("✅ Inserção de teste: OK")
            
            # Rollback do teste
            db.session.rollback()
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste: {str(e)}")
            try:
                db.session.rollback()
            except:
                pass
            return False

if __name__ == "__main__":
    print("🚀 === MIGRAÇÃO DE PREFERÊNCIAS ALIMENTARES ===\n")
    
    # Verificar se está no contexto correto
    print(f"📁 Diretório atual: {os.getcwd()}")
    print(f"🗃️  Arquivo do banco: {app.config.get('SQLALCHEMY_DATABASE_URI', 'N/A')}")
    
    sucesso = criar_tabela_preferencias()
    
    if sucesso:
        # Testar operações
        teste_ok = testar_operacoes_basicas()
        
        if teste_ok:
            print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("📊 Tabela preferencias_usuario está pronta para uso.")
            print("✅ Testes básicos passaram.")
        else:
            print("\n⚠️  MIGRAÇÃO CRIADA, MAS TESTES FALHARAM!")
    else:
        print("\n❌ MIGRAÇÃO FALHOU!")
        print("🔧 Verifique os logs de erro acima.")
