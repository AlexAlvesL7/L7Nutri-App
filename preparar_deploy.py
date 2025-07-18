#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para preparar arquivos finais para deploy Hostinger
"""

import os
import shutil
import zipfile

def criar_pasta_deploy():
    """
    Cria pasta com arquivos limpos para deploy
    """
    print("=== PREPARANDO DEPLOY HOSTINGER ===")
    
    # Criar pasta de deploy
    deploy_path = "deploy_hostinger"
    if os.path.exists(deploy_path):
        shutil.rmtree(deploy_path)
    os.makedirs(deploy_path)
    
    # Arquivos essenciais
    arquivos_essenciais = [
        'app.py',
        'requirements.txt',
        '.env',
        'DEPLOY_FINAL.md'
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
    
    # Copiar pasta static se existir
    if os.path.exists('static'):
        shutil.copytree('static', os.path.join(deploy_path, 'static'))
        print("✅ Copiado: static/")
    
    # Criar arquivo ZIP
    with zipfile.ZipFile('L7Nutri_Deploy.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deploy_path)
                zipf.write(file_path, arcname)
                
    print(f"\n🎉 DEPLOY PREPARADO COM SUCESSO!")
    print(f"📁 Pasta: {deploy_path}/")
    print(f"📦 Arquivo ZIP: L7Nutri_Deploy.zip")
    print(f"\n📋 INSTRUÇÕES:")
    print(f"1. Extrair L7Nutri_Deploy.zip na pasta /public_html da Hostinger")
    print(f"2. Configurar aplicação Python no painel")
    print(f"3. Instalar dependências: pip install -r requirements.txt")
    print(f"4. Testar: https://seudominio.com/")
    
    return True

if __name__ == '__main__':
    criar_pasta_deploy()
