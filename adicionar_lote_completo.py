import sqlite3
import json

# Conectar ao banco
conn = sqlite3.connect('nutricao.db')
cursor = conn.cursor()

# Carregar todos os 3 arquivos JSON com os alimentos
arquivos = [
    'alimentos_taco_parte2.json',
    'alimentos_adicionais_p2.json',
    'alimentos_adicionais_p3.json',
    'alimentos_adicionais_p4.json'
]

total_adicionados = 0
categorias = {}

# Função para carregar e inserir alimentos
def inserir_alimentos_do_arquivo(arquivo):
    global total_adicionados
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            alimentos = json.load(f)
        
        for alimento in alimentos:
            try:
                # Verificar se o alimento já existe
                cursor.execute("SELECT id FROM alimento WHERE nome = ?", (alimento['nome'],))
                if cursor.fetchone():
                    print(f"❌ {alimento['nome']} já existe no banco")
                    continue
                
                # Inserir novo alimento
                cursor.execute("""
                    INSERT INTO alimento (nome, categoria, calorias, proteinas, carboidratos, gorduras, 
                                        fibras, sodio, acucar, colesterol, porcao_referencia, fonte_dados)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alimento['nome'],
                    alimento['categoria'],
                    alimento['calorias'],
                    alimento['proteinas'],
                    alimento['carboidratos'],
                    alimento['gorduras'],
                    alimento['fibras'],
                    alimento['sodio'],
                    alimento['acucar'],
                    alimento['colesterol'],
                    alimento['porcao_referencia'],
                    alimento['fonte_dados']
                ))
                
                # Contar por categoria
                categoria = alimento['categoria']
                if categoria not in categorias:
                    categorias[categoria] = 0
                categorias[categoria] += 1
                
                total_adicionados += 1
                print(f"✅ {alimento['nome']} adicionado")
                
            except KeyError as e:
                print(f"❌ Erro no alimento {alimento['nome']}: campo {e} não encontrado")
            except Exception as e:
                print(f"❌ Erro ao inserir {alimento['nome']}: {e}")
                
    except FileNotFoundError:
        print(f"📂 Arquivo {arquivo} não encontrado, pulando...")
    except Exception as e:
        print(f"❌ Erro ao processar arquivo {arquivo}: {e}")

# Processar todos os arquivos
print("🚀 ADICIONANDO ALIMENTOS EM LOTE...")
print("=" * 50)

for arquivo in arquivos:
    print(f"\n📁 Processando {arquivo}...")
    inserir_alimentos_do_arquivo(arquivo)

# Salvar alterações
conn.commit()

# Relatório final
print("\n" + "=" * 50)
print("📊 RELATÓRIO FINAL")
print("=" * 50)
print(f"🎉 Total de alimentos adicionados: {total_adicionados}")
print(f"🗂️  Categorias processadas: {len(categorias)}")

print("\n📋 ALIMENTOS POR CATEGORIA:")
for categoria, quantidade in sorted(categorias.items()):
    print(f"   🔹 {categoria}: {quantidade} alimentos")

# Verificar total no banco
cursor.execute("SELECT COUNT(*) FROM alimento")
total_banco = cursor.fetchone()[0]
print(f"\n💾 Total de alimentos no banco: {total_banco}")

# Fechar conexão
conn.close()
print("\n✅ Processo concluído com sucesso!")
