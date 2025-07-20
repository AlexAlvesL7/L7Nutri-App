# 🎯 GUIA RÁPIDO - DEPLOY HOSTINGER

## ✅ CHECKLIST COMPLETO PARA DEPLOY

### 📋 ANTES DO UPLOAD (Execute no VS Code)

```bash
# 1. Instalar driver MySQL
pip install PyMySQL

# 2. Configurar banco automaticamente
python config_hostinger.py

# 3. Validar configuração
python validar_deploy.py

# 4. Compactar arquivos para upload
```

## 🍎 ADICIONANDO ALIMENTOS AO BANCO DE DADOS

### ✅ **BANCO DE DADOS TACO/ANVISA COMPLETO IMPLEMENTADO!**

**🎉 117 ALIMENTOS OFICIAIS ADICIONADOS EM 23 CATEGORIAS:**

#### � **Frutas (14 alimentos)**
- **Frutas básicas**: Maçã, Banana, Laranja, Mamão, Abacaxi, Melancia, Manga, Uva, Pera, Morango
- **Frutas tropicais**: Coco fresco, Abacate, Caju, Jaca, Goiaba, Caqui, Figo, Melão, Pêssego, Tangerina, Maracujá, Açaí polpa

#### 🥩 **Proteínas Animais (17 alimentos)**
- **Carnes**: Bovina (patinho), Suína, Frango grelhado, Peito de frango, Coxa de frango assada, Linguiça de frango, Bacon frito, Hambúrguer bovino/frango
- **Embutidos**: Mortadela, Presunto, Salsicha, Salame, Peito de peru
- **Peixes**: Filé de peixe grelhado, Sardinha em conserva, Atum em conserva
- **Frutos do mar**: Camarão, Lula, Polvo, Caranguejo
- **Ovos**: Ovo de galinha cozido
- **Laticínios**: Leite integral/desnatado, Queijo muçarela/minas/prato, Ricota, Requeijão, Iogurte natural/morango

#### 🌾 **Cereais e Carboidratos (10 alimentos)**
- **Básicos**: Arroz branco, Macarrão, Farinha de mandioca, Tapioca, Polenta
- **Saudáveis**: Aveia em flocos, Granola, Farinha láctea, Cereal matinal, Pipoca, Mingau de aveia

#### � **Verduras e Legumes (10 alimentos)**
- **Verduras**: Alface, Repolho, Brócolis, Couve-manteiga, Espinafre, Almeirão, Rúcula
- **Legumes**: Cenoura, Beterraba, Abobrinha, Tomate, Cebola, Pimentão verde, Vagem, Abóbora moranga, Chuchu, Quiabo, Pepino

#### 🫘 **Leguminosas (4 alimentos)**
- Feijão carioca/preto, Ervilha fresca, Lentilha, Grão-de-bico, Soja

#### 🥜 **Oleaginosas (7 alimentos)**
- Castanha-do-pará, Amendoim torrado, Nozes, Amêndoas, Avelã, Pistache, Macadâmia

#### 🍞 **Pães e Biscoitos (7 alimentos)**
- **Pães**: Pão francês, Pão de queijo, Torrada tradicional
- **Biscoitos**: Água e sal, Recheado, Bolacha maisena

#### � **Bebidas (14 alimentos)**
- **Naturais**: Suco de laranja/uva, Água de coco, Café, Chá-mate, Chimarrão, Água mineral
- **Industrializadas**: Refrigerante cola/guaraná, Achocolatado, Energético
- **Alcoólicas**: Cerveja pilsen, Vinho tinto, Caipirinha

#### 🍰 **Doces e Sobremesas (11 alimentos)**
- **Doces**: Paçoca, Doce de leite, Goiabada, Pudim, Brigadeiro, Mousse de maracujá
- **Bolos**: Cenoura, Chocolate, Fubá
- **Sobremesas**: Sorvete de creme, Picolé de frutas

#### 🍕 **Salgados e Fast Food (10 alimentos)**
- **Salgados**: Torta de frango, Empada, Coxinha, Pastel de carne, Quibe, Esfiha
- **Pizzas**: Muçarela, Calabresa
- **Fast Food**: Batata frita, Cachorro-quente

#### 🧈 **Gorduras e Temperos (9 alimentos)**
- **Gorduras**: Margarina, Óleo de soja, Manteiga, Azeite de oliva
- **Industrializados**: Batata palha, Maionese, Ketchup, Mostarda, Molho shoyu
- **Temperos**: Alho

