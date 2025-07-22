"""
🔍 DIAGNÓSTICO DE COLUNAS - L7NUTRI
Script para verificar diferenças entre modelo Python e tabela real do banco

Data: 22/07/2025
Autor: Sistema de Prevenção de Erros
"""

import os
import sys
from datetime import datetime

def verificar_colunas_modelo_vs_banco():
    """
    Compara colunas definidas no modelo Python com as existentes no banco
    """
    print("🔍 DIAGNÓSTICO DE COLUNAS - MODELO vs BANCO")
    print("=" * 60)
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print()
    
    # Colunas definidas no modelo Usuario (app.py)
    colunas_modelo = [
        'id', 'nome', 'email', 'username', 'password',
        'idade', 'sexo', 'peso', 'altura', 'nivel_atividade',
        # 'fator_atividade',  # REMOVIDA TEMPORARIAMENTE
        'objetivo', 'email_verificado', 'token_verificacao', 
        'token_expiracao', 'data_criacao', 'ultimo_login',
        'onboarding_completo', 'questionario_respondido'
    ]
    
    print("📋 COLUNAS NO MODELO PYTHON:")
    for i, coluna in enumerate(colunas_modelo, 1):
        print(f"   {i:2d}. {coluna}")
    
    print(f"\n✅ Total de colunas no modelo: {len(colunas_modelo)}")
    
    print("\n⚠️  COLUNAS REMOVIDAS TEMPORARIAMENTE:")
    print("   - fator_atividade (não existe na tabela real)")
    
    print("\n🎯 INSTRUÇÕES PARA VERIFICAR BANCO:")
    print("1. Acesse: https://dashboard.render.com/")
    print("2. Vá em PostgreSQL Database")
    print("3. Conecte via Web Shell ou External Connection")
    print("4. Execute: \\d usuario")
    print("5. Compare as colunas listadas com as do modelo acima")
    
    print("\n💡 COMO ADICIONAR COLUNA FATOR_ATIVIDADE:")
    print("```sql")
    print("ALTER TABLE usuario ADD COLUMN fator_atividade REAL;")
    print("```")
    
    print("\n🔧 APÓS ADICIONAR A COLUNA:")
    print("1. Descomente a linha no modelo Usuario:")
    print("   # fator_atividade = db.Column(db.Float)")
    print("2. Descomente a função salvar_fator_atividade()")
    print("3. Remova os getattr() e volte para usuario.fator_atividade")
    
    print("\n" + "=" * 60)
    print("🎯 STATUS ATUAL: Sistema funcional sem fator_atividade")
    print("🚀 PRÓXIMO PASSO: Testar cadastro/login")

if __name__ == "__main__":
    verificar_colunas_modelo_vs_banco()
