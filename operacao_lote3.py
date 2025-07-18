#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 OPERAÇÃO BASE DE OURO - LOTE 3
Adicionando alimentos essenciais ao banco MySQL de produção
Grãos, Proteínas, Frutas, Verduras e Legumes (Expansão)
"""

import os
import sys
from app import app, db, Alimento

def adicionar_lote_3_base_ouro():
    """
    Adiciona o terceiro lote de alimentos essenciais
    LOTE 3: Graos, Proteinas, Frutas, Verduras e Legumes (Expansao)
    """
    print("OPERACAO BASE DE OURO - LOTE 3")
    print("=" * 50)
    print("Adicionando alimentos essenciais ao banco MySQL...")
    
    # === GRAOS, PAES E MASSAS (EXPANSAO) ===
    graos_paes_massas = [
        ("Aveia em Flocos", 389, 16.9, 66.3, 6.9),
        ("Tapioca (Goma hidratada)", 240, 0.0, 60.0, 0.0),
        ("Pao de Queijo", 335, 5.5, 37.5, 18.0),
        ("Milho Verde, cozido", 86, 3.2, 19.0, 1.2),
    ]
    
    # === PROTEINAS (EXPANSAO) ===
    proteinas_expansao = [
        ("Carne de Porco (Bisteca), grelhada", 283, 25.8, 0.0, 19.3),
        ("Sardinha em Lata (em oleo)", 208, 24.6, 0.0, 11.5),
        ("Linguica Toscana, grelhada", 322, 16.0, 0.7, 28.0),
        ("Tofu", 76, 8.1, 1.9, 4.8),
    ]
    
    # === FRUTAS, VERDURAS E LEGUMES (EXPANSAO) ===
    frutas_verduras_legumes = [
        ("Uva Thompson", 69, 0.7, 18.1, 0.2),
        ("Manga Palmer", 60, 0.8, 15.0, 0.4),
        ("Couve Manteiga, refogada", 90, 2.7, 7.6, 6.1),
        ("Quiabo, cozido", 33, 1.9, 7.0, 0.2),
        ("Palmito Pupunha, em conserva", 28, 2.5, 4.2, 0.3),
    ]
    
    # Combinando todas as categorias
    todos_alimentos_lote3 = graos_paes_massas + proteinas_expansao + frutas_verduras_legumes
    
    with app.app_context():
        print(f"Processando {len(todos_alimentos_lote3)} alimentos do Lote 3...")
        
        alimentos_adicionados = 0
        alimentos_existentes = 0
        
        # === GRAOS, PAES E MASSAS ===
        print("\nGRAOS, PAES E MASSAS (EXPANSAO)")
        for nome, cal, prot, carb, gord in graos_paes_massas:
            if not Alimento.query.filter_by(nome=nome).first():
                alimento = Alimento(
                    nome=nome,
                    calorias=cal,
                    proteinas=prot,
                    carboidratos=carb,
                    gorduras=gord
                )
                db.session.add(alimento)
                print(f"ADICIONADO: {nome} ({cal} kcal)")
                alimentos_adicionados += 1
            else:
                print(f"JA EXISTE: {nome}")
                alimentos_existentes += 1
        
        # === PROTEINAS ===
        print("\nPROTEINAS (EXPANSAO)")
        for nome, cal, prot, carb, gord in proteinas_expansao:
            if not Alimento.query.filter_by(nome=nome).first():
                alimento = Alimento(
                    nome=nome,
                    calorias=cal,
                    proteinas=prot,
                    carboidratos=carb,
                    gorduras=gord
                )
                db.session.add(alimento)
                print(f"ADICIONADO: {nome} ({cal} kcal)")
                alimentos_adicionados += 1
            else:
                print(f"JA EXISTE: {nome}")
                alimentos_existentes += 1
        
        # === FRUTAS, VERDURAS E LEGUMES ===
        print("\nFRUTAS, VERDURAS E LEGUMES (EXPANSAO)")
        for nome, cal, prot, carb, gord in frutas_verduras_legumes:
            if not Alimento.query.filter_by(nome=nome).first():
                alimento = Alimento(
                    nome=nome,
                    calorias=cal,
                    proteinas=prot,
                    carboidratos=carb,
                    gorduras=gord
                )
                db.session.add(alimento)
                print(f"ADICIONADO: {nome} ({cal} kcal)")
                alimentos_adicionados += 1
            else:
                print(f"JA EXISTE: {nome}")
                alimentos_existentes += 1
        
        try:
            db.session.commit()
            print(f"\nLOTE 3 ADICIONADO COM SUCESSO!")
            print(f"RESUMO:")
            print(f"Novos alimentos: {alimentos_adicionados}")
            print(f"Ja existentes: {alimentos_existentes}")
            print(f"Total processado: {len(todos_alimentos_lote3)}")
            
            # Estatisticas por categoria
            print(f"\nPOR CATEGORIA:")
            print(f"Graos, Paes e Massas: {len(graos_paes_massas)} itens")
            print(f"Proteinas: {len(proteinas_expansao)} itens")
            print(f"Frutas, Verduras e Legumes: {len(frutas_verduras_legumes)} itens")
            
            # Total geral no banco
            total_geral = Alimento.query.count()
            print(f"\nTOTAL DE ALIMENTOS NO BANCO: {total_geral}")
            
            print(f"\nBASE DE OURO EXPANDIDA!")
            print(f"Seu diario alimentar agora tem uma base ainda mais rica!")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"ERRO ao salvar no banco: {str(e)}")
            return False

def mostrar_estatisticas_finais():
    """
    Mostra estatisticas finais da base de alimentos
    """
    with app.app_context():
        print("\nESTATISTICAS FINAIS DA BASE DE OURO")
        print("=" * 50)
        
        # Contagem total
        total = Alimento.query.count()
        print(f"Total de alimentos cadastrados: {total}")
        
        # Ultimos 10 adicionados
        print(f"\nUltimos 10 alimentos adicionados:")
        ultimos = Alimento.query.order_by(Alimento.id.desc()).limit(10).all()
        for i, alimento in enumerate(ultimos, 1):
            print(f"   {i:2d}. {alimento.nome} ({alimento.calorias} kcal)")
        
        print(f"\nSUA BASE DE ALIMENTOS ESTA COMPLETA!")
        print(f"Pronto para criar diarios alimentares de elite!")

if __name__ == '__main__':
    # Forcar modo producao para usar MySQL
    os.environ['FLASK_ENV'] = 'production'
    
    print("OPERACAO BASE DE OURO - LOTE 3")
    print("Expandindo a base de alimentos com:")
    print("Graos, Paes e Massas: 4 itens")
    print("Proteinas: 4 itens")
    print("Frutas, Verduras e Legumes: 5 itens")
    print()
    
    print("Iniciando Operacao Base de Ouro - Lote 3...")
    
    if adicionar_lote_3_base_ouro():
        mostrar_estatisticas_finais()
        print("\nMISSAO CUMPRIDA!")
    else:
        print("\nFalha na operacao")