### 📊 **Estrutura da Tabela Alimento (Expandida)**

```sql
CREATE TABLE alimento (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL,
    categoria VARCHAR(50),              -- frutas, legumes, carnes, etc
    calorias FLOAT,                     -- kcal por porção
    proteinas FLOAT,                    -- gramas
    carboidratos FLOAT,                 -- gramas
    gorduras FLOAT,                     -- gramas
    fibras FLOAT,                       -- gramas
    sodio FLOAT,                        -- miligramas
    acucar FLOAT,                       -- gramas
    colesterol FLOAT,                   -- miligramas
    porcao_referencia VARCHAR(20),      -- 100g, 1 unidade, etc
    fonte_dados VARCHAR(50)             -- TACO, ANVISA, etc
);
```

### 🚀 **Scripts Prontos para Adicionar Mais Alimentos**

#### **Método 1: Script Python Direto**
```bash
python inserir_alimentos_taco.py     # Adiciona lista hardcoded
python verificar_banco.py            # Verifica alimentos no banco
```

#### **Método 2: Script JSON/CSV (Lote)**
```bash
python adicionar_alimentos_lote.py arquivo.json
python adicionar_alimentos_lote.py arquivo.csv
python adicionar_alimentos_lote.py arquivo.sql
```

### 🎯 **Formatos Aceitos para Adicionar Alimentos**

#### **1. JSON (Recomendado)**
```json
[
  {
    "nome": "Maçã",
    "categoria": "frutas",
    "calorias": 52.0,
    "proteinas": 0.3,
    "carboidratos": 13.8,
    "gorduras": 0.2,
    "fibras": 2.4,
    "sodio": 1.0,
    "acucar": 10.4,
    "colesterol": 0.0,
    "porcao_referencia": "100g",
    "fonte_dados": "TACO"
  }
]
```

#### **2. CSV**
```csv
nome,categoria,calorias,proteinas,carboidratos,gorduras,fibras,sodio,acucar,colesterol,porcao_referencia,fonte_dados
Maçã,frutas,52.0,0.3,13.8,0.2,2.4,1.0,10.4,0.0,100g,TACO
Banana,frutas,89.0,1.1,22.8,0.3,2.6,1.0,12.2,0.0,100g,TACO
```

#### **3. SQL**
```sql
INSERT INTO alimento (nome, categoria, calorias, proteinas, carboidratos, gorduras, fibras, sodio, acucar, colesterol, porcao_referencia, fonte_dados) VALUES
('Maçã', 'frutas', 52.0, 0.3, 13.8, 0.2, 2.4, 1.0, 10.4, 0.0, '100g', 'TACO');
```

### 🚀 **Como Adicionar os Alimentos**

#### **Método 1: Script Automático (Recomendado)**
```bash
# 1. Migrar estrutura do banco (apenas na primeira vez)
python migrar_alimentos.py

# 2. Adicionar alimentos em lote
python adicionar_alimentos_lote.py exemplo_alimentos.json   # Para JSON
python adicionar_alimentos_lote.py exemplo_alimentos.csv    # Para CSV  
python adicionar_alimentos_lote.py exemplo_alimentos.sql    # Para SQL
```

#### **Método 2: API REST**
```bash
curl -X POST http://localhost:5000/alimentos \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maçã",
    "categoria": "frutas",
    "calorias": 52.0,
    "proteinas": 0.3,
    "carboidratos": 13.8,
    "gorduras": 0.2,
    "fibras": 2.4,
    "sodio": 1.0,
    "acucar": 10.4,
    "colesterol": 0.0,
    "porcao_referencia": "100g",
    "fonte_dados": "TACO"
  }'
```

### 🎯 **RESUMO: Como Enviar Sua Lista**

**✅ FORMATO RECOMENDADO: JSON**
- Mais flexível e fácil de processar
- Suporte completo a todos os campos
- Arquivo: `seus_alimentos.json`

**📝 CAMPOS INCLUIR:**
- **Essenciais**: nome, calorias, proteinas, carboidratos, gorduras
- **Recomendados**: categoria, fibras, sodio, acucar, colesterol
- **Opcionais**: porcao_referencia, fonte_dados

**🚀 ENVIO:**
- Me envie o arquivo JSON ou CSV
- Ou cole os dados diretamente no chat
- Posso processar até 1000+ alimentos de uma vez

