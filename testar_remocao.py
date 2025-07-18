import sqlite3
import requests
import json

def testar_remocao():
    # Primeiro, vamos ver os registros atuais
    conn = sqlite3.connect('nutricao.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT r.id, r.usuario_id, r.data, r.tipo_refeicao, r.quantidade_gramas, 
               a.nome as alimento_nome
        FROM registro_alimentar r
        JOIN alimento a ON r.alimento_id = a.id
        ORDER BY r.id DESC
    ''')
    
    registros = cursor.fetchall()
    print("REGISTROS ANTES DA REMOÇÃO:")
    print("="*60)
    for registro in registros:
        print(f"ID: {registro[0]} | {registro[5]} | {registro[3]}")
    
    if registros:
        # Pega o ID do último registro para testar remoção
        ultimo_id = registros[0][0]
        print(f"\n🗑️ Testando remoção do registro ID: {ultimo_id}")
        
        # Testa a API de remoção
        url = 'http://localhost:5000/api/diario/remover'
        data = {'registro_id': ultimo_id}
        
        try:
            response = requests.post(url, json=data)
            print(f"Status: {response.status_code}")
            print(f"Resposta: {response.json()}")
            
            if response.status_code == 200:
                # Verifica se foi removido do banco
                cursor.execute('SELECT COUNT(*) FROM registro_alimentar WHERE id = ?', (ultimo_id,))
                count = cursor.fetchone()[0]
                if count == 0:
                    print("✅ Registro removido com sucesso do banco!")
                else:
                    print("❌ Registro ainda existe no banco!")
            
        except Exception as e:
            print(f"Erro na requisição: {e}")
    else:
        print("Nenhum registro encontrado para testar remoção.")
    
    conn.close()

if __name__ == "__main__":
    testar_remocao()
