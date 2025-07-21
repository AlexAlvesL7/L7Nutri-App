#!/usr/bin/env python3
"""
Script para verificar problemas de indentação no app.py
"""

def verificar_indentacao(arquivo):
    """Verifica problemas de indentação em um arquivo Python"""
    problemas = []
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    for i, linha in enumerate(linhas, 1):
        # Remover quebras de linha para análise
        linha_clean = linha.rstrip('\n\r')
        
        # Verificar se há mistura de tabs e espaços
        if '\t' in linha and '    ' in linha:
            problemas.append(f"Linha {i}: Mistura de tabs e espaços")
        
        # Verificar indentação estranha (não múltiplo de 4)
        espacos_iniciais = len(linha) - len(linha.lstrip(' '))
        if espacos_iniciais > 0 and espacos_iniciais % 4 != 0:
            problemas.append(f"Linha {i}: Indentação {espacos_iniciais} espaços (não múltiplo de 4)")
        
        # Verificar linhas muito indentadas (possível problema)
        if espacos_iniciais > 24:  # Mais de 6 níveis de indentação
            problemas.append(f"Linha {i}: Indentação excessiva ({espacos_iniciais} espaços)")
    
    return problemas

def main():
    print("🔍 VERIFICANDO INDENTAÇÃO DO app.py")
    print("=" * 50)
    
    try:
        problemas = verificar_indentacao('app.py')
        
        if not problemas:
            print("✅ Nenhum problema de indentação encontrado!")
        else:
            print(f"❌ {len(problemas)} problemas encontrados:")
            for problema in problemas[:10]:  # Mostrar apenas os primeiros 10
                print(f"  - {problema}")
            
            if len(problemas) > 10:
                print(f"  ... e mais {len(problemas) - 10} problemas")
    
    except Exception as e:
        print(f"❌ Erro ao verificar arquivo: {e}")
    
    print("\n" + "=" * 50)
    
    # Tentar compilar
    try:
        import py_compile
        py_compile.compile('app.py', doraise=True)
        print("✅ Arquivo compila sem erros de sintaxe!")
    except py_compile.PyCompileError as e:
        print(f"❌ Erro de sintaxe: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
