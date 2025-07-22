# Correções Temporárias para Compatibilidade com Banco de Dados

## Problema Identificado
O modelo Usuario no Python tem 24 colunas, mas a tabela no PostgreSQL só tem 11 colunas básicas.

## Campos Comentados no Modelo (13 campos ausentes):
1. `email_verificado` - Boolean para verificação de email
2. `token_verificacao` - String para token de verificação
3. `token_expiracao` - DateTime para expiração do token
4. `data_criacao` - DateTime de criação da conta
5. `ultimo_login` - DateTime do último login
6. `onboarding_completo` - Boolean para completude do onboarding
7. `dados_questionario` - JSON com dados do questionário
8. `plano_personalizado` - JSON com plano personalizado
9. `dicas_l7chef` - JSON com dicas do L7Chef
10. `analise_nutricional` - JSON com análise nutricional
11. `tentativas_login` - Integer com tentativas de login
12. `bloqueado_ate` - DateTime até quando está bloqueado
13. `ip_cadastro` - String com IP de cadastro

## Alterações Temporárias Realizadas:

### 1. Métodos da Classe Usuario
- `esta_verificado()`: Usa getattr() com default True
- `esta_onboarding_completo()`: Usa getattr() com default True
- `pode_acessar_diario()`: Usa getattr() com default True
- `token_valido()`: Usa getattr() para token_expiracao
- `esta_bloqueado()`: Usa getattr() para bloqueado_ate

### 2. Decorators de Segurança
- `requer_email_verificado`: Usa getattr() para email_verificado
- `requer_onboarding_completo`: Usa getattr() para onboarding_completo

### 3. Funções de Cadastro e Login
- Comentado atribuições de campos inexistentes no novo usuário
- Comentado update de ultimo_login
- Simplificado lógica de verificação de email existente

### 4. Funcionalidades Temporariamente Desabilitadas
- Verificação de email (retorna sucesso automático)
- Reenvio de verificação (retorna sucesso automático)
- Salvamento de dados_questionario
- Salvamento de analise_nutricional
- Update de ultimo_login

### 5. Funções de Análise Nutricional
- Usa getattr() para acessar campos opcionais
- Comentado salvamento de novas análises

## Status Atual:
✅ Sistema funcional com 11 campos básicos
✅ Compatibilidade com banco existente
✅ Funcionalidades básicas de cadastro e login operacionais
❌ Funcionalidades avançadas temporariamente desabilitadas

## Próximos Passos:
1. Executar o arquivo `adicionar_colunas.sql` no PostgreSQL do Render
2. Descomentar todas as linhas comentadas no modelo Usuario
3. Restaurar funcionalidades temporariamente desabilitadas
4. Fazer novo deploy da aplicação
5. Testar todas as funcionalidades completas

## Arquivos para Migração:
- `adicionar_colunas.sql` - Comandos SQL para adicionar 13 colunas
- `verificar_colunas_completo.py` - Script para verificar alinhamento

## Comando para Verificar Status:
```bash
python verificar_colunas_completo.py
```
