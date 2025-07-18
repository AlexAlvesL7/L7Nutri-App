#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para preparar deploy no Render
"""

import os
import shutil
import zipfile

def criar_deploy_render():
    """
    Cria pasta com arquivos otimizados para Render
    """
    print("=== PREPARANDO DEPLOY RENDER ===")
    
    # Criar pasta de deploy
    deploy_path = "deploy_render"
    if os.path.exists(deploy_path):
        shutil.rmtree(deploy_path)
    os.makedirs(deploy_path)
    
    # Arquivos essenciais para Render
    arquivos_essenciais = [
        'main.py',          # Aplicação principal
        'requirements.txt', # Dependências
        'Procfile',         # Configuração do servidor
        'DEPLOY_RENDER.md'  # Documentação
    ]
    
    # Copiar arquivos essenciais
    for arquivo in arquivos_essenciais:
        if os.path.exists(arquivo):
            shutil.copy2(arquivo, deploy_path)
            print(f"✅ Copiado: {arquivo}")
    
    # Copiar pasta templates
    if os.path.exists('templates'):
        shutil.copytree('templates', os.path.join(deploy_path, 'templates'))
        print("✅ Copiado: templates/")
    
    # Criar arquivo ZIP
    with zipfile.ZipFile('L7Nutri_Render.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deploy_path)
                zipf.write(file_path, arcname)
    
    print(f"\n🎉 DEPLOY RENDER PREPARADO!")
    print(f"📁 Pasta: {deploy_path}/")
    print(f"📦 Arquivo ZIP: L7Nutri_Render.zip")
    print(f"\n📋 PRÓXIMOS PASSOS:")
    print(f"1. Clique em 'New Web Service' no Render")
    print(f"2. Conecte seu repositório GitHub")
    print(f"3. Configure as variáveis de ambiente")
    print(f"4. Deploy automático!")
    
    return True

if __name__ == '__main__':
    criar_deploy_render()
