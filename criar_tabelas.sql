-- ================================================
-- SCRIPT SQL PARA CRIAR TABELAS L7NUTRI
-- Execute este script no phpMyAdmin da Hostinger
-- ================================================

-- Criar tabela usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_usuario VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela alimentos
CREATE TABLE IF NOT EXISTS alimentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    calorias DECIMAL(10,2) NOT NULL,
    proteinas DECIMAL(10,2) NOT NULL,
    carboidratos DECIMAL(10,2) NOT NULL,
    gorduras DECIMAL(10,2) NOT NULL
);

-- Criar tabela diarios
CREATE TABLE IF NOT EXISTS diarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    data_entrada DATE NOT NULL,
    alimento_id INT NOT NULL,
    quantidade DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (alimento_id) REFERENCES alimentos(id)
);

-- Inserir usuario admin inicial
INSERT INTO usuarios (nome_usuario, email, senha_hash) VALUES 
('admin', 'admin@l7nutri.com', 'scrypt:32768:8:1$2uVFNhPfA7NtKfh7$a8c8b8d8e8f8g8h8i8j8k8l8m8n8o8p8q8r8s8t8u8v8w8x8y8z8');

-- Inserir alimentos base (26 alimentos)
INSERT INTO alimentos (nome, calorias, proteinas, carboidratos, gorduras) VALUES 
('Arroz Branco, cozido', 130, 2.7, 28.2, 0.3),
('Feijao Preto, cozido', 132, 8.9, 23.0, 0.5),
('Frango, peito sem pele', 165, 31.0, 0.0, 3.6),
('Ovo de galinha, cozido', 155, 13.0, 1.1, 11.0),
('Banana, madura', 89, 1.1, 22.8, 0.3),
('Batata doce, cozida', 86, 1.6, 20.1, 0.1),
('Brocolis, cozido', 34, 2.8, 7.0, 0.4),
('Cenoura, crua', 41, 0.9, 9.6, 0.2),
('Tomate, maduro', 18, 0.9, 3.9, 0.2),
('Alface, crespa', 15, 1.4, 3.0, 0.1),
('Aveia em Flocos', 389, 16.9, 66.3, 6.9),
('Tapioca (Goma hidratada)', 240, 0.0, 60.0, 0.0),
('Pao de Queijo', 335, 5.5, 37.5, 18.0),
('Milho Verde, cozido', 86, 3.2, 19.0, 1.2),
('Carne de Porco (Bisteca), grelhada', 283, 25.8, 0.0, 19.3),
('Sardinha em Lata (em oleo)', 208, 24.6, 0.0, 11.5),
('Linguica Toscana, grelhada', 322, 16.0, 0.7, 28.0),
('Tofu', 76, 8.1, 1.9, 4.8),
('Uva Thompson', 69, 0.7, 18.1, 0.2),
('Manga Palmer', 60, 0.8, 15.0, 0.4),
('Couve Manteiga, refogada', 90, 2.7, 7.6, 6.1),
('Quiabo, cozido', 33, 1.9, 7.0, 0.2),
('Palmito Pupunha, em conserva', 28, 2.5, 4.2, 0.3),
('Batata Inglesa, cozida', 87, 1.9, 19.6, 0.1),
('Carne Bovina, alcatra', 163, 29.2, 0.0, 4.8),
('Leite integral', 61, 3.2, 4.6, 3.2);

-- Verificar tabelas criadas
SHOW TABLES;

-- Verificar dados inseridos
SELECT COUNT(*) as total_usuarios FROM usuarios;
SELECT COUNT(*) as total_alimentos FROM alimentos;
SELECT COUNT(*) as total_diarios FROM diarios;
