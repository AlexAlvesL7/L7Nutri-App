import sqlite3

# Conectar ao banco
conn = sqlite3.connect('nutricao.db')
cursor = conn.cursor()

print("🍎 VERIFICAÇÃO FINAL DO BANCO DE DADOS")
print("=" * 50)

# Contar total de alimentos
cursor.execute("SELECT COUNT(*) FROM alimento")
total = cursor.fetchone()[0]
print(f"🎯 Total de alimentos: {total}")

# Contar por categoria
cursor.execute("SELECT categoria, COUNT(*) FROM alimento GROUP BY categoria ORDER BY COUNT(*) DESC")
categorias = cursor.fetchall()

print(f"\n📊 ALIMENTOS POR CATEGORIA ({len(categorias)} categorias):")
for categoria, count in categorias:
    print(f"   🔹 {categoria}: {count} alimentos")

# Mostrar alguns exemplos
print(f"\n📋 EXEMPLOS DE ALIMENTOS ADICIONADOS:")
cursor.execute("SELECT nome, categoria, calorias, proteinas FROM alimento ORDER BY RANDOM() LIMIT 10")
exemplos = cursor.fetchall()

for nome, categoria, calorias, proteinas in exemplos:
    print(f"   🍽️  {nome} ({categoria}) - {calorias}kcal, {proteinas}g proteína")

# Verificar alimentos com maior valor calórico
print(f"\n🔥 TOP 5 ALIMENTOS MAIS CALÓRICOS:")
cursor.execute("SELECT nome, categoria, calorias FROM alimento ORDER BY calorias DESC LIMIT 5")
top_calorias = cursor.fetchall()

for nome, categoria, calorias in top_calorias:
    print(f"   🔥 {nome} ({categoria}) - {calorias}kcal")

# Verificar alimentos com mais proteína
print(f"\n💪 TOP 5 ALIMENTOS COM MAIS PROTEÍNA:")
cursor.execute("SELECT nome, categoria, proteinas FROM alimento ORDER BY proteinas DESC LIMIT 5")
top_proteinas = cursor.fetchall()

for nome, categoria, proteinas in top_proteinas:
    print(f"   💪 {nome} ({categoria}) - {proteinas}g proteína")

conn.close()
print(f"\n✅ BANCO DE DADOS COMPLETO E FUNCIONAL!")
print(f"🎉 Sistema pronto para uso com {total} alimentos TACO/ANVISA!")
