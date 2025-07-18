from app import app, db, Alimento

with app.app_context():
    total = Alimento.query.count()
    print(f"📦 Total de alimentos no banco: {total}")
    
    print("\n🔍 Últimos 10 alimentos:")
    ultimos = Alimento.query.order_by(Alimento.id.desc()).limit(10).all()
    for a in ultimos:
        print(f"• {a.nome} - {a.calorias} kcal")
