"""
🔍 VERIFICAÇÃO COMPLETA DE COLUNAS - L7NUTRI
Script para identificar diferenças entre modelo Python e tabela real

Data: 22/07/2025
Autor: Sistema de Diagnóstico Avançado
"""

import re
import os

def extrair_colunas_modelo():
    """
    Extrai todas as colunas definidas no modelo Usuario do app.py
    """
    colunas_modelo = []
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Encontrar a classe Usuario
        inicio_usuario = conteudo.find('class Usuario(db.Model):')
        if inicio_usuario == -1:
            print("❌ Classe Usuario não encontrada no app.py")
            return []
        
        # Encontrar o final da classe (próxima classe ou final do arquivo)
        proxima_classe = conteudo.find('\nclass ', inicio_usuario + 1)
        if proxima_classe == -1:
            fim_usuario = len(conteudo)
        else:
            fim_usuario = proxima_classe
        
        classe_usuario = conteudo[inicio_usuario:fim_usuario]
        
        # Extrair linhas com db.Column
        linhas = classe_usuario.split('\n')
        for linha in linhas:
            linha = linha.strip()
            if '= db.Column(' in linha and not linha.startswith('#'):
                # Extrair nome da coluna
                match = re.match(r'(\w+)\s*=\s*db\.Column\(', linha)
                if match:
                    nome_coluna = match.group(1)
                    # Extrair tipo da coluna
                    tipo_match = re.search(r'db\.Column\(([^,)]+)', linha)
                    tipo = tipo_match.group(1) if tipo_match else 'UNKNOWN'
                    
                    # Verificar se tem default
                    default = None
                    if 'default=' in linha:
                        default_match = re.search(r'default=([^,)]+)', linha)
                        if default_match:
                            default = default_match.group(1)
                    
                    # Verificar nullable
                    nullable = True
                    if 'nullable=False' in linha:
                        nullable = False
                    
                    colunas_modelo.append({
                        'nome': nome_coluna,
                        'tipo': tipo,
                        'default': default,
                        'nullable': nullable,
                        'linha_original': linha
                    })
        
        return colunas_modelo
    
    except Exception as e:
        print(f"❌ Erro ao ler app.py: {e}")
        return []

def gerar_sql_adicionar_colunas(colunas_modelo, colunas_basicas_existentes):
    """
    Gera comandos SQL para adicionar colunas faltantes
    """
    
    # Colunas que sabemos que existem no banco (básicas)
    colunas_existentes = set(colunas_basicas_existentes)
    
    comandos_sql = []
    colunas_faltantes = []
    
    for coluna in colunas_modelo:
        nome = coluna['nome']
        
        if nome not in colunas_existentes:
            colunas_faltantes.append(coluna)
            
            # Mapear tipos SQLAlchemy para PostgreSQL
            tipo_sql = mapear_tipo_postgresql(coluna['tipo'])
            
            # Construir comando SQL
            sql = f"ALTER TABLE usuario ADD COLUMN {nome} {tipo_sql}"
            
            # Adicionar default se existir
            if coluna['default']:
                default_sql = converter_default_sql(coluna['default'])
                if default_sql:
                    sql += f" DEFAULT {default_sql}"
            
            # Adicionar NOT NULL se necessário
            if not coluna['nullable']:
                sql += " NOT NULL"
            
            sql += ";"
            comandos_sql.append(sql)
    
    return comandos_sql, colunas_faltantes

def mapear_tipo_postgresql(tipo_sqlalchemy):
    """
    Mapeia tipos SQLAlchemy para PostgreSQL
    """
    mapeamento = {
        'db.Integer': 'INTEGER',
        'db.String(150)': 'VARCHAR(150)',
        'db.String(80)': 'VARCHAR(80)',
        'db.String(120)': 'VARCHAR(120)',
        'db.String(50)': 'VARCHAR(50)',
        'db.String(100)': 'VARCHAR(100)',
        'db.String(10)': 'VARCHAR(10)',
        'db.String(255)': 'VARCHAR(255)',
        'db.String(40)': 'VARCHAR(40)',
        'db.Float': 'REAL',
        'db.Boolean': 'BOOLEAN',
        'db.DateTime': 'TIMESTAMP',
        'db.Date': 'DATE',
        'db.Text': 'TEXT',
        'db.JSON': 'JSONB'
    }
    
    # Buscar mapeamento exato primeiro
    if tipo_sqlalchemy in mapeamento:
        return mapeamento[tipo_sqlalchemy]
    
    # Buscar por padrões
    if 'String(' in tipo_sqlalchemy:
        match = re.search(r'String\((\d+)\)', tipo_sqlalchemy)
        if match:
            tamanho = match.group(1)
            return f'VARCHAR({tamanho})'
    
    # Tipos básicos
    if 'Integer' in tipo_sqlalchemy:
        return 'INTEGER'
    elif 'Float' in tipo_sqlalchemy:
        return 'REAL'
    elif 'Boolean' in tipo_sqlalchemy:
        return 'BOOLEAN'
    elif 'DateTime' in tipo_sqlalchemy:
        return 'TIMESTAMP'
    elif 'Date' in tipo_sqlalchemy:
        return 'DATE'
    elif 'Text' in tipo_sqlalchemy:
        return 'TEXT'
    elif 'JSON' in tipo_sqlalchemy:
        return 'JSONB'
    
    # Default
    return 'TEXT'

