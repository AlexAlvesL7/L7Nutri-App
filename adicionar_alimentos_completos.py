#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar alimentos completos ao banco de dados
Inclui verduras, legumes, oleaginosas, sementes e industrializados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Alimento

def adicionar_alimentos_completos():
    """
    Adiciona uma base completa de alimentos nutritivos
    """
    
    # === VERDURAS E LEGUMES (EXPANSÃO) ===
    verduras_legumes = [
        {"nome": "Couve-flor, cozida", "calorias": 23, "proteinas": 1.8, "carboidratos": 4.1, "gorduras": 0.5},
        {"nome": "Abobrinha, cozida", "calorias": 17, "proteinas": 1.2, "carboidratos": 3.1, "gorduras": 0.3},
        {"nome": "Berinjela, cozida", "calorias": 35, "proteinas": 1.0, "carboidratos": 8.7, "gorduras": 0.2},
        {"nome": "Espinafre, cozido", "calorias": 23, "proteinas": 3.0, "carboidratos": 3.7, "gorduras": 0.3},
        {"nome": "Pimentão Verde, cru", "calorias": 20, "proteinas": 0.9, "carboidratos": 4.6, "gorduras": 0.2},
        {"nome": "Beterraba, cozida", "calorias": 44, "proteinas": 1.7, "carboidratos": 10.0, "gorduras": 0.2},
    ]
    
    # === OLEAGINOSAS E SEMENTES ===
    oleaginosas_sementes = [
        {"nome": "Castanha-do-Pará", "calorias": 656, "proteinas": 14.3, "carboidratos": 12.3, "gorduras": 66.3},
        {"nome": "Amêndoas", "calorias": 579, "proteinas": 21.2, "carboidratos": 21.6, "gorduras": 49.9},
        {"nome": "Pasta de Amendoim Integral", "calorias": 588, "proteinas": 25.1, "carboidratos": 20.0, "gorduras": 50.0},
        {"nome": "Semente de Chia", "calorias": 486, "proteinas": 16.5, "carboidratos": 42.1, "gorduras": 30.7},
    ]
    
    # === INDUSTRIALIZADOS E BEBIDAS ===
    industrializados_bebidas = [
        {"nome": "Peito de Peru Defumado", "calorias": 111, "proteinas": 22.0, "carboidratos": 1.5, "gorduras": 1.7},
        {"nome": "Atum em Óleo, drenado", "calorias": 198, "proteinas": 29.0, "carboidratos": 0.0, "gorduras": 8.2},
        {"nome": "Atum em Água, drenado", "calorias": 116, "proteinas": 26.0, "carboidratos": 0.0, "gorduras": 0.8},
        {"nome": "Café Coado, sem açúcar", "calorias": 2, "proteinas": 0.1, "carboidratos": 0.0, "gorduras": 0.0},
        {"nome": "Suco de Laranja Natural", "calorias": 45, "proteinas": 0.7, "carboidratos": 10.4, "gorduras": 0.2},
    ]
    
    # Combinando todas as categorias
    todos_alimentos = verduras_legumes + oleaginosas_sementes + industrializados_bebidas
    
    with app.app_context():
        print("🥗 Iniciando adição de alimentos completos...")
        
        alimentos_adicionados = 0
        alimentos_existentes = 0
        
        for alimento_data in todos_alimentos:
            # Verifica se o alimento já existe
            alimento_existente = Alimento.query.filter_by(nome=alimento_data["nome"]).first()
            
            if alimento_existente:
                print(f"⚠️  Alimento já existe: {alimento_data['nome']}")
                alimentos_existentes += 1
                continue
            
            # Cria novo alimento
            novo_alimento = Alimento(
                nome=alimento_data["nome"],
                calorias=alimento_data["calorias"],
                proteinas=alimento_data["proteinas"],
                carboidratos=alimento_data["carboidratos"],
                gorduras=alimento_data["gorduras"]
            )
            
            try:
                db.session.add(novo_alimento)
                db.session.commit()
                print(f"✅ Adicionado: {alimento_data['nome']} ({alimento_data['calorias']} kcal)")
                alimentos_adicionados += 1
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao adicionar {alimento_data['nome']}: {str(e)}")
        
        print(f"\n📊 RESUMO:")
        print(f"✅ Alimentos adicionados: {alimentos_adicionados}")
        print(f"⚠️  Alimentos já existentes: {alimentos_existentes}")
        print(f"📈 Total processado: {len(todos_alimentos)}")
        
        # Estatísticas por categoria
        print(f"\n📋 POR CATEGORIA:")
        print(f"🥬 Verduras e Legumes: {len(verduras_legumes)} itens")
        print(f"🥜 Oleaginosas e Sementes: {len(oleaginosas_sementes)} itens")
        print(f"🥤 Industrializados e Bebidas: {len(industrializados_bebidas)} itens")
        
        print(f"\n🎉 Base de alimentos expandida com sucesso!")
        
        # Mostrar total de alimentos no banco
        total_alimentos = Alimento.query.count()
        print(f"📦 Total de alimentos no banco: {total_alimentos}")

if __name__ == '__main__':
    adicionar_alimentos_completos()