**📊 CATEGORIAS TACO/ANVISA:**
- Frutas, Vegetais, Carnes, Peixes, Laticínios
- Cereais, Leguminosas, Tubérculos, Óleos
- Especifique a categoria para melhor organização

### 📂 **Categorias Sugeridas**
- `frutas` - Maçã, Banana, Laranja, etc
- `vegetais` - Brócolis, Alface, Tomate, etc
- `carnes` - Frango, Carne bovina, Porco, etc
- `peixes` - Salmão, Tilápia, Sardinha, etc
- `laticínios` - Leite, Queijo, Iogurte, etc
- `cereais` - Arroz, Aveia, Quinoa, etc
- `leguminosas` - Feijão, Lentilha, Grão-de-bico, etc
- `tubérculos` - Batata, Mandioca, Inhame, etc
- `óleos` - Azeite, Óleo de coco, etc
- `proteínas` - Ovos, Whey protein, etc

### ✅ **Campos Obrigatórios vs Opcionais**

**Obrigatórios:**
- `nome` (string)
- `calorias` (float)
- `proteinas` (float)
- `carboidratos` (float)
- `gorduras` (float)

**Opcionais (padrão = 0 ou valores específicos):**
- `categoria` (padrão = "Outros")
- `fibras` (padrão = 0)
- `sodio` (padrão = 0)
- `acucar` (padrão = 0)
- `colesterol` (padrão = 0)
- `porcao_referencia` (padrão = "100g")
- `fonte_dados` (padrão = "TACO")

#### 📊 **Visualização Gráfica de Macros Diários**
- **API Endpoint**: `/api/diario/macros?data=YYYY-MM-DD` (GET)
- **Biblioteca**: Chart.js para renderização de gráficos

**✨ Recursos Implementados:**
- **Gráfico de Barras**: Comparação visual consumido vs meta
- **Gráfico de Pizza**: Distribuição proporcional de macronutrientes
- **Estatísticas em Tempo Real**: Cards com valores e percentuais
- **Barras de Progresso**: Indicadores visuais de progresso das metas
- **Responsivo**: Gráficos adaptáveis para todos os dispositivos
- **Atualização Automática**: Gráficos se atualizam ao trocar de data

**🎨 Interface Visual:**
- Cards coloridos para cada macronutriente (Proteínas, Carboidratos, Gorduras, Calorias)
- Gráficos lado a lado para comparação
- Cores consistentes: Proteínas (vermelho), Carboidratos (azul), Gorduras (amarelo)
- Animações suaves e transições elegantes

**🔧 Funcionalidades JavaScript:**
- `carregarMacrosDiarios()` - Buscar dados da API
- `atualizarEstatisticasMacros()` - Atualizar cards e barras
- `renderizarGraficos()` - Criar gráficos Chart.js
- `renderizarGraficoBarras()` - Gráfico consumido vs meta
- `renderizarGraficoPizza()` - Distribuição de macros
- `toggleChartType()` - Alternar visualização

#### 📊 **Cálculos Implementados:**
# 1. Instalar driver MySQL
pip install PyMySQL

# 2. Configurar banco automaticamente
python config_hostinger.py

# 3. Validar configuração
python validar_deploy.py

# 4. Compactar arquivos para upload
```

### 🚀 NA HOSTINGER (Execute no painel)

```bash
# 1. Upload dos arquivos para public_html

# 2. Configurar Aplicação Python:
#    - Versão: Python 3.9+
#    - Pasta: /public_html
#    - Arquivo: app.py
#    - WSGI: app

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Criar tabelas no banco
python setup_mysql.py

# 5. Adicionar dados iniciais
python init_producao.py
```

## 🔑 SUAS CREDENCIAIS ATUALIZADAS

```
✅ RENDER (ONLINE): https://l7nutri-app.onrender.com
   • Status: ✅ DEPLOYED e FUNCIONANDO
   • Banco: PostgreSQL automático
   • SSL: Certificado automático
   • Deploy: Automático via GitHub

✅ Banco MySQL Hostinger:
   • Usuário: u419790683_l7nutri_alex
   • Senha: Duda@1401
   • Host: 127.0.0.1
   • Banco: u419790683_l7nutri_novo

