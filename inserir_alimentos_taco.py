#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db

# Lista de alimentos TACO
alimentos_taco = [
    ("Arroz branco cozido", "cereais", 128, 2.5, 28.0, 0.2, 1.6, 1.0, 0.0, 0.0, "100g", "TACO"),
    ("Feijão carioca cozido", "leguminosas", 76, 4.8, 13.6, 0.5, 8.5, 1.0, 0.3, 0.0, "100g", "TACO"),
    ("Feijão preto cozido", "leguminosas", 77, 4.5, 14.0, 0.5, 8.4, 1.0, 0.3, 0.0, "100g", "TACO"),
    ("Macarrão cozido", "cereais", 131, 4.5, 26.0, 1.1, 1.3, 1.0, 0.5, 0.0, "100g", "TACO"),
    ("Pão francês", "pães", 135, 4.3, 27.0, 0.8, 1.3, 340.0, 1.0, 0.0, "50g (1 unidade)", "TACO"),
    ("Farinha de mandioca", "cereais", 365, 1.6, 88.0, 0.3, 6.4, 0.0, 2.0, 0.0, "100g", "TACO"),
    ("Batata cozida", "tubérculos", 52, 1.2, 12.0, 0.1, 1.3, 1.0, 0.8, 0.0, "100g", "TACO"),
    ("Mandioca cozida", "tubérculos", 125, 0.6, 30.0, 0.2, 1.8, 2.0, 1.0, 0.0, "100g", "TACO"),
    ("Carne bovina cozida (patinho)", "carnes", 219, 32.0, 0.0, 9.0, 0.0, 60.0, 0.0, 84.0, "100g", "TACO"),
    ("Carne suína cozida", "carnes", 212, 29.2, 0.0, 9.7, 0.0, 55.0, 0.0, 82.0, "100g", "TACO"),
    ("Frango grelhado (peito)", "carnes", 163, 31.0, 0.0, 3.1, 0.0, 53.0, 0.0, 85.0, "100g", "TACO"),
    ("Peito de frango cozido", "carnes", 170, 29.0, 0.0, 5.0, 0.0, 60.0, 0.0, 85.0, "100g", "TACO"),
    ("Ovo de galinha cozido", "ovos", 146, 13.0, 1.2, 9.5, 0.0, 125.0, 1.1, 373.0, "60g (1 unidade)", "TACO"),
    ("Leite integral", "laticínios", 61, 3.2, 4.7, 3.4, 0.0, 50.0, 4.7, 14.0, "100ml", "TACO"),
    ("Queijo muçarela", "laticínios", 328, 25.0, 2.3, 25.0, 0.0, 600.0, 1.0, 88.0, "100g", "TACO"),
    ("Queijo minas frescal", "laticínios", 264, 17.0, 3.1, 20.0, 0.0, 500.0, 1.5, 53.0, "100g", "TACO"),
    ("Iogurte natural", "laticínios", 59, 3.6, 5.0, 3.3, 0.0, 52.0, 5.0, 13.0, "100g", "TACO"),
    ("Banana prata", "frutas", 98, 1.3, 26.0, 0.1, 2.2, 1.0, 14.5, 0.0, "100g", "TACO"),
    ("Maçã", "frutas", 54, 0.3, 14.0, 0.2, 1.5, 1.0, 10.0, 0.0, "100g", "TACO"),
    ("Laranja pera", "frutas", 46, 0.7, 11.6, 0.2, 2.2, 0.0, 9.0, 0.0, "100g", "TACO"),
    ("Mamão papaya", "frutas", 45, 0.5, 11.2, 0.1, 1.8, 1.0, 8.3, 0.0, "100g", "TACO"),
    ("Abacaxi", "frutas", 48, 0.9, 12.0, 0.1, 1.0, 1.0, 10.0, 0.0, "100g", "TACO"),
    ("Melancia", "frutas", 30, 0.6, 8.0, 0.1, 0.3, 1.0, 6.2, 0.0, "100g", "TACO"),
    ("Mamão formosa", "frutas", 36, 0.7, 8.6, 0.1, 1.0, 1.0, 7.5, 0.0, "100g", "TACO"),
    ("Manga", "frutas", 60, 0.8, 15.0, 0.2, 1.6, 1.0, 13.7, 0.0, "100g", "TACO"),
    ("Uva", "frutas", 60, 0.5, 14.0, 0.2, 0.9, 1.0, 13.6, 0.0, "100g", "TACO"),
    ("Pera", "frutas", 53, 0.4, 14.0, 0.2, 3.1, 1.0, 9.8, 0.0, "100g", "TACO"),
    ("Morango", "frutas", 30, 0.8, 7.0, 0.3, 2.0, 1.0, 4.5, 0.0, "100g", "TACO"),
    ("Alface", "verduras", 15, 1.4, 2.9, 0.2, 2.0, 5.0, 0.8, 0.0, "100g", "TACO"),
    ("Cenoura cozida", "legumes", 40, 0.9, 9.2, 0.2, 2.8, 44.0, 4.7, 0.0, "100g", "TACO"),
    ("Beterraba cozida", "legumes", 49, 1.8, 11.0, 0.1, 2.8, 46.0, 7.9, 0.0, "100g", "TACO"),
    ("Repolho", "verduras", 17, 1.3, 3.9, 0.1, 2.5, 5.0, 2.0, 0.0, "100g", "TACO"),
    ("Brócolis cozido", "verduras", 25, 3.0, 4.0, 0.4, 3.3, 19.0, 1.4, 0.0, "100g", "TACO"),
    ("Abobrinha cozida", "legumes", 20, 1.0, 4.3, 0.1, 1.3, 0.0, 2.4, 0.0, "100g", "TACO"),
    ("Tomate", "legumes", 19, 0.9, 4.2, 0.2, 1.2, 3.0, 2.6, 0.0, "100g", "TACO"),
    ("Cebola", "legumes", 40, 1.1, 9.3, 0.1, 1.7, 2.0, 4.2, 0.0, "100g", "TACO"),
]

def main():
    with app.app_context():
        print("🔄 Criando tabelas...")
        db.create_all()
        
        # Importar o modelo aqui para evitar problemas de importação circular
        from app import Alimento
        
        contador_adicionados = 0
        contador_existentes = 0
        
        for dados in alimentos_taco:
            nome, categoria, calorias, proteinas, carbs, gorduras, fibras, sodio, acucar, colesterol, porcao, fonte = dados
            
            # Verifica se já existe
            existente = Alimento.query.filter_by(nome=nome).first()
            if existente:
                print(f"⚠️  {nome} - já existe")
                contador_existentes += 1
                continue
            
            # Cria novo alimento
            alimento = Alimento(
                nome=nome,
                categoria=categoria,
                calorias=calorias,
                proteinas=proteinas,
                carboidratos=carbs,
                gorduras=gorduras,
                fibras=fibras,
                sodio=sodio,
                acucar=acucar,
                colesterol=colesterol,
                porcao_referencia=porcao,
                fonte_dados=fonte
            )
            
            db.session.add(alimento)
            print(f"✅ {nome} - adicionado")
            contador_adicionados += 1
        
        # Salvar tudo
        try:
            db.session.commit()
            print(f"\n🎉 CONCLUÍDO!")
            print(f"   ✅ Adicionados: {contador_adicionados}")
            print(f"   ⚠️  Já existiam: {contador_existentes}")
            print(f"   📊 Total: {contador_adicionados + contador_existentes}")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            db.session.rollback()

if __name__ == "__main__":
    main()
