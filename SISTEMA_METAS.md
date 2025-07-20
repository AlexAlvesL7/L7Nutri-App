# 🎯 SISTEMA DE METAS NUTRICIONAIS - L7NUTRI

## 📋 VISÃO GERAL

O Sistema de Metas Nutricionais do L7Nutri calcula automaticamente:
- **TMB (Taxa Metabólica Basal)** usando a fórmula de Mifflin-St Jeor
- **Gasto energético total** baseado no nível de atividade física
- **Meta calórica diária** ajustada pelo objetivo do usuário
- **Distribuição de macronutrientes** personalizada

## 🔧 IMPLEMENTAÇÃO TÉCNICA

### **API Endpoint**
```
GET /api/onboarding/metas
Authorization: Bearer <JWT_TOKEN>
```

### **Páginas Web**
- `/metas-nutricionais` - Página principal para usuários logados
- `/demo-metas` - Demonstração pública do sistema

### **Resposta da API**
```json
{
  "usuario_info": {
    "nome": "João Silva",
    "idade": 30,
    "sexo": "masculino",
    "peso": 80,
    "altura": 175,
    "objetivo": "manter_peso",
    "fator_atividade": 1.375
  },
  "calculos": {
    "tmb": 1750,
    "gasto_total": 2406,
    "ajuste_calorico": 0,
    "meta_calorica": 2406
  },
  "macronutrientes": {
    "proteina_g": 150.4,
    "proteina_kcal": 602,
    "proteina_perc": 25,
    "carboidrato_g": 301.0,
    "carboidrato_kcal": 1203,
    "carboidrato_perc": 50,
    "gordura_g": 66.8,
    "gordura_kcal": 601,
    "gordura_perc": 25
  },
  "resumo": {
    "total_calorias": 2406,
    "total_proteina": 150.4,
    "total_carboidrato": 301.0,
    "total_gordura": 66.8
  }
}
```

## 📊 LÓGICA DOS CÁLCULOS

### **1. TMB (Taxa Metabólica Basal)**
```python
# Fórmula de Mifflin-St Jeor (mais precisa)
if sexo == 'masculino':
    tmb = (10 * peso) + (6.25 * altura) - (5 * idade) + 5
else:
    tmb = (10 * peso) + (6.25 * altura) - (5 * idade) - 161
```

### **2. Gasto Energético Total**
```python
gasto_total = tmb * fator_atividade

# Fatores de atividade:
# 1.2   - Sedentário (sem exercício)
# 1.375 - Leve (1-3 dias/semana)
# 1.55  - Moderado (3-5 dias/semana)
# 1.725 - Intenso (6-7 dias/semana)
# 1.9   - Muito intenso (2x/dia)
```

### **3. Ajuste por Objetivo**
```python
ajustes_caloricos = {
    'perder_peso': -500,      # Déficit de 500 kcal
    'emagrecer': -500,        
    'manter_peso': 0,         # Manutenção
    'manter': 0,              
    'vida_saudavel': 0,       
    'ganhar_peso': +400,      # Superávit de 400 kcal
    'ganhar_massa': +500,     # Superávit de 500 kcal
    'performance': +300       
}
```

### **4. Distribuição de Macronutrientes**
```python
# Percentuais padrão
perc_proteina = 0.25     # 25%
perc_carboidrato = 0.50  # 50%
perc_gordura = 0.25      # 25%

# Ajustes por objetivo:
if objetivo == 'ganhar_massa':
    perc_proteina = 0.30      # 30%
    perc_carboidrato = 0.45   # 45%
    perc_gordura = 0.25       # 25%

elif objetivo == 'perder_peso':
    perc_proteina = 0.35      # 35%
    perc_carboidrato = 0.40   # 40%
    perc_gordura = 0.25       # 25%
```

### **5. Conversão para Gramas**
```python
# Proteína e carboidrato: 4 kcal/g
# Gordura: 9 kcal/g

proteina_g = (meta_calorica * perc_proteina) / 4
carboidrato_g = (meta_calorica * perc_carboidrato) / 4
gordura_g = (meta_calorica * perc_gordura) / 9
```

## 🎨 INTERFACE DO USUÁRIO

### **Componentes Visuais**
- **Header**: Título e informações do usuário
- **Meta Principal**: Calorias diárias em destaque
- **Cálculos Base**: TMB, Gasto Total, Ajuste
- **Macronutrientes**: Cards coloridos para cada macro
- **Resumo**: Visão geral das metas
- **Botão de Ação**: Link para o diário alimentar

### **Design Responsivo**
- Grid flexível para diferentes tamanhos de tela
- Cards adaptativos
- Cores temáticas por macronutriente:
  - 🔴 Proteína: Vermelho (#dc3545)
  - 🟡 Carboidrato: Amarelo (#ffc107)
  - 🔵 Gordura: Azul (#17a2b8)

## 🔄 FLUXO DE INTEGRAÇÃO

### **1. Onboarding Completo**
```
Usuário → Cadastro → Perfil → Atividade → Objetivo → Metas
```

### **2. Requisitos de Dados**
- ✅ Idade, sexo, peso, altura
- ✅ Fator de atividade física
- ✅ Objetivo nutricional
- ✅ Token JWT válido

### **3. Tratamento de Erros**
```javascript
// Exemplos de erros tratados:
- Token inválido ou expirado
- Dados do perfil incompletos
- Objetivo não definido
- Erro de conexão com API
```

## 🧪 TESTANDO O SISTEMA

### **1. Demo Pública**
Acesse `/demo-metas` para testar sem login:
- Formulário interativo
- Cálculos em tempo real
- Explicação passo a passo
- Visualização dos resultados

### **2. API Direta**
```bash
# Teste com token JWT
curl -X GET "http://localhost:5000/api/onboarding/metas" \
  -H "Authorization: Bearer SEU_TOKEN_JWT"
```

### **3. Página Completa**
Acesse `/metas-nutricionais` com usuário logado:
- Interface completa
- Dados reais do usuário
- Integração com JavaScript

## 📈 BENEFÍCIOS IMPLEMENTADOS

✅ **Precisão Científica**: Fórmula de Mifflin-St Jeor validada
✅ **Personalização Total**: Ajustes baseados no perfil individual
✅ **Interface Intuitiva**: Design moderno e responsivo
✅ **Integração Completa**: API + Frontend + Autenticação
✅ **Escalabilidade**: Estrutura preparada para expansões
✅ **Experiência do Usuário**: Feedback visual imediato

## 🚀 PRÓXIMAS EXPANSÕES

- 📊 Integração com diário alimentar
- 🔔 Notificações de progresso
- 📈 Gráficos de evolução
- 🤖 Sugestões da IA Gemini
- 📱 Progressive Web App (PWA)

---

**🎯 O sistema está 100% funcional e pronto para produção!**