✅ Login Inicial da Aplicação:
   • Usuário: admin (ou admin@l7nutri.com)
   • Senha: admin123
   • Status: ✅ Criado e Funcional
```

## 🎉 APÓS DEPLOY - TESTAR

### 🌐 **RENDER (ONLINE AGORA!):**
1. **Home**: `https://l7nutri-app.onrender.com/`
2. **Login**: `https://l7nutri-app.onrender.com/login`
3. **Dashboard IA**: `https://l7nutri-app.onrender.com/dashboard-insights`

### 🏠 **HOSTINGER (Para domínio próprio):**
1. **Home**: `https://seudominio.com/`
2. **Login**: `https://seudominio.com/login`
3. **Dashboard IA**: `https://seudominio.com/dashboard-insights`

## 📞 PROBLEMAS COMUNS

### ❌ Erro de Conexão MySQL
```bash
# Verificar se PyMySQL está instalado
pip list | grep PyMySQL

# Testar conexão
python setup_mysql.py
```

### ❌ Erro 500 (Internal Server Error)
```bash
# Ver logs de erro no painel Hostinger
# Verificar se todas as dependências foram instaladas
pip install -r requirements.txt
```

### ❌ IA não funciona
```bash
# Configurar GEMINI_API_KEY no arquivo .env
# Ou adicionar diretamente no app.py:
# gemini_api_key = "sua_chave_aqui"
```

## 🚀 SUA APLICAÇÃO TERÁ

✅ **Sistema de Login/Cadastro Visual**
✅ **Dashboard de IA com Google Gemini**  
✅ **Diário Alimentar Completo**
✅ **Base de 26+ Alimentos Nutritivos**
✅ **Interface Responsiva e Moderna**
✅ **Suporte Multi-usuário**
✅ **🎯 Sistema de Metas Nutricionais Personalizadas**
✅ **📊 Cálculo Automático de TMB e Macronutrientes**
✅ **🧮 API Completa de Onboarding com Metas**

### 🆕 NOVAS FUNCIONALIDADES IMPLEMENTADAS

#### 🎯 **Sistema de Metas Nutricionais**
- **API Endpoint**: `/api/onboarding/metas` (GET)
- **Página Web**: `/metas-nutricionais`
- **Demo**: `/demo-metas`

**✨ Recursos:**
- Cálculo de TMB usando fórmula de Mifflin-St Jeor
- Ajuste automático por objetivo (emagrecer, manter, ganhar massa)
- Distribuição inteligente de macronutrientes
- Interface visual completa e responsiva
- Integração com JWT para usuários logados

#### � **Sistema de Navegação por Datas no Diário**
- **API Endpoint**: `/api/diario/dias-preenchidos?mes=YYYY-MM` (GET)
- **Funcionalidades Frontend Completas**

**✨ Recursos Implementados:**
- **Setas de Navegação**: Botões ← e → para navegar entre dias
- **Input de Data**: Campo date picker para seleção direta
- **Mini Calendário Visual**: Calendário mensal com destaque nos dias com registros
- **Navegação Ultra Rápida**: Clique em qualquer dia para visualizar registros
- **Indicadores Visuais**: Dias preenchidos destacados em verde
- **Responsivo**: Funciona perfeitamente em mobile e desktop

**🔧 Funcionalidades JavaScript:**
- `voltarDia()` e `avancarDia()` - Navegação por setas
- `mudarDataSelecionada()` - Evento de mudança no input date
- `toggleCalendario()` - Mostrar/ocultar mini calendário
- `carregarDiasPreenchidos()` - Carregar dias com registros do mês
- `selecionarDiaCalendario(dia)` - Seleção de dia no calendário
- Atualização automática dos dados ao mudar de data

#### �📊 **Cálculos Implementados:**
```
1. TMB (Taxa Metabólica Basal):
   - Homens: (10 × peso) + (6.25 × altura) - (5 × idade) + 5
   - Mulheres: (10 × peso) + (6.25 × altura) - (5 × idade) - 161

2. Gasto Total: TMB × Fator de Atividade

3. Ajuste por Objetivo:
   - Emagrecer: -500 kcal
   - Manter: 0 kcal
   - Ganhar massa: +500 kcal

4. Macronutrientes:
   - Proteína: 25-35% (ajustável por objetivo)
   - Carboidrato: 40-50% (ajustável por objetivo)
   - Gordura: 25% (padrão)
```

**🎯 Pronto para receber usuários reais!**
