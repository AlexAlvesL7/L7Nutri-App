import sqlite3

# Conectar ao banco
conn = sqlite3.connect('nutricao.db')
cursor = conn.cursor()

# Criar tabela alimento com estrutura completa
cursor.execute('''
    CREATE TABLE IF NOT EXISTS alimento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(100) UNIQUE NOT NULL,
        categoria VARCHAR(50) DEFAULT 'Outros',
        calorias FLOAT NOT NULL,
        proteinas FLOAT NOT NULL,
        carboidratos FLOAT NOT NULL,
        gorduras FLOAT NOT NULL,
        fibras FLOAT DEFAULT 0,
        sodio FLOAT DEFAULT 0,
        acucar FLOAT DEFAULT 0,
        colesterol FLOAT DEFAULT 0,
        porcao_referencia VARCHAR(20) DEFAULT '100g',
        fonte_dados VARCHAR(50) DEFAULT 'TACO'
    )
''')

# Criar outras tabelas necessárias
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        senha VARCHAR(100) NOT NULL,
        idade INTEGER,
        peso FLOAT,
        altura FLOAT,
        sexo CHAR(1),
        nivel_atividade VARCHAR(20),
        objetivo VARCHAR(20)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS registro_alimentar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        data DATE NOT NULL,
        tipo_refeicao VARCHAR(20) NOT NULL,
        alimento_id INTEGER NOT NULL,
        quantidade_gramas FLOAT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuario(id),
        FOREIGN KEY (alimento_id) REFERENCES alimento(id)
    )
''')

# Salvar mudanças
conn.commit()

# Verificar se as tabelas foram criadas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = cursor.fetchall()

print("✅ BANCO DE DADOS CRIADO COM SUCESSO!")
print("📊 Tabelas criadas:")
for tabela in tabelas:
    print(f"   🔹 {tabela[0]}")

# Verificar estrutura da tabela alimento
cursor.execute("PRAGMA table_info(alimento)")
colunas = cursor.fetchall()

print(f"\n📋 Estrutura da tabela 'alimento' ({len(colunas)} colunas):")
for coluna in colunas:
    print(f"   🔸 {coluna[1]} ({coluna[2]})")

conn.close()
print("\n🎉 Pronto para adicionar alimentos!")
