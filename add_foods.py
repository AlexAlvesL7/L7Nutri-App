from app import app, db, Alimento

# Lista completa de alimentos para adicionar
alimentos_novos = [
    # Verduras e Legumes (Expansão)
    ("Couve-flor, cozida", 23, 1.8, 4.1, 0.5),
    ("Abobrinha, cozida", 17, 1.2, 3.1, 0.3),
    ("Berinjela, cozida", 35, 1.0, 8.7, 0.2),
    ("Espinafre, cozido", 23, 3.0, 3.7, 0.3),
    ("Pimentão Verde, cru", 20, 0.9, 4.6, 0.2),
    ("Beterraba, cozida", 44, 1.7, 10.0, 0.2),
    
    # Oleaginosas e Sementes
    ("Castanha-do-Pará", 656, 14.3, 12.3, 66.3),
    ("Amêndoas", 579, 21.2, 21.6, 49.9),
    ("Pasta de Amendoim Integral", 588, 25.1, 20.0, 50.0),
    ("Semente de Chia", 486, 16.5, 42.1, 30.7),
    
    # Industrializados e Bebidas
    ("Peito de Peru Defumado", 111, 22.0, 1.5, 1.7),
    ("Atum em Óleo, drenado", 198, 29.0, 0.0, 8.2),
    ("Atum em Água, drenado", 116, 26.0, 0.0, 0.8),
    ("Café Coado, sem açúcar", 2, 0.1, 0.0, 0.0),
    ("Suco de Laranja Natural", 45, 0.7, 10.4, 0.2),
]

with app.app_context():
    adicionados = 0
    for nome, cal, prot, carb, gord in alimentos_novos:
        if not Alimento.query.filter_by(nome=nome).first():
            alimento = Alimento(nome=nome, calorias=cal, proteinas=prot, carboidratos=carb, gorduras=gord)
            db.session.add(alimento)
            adicionados += 1
            print(f"✅ {nome}")
    
    db.session.commit()
    print(f"\n📊 {adicionados} alimentos adicionados!")
    print(f"📦 Total no banco: {Alimento.query.count()}")
