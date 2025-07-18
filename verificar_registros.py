import sqlite3

conn = sqlite3.connect('nutricao.db')
cursor = conn.cursor()

# Lista todos os registros da tabela registro_alimentar
cursor.execute('''
    SELECT r.id, r.usuario_id, r.data, r.tipo_refeicao, r.quantidade_gramas, 
           a.nome as alimento_nome
    FROM registro_alimentar r
    JOIN alimento a ON r.alimento_id = a.id
    ORDER BY r.data DESC, r.id DESC
''')

registros = cursor.fetchall()

print('REGISTROS DO DIÁRIO ALIMENTAR:')
print('=' * 80)
print(f"{'ID':3} | {'USER':4} | {'DATA':10} | {'REFEIÇÃO':15} | {'QTDE':4} | {'ALIMENTO':30}")
print('-' * 80)

for registro in registros:
    id_reg, user_id, data, tipo_refeicao, qtde, alimento = registro
    print(f"{id_reg:3} | {user_id:4} | {data:10} | {tipo_refeicao:15} | {qtde:4.0f}g | {alimento:30}")

print('-' * 80)
print(f"Total de registros: {len(registros)}")

conn.close()
