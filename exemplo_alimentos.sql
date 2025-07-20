-- Exemplo de comandos SQL para inserir alimentos
-- Base: Tabela TACO e fontes oficiais ANVISA

INSERT INTO alimento (nome, categoria, calorias, proteinas, carboidratos, gorduras, fibras, sodio, acucar, colesterol, porcao_referencia, fonte_dados) VALUES
('Maçã', 'frutas', 52.0, 0.3, 13.8, 0.2, 2.4, 1.0, 10.4, 0.0, '100g', 'TACO'),
('Banana', 'frutas', 89.0, 1.1, 22.8, 0.3, 2.6, 1.0, 12.2, 0.0, '100g', 'TACO'),
('Arroz branco cozido', 'cereais', 130.0, 2.7, 28.1, 0.3, 0.4, 1.0, 0.1, 0.0, '100g', 'TACO'),
('Peito de frango grelhado', 'carnes', 165.0, 31.0, 0.0, 3.6, 0.0, 74.0, 0.0, 85.0, '100g', 'TACO'),
('Brócolis cozido', 'vegetais', 25.0, 3.4, 4.0, 0.4, 3.4, 8.0, 1.9, 0.0, '100g', 'TACO'),
('Leite integral', 'laticínios', 61.0, 3.2, 4.3, 3.5, 0.0, 43.0, 4.3, 11.0, '100ml', 'TACO'),
('Ovo cozido', 'proteínas', 155.0, 13.0, 1.1, 11.0, 0.0, 124.0, 1.1, 372.0, '100g', 'TACO'),
('Batata inglesa cozida', 'tubérculos', 52.0, 1.9, 11.9, 0.1, 1.3, 2.0, 0.9, 0.0, '100g', 'TACO'),
('Feijão preto cozido', 'leguminosas', 77.0, 4.5, 14.0, 0.5, 8.4, 2.0, 0.3, 0.0, '100g', 'TACO'),
('Azeite de oliva', 'óleos', 884.0, 0.0, 0.0, 100.0, 0.0, 2.0, 0.0, 0.0, '100ml', 'TACO'),
('Laranja', 'frutas', 47.0, 0.9, 11.7, 0.1, 2.2, 1.0, 9.4, 0.0, '100g', 'TACO'),
('Tomate', 'vegetais', 18.0, 0.9, 3.9, 0.2, 1.2, 5.0, 2.6, 0.0, '100g', 'TACO'),
('Alface', 'vegetais', 15.0, 1.4, 2.9, 0.2, 2.0, 9.0, 1.3, 0.0, '100g', 'TACO'),
('Salmão grelhado', 'peixes', 208.0, 25.4, 0.0, 12.4, 0.0, 98.0, 0.0, 70.0, '100g', 'TACO'),
('Aveia em flocos', 'cereais', 394.0, 13.9, 67.0, 8.5, 9.1, 2.0, 0.0, 0.0, '100g', 'TACO');
