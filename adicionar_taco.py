#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from app import app, db, Alimento

def main():
    with open('alimentos_taco_completos.json', 'r', encoding='utf-8') as f:
        alimentos_data = json.load(f)

    contador_adicionados = 0
    contador_existentes = 0

    with app.app_context():
        # Criar tabelas se necessário
        db.create_all()
        
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

if __name__ == "__main__":
    main()