def converter_default_sql(default_python):
    """
    Converte valores default Python para SQL
    """
    conversoes = {
        'False': 'false',
        'True': 'true',
        'datetime.utcnow': 'now()',
        'date.today': 'CURRENT_DATE',
        '0': '0'
    }
    
    if default_python in conversoes:
        return conversoes[default_python]
    
    if default_python.startswith("'") and default_python.endswith("'"):
        return default_python  # Já é string SQL
    
    if default_python.isdigit():
        return default_python  # Número
    
    return None  # Não conseguiu converter

def main():
    print("🔍 VERIFICAÇÃO COMPLETA DE COLUNAS - L7NUTRI")
    print("=" * 60)
    
    # Colunas básicas que sabemos que existem (baseado no DBeaver)
    colunas_basicas = [
        'id', 'nome', 'email', 'username', 'password',
        'idade', 'sexo', 'peso', 'altura', 'nivel_atividade', 'objetivo'
    ]
    
    print("📋 COLUNAS BÁSICAS EXISTENTES NO BANCO:")
    for i, col in enumerate(colunas_basicas, 1):
        print(f"   {i:2d}. {col}")
    
    print(f"\n✅ Total de colunas básicas: {len(colunas_basicas)}")
    
    # Extrair colunas do modelo
    print("\n🔍 EXTRAINDO COLUNAS DO MODELO PYTHON...")
    colunas_modelo = extrair_colunas_modelo()
    
    if not colunas_modelo:
        print("❌ Não foi possível extrair colunas do modelo")
        return
    
    print("📋 COLUNAS DEFINIDAS NO MODELO USUARIO:")
    for i, col in enumerate(colunas_modelo, 1):
        status = "✅" if col['nome'] in colunas_basicas else "❌"
        print(f"   {i:2d}. {status} {col['nome']} ({col['tipo']})")
    
    # Gerar comandos SQL
    print("\n🔧 GERANDO COMANDOS SQL PARA COLUNAS FALTANTES...")
    comandos_sql, colunas_faltantes = gerar_sql_adicionar_colunas(colunas_modelo, colunas_basicas)
    
    if not colunas_faltantes:
        print("✅ TODAS AS COLUNAS JÁ EXISTEM NO BANCO!")
        return
    
    print(f"\n❌ ENCONTRADAS {len(colunas_faltantes)} COLUNAS FALTANTES:")
    for col in colunas_faltantes:
        print(f"   - {col['nome']} ({col['tipo']})")
    
    print(f"\n📜 COMANDOS SQL PARA EXECUTAR NO BANCO:")
    print("=" * 50)
    for i, sql in enumerate(comandos_sql, 1):
        print(f"-- {i}. Adicionar coluna {colunas_faltantes[i-1]['nome']}")
        print(sql)
        print()
    
    # Salvar em arquivo
    with open('adicionar_colunas.sql', 'w', encoding='utf-8') as f:
        f.write("-- COMANDOS SQL PARA ADICIONAR COLUNAS FALTANTES\n")
        f.write("-- Gerado automaticamente em 22/07/2025\n\n")
        for i, sql in enumerate(comandos_sql, 1):
            f.write(f"-- {i}. Adicionar coluna {colunas_faltantes[i-1]['nome']}\n")
            f.write(sql + "\n\n")
    
    print("💾 Comandos salvos em: adicionar_colunas.sql")
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Acesse o painel do Render PostgreSQL")
    print("2. Execute os comandos SQL acima")
    print("3. Faça um novo deploy da aplicação")
    print("4. Teste o cadastro novamente")
    
    print(f"\n📊 RESUMO:")
    print(f"   - Colunas no modelo: {len(colunas_modelo)}")
    print(f"   - Colunas existentes: {len(colunas_basicas)}")
    print(f"   - Colunas faltantes: {len(colunas_faltantes)}")

if __name__ == "__main__":
    main()
