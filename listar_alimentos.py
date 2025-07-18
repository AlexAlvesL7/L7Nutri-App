import sqlite3

conn = sqlite3.connect('nutricao.db')
cursor = conn.cursor()

cursor.execute('SELECT nome, calorias, proteinas, carboidratos, gorduras FROM alimento ORDER BY nome')
alimentos = cursor.fetchall()

print('ALIMENTOS CADASTRADOS NO BANCO:')
print('=' * 80)
print(f"{'NOME':35} | {'CAL':4} | {'PROT':5} | {'CARB':5} | {'GORD':5}")
print('-' * 80)

for alimento in alimentos:
    nome, cal, prot, carb, gord = alimento
    print(f"{nome:35} | {cal:4.0f} | {prot:5.1f} | {carb:5.1f} | {gord:5.1f}")

print('-' * 80)
print(f"Total de alimentos: {len(alimentos)}")

conn.close()
