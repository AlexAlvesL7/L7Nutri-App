#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOTE 3 - BASE DE OURO
Adicionando mais alimentos essenciais ao banco MySQL de produção
Grãos, Pães, Massas, Proteínas e Frutas/Verduras/Legumes (Expansão)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Alimento

def adicionar_lote3_base_ouro():
    """
    Adiciona o terceiro lote de alimentos essenciais
    """
    print("🥇 LOTE 3 - BASE DE OURO - OPERAÇÃO EM ANDAMENTO")
    print("=" * 60)
    
    # === GRÃOS, PÃES E MASSAS (EXPANSÃO) ===
    graos_paes_massas = [
        ("Aveia em Flocos", 389, 16.9, 66.3, 6.9),
        ("Tapioca (Goma hidratada)", 240, 0.0, 60.0, 0.0),
        ("Pão de Queijo", 335, 5.5, 37.5, 18.0),
        ("Milho Verde, cozido", 86, 3.2, 19.0, 1.2),
    ]
    
    # === PROTEÍNAS (EXPANSÃO) ===
    proteinas_expansao = [
        ("Carne de Porco (Bisteca), grelhada", 283, 25.8, 0.0, 19.3),
        ("Sardinha em Lata (em óleo)", 208, 24.6, 0.0, 11.5),
        ("Linguiça Toscana, grelhada", 322, 16.0, 0.7, 28.0),
        ("Tofu", 76, 8.1, 1.9, 4.8),
    ]
    
    # === FRUTAS, VERDURAS E LEGUMES (EXPANSÃO) ===
    frutas_verduras_legumes = [
        ("Uva Thompson", 69, 0.7, 18.1, 0.2),
        ("Manga Palmer", 60, 0.8, 15.0, 0.4),
        ("Couve Manteiga, refogada", 90, 2.7, 7.6, 6.1),
        ("Quiabo, cozido", 33, 1.9, 7.0, 0.2),
        ("Palmito Pupunha, em conserva", 28, 2.5, 4.2, 0.3),
    ]
    
    # Combinar todos os alimentos
    todos_alimentos_lote3 = graos_paes_massas + proteinas_expansao + frutas_verduras_legumes
    
    # Forçar modo produção para salvar no MySQL
    os.environ['FLASK_ENV'] = 'production'
    
    with app.app_context():
        print("🎯 Conectando ao banco MySQL de produção...")
        
        alimentos_adicionados = 0
        alimentos_existentes = 0
        
        # Processar cada categoria
        categorias = [
            ("🌾 GRÃOS, PÃES E MASSAS", graos_paes_massas),
            ("🥩 PROTEÍNAS", proteinas_expansao),
            ("🍇 FRUTAS, VERDURAS E LEGUMES", frutas_verduras_legumes)
        ]
        
        for categoria_nome, categoria_alimentos in categorias:
            print(f"\n{categoria_nome}:")
            
            for nome, cal, prot, carb, gord in categoria_alimentos:
                # Verificar se já existe
                alimento_existente = Alimento.query.filter_by(nome=nome).first()
                
                if alimento_existente:
                    print(f"  ⚠️  {nome} (já existe)")
                    alimentos_existentes += 1
                    continue
                
                # Criar novo alimento
                novo_alimento = Alimento(
                    nome=nome,
                    calorias=cal,
                    proteinas=prot,
                    carboidratos=carb,
                    gorduras=gord
                )
                
                try:
                    db.session.add(novo_alimento)
                    db.session.commit()
                    print(f"  ✅ {nome} ({cal} kcal)")
                    alimentos_adicionados += 1
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"  ❌ Erro ao adicionar {nome}: {str(e)}")
        
        print(f"\n🏆 LOTE 3 - OPERAÇÃO CONCLUÍDA!")
        print(f"✅ Alimentos adicionados: {alimentos_adicionados}")
        print(f"⚠️  Alimentos já existentes: {alimentos_existentes}")
        print(f"📦 Total processado: {len(todos_alimentos_lote3)}")
        
        # Estatísticas finais
        total_alimentos = Alimento.query.count()
        print(f"\n🎉 BANCO DE DADOS ATUALIZADO!")
        print(f"📊 Total de alimentos no banco: {total_alimentos}")
        
        # Mostrar últimos alimentos adicionados
        if alimentos_adicionados > 0:
            print(f"\n🔍 Últimos {min(5, alimentos_adicionados)} alimentos adicionados:")
            ultimos = Alimento.query.order_by(Alimento.id.desc()).limit(5).all()
            for alimento in ultimos:
                print(f"  • {alimento.nome} - {alimento.calorias} kcal")

if __name__ == '__main__':
    print("🚀 MISSÃO: LOTE 3 DA BASE DE OURO")
    print("Adicionando alimentos essenciais ao banco MySQL de produção")
    print("=" * 60)
    
    resposta = input("🎯 Confirma execução do Lote 3? (s/n): ")
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        adicionar_lote3_base_ouro()
    else:
        print("❌ Operação cancelada")
