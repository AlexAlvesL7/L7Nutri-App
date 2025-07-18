import sqlite3

# Conecta ao banco
conn = sqlite3.connect('nutricao.db')
cursor = conn.cursor()

# Lista todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = cursor.fetchall()
print("Tabelas existentes:", tabelas)

# Para cada tabela, mostra a estrutura
for tabela in tabelas:
    nome_tabela = tabela[0]
    print(f"\nEstrutura da tabela '{nome_tabela}':")
    cursor.execute(f"PRAGMA table_info({nome_tabela})")
    colunas = cursor.fetchall()
    for coluna in colunas:
        print(f"  - {coluna[1]} ({coluna[2]})")

conn.close()
