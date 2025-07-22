# 🚨 PROTOCOLO DE CORREÇÃO L7NUTRI - OBRIGATÓRIO

## ⚠️ **DIRETRIZES CRÍTICAS** 
**SEMPRE SEGUIR ANTES DE QUALQUER COMMIT**

---

## 📋 **CHECKLIST OBRIGATÓRIO**

### **✅ 1. VERIFICAR INDENTAÇÃO**
```bash
# Verificar TODO o bloco alterado
# Garantir 4 espaços por nível
# Sem mistura de tabs e espaços
```

### **✅ 2. VERIFICAR LOCALIZAÇÃO**
```bash
# Imports no topo do arquivo
# Funções em locais apropriados
# Classes organizadas logicamente
```

### **✅ 3. COMPILAÇÃO OBRIGATÓRIA**
```bash
python -m py_compile app.py
# DEVE rodar SEM ERROS antes de continuar
```

### **✅ 4. MIGRATIONS (Se alterou models)**
```bash
python -m flask db migrate -m "Descrição da alteração"
python -m flask db upgrade
# Sempre que mexer em modelos SQLAlchemy
```

### **✅ 5. TESTES BÁSICOS**
```bash
# Teste manual da funcionalidade alterada
# Ou testes automáticos se disponíveis
python -c "import app; print('Import OK')"
```

### **✅ 6. VERIFICAR TERMINAL**
```bash
# Ler TODO warning, erro ou output
# Corrigir TODOS os problemas antes de commitar
# Não ignorar nenhuma mensagem de erro
```

### **✅ 7. COMMIT E PUSH**
```bash
# SÓ DEPOIS de todas as verificações acima
git add arquivo.py
git commit -m "Descrição detalhada da correção"
git push origin main
```

---

## 🚨 **EXEMPLOS DE VERIFICAÇÃO**

### **❌ NUNCA FAZER:**
```bash
# Commit direto sem testar
git add . && git commit -m "fix" && git push

# Ignorar erros de compilação
python -m py_compile app.py  # ❌ Erro encontrado
git commit -m "fix anyway"   # ❌ NUNCA FAZER ISSO

# Alterar modelo sem migration
# Modificar classe Usuario sem rodar flask db migrate
```

### **✅ SEMPRE FAZER:**
```bash
# 1. Alterar código
# 2. Verificar indentação
# 3. Compilar
python -m py_compile app.py  # ✅ Sem erros

# 4. Se alterou modelo:
python -m flask db migrate -m "Correção modelo X"

# 5. Testar
python -c "import app; print('OK')"  # ✅ Funcionando

# 6. Commit detalhado
git add app.py
git commit -m "🔧 Correção específica: problema X resolvido"
git push origin main
```

---

## 📊 **HISTÓRICO DE APLICAÇÃO**

### **✅ Correção f9e6180 (21/07/2025)**
**Problema:** `NoForeignKeysError` entre StreakUsuario e Usuario
**Protocolo Aplicado:**
- ✅ Verificada indentação
- ✅ `python -m py_compile app.py` (sem erros)
- ✅ Teste de importação realizado  
- ✅ Commit detalhado com explicação completa
- ✅ Deploy seguro aplicado

**Resultado:** Relacionamento SQLAlchemy corrigido

---

## 🎯 **RESPONSABILIDADE**

> **"Este protocolo DEVE ser seguido em TODAS as alterações que possam comprometer nosso trabalho"**

### **Por que é crítico:**
1. **Produção estável:** Evita quebrar sistema em produção
2. **Debug eficiente:** Problemas identificados localmente
3. **Histórico limpo:** Commits organizados e rastreáveis
4. **Colaboração efetiva:** Mudanças documentadas e testadas

### **Quando aplicar:**
- ✅ Alterações em modelos SQLAlchemy
- ✅ Modificações em rotas críticas
- ✅ Correções de bugs em produção
- ✅ Refatoração de código
- ✅ **TODAS** as alterações em `app.py`

---

## 📞 **EM CASO DE DÚVIDA**

1. 🛑 **PARE** antes de fazer commit
2. 🔍 **REVISE** cada item do checklist
3. 🧪 **TESTE** localmente primeiro
4. 📝 **DOCUMENTE** a alteração no commit
5. ✅ **SÓ ENTÃO** faça push para produção

---

**📅 Criado:** 21/07/2025  
**📝 Versão:** 1.0  
**🎯 Status:** OBRIGATÓRIO PARA TODA A EQUIPE
