import sqlite3

conn = sqlite3.connect('nutricao.db')
cursor = conn.cursor()

print("=== VERIFICAÇÃO DO BANCO ===")

# Verificar tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = cursor.fetchall()
print(f"Tabelas: {[t[0] for t in tabelas]}")

# Verificar registros alimentares
cursor.execute("SELECT COUNT(*) FROM registro_alimentar")
total_registros = cursor.fetchone()[0]
print(f"Total registros alimentares: {total_registros}")

# Verificar alimentos
cursor.execute("SELECT COUNT(*) FROM alimento")
total_alimentos = cursor.fetchone()[0]
print(f"Total alimentos: {total_alimentos}")

# Se não há registros, criar alguns
if total_registros == 0 and total_alimentos > 0:
    print("\nCriando registros de teste...")
    
    # Pegar alguns alimentos
    cursor.execute("SELECT id FROM alimento LIMIT 5")
    alimentos = [row[0] for row in cursor.fetchall()]
    
    # Criar registros para os últimos 3 dias
    from datetime import datetime, timedelta
    
    for i in range(3):
        data = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        for alimento_id in alimentos[:2]:  # 2 alimentos por dia
            cursor.execute("""
                INSERT INTO registro_alimentar 
                (usuario_id, data, tipo_refeicao, alimento_id, quantidade_gramas)
                VALUES (1, ?, 'almoco', ?, 100)
            """, (data, alimento_id))
    
    conn.commit()
    print("Registros de teste criados!")

# Verificar registros recentes
cursor.execute("""
    SELECT r.data, r.tipo_refeicao, a.nome, r.quantidade_gramas
    FROM registro_alimentar r
    JOIN alimento a ON r.alimento_id = a.id
    WHERE r.usuario_id = 1
    ORDER BY r.data DESC
    LIMIT 10
""")

registros = cursor.fetchall()
print(f"\nÚltimos registros ({len(registros)}):")
for r in registros:
    print(f"  {r[0]} - {r[1]} - {r[2]} ({r[3]}g)")

conn.close()
print("\n✅ Verificação concluída!")
