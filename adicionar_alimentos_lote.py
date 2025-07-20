#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar alimentos em lote ao banco de dados L7Nutri
Aceita dados da Tabela TACO e outras fontes oficiais
"""

import json
import csv
import os
import sys
from app import app, db, Alimento

def adicionar_alimentos_json(arquivo_json):
    """
    Adiciona alimentos a partir de um arquivo JSON
    
    Formato esperado:
    [
        {
            "nome": "Nome do Alimento",
            "categoria": "frutas", 
            "calorias": 52.0,
            "proteinas": 0.9,
            "carboidratos": 13.8,
            "gorduras": 0.2,
            "fibras": 2.4,
            "sodio": 1.0,
            "acucar": 10.4,
            "colesterol": 0.0,
            "porcao_referencia": "100g",
            "fonte_dados": "TACO"
        }
    ]
    """
    try:
        with open(arquivo_json, 'r', encoding='utf-8') as f:
            alimentos_data = json.load(f)
        
        contador_adicionados = 0
        contador_existentes = 0
        
        with app.app_context():
            for item in alimentos_data:
                # Verifica se o alimento já existe
                alimento_existente = Alimento.query.filter_by(nome=item['nome']).first()
                
                if alimento_existente:
                    print(f"⚠️  Alimento já existe: {item['nome']}")
                    contador_existentes += 1
                    continue
                
                # Cria novo alimento
                novo_alimento = Alimento(
                    nome=item['nome'],
                    categoria=item.get('categoria', 'Outros'),
                    calorias=float(item.get('calorias', 0)),
                    proteinas=float(item.get('proteinas', 0)),
                    carboidratos=float(item.get('carboidratos', 0)),
                    gorduras=float(item.get('gorduras', 0)),
                    fibras=float(item.get('fibras', 0)),
                    sodio=float(item.get('sodio', 0)),
                    acucar=float(item.get('acucar', 0)),
                    colesterol=float(item.get('colesterol', 0)),
                    porcao_referencia=item.get('porcao_referencia', '100g'),
                    fonte_dados=item.get('fonte_dados', 'TACO')
                )
                
                db.session.add(novo_alimento)
                print(f"✅ Adicionado: {item['nome']}")
                contador_adicionados += 1
            
            # Commit de todas as alterações
            db.session.commit()
            
        print(f"\n🎉 RESUMO:")
        print(f"   Alimentos adicionados: {contador_adicionados}")
        print(f"   Alimentos já existentes: {contador_existentes}")
        print(f"   Total processado: {len(alimentos_data)}")
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo JSON: {str(e)}")
        db.session.rollback()

def adicionar_alimentos_csv(arquivo_csv):
    """
    Adiciona alimentos a partir de um arquivo CSV
    
    Colunas esperadas:
    nome,categoria,calorias,proteinas,carboidratos,gorduras,fibras,sodio,acucar,colesterol,porcao_referencia,fonte_dados
    """
    try:
        contador_adicionados = 0
        contador_existentes = 0
        
        with app.app_context():
            with open(arquivo_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Verifica se o alimento já existe
                    alimento_existente = Alimento.query.filter_by(nome=row['nome']).first()
                    
                    if alimento_existente:
                        print(f"⚠️  Alimento já existe: {row['nome']}")
                        contador_existentes += 1
                        continue
                    
                    # Cria novo alimento
                    novo_alimento = Alimento(
                        nome=row['nome'],
                        categoria=row.get('categoria', 'Outros'),
                        calorias=float(row.get('calorias', 0)) if row.get('calorias') else 0,
                        proteinas=float(row.get('proteinas', 0)) if row.get('proteinas') else 0,
                        carboidratos=float(row.get('carboidratos', 0)) if row.get('carboidratos') else 0,
                        gorduras=float(row.get('gorduras', 0)) if row.get('gorduras') else 0,
                        fibras=float(row.get('fibras', 0)) if row.get('fibras') else 0,
                        sodio=float(row.get('sodio', 0)) if row.get('sodio') else 0,
                        acucar=float(row.get('acucar', 0)) if row.get('acucar') else 0,
                        colesterol=float(row.get('colesterol', 0)) if row.get('colesterol') else 0,
                        porcao_referencia=row.get('porcao_referencia', '100g'),
                        fonte_dados=row.get('fonte_dados', 'TACO')
                    )
                    
                    db.session.add(novo_alimento)
                    print(f"✅ Adicionado: {row['nome']}")
                    contador_adicionados += 1
                
                # Commit de todas as alterações
                db.session.commit()
                
        print(f"\n🎉 RESUMO:")
        print(f"   Alimentos adicionados: {contador_adicionados}")
        print(f"   Alimentos já existentes: {contador_existentes}")
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo CSV: {str(e)}")
        db.session.rollback()

def executar_comandos_sql(arquivo_sql):
    """
    Executa comandos SQL para inserir alimentos
    
    Formato esperado:
    INSERT INTO alimento (nome, categoria, calorias, proteinas, carboidratos, gorduras, fibras, sodio, acucar, colesterol, porcao_referencia, fonte_dados) 
    VALUES ('Nome do Alimento', 'categoria', 52.0, 0.9, 13.8, 0.2, 2.4, 1.0, 10.4, 0.0, '100g', 'TACO');
    """
    try:
        with app.app_context():
            with open(arquivo_sql, 'r', encoding='utf-8') as f:
                comandos_sql = f.read()
            
            # Executa os comandos SQL
            db.session.execute(comandos_sql)
            db.session.commit()
            
        print(f"✅ Comandos SQL executados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao executar comandos SQL: {str(e)}")
        db.session.rollback()

def criar_tabela_alimentos():
    """Cria a tabela de alimentos se não existir"""
    with app.app_context():
        db.create_all()
        print("✅ Tabela de alimentos criada/verificada!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python adicionar_alimentos_lote.py <arquivo>")
        print("Formatos suportados: .json, .csv, .sql")
        sys.exit(1)
    
    arquivo = sys.argv[1]
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        sys.exit(1)
    
    # Criar tabela se não existir
    criar_tabela_alimentos()
    
    # Processar baseado na extensão do arquivo
    if arquivo.endswith('.json'):
        print(f"📁 Processando arquivo JSON: {arquivo}")
        adicionar_alimentos_json(arquivo)
    elif arquivo.endswith('.csv'):
        print(f"📁 Processando arquivo CSV: {arquivo}")
        adicionar_alimentos_csv(arquivo)
    elif arquivo.endswith('.sql'):
        print(f"📁 Executando comandos SQL: {arquivo}")
        executar_comandos_sql(arquivo)
    else:
        print("❌ Formato de arquivo não suportado. Use .json, .csv ou .sql")
        sys.exit(1)
