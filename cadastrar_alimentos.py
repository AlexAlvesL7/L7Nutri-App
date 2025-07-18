#!/usr/bin/env python3
"""
Script para cadastrar alimentos em lote no banco de dados
"""

import sqlite3
import os

# Lista de alimentos para cadastrar
alimentos = [
    # Carboidratos Base
    {
        'nome': 'Arroz Branco, cozido',
        'calorias_por_100g': 128,
        'proteinas_por_100g': 2.5,
        'carboidratos_por_100g': 28.1,
        'gorduras_por_100g': 0.2,
        'categoria': 'Carboidratos'
    },
    {
        'nome': 'Feijão Carioca, cozido',
        'calorias_por_100g': 76,
        'proteinas_por_100g': 4.8,
        'carboidratos_por_100g': 13.6,
        'gorduras_por_100g': 0.5,
        'categoria': 'Carboidratos'
    },
    {
        'nome': 'Batata Inglesa, cozida',
        'calorias_por_100g': 86,
        'proteinas_por_100g': 1.9,
        'carboidratos_por_100g': 20.0,
        'gorduras_por_100g': 0.1,
        'categoria': 'Carboidratos'
    },
    {
        'nome': 'Pão Francês',
        'calorias_por_100g': 289,
        'proteinas_por_100g': 9.0,
        'carboidratos_por_100g': 58.7,
        'gorduras_por_100g': 2.5,
        'categoria': 'Carboidratos'
    },
    # Proteínas
    {
        'nome': 'Peito de Frango, grelhado',
        'calorias_por_100g': 165,
        'proteinas_por_100g': 31.0,
        'carboidratos_por_100g': 0.0,
        'gorduras_por_100g': 3.6,
        'categoria': 'Proteínas'
    },
    {
        'nome': 'Bife de Alcatra, grelhado',
        'calorias_por_100g': 200,
        'proteinas_por_100g': 35.0,
        'carboidratos_por_100g': 0.0,
        'gorduras_por_100g': 6.0,
        'categoria': 'Proteínas'
    },
    {
        'nome': 'Ovo de Galinha, cozido',
        'calorias_por_100g': 155,
        'proteinas_por_100g': 13.0,
        'carboidratos_por_100g': 1.1,
        'gorduras_por_100g': 11.0,
        'categoria': 'Proteínas'
    },
    # Frutas e Laticínios
    {
        'nome': 'Banana Prata',
        'calorias_por_100g': 98,
        'proteinas_por_100g': 1.3,
        'carboidratos_por_100g': 26.0,
        'gorduras_por_100g': 0.1,
        'categoria': 'Frutas'
    },
    {
        'nome': 'Maçã Fuji',
        'calorias_por_100g': 56,
        'proteinas_por_100g': 0.3,
        'carboidratos_por_100g': 15.2,
        'gorduras_por_100g': 0.0,
        'categoria': 'Frutas'
    },
    {
        'nome': 'Leite Integral (Líquido)',
        'calorias_por_100g': 61,
        'proteinas_por_100g': 3.2,
        'carboidratos_por_100g': 4.7,
        'gorduras_por_100g': 3.3,
        'categoria': 'Laticínios'
    }
]

def cadastrar_alimentos():
    """Cadastra todos os alimentos no banco de dados"""
    
    # Conecta ao banco de dados
    db_path = 'nutricao.db'
    
    if not os.path.exists(db_path):
        print("❌ Arquivo nutricao.db não encontrado!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica se a tabela existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='alimento'
        """)
        
        if not cursor.fetchone():
            print("❌ Tabela 'alimento' não encontrada no banco!")
            return False
        
        # Cadastra cada alimento
        alimentos_cadastrados = 0
        alimentos_ja_existentes = 0
        
        for alimento in alimentos:
            # Verifica se o alimento já existe
            cursor.execute("""
                SELECT id FROM alimento WHERE nome = ?
            """, (alimento['nome'],))
            
            if cursor.fetchone():
                print(f"⚠️  {alimento['nome']} já existe no banco")
                alimentos_ja_existentes += 1
                continue
            
            # Insere o novo alimento (ajustando para a estrutura correta)
            cursor.execute("""
                INSERT INTO alimento (
                    nome, calorias, proteinas, 
                    carboidratos, gorduras
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                alimento['nome'],
                alimento['calorias_por_100g'],
                alimento['proteinas_por_100g'],
                alimento['carboidratos_por_100g'],
                alimento['gorduras_por_100g']
            ))
            
            print(f"✅ {alimento['nome']} cadastrado com sucesso!")
            alimentos_cadastrados += 1
        
        # Confirma as alterações
        conn.commit()
        conn.close()
        
        print(f"\n📊 Resumo:")
        print(f"   • Alimentos cadastrados: {alimentos_cadastrados}")
        print(f"   • Alimentos já existentes: {alimentos_ja_existentes}")
        print(f"   • Total processados: {len(alimentos)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao cadastrar alimentos: {str(e)}")
        return False

if __name__ == "__main__":
    print("🍎 Iniciando cadastro de alimentos...")
    print("=" * 50)
    
    sucesso = cadastrar_alimentos()
    
    print("=" * 50)
    if sucesso:
        print("✅ Processo concluído com sucesso!")
    else:
        print("❌ Processo finalizado com erros!")
