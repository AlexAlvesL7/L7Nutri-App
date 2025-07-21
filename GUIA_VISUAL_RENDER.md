# 🎯 GUIA VISUAL - NAVEGAÇÃO PAINEL RENDER POSTGRESQL

## 📱 PASSO A PASSO COM DESCRIÇÕES VISUAIS

### **Passo 1: Login no Render**
```
🌐 Acesse: https://dashboard.render.com/
🔑 Faça login com suas credenciais
```

### **Passo 2: Localizar Banco PostgreSQL**
```
📋 No Dashboard principal, você verá uma lista de serviços
🔍 PROCURE por:
   - Seção "PostgreSQL" no menu lateral, OU
   - Card/item com nome do seu banco (ex: "l7nutri-database")
   - Ícone de banco de dados (🗄️)

🖱️ CLIQUE no nome do banco PostgreSQL
```

### **Passo 3: Painel do Banco**
```
📊 Você estará agora na página específica do banco
📌 VERÁ abas no topo:
   [ Info ] [ Connect ] [ Metrics ] [ Settings ] [ Logs ]

🎯 CLIQUE na aba "Connect"
```

### **Passo 4: Aba Connect**
```
🔗 Na aba Connect, você verá seções como:

┌─ Internal Database URL ─────────────────┐
│ postgresql://internal.url...            │
│ (Para apps dentro do Render)            │
└─────────────────────────────────────────┘

┌─ External Database URL ─────────────────┐
│ postgresql://user:pass@host:port/db     │
│ [📋 Copy] [👁️ Show]                     │
│ (Para conexões externas)                │
└─────────────────────────────────────────┘

🔍 PROCURE TAMBÉM POR:
   - Botão "Open Database Shell" 
   - Link "Console"
   - "Web Terminal"
   - "SQL Shell"
```

### **Passo 5A: Se encontrar Web Shell**
```
🖥️ CLIQUE em "Open Database Shell" ou similar
⚡ Abrirá uma janela/iframe com terminal preto
💬 Verá prompt como: database_name=#

✅ CONECTADO! Pule para comandos SQL
```

### **Passo 5B: Se NÃO encontrar Web Shell**
```
📋 CLIQUE em "Copy" na External Database URL
📝 Cole em um editor de texto
📱 A URL será algo como:
   postgresql://l7nutri_abc:xyz123@dpg-abc-xyz.oregon-postgres.render.com:5432/l7nutri_db

🛠️ Use essa URL em DBeaver, pgAdmin ou psql
```

---

## 🛠️ INSTALAÇÃO RÁPIDA DBEAVER (Recomendado)

### **Se escolher DBeaver:**
```
1. 📥 Download: https://dbeaver.io/download/
2. ⚡ Instalar (Next, Next, Finish)
3. 🚀 Abrir DBeaver
4. 🔌 New Database Connection
5. 🐘 Escolher "PostgreSQL"  
6. 📋 Cole a URL do Render OU preencha campos separados
7. ✅ Test Connection
8. 🎯 Se conectar → Abrir SQL Console
```

---

## 🚨 TROUBLESHOOTING

### **Se não conseguir encontrar o banco:**
```
❓ Possíveis nomes/locais:
   - "PostgreSQL" no menu lateral
   - Nome do app + "-database" 
   - Seção "Services" → filtrar por "Database"
   - Buscar por ícone 🗄️
```

### **Se não conseguir conectar:**
```
❌ Problemas comuns:
   - URL copiada incompleta
   - Firewall bloqueando conexão
   - Banco pausado/suspenso (plano free)
   
💡 Soluções:
   - Copiar URL completa novamente
   - Tentar conexão via Web Shell do Render
   - Verificar se banco está ativo (não pausado)
```

### **Se Web Shell não responder:**
```
⏱️ Web Shell pode ser lento
🔄 Aguarde 10-30 segundos
🔁 Tente recarregar página
📱 Use cliente externo como backup
```

---

## 🎯 PRÓXIMO PASSO

✅ **Assim que conseguir conectar**, volte para `INSTRUCOES_BANCO_MANUAL.md` 
🔍 Execute os comandos SQL da seção 3
🎪 Procure pela tabela `conquistas_usuarios`!
