import sys
import os
sys.path.append('.')
os.environ['FLASK_ENV'] = 'production'

from app import app, db, Alimento

print("Testando conexao MySQL...")

with app.app_context():
    try:
        total = Alimento.query.count()
        print(f"Total alimentos no banco: {total}")
        
        # Adicionar os alimentos do Lote 3
        novos_alimentos = [
            ("Aveia em Flocos", 389, 16.9, 66.3, 6.9),
            ("Tapioca (Goma hidratada)", 240, 0.0, 60.0, 0.0),
            ("Pao de Queijo", 335, 5.5, 37.5, 18.0),
            ("Milho Verde, cozido", 86, 3.2, 19.0, 1.2),
            ("Carne de Porco (Bisteca), grelhada", 283, 25.8, 0.0, 19.3),
            ("Sardinha em Lata (em oleo)", 208, 24.6, 0.0, 11.5),
            ("Linguica Toscana, grelhada", 322, 16.0, 0.7, 28.0),
            ("Tofu", 76, 8.1, 1.9, 4.8),
            ("Uva Thompson", 69, 0.7, 18.1, 0.2),
            ("Manga Palmer", 60, 0.8, 15.0, 0.4),
            ("Couve Manteiga, refogada", 90, 2.7, 7.6, 6.1),
            ("Quiabo, cozido", 33, 1.9, 7.0, 0.2),
            ("Palmito Pupunha, em conserva", 28, 2.5, 4.2, 0.3),
        ]
        
        adicionados = 0
        existentes = 0
        
        for nome, cal, prot, carb, gord in novos_alimentos:
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
                adicionados += 1
            else:
                print(f"JA EXISTE: {nome}")
                existentes += 1
        
        db.session.commit()
        
        print(f"\nRESUMO:")
        print(f"Novos alimentos: {adicionados}")
        print(f"Ja existentes: {existentes}")
        print(f"Total no banco apos adicao: {Alimento.query.count()}")
        print("\nLOTE 3 CONCLUIDO COM SUCESSO!")
        
    except Exception as e:
        print(f"ERRO: {e}")
        db.session.rollback()
