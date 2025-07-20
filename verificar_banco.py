#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db, Alimento

def verificar_alimentos():
    with app.app_context():
        # Contar total de alimentos
        total = Alimento.query.count()
        print(f"📊 Total de alimentos no banco: {total}")
        
        if total > 0:
            print("\n📋 Últimos 10 alimentos adicionados:")
            alimentos = Alimento.query.order_by(Alimento.id.desc()).limit(10).all()
            
            for alimento in alimentos:
                print(f"   • {alimento.nome} ({alimento.categoria}) - {alimento.calorias} kcal")
            
            print("\n🔍 Verificando por categoria:")
            categorias = db.session.query(Alimento.categoria, db.func.count(Alimento.id)).group_by(Alimento.categoria).all()
            
            for categoria, quantidade in categorias:
                print(f"   • {categoria}: {quantidade} alimentos")
                
            print("\n✅ Banco de dados funcionando corretamente!")
        else:
            print("⚠️  Nenhum alimento encontrado no banco.")

if __name__ == "__main__":
    verificar_alimentos()
