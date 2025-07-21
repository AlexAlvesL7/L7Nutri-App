# 🔍 INSTRUÇÕES PARA INVESTIGAÇÃO MANUAL DO BANCO POSTGRESQL

## 📋 PASSOS PARA ACESSAR O BANCO VIA PAINEL RENDER

### 1. **Acessar Painel do Render**
1. Acesse: https://dashboard.render.com/
2. Faça login na sua conta
3. Vá para a seção "PostgreSQL" ou "Databases"
4. Selecione o banco do projeto L7Nutri

> 💡 **DICA:** Se tiver dificuldade navegando no painel, consulte o arquivo `GUIA_VISUAL_RENDER.md` para instruções detalhadas com descrições visuais!

### 2. **Conectar ao Banco - PASSO A PASSO DETALHADO**

#### **🖥️ OPÇÃO A - Via Painel Web do Render (MAIS FÁCIL)**
1. **No painel do banco PostgreSQL:**
   - Você verá abas como: "Info", "Connect", "Metrics", etc.
   - Clique na aba **"Connect"**

2. **Na aba Connect:**
   - Você verá seções como:
     - "Internal Database URL" (para apps no Render)
     - "External Database URL" (para conexões externas)
   - **IMPORTANTE:** Procure por um botão/link **"Open Database Shell"** ou **"Console"**
   - Se existir, clique nele → Abrirá um terminal web direto no PostgreSQL

3. **Se encontrar o Web Shell:**
   - Uma tela preta/terminal aparecerá
   - Você estará conectado diretamente ao PostgreSQL
   - **Pule para a seção 3 (Comandos SQL)**

#### **🔗 OPÇÃO B - External Connection (se não tiver Web Shell)**
1. **Na aba "Connect", procure por:**
   - Campo "External Database URL" 
   - Algo como: `postgresql://user:password@host:port/database`

2. **Copie TODA a URL** (exemplo):
   ```
   postgresql://l7nutri_user:abc123xyz@dpg-xyz-a.oregon-postgres.render.com:5432/l7nutri_db
   ```

3. **Cole a URL em um dos clientes abaixo:**

#### **🛠️ OPÇÃO C - Usando Clientes Externos**

**C1 - DBeaver (Recomendado - Grátis):**
1. Baixe: https://dbeaver.io/download/
2. Instale e abra
3. Novo Connection → PostgreSQL
4. Cole a URL do Render na seção "Connection URL"
5. OU preencha manualmente:
   - Host: (extrair da URL)
   - Port: 5432
   - Database: (nome do banco)
   - Username: (usuário da URL)
   - Password: (senha da URL)

**C2 - pgAdmin (Grátis):**
1. Baixe: https://www.pgadmin.org/download/
2. Instale e abra
3. Add New Server
4. Preencha com dados da URL do Render

**C3 - Terminal Local (se tiver psql instalado):**
```bash
# Cole diretamente a URL:
psql "postgresql://user:password@host:port/database"
```

#### **✅ COMO SABER SE CONECTOU CORRETAMENTE**

**Se usando Web Shell do Render:**
- Verá prompt como: `database_name=#` ou `postgres=#`
- Pode digitar comandos SQL diretamente

**Se usando DBeaver/pgAdmin:**
- Árvore de conexão mostrará "Connected"
- Pode abrir "SQL Console" ou "Query Tool"

**Se usando terminal psql:**
- Verá prompt como: `l7nutri_db=>` 
- Pode digitar comandos SQL

**TESTE DE CONEXÃO:**
Digite: `SELECT version();`
- Se retornar versão do PostgreSQL → ✅ Conectado!
- Se der erro → ❌ Problema de conexão

### 3. **Comandos SQL para Executar**

```sql
-- 1. LISTAR TODAS AS TABELAS
\dt

-- OU se não estiver em psql:
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- 2. PROCURAR TABELA CONQUISTAS_USUARIOS
-- (Veja se aparece na lista acima)

-- 3. SE A TABELA EXISTIR, VER ESTRUTURA:
\d conquistas_usuarios

-- OU:
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'conquistas_usuarios';

-- 4. CONTAR REGISTROS (se existir):
SELECT COUNT(*) FROM conquistas_usuarios;

-- 5. SE CONFIRMAR QUE PODE DELETAR:
DROP TABLE conquistas_usuarios;

-- 6. CONFIRMAR REMOÇÃO:
\dt
-- (conquistas_usuarios NÃO deve aparecer mais)
```

### 4. **Resultados Esperados**

**Se tabela EXISTIR:**
```
✅ CAUSA RAIZ CONFIRMADA!
- Tabela órfã `conquistas_usuarios` existe no banco
- Código atual não tem modelo para ela  
- SQLAlchemy falha ao tentar mapear
- SOLUÇÃO: Deletar a tabela
```

**Se tabela NÃO EXISTIR:**
```
❓ PROBLEMA MAIS COMPLEXO
- Pode ser cache persistente do Render
- Pode ser problema de migração
- SOLUÇÃO: Investigar logs do Render/Flask
```

### 5. **Após Deletar Tabela (se necessário)**

```bash
# No projeto local, executar:
flask db upgrade

# OU se usar ambiente virtual:
python -m flask db upgrade
```

### 6. **Reiniciar Serviço Render**
1. No painel do Render, vá para o serviço L7Nutri
2. Clique em "Manual Deploy" ou "Restart"
3. Aguarde reinicialização

### 7. **Testar Sistema**
```bash
# Testar API básica:
curl https://l7nutri-app.onrender.com/api/teste

# Testar diagnóstico:
curl https://l7nutri-app.onrender.com/api/diagnostico-db

# Testar cadastro:
curl https://l7nutri-app.onrender.com/cadastro
```

---

## 🎯 **RESULTADO ESPERADO**

Após remover tabela órfã e reiniciar:
- ✅ Status 200 em `/api/teste`  
- ✅ Status 200 em `/api/diagnostico-db`
- ✅ Página de cadastro carrega normalmente
- ✅ Sistema completamente funcional

---

## ⚠️ **BACKUP ANTES DE DELETAR**

Se a tabela `conquistas_usuarios` tiver dados importantes:

```sql
-- FAZER BACKUP ANTES:
CREATE TABLE conquistas_usuarios_backup AS SELECT * FROM conquistas_usuarios;

-- DEPOIS DELETAR:
DROP TABLE conquistas_usuarios;

-- SE PRECISAR RESTAURAR:
CREATE TABLE conquistas_usuarios AS SELECT * FROM conquistas_usuarios_backup;
```
