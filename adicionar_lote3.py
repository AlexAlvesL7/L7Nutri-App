import sys
import os
sys.path.append('.')

# Forcar SQLite para teste local
os.environ['FLASK_ENV'] = 'development'

from app import app, db, Alimento

print("=== OPERACAO BASE DE OURO - LOTE 3 ===")
print("Adicionando 13 novos alimentos ao banco local...")

with app.app_context():
    try:
        # Criar tabelas se nao existirem
        db.create_all()
        
        total_antes = Alimento.query.count()
        print(f"Total de alimentos antes: {total_antes}")
        
        # LOTE 3: Alimentos essenciais
        novos_alimentos = [
            # Graos, Paes e Massas
            ("Aveia em Flocos", 389, 16.9, 66.3, 6.9),
            ("Tapioca (Goma hidratada)", 240, 0.0, 60.0, 0.0),
            ("Pao de Queijo", 335, 5.5, 37.5, 18.0),
            ("Milho Verde, cozido", 86, 3.2, 19.0, 1.2),
            
            # Proteinas
            ("Carne de Porco (Bisteca), grelhada", 283, 25.8, 0.0, 19.3),
            ("Sardinha em Lata (em oleo)", 208, 24.6, 0.0, 11.5),
            ("Linguica Toscana, grelhada", 322, 16.0, 0.7, 28.0),
            ("Tofu", 76, 8.1, 1.9, 4.8),
            
            # Frutas, Verduras e Legumes
            ("Uva Thompson", 69, 0.7, 18.1, 0.2),
            ("Manga Palmer", 60, 0.8, 15.0, 0.4),
            ("Couve Manteiga, refogada", 90, 2.7, 7.6, 6.1),
            ("Quiabo, cozido", 33, 1.9, 7.0, 0.2),
            ("Palmito Pupunha, em conserva", 28, 2.5, 4.2, 0.3),
        ]
        
        print(f"\nProcessando {len(novos_alimentos)} alimentos...")
        
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
                print(f"+ {nome} ({cal} kcal)")
                adicionados += 1
            else:
                print(f"= {nome} (ja existe)")
                existentes += 1
        
        db.session.commit()
        
        total_depois = Alimento.query.count()
        
        print(f"\n=== RESUMO FINAL ===")
        print(f"Alimentos adicionados: {adicionados}")
        print(f"Ja existentes: {existentes}")
        print(f"Total antes: {total_antes}")
        print(f"Total depois: {total_depois}")
        print(f"Diferenca: +{total_depois - total_antes}")
        
        print(f"\n=== LOTE 3 CONCLUIDO COM SUCESSO! ===")
        print(f"Sua base de alimentos agora tem {total_depois} opcoes!")
        
        # Mostrar ultimos 5 adicionados
        print(f"\nUltimos 5 alimentos adicionados:")
        ultimos = Alimento.query.order_by(Alimento.id.desc()).limit(5).all()
        for i, alimento in enumerate(ultimos, 1):
            print(f"  {i}. {alimento.nome} ({alimento.calorias} kcal)")
            
    except Exception as e:
        print(f"ERRO: {e}")
        db.session.rollback()
