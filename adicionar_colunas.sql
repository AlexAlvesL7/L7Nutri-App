-- COMANDOS SQL PARA ADICIONAR COLUNAS FALTANTES
-- Gerado automaticamente em 22/07/2025

-- 1. Adicionar coluna email_verificado
ALTER TABLE usuario ADD COLUMN email_verificado BOOLEAN DEFAULT false NOT NULL;

-- 2. Adicionar coluna token_verificacao
ALTER TABLE usuario ADD COLUMN token_verificacao TEXT;

-- 3. Adicionar coluna token_expiracao
ALTER TABLE usuario ADD COLUMN token_expiracao TIMESTAMP;

-- 4. Adicionar coluna data_criacao
ALTER TABLE usuario ADD COLUMN data_criacao TIMESTAMP DEFAULT now();

-- 5. Adicionar coluna ultimo_login
ALTER TABLE usuario ADD COLUMN ultimo_login TIMESTAMP;

-- 6. Adicionar coluna onboarding_completo
ALTER TABLE usuario ADD COLUMN onboarding_completo BOOLEAN DEFAULT false NOT NULL;

-- 7. Adicionar coluna dados_questionario
ALTER TABLE usuario ADD COLUMN dados_questionario JSONB;

-- 8. Adicionar coluna plano_personalizado
ALTER TABLE usuario ADD COLUMN plano_personalizado JSONB;

-- 9. Adicionar coluna dicas_l7chef
ALTER TABLE usuario ADD COLUMN dicas_l7chef JSONB;

-- 10. Adicionar coluna analise_nutricional
ALTER TABLE usuario ADD COLUMN analise_nutricional JSONB;

-- 11. Adicionar coluna tentativas_login
ALTER TABLE usuario ADD COLUMN tentativas_login INTEGER DEFAULT 0;

-- 12. Adicionar coluna bloqueado_ate
ALTER TABLE usuario ADD COLUMN bloqueado_ate TIMESTAMP;

-- 13. Adicionar coluna ip_cadastro
ALTER TABLE usuario ADD COLUMN ip_cadastro TEXT;

