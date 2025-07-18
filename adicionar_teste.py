import sqlite3

# Adicionar um registro de teste
conn = sqlite3.connect('nutricao.db')
cursor = conn.cursor()

cursor.execute('''
    INSERT INTO registro_alimentar (usuario_id, data, tipo_refeicao, alimento_id, quantidade_gramas) 
    VALUES (1, "2025-07-16", "jantar", 2, 100)
''')

conn.commit()
print("Registro de teste adicionado para jantar")

# Listar registros atuais
cursor.execute('''
    SELECT r.id, r.usuario_id, r.data, r.tipo_refeicao, r.quantidade_gramas, 
           a.nome as alimento_nome
    FROM registro_alimentar r
    JOIN alimento a ON r.alimento_id = a.id
    ORDER BY r.id DESC
''')

registros = cursor.fetchall()
print("\nREGISTROS ATUAIS:")
print("="*60)
for registro in registros:
    print(f"ID: {registro[0]} | {registro[5]} | {registro[3]}")

conn.close()
