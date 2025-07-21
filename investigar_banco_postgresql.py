#!/usr/bin/env python3
"""
🔍 INVESTIGAÇÃO BANCO POSTGRESQL - L7NUTRI
Script para investigar tabelas órfãs no banco PostgreSQL do Render
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
from datetime import datetime

def log_resultado(titulo, conteudo):
    """Log formatado dos resultados"""
    print(f"\n{'='*60}")
    print(f"🔍 {titulo}")
    print('='*60)
    print(conteudo)
    print('='*60)

def investigar_via_api():
    """Tenta investigar via API caso o banco esteja funcionando"""
    print("\n🌐 TENTATIVA 1: Investigação via API...")
    
    try:
        # Testa API básica
        response = requests.get("https://l7nutri-app.onrender.com/api/teste", timeout=30)
        log_resultado("API BÁSICA", f"Status: {response.status_code}\nResposta: {response.text[:500]}")
        
        if response.status_code == 200:
            # Tenta diagnóstico do banco
            response = requests.get("https://l7nutri-app.onrender.com/api/diagnostico-db", timeout=30)
            log_resultado("DIAGNÓSTICO BANCO VIA API", f"Status: {response.status_code}\nResposta: {response.text[:1000]}")
            return True
            
    except Exception as e:
        log_resultado("ERRO API", f"Falha na conexão via API: {str(e)}")
    
    return False

def conectar_postgresql_direto():
    """Tenta conectar diretamente ao PostgreSQL usando variáveis comuns"""
    print("\n🐘 TENTATIVA 2: Conexão direta PostgreSQL...")
    
    # Possíveis variáveis de ambiente do Render
    possible_vars = [
        'DATABASE_URL',
        'POSTGRES_URL', 
        'POSTGRESQL_URL',
        'RENDER_DATABASE_URL'
    ]
    
    database_url = None
    for var in possible_vars:
        database_url = os.getenv(var)
        if database_url:
            print(f"✅ Encontrada variável: {var}")
            break
    
    if not database_url:
        print("❌ Nenhuma variável de banco encontrada")
        print("💡 Variáveis tentadas:", possible_vars)
        return False
    
    try:
        # Ajusta URL se necessário
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        print(f"🔗 Conectando ao banco...")
        print(f"   URL: {database_url[:50]}...")
        
        # Conecta ao banco
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Lista todas as tabelas
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        tabelas = cursor.fetchall()
        
        tabelas_list = [t['tablename'] for t in tabelas]
        log_resultado("TODAS AS TABELAS", "\n".join(tabelas_list))
        
        # 2. Verifica se conquistas_usuarios existe
        tem_conquistas = 'conquistas_usuarios' in tabelas_list
        log_resultado("TABELA CONQUISTAS_USUARIOS", 
                     f"Existe: {'✅ SIM' if tem_conquistas else '❌ NÃO'}")
        
        if tem_conquistas:
            # 3. Mostra estrutura da tabela conquistas_usuarios
            cursor.execute("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = 'conquistas_usuarios'
                ORDER BY ordinal_position;
            """)
            estrutura = cursor.fetchall()
            
            estrutura_str = "\n".join([
                f"  {col['column_name']} | {col['data_type']} | NULL: {col['is_nullable']} | Default: {col['column_default']}"
                for col in estrutura
            ])
            log_resultado("ESTRUTURA CONQUISTAS_USUARIOS", estrutura_str)
            
            # 4. Conta registros
            cursor.execute("SELECT COUNT(*) FROM conquistas_usuarios;")
            count = cursor.fetchone()['count']
            log_resultado("DADOS EM CONQUISTAS_USUARIOS", f"Total de registros: {count}")
            
            # 5. Pergunta se deve deletar
            print(f"\n{'⚠️'*20}")
            print("🚨 ATENÇÃO: Tabela conquistas_usuarios ENCONTRADA!")
            print("🚨 Esta tabela está causando erro de inicialização do SQLAlchemy")
            print("🚨 O código atual NÃO tem modelo para esta tabela")
            print(f"{'⚠️'*20}")
            
            resposta = input("\n❓ Deletar tabela conquistas_usuarios? (sim/NAO): ").strip().lower()
            
            if resposta in ['sim', 's', 'yes', 'y']:
                cursor.execute("DROP TABLE conquistas_usuarios;")
                conn.commit()
                log_resultado("TABELA DELETADA", "✅ Tabela conquistas_usuarios removida com sucesso!")
                
                # Confirma remoção
                cursor.execute("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public' AND tablename = 'conquistas_usuarios';
                """)
                confirmacao = cursor.fetchall()
                
                if not confirmacao:
                    log_resultado("CONFIRMAÇÃO", "✅ Tabela conquistas_usuarios não existe mais!")
                else:
                    log_resultado("ERRO", "❌ Tabela ainda existe após tentativa de remoção!")
                    
            else:
                log_resultado("AÇÃO CANCELADA", "❌ Tabela conquistas_usuarios mantida")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        log_resultado("ERRO POSTGRESQL", f"Falha na conexão direta: {str(e)}")
        return False

def gerar_relatorio_final():
    """Gera relatório final da investigação"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    relatorio = f"""
{'='*80}
🔍 RELATÓRIO FINAL - INVESTIGAÇÃO BANCO POSTGRESQL
Data: {timestamp}
{'='*80}

✅ RESULTADOS DA INVESTIGAÇÃO:
- Tentativa via API: {'Sucesso' if investigar_via_api() else 'Falhou'}
- Conexão direta PostgreSQL: {'Em andamento...' if not investigar_via_api() else 'Não necessária'}

📋 PRÓXIMAS AÇÕES RECOMENDADAS:
1. Se tabela conquistas_usuarios foi encontrada e removida:
   → Executar: flask db upgrade
   → Reiniciar serviço Render
   → Testar APIs

2. Se tabela NÃO foi encontrada:
   → Problema pode ser outro (cache persistent, etc.)
   → Investigar logs do Render

3. Se conexão falhou:
   → Usar painel web do Render
   → Conectar via pgAdmin/DBeaver com credenciais do painel

{'='*80}
"""
    
    print(relatorio)

def main():
    """Função principal"""
    print("🔍 INICIANDO INVESTIGAÇÃO BANCO POSTGRESQL L7NUTRI")
    print(f"Timestamp: {datetime.now()}")
    
    # Tenta investigação via API primeiro
    api_ok = investigar_via_api()
    
    if not api_ok:
        # Se API falhou, tenta conexão direta
        db_ok = conectar_postgresql_direto()
        
        if not db_ok:
            print("\n❌ AMBAS TENTATIVAS FALHARAM")
            print("\n💡 SOLUÇÕES ALTERNATIVAS:")
            print("1. Acessar painel do Render → PostgreSQL → Connect → Copy connection string")
            print("2. Usar DBeaver/pgAdmin com as credenciais do painel")
            print("3. Usar o console web do PostgreSQL no próprio Render")
    
    gerar_relatorio_final()

if __name__ == "__main__":
    main()
